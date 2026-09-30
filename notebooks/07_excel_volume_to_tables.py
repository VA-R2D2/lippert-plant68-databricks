# Databricks notebook source
import json
import io
import re
from pathlib import Path

import pandas as pd
from pyspark.sql.functions import current_timestamp, lit

TARGET_CATALOG = "lipperttech_dev"
TARGET_SCHEMA = "bronze"
LANDING_ROOT = "abfss://landing@stltdapdatalakebrnzdeus.dfs.core.windows.net/transactional/microsoft_sample"
DEFAULT_BRONZE_ROOT = "abfss://bronze@stltdapdatalakebrnzdeus.dfs.core.windows.net/microsoft sample"
HEADER_SCAN_ROWS = 3
HEADER_LOOKAHEAD_ROWS = 5
MIN_HEADER_CELLS = 2
MIN_HEADER_TEXT_RATIO = 0.6
MIN_HEADER_UNIQUE_RATIO = 0.8

dbutils.widgets.text("bronze_storage_root", DEFAULT_BRONZE_ROOT)
BRONZE_STORAGE_ROOT = (
    dbutils.widgets.get("bronze_storage_root").strip().rstrip("/")
    or DEFAULT_BRONZE_ROOT
)

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


def combine_header_band(
    frame: pd.DataFrame, start: int, depth: int
) -> list[str]:
    values_by_column = frame.iloc[start : start + depth].transpose().values.tolist()
    combined = []
    for values in values_by_column:
        parts = []
        for value in values:
            if is_nonempty_cell(value):
                text = str(value).strip()
                if not parts or text != parts[-1]:
                    parts.append(text)
        combined.append("_".join(parts))
    return combined


def is_main_subheader_band(frame: pd.DataFrame, start: int) -> bool:
    if start + 2 >= len(frame):
        return False

    main_values = list(frame.iloc[start + 1])
    subheader_values = list(frame.iloc[start + 2])
    main_count = sum(is_nonempty_cell(value) for value in main_values)
    subheader_count = sum(
        is_nonempty_cell(value) for value in subheader_values
    )
    return main_count >= MIN_HEADER_CELLS and subheader_count >= MIN_HEADER_CELLS


def is_two_row_header_band(frame: pd.DataFrame, start: int) -> bool:
    if start + 1 >= len(frame):
        return False

    first_values = list(frame.iloc[start])
    second_values = list(frame.iloc[start + 1])
    first_count = sum(is_nonempty_cell(value) for value in first_values)
    second_count = sum(is_nonempty_cell(value) for value in second_values)
    return second_count >= MIN_HEADER_CELLS and (
        first_count == 0 or first_count >= MIN_HEADER_CELLS
    )


def detect_header_band(frame: pd.DataFrame) -> tuple[int, int]:
    best_candidate: tuple[float, int, int] | None = None
    scan_limit = min(HEADER_SCAN_ROWS, len(frame))

    for start in range(min(1, scan_limit)):
        for depth in range(1, 2):
            values = combine_header_band(frame, start, depth)
            populated_indexes = [
                index
                for index, value in enumerate(values)
                if is_nonempty_cell(value)
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
            if (
                text_ratio < MIN_HEADER_TEXT_RATIO
                or unique_ratio < MIN_HEADER_UNIQUE_RATIO
            ):
                continue

            following_rows = frame.iloc[
                start + depth : start + depth + HEADER_LOOKAHEAD_ROWS,
                populated_indexes,
            ]
            minimum_supported_cells = max(1, populated_count // 2)
            supporting_rows = sum(
                sum(is_nonempty_cell(value) for value in row)
                >= minimum_supported_cells
                for row in following_rows.itertuples(index=False, name=None)
            )
            if supporting_rows == 0:
                continue

            score = (
                populated_count * 4
                + text_ratio * 3
                + unique_ratio * 2
                + min(supporting_rows, 3)
                + depth * 0.5
                - start * 0.01
            )
            if depth == 3 and is_main_subheader_band(frame, start):
                score += 1.0
            if depth == 2 and is_two_row_header_band(frame, start):
                score += 0.5
            if best_candidate is None or score > best_candidate[0]:
                best_candidate = (score, start, depth)

    if best_candidate is None:
        raise ValueError(
            f"No credible header row found in the first {scan_limit} non-empty rows."
        )

    return best_candidate[1], best_candidate[2]


def has_two_row_header_before_blank(frame: pd.DataFrame) -> bool:
    if len(frame) < 3:
        return False

    first_blank_row = next(
        (
            position
            for position in range(2, len(frame))
            if frame.iloc[position].isna().all()
        ),
        None,
    )
    if first_blank_row is None:
        return False

    header_values = combine_header_band(frame, 0, 2)
    header_count = sum(is_nonempty_cell(value) for value in header_values)
    data_after_blank = frame.iloc[first_blank_row + 1 :].dropna(
        axis="index", how="all"
    )
    return header_count >= MIN_HEADER_CELLS and not data_after_blank.empty


spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{TARGET_CATALOG}`.`{TARGET_SCHEMA}`")

excel_files = []
for landing_file in dbutils.fs.ls(LANDING_ROOT):
    if landing_file.name.lower().endswith((".xlsx", ".xlsm")):
        content = (
            spark.read.format("binaryFile")
            .load(landing_file.path)
            .select("content")
            .first()["content"]
        )
        excel_files.append((landing_file.name, bytes(content)))

if not excel_files:
    raise ValueError(f"No supported Excel files found in {LANDING_ROOT}")

summary = []
header_parse_failures = []
table_names: set[str] = set()

for excel_file_name, excel_content in excel_files:
    worksheets = pd.read_excel(
        io.BytesIO(excel_content),
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
            header_start, header_depth = detect_header_band(raw_frame)
        except ValueError as error:
            header_parse_failures.append(
                {
                    "source_file": excel_file_name,
                    "source_sheet": sheet_name,
                    "reason": str(error),
                }
            )
            continue

        header_excel_row = int(raw_frame.index[header_start]) + 1
        frame = raw_frame.iloc[header_start + header_depth :].copy()
        frame.columns = normalize_columns(
            combine_header_band(raw_frame, header_start, header_depth)
        )
        frame = frame.dropna(axis="index", how="all")
        if not frame.empty and len(frame.columns) > 0:
            populated.append((sheet_name, frame, header_excel_row))

    for sheet_name, frame, header_excel_row in populated:
        table_name = normalize_identifier(Path(excel_file_name).stem, "excel_data")
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
            .withColumn("__source_file", lit(excel_file_name))
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
                "source_file": excel_file_name,
                "source_sheet": sheet_name,
                "detected_header_row": header_excel_row,
                "table": f"{TARGET_CATALOG}.{TARGET_SCHEMA}.{table_name}",
                "storage_path": table_path,
                "rows": spark_frame.count(),
                "columns": len(spark_frame.columns),
            }
        )

print(json.dumps(summary, indent=2))
print("Header parsing failures skipped:")
print(json.dumps(header_parse_failures, indent=2))
dbutils.notebook.exit(json.dumps(summary))