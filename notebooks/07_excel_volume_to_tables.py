# Databricks notebook source
import json
import re
from pathlib import Path

import pandas as pd
from pyspark.sql.functions import current_timestamp, lit

VOLUME_PATH = "/Volumes/lippert68/default/production_scheduling_data"
TARGET_CATALOG = "lippert68"
TARGET_SCHEMA = "default"


def normalize_identifier(value: str, fallback: str) -> str:
    identifier = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip()).strip("_").lower()
    identifier = re.sub(r"_+", "_", identifier)
    if not identifier:
        identifier = fallback
    if identifier[0].isdigit():
        identifier = f"col_{identifier}"
    return identifier


def normalize_columns(columns: list[object]) -> list[str]:
    normalized = []
    occurrences: dict[str, int] = {}
    for index, column in enumerate(columns, start=1):
        base = normalize_identifier(str(column), f"column_{index}")
        occurrences[base] = occurrences.get(base, 0) + 1
        suffix = occurrences[base]
        normalized.append(base if suffix == 1 else f"{base}_{suffix}")
    return normalized


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
    worksheets = pd.read_excel(excel_file, sheet_name=None, dtype=object, engine="openpyxl")
    populated = []
    for sheet_name, frame in worksheets.items():
        frame = frame.dropna(axis="index", how="all").dropna(axis="columns", how="all")
        if not frame.empty and len(frame.columns) > 0:
            populated.append((sheet_name, frame))

    for sheet_name, frame in populated:
        table_name = normalize_identifier(excel_file.stem, "excel_data")
        if len(populated) > 1:
            table_name = f"{table_name}__{normalize_identifier(sheet_name, 'sheet')}"

        if table_name in table_names:
            raise ValueError(f"Duplicate normalized table name: {table_name}")
        table_names.add(table_name)

        frame.columns = normalize_columns(list(frame.columns))
        frame = frame.where(pd.notna(frame), None)
        for column in frame.columns:
            frame[column] = frame[column].map(lambda value: None if value is None else str(value))

        spark_frame = (
            spark.createDataFrame(frame)
            .withColumn("__source_file", lit(excel_file.name))
            .withColumn("__source_sheet", lit(sheet_name))
            .withColumn("__ingested_at", current_timestamp())
        )
        full_table_name = f"`{TARGET_CATALOG}`.`{TARGET_SCHEMA}`.`{table_name}`"
        (
            spark_frame.write
            .format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(full_table_name)
        )
        summary.append(
            {
                "source_file": excel_file.name,
                "source_sheet": sheet_name,
                "table": f"{TARGET_CATALOG}.{TARGET_SCHEMA}.{table_name}",
                "rows": spark_frame.count(),
                "columns": len(spark_frame.columns),
            }
        )

print(json.dumps(summary, indent=2))
dbutils.notebook.exit(json.dumps(summary))