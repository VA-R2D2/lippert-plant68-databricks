# Databricks notebook source
import json
import re
from pathlib import Path

import pandas as pd
from pyspark.sql.functions import current_timestamp, lit

VOLUME_PATH = "/Volumes/lippert68/default/production_scheduling_data"
TARGET_CATALOG = "lippert68"
TARGET_SCHEMA = "bronze"
HEADER_SCAN_ROWS = 25
HEADER_LOOKAHEAD_ROWS = 5
MIN_HEADER_CELLS = 2
MIN_HEADER_TEXT_RATIO = 0.6
MIN_HEADER_UNIQUE_RATIO = 0.8

dbutils.widgets.text("bronze_storage_root", "")
BRONZE_STORAGE_ROOT = dbutils.widgets.get("bronze_storage_root").strip().rstrip("/")

if not BRONZE_STORAGE_ROOT:
    raise ValueError("Set bronze_storage_root to the approved Bronze storage path.")


def normalize_identifier(value: str, fallback: str) -> str:
    identifier = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip()).strip("_").lower()
    identifier = re.sub(r"_+", "_", identifier)
    if not identifier:
        identifier = fallback
    if identifier[0].isdigit():
        identifier = f"col_{identifier}"
    return identifier


def qualified_name(catalog: str, schema: str, table: str) -> str:
    escaped = [value.replace("`", "``") for value in (catalog, schema, table)]
    return ".".join(f"`{value}`" for value in escaped)


def validate_table_location(
    catalog: str, schema: str, table: str, expected_path: str
) -> None:
    table_name = f"{catalog}.{schema}.{table}"
    if not spark.catalog.tableExists(table_name):
        return

    qualified_table = qualified_name(catalog, schema, table)
    actual_path = (
        spark.sql(f"DESCRIBE DETAIL {qualified_table}")
        .select("location")
        .first()["location"]
        .rstrip("/")
    )
    if actual_path != expected_path:
        raise ValueError(
            f"{table_name} is registered at {actual_path}, not {expected_path}."
        )


def normalize_columns(columns: list[object]) -> list[str]:
    normalized = []
    occurrences: dict[str, int] = {}
    for index, column in enumerate(columns, start=1):
        value = "" if pd.isna(column) else str(column)
        base = normalize_identifier(value, f"column_{index}")
        occurrences[base] = occurrences.get(base, 0) + 1
        suffix = occurrences[base]
        normalized.append(base if suffix == 1 else f"{base}_{suffix}")
    return normalized


def is_nonempty_cell(value: object) -> bool:
    return not pd.isna(value) and bool(str(value).strip())


def detect_header_row(frame: pd.DataFrame) -> int:
    best_candidate: tuple[float, int] | None = None
    scan_limit = min(HEADER_SCAN_ROWS, len(frame))

    for position in range(scan_limit):
        values = list(frame.iloc[position])
        populated_indexes = [
            index for index, value in enumerate(values) if is_nonempty_cell(value)
        ]
        populated_count = len(populated_indexes)
        if populated_count < MIN_HEADER_CELLS:
            continue

        labels = [str(values[index]).strip() for index in populated_indexes]
        text_ratio = sum(
            isinstance(values[index], str) for index in populated_indexes
        ) / populated_count
        normalized_labels = [
            re.sub(r"[^a-zA-Z0-9_]+", "_", label).strip("_").lower()
            for label in labels
        ]
        unique_ratio = len(set(normalized_labels)) / populated_count
        if text_ratio < MIN_HEADER_TEXT_RATIO or unique_ratio < MIN_HEADER_UNIQUE_RATIO:
            continue

        following_rows = frame.iloc[
            position + 1 : position + 1 + HEADER_LOOKAHEAD_ROWS,
            populated_indexes,
        ]
        minimum_supported_cells = max(1, populated_count // 2)
        supporting_rows = sum(
            sum(is_nonempty_cell(value) for value in row) >= minimum_supported_cells
            for row in following_rows.itertuples(index=False, name=None)
        )
        if supporting_rows == 0:
            continue

        score = (
            populated_count * 4
            + text_ratio * 3
            + unique_ratio * 2
            + min(supporting_rows, 3)
            - position * 0.01
        )
        if best_candidate is None or score > best_candidate[0]:
            best_candidate = (score, position)

    if best_candidate is None:
        raise ValueError(
            f"No credible header row found in the first {scan_limit} non-empty rows."
        )

    return best_candidate[1]


spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{TARGET_CATALOG}`.`{TARGET_SCHEMA}`")

excel_files = sorted(
    path
    for path in Path(VOLUME_PATH).iterdir()
    if path.is_file() and path.suffix.lower() in {".xlsx", ".xlsm"}
)

if not excel_files:
    raise ValueError(f"No supported Excel files found in {VOLUME_PATH}")

summary = []
table_names: set[str] = set()

for excel_file in excel_files:
    worksheets = pd.read_excel(
        excel_file,
        sheet_name=None,
        header=None,
        dtype=object,
        engine="openpyxl",
    )
    populated = []
    for sheet_name, raw_frame in worksheets.items():
        raw_frame = raw_frame.dropna(axis="index", how="all").dropna(
            axis="columns", how="all"
        )
        if raw_frame.empty or len(raw_frame.columns) == 0:
            continue

        try:
            header_position = detect_header_row(raw_frame)
        except ValueError as error:
            raise ValueError(
                f"Unable to identify a header for {excel_file.name} / {sheet_name}: {error}"
            ) from error

        header_excel_row = int(raw_frame.index[header_position]) + 1
        frame = raw_frame.iloc[header_position + 1 :].copy()
        frame.columns = normalize_columns(list(raw_frame.iloc[header_position]))
        frame = frame.dropna(axis="index", how="all")
        if not frame.empty and len(frame.columns) > 0:
            populated.append((sheet_name, frame, header_excel_row))

    for sheet_name, frame, header_excel_row in populated:
        table_name = normalize_identifier(excel_file.stem, "excel_data")
        if len(populated) > 1:
            table_name = f"{table_name}__{normalize_identifier(sheet_name, 'sheet')}"

        if table_name in table_names:
            raise ValueError(f"Duplicate normalized table name: {table_name}")
        table_names.add(table_name)

        source_row_numbers = [int(index) + 1 for index in frame.index]
        frame.columns = normalize_columns(list(frame.columns))
        frame = frame.where(pd.notna(frame), None)
        for column in frame.columns:
            frame[column] = frame[column].map(lambda value: None if value is None else str(value))
        frame["__source_row_number"] = source_row_numbers

        spark_frame = (
            spark.createDataFrame(frame)
            .withColumn("__source_file", lit(excel_file.name))
            .withColumn("__source_sheet", lit(sheet_name))
            .withColumn("__header_row", lit(header_excel_row))
            .withColumn("__ingested_at", current_timestamp())
        )
        full_table_name = qualified_name(TARGET_CATALOG, TARGET_SCHEMA, table_name)
        table_path = f"{BRONZE_STORAGE_ROOT}/{table_name}"
        validate_table_location(
            TARGET_CATALOG, TARGET_SCHEMA, table_name, table_path
        )
        (
            spark_frame.write
            .format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .option("path", table_path)
            .saveAsTable(full_table_name)
        )
        summary.append(
            {
                "source_file": excel_file.name,
                "source_sheet": sheet_name,
                "detected_header_row": header_excel_row,
                "table": f"{TARGET_CATALOG}.{TARGET_SCHEMA}.{table_name}",
                "storage_path": table_path,
                "rows": spark_frame.count(),
                "columns": len(spark_frame.columns),
            }
        )

print(json.dumps(summary, indent=2))
dbutils.notebook.exit(json.dumps(summary))