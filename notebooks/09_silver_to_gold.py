# Databricks notebook source
import json

from pyspark.sql.functions import col, countDistinct, current_timestamp, max as spark_max
from pyspark.sql.types import (
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

SOURCE_CATALOG = "lippert68"
SOURCE_SCHEMA = "silver"
TARGET_CATALOG = "lippert68"
TARGET_SCHEMA = "gold"
TARGET_TABLE = "production_scheduling_dataset_inventory"

dbutils.widgets.text("gold_storage_root", "")
GOLD_STORAGE_ROOT = dbutils.widgets.get("gold_storage_root").strip().rstrip("/")

if not GOLD_STORAGE_ROOT:
    raise ValueError("Set gold_storage_root to the approved Gold storage path.")


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


spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{TARGET_CATALOG}`.`{TARGET_SCHEMA}`")

source_tables = sorted(
    row.tableName
    for row in spark.sql(
        f"SHOW TABLES IN `{SOURCE_CATALOG}`.`{SOURCE_SCHEMA}`"
    ).collect()
    if not row.isTemporary
)

if not source_tables:
    raise ValueError(f"No Silver tables found in {SOURCE_CATALOG}.{SOURCE_SCHEMA}")

inventory_rows = []

for table_name in source_tables:
    source_name = qualified_name(SOURCE_CATALOG, SOURCE_SCHEMA, table_name)
    frame = spark.table(source_name)
    columns = set(frame.columns)

    source_file_count = (
        frame.where(col("__source_file").isNotNull())
        .agg(countDistinct("__source_file").alias("value"))
        .first()["value"]
        if "__source_file" in columns
        else 0
    )
    source_sheet_count = (
        frame.where(col("__source_sheet").isNotNull())
        .agg(countDistinct("__source_sheet").alias("value"))
        .first()["value"]
        if "__source_sheet" in columns
        else 0
    )
    last_ingested_at = (
        frame.agg(spark_max("__ingested_at").alias("value")).first()["value"]
        if "__ingested_at" in columns
        else None
    )
    last_silver_processed_at = (
        frame.agg(spark_max("__silver_processed_at").alias("value")).first()["value"]
        if "__silver_processed_at" in columns
        else None
    )

    inventory_rows.append(
        (
            SOURCE_CATALOG,
            SOURCE_SCHEMA,
            table_name,
            frame.count(),
            len(frame.columns),
            source_file_count,
            source_sheet_count,
            last_ingested_at,
            last_silver_processed_at,
        )
    )

inventory_schema = StructType(
    [
        StructField("source_catalog", StringType(), False),
        StructField("source_schema", StringType(), False),
        StructField("table_name", StringType(), False),
        StructField("row_count", LongType(), False),
        StructField("column_count", IntegerType(), False),
        StructField("source_file_count", LongType(), False),
        StructField("source_sheet_count", LongType(), False),
        StructField("last_ingested_at", TimestampType(), True),
        StructField("last_silver_processed_at", TimestampType(), True),
    ]
)

gold_frame = spark.createDataFrame(inventory_rows, inventory_schema).withColumn(
    "__gold_processed_at", current_timestamp()
)
target_name = qualified_name(TARGET_CATALOG, TARGET_SCHEMA, TARGET_TABLE)
table_path = f"{GOLD_STORAGE_ROOT}/{TARGET_TABLE}"
validate_table_location(TARGET_CATALOG, TARGET_SCHEMA, TARGET_TABLE, table_path)

(
    gold_frame.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", table_path)
    .saveAsTable(target_name)
)

result = {
    "target_table": f"{TARGET_CATALOG}.{TARGET_SCHEMA}.{TARGET_TABLE}",
    "storage_path": table_path,
    "datasets": gold_frame.count(),
}
print(json.dumps(result, indent=2))
dbutils.notebook.exit(json.dumps(result))