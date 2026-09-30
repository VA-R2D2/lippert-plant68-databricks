# Databricks notebook source
import json
import re

from pyspark.sql.functions import col, current_timestamp, trim, when
from pyspark.sql.types import StringType

SOURCE_CATALOG = "lipperttech_dev"
SOURCE_SCHEMA = "bronze"
TARGET_CATALOG = "lipperttech_dev"
TARGET_SCHEMA = "silver"
DEFAULT_SILVER_ROOT = "abfss://silver@stltdapdatalakeslvrdeus.dfs.core.windows.net/microsoft_sample"

dbutils.widgets.text("silver_storage_root", DEFAULT_SILVER_ROOT)
SILVER_STORAGE_ROOT = (
    dbutils.widgets.get("silver_storage_root").strip().rstrip("/")
    or DEFAULT_SILVER_ROOT
)

if not SILVER_STORAGE_ROOT:
    raise ValueError("Set silver_storage_root to the approved Silver storage path.")


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


def sanitize_column_name(column_name: str, fallback: str) -> str:
    sanitized = re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", column_name)
    return sanitized or fallback


spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{TARGET_CATALOG}`.`{TARGET_SCHEMA}`")

source_tables = sorted(
    row.tableName
    for row in spark.sql(
        f"SHOW TABLES IN `{SOURCE_CATALOG}`.`{SOURCE_SCHEMA}`"
    ).collect()
    if not row.isTemporary
)

if not source_tables:
    raise ValueError(f"No Bronze tables found in {SOURCE_CATALOG}.{SOURCE_SCHEMA}")

summary = []

for table_name in source_tables:
    source_name = qualified_name(SOURCE_CATALOG, SOURCE_SCHEMA, table_name)
    target_name = qualified_name(TARGET_CATALOG, TARGET_SCHEMA, table_name)
    table_path = f"{SILVER_STORAGE_ROOT}/{table_name}"
    validate_table_location(TARGET_CATALOG, TARGET_SCHEMA, table_name, table_path)
    bronze_frame = spark.table(source_name)
    source_columns = [
        column_name
        for column_name in bronze_frame.columns
        if not column_name.startswith("__")
    ]
    if not source_columns:
        raise ValueError(
            f"No non-metadata Bronze columns found in {SOURCE_CATALOG}.{SOURCE_SCHEMA}.{table_name}"
        )
    source_frame = bronze_frame.select(
        *[
            col(f"`{column_name.replace('`', '``')}`")
            for column_name in source_columns
        ]
    )

    used_column_names: set[str] = set()
    renamed_columns = []
    for index, column_name in enumerate(source_frame.columns, start=1):
        sanitized_name = sanitize_column_name(column_name, f"column_{index}")
        base_name = sanitized_name
        suffix = 2
        while sanitized_name in used_column_names:
            sanitized_name = f"{base_name}_{suffix}"
            suffix += 1
        used_column_names.add(sanitized_name)
        renamed_columns.append(
            col(f"`{column_name.replace('`', '``')}`").alias(sanitized_name)
        )

    silver_frame = source_frame.select(*renamed_columns)

    cleaned_columns = []
    for field in silver_frame.schema.fields:
        column_name = field.name
        column_ref = col(f"`{column_name.replace('`', '``')}`")
        if isinstance(field.dataType, StringType):
            column_ref = when(trim(column_ref) == "", None).otherwise(
                trim(column_ref)
            )
        cleaned_columns.append(column_ref.alias(column_name))
    silver_frame = silver_frame.select(*cleaned_columns)

    source_rows = source_frame.count()
    silver_frame = silver_frame.dropDuplicates().withColumn(
        "__silver_processed_at", current_timestamp()
    )
    silver_rows = silver_frame.count()

    (
        silver_frame.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .option("path", table_path)
        .saveAsTable(target_name)
    )

    summary.append(
        {
            "source_table": f"{SOURCE_CATALOG}.{SOURCE_SCHEMA}.{table_name}",
            "target_table": f"{TARGET_CATALOG}.{TARGET_SCHEMA}.{table_name}",
            "storage_path": table_path,
            "source_rows": source_rows,
            "silver_rows": silver_rows,
            "duplicates_removed": source_rows - silver_rows,
        }
    )

print(json.dumps(summary, indent=2))
dbutils.notebook.exit(json.dumps(summary))