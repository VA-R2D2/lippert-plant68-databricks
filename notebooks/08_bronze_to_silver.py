# Databricks notebook source
import json

from pyspark.sql.functions import col, current_timestamp, trim, when
from pyspark.sql.types import StringType

SOURCE_CATALOG = "lippert68"
SOURCE_SCHEMA = "bronze"
TARGET_CATALOG = "lippert68"
TARGET_SCHEMA = "silver"


def qualified_name(catalog: str, schema: str, table: str) -> str:
    escaped = [value.replace("`", "``") for value in (catalog, schema, table)]
    return ".".join(f"`{value}`" for value in escaped)


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
    source_frame = spark.table(source_name)
    silver_frame = source_frame

    for field in source_frame.schema.fields:
        if isinstance(field.dataType, StringType):
            column_name = field.name
            stripped = trim(col(f"`{column_name.replace('`', '``')}`"))
            silver_frame = silver_frame.withColumn(
                column_name,
                when(stripped == "", None).otherwise(stripped),
            )

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
        .saveAsTable(target_name)
    )

    summary.append(
        {
            "source_table": f"{SOURCE_CATALOG}.{SOURCE_SCHEMA}.{table_name}",
            "target_table": f"{TARGET_CATALOG}.{TARGET_SCHEMA}.{table_name}",
            "source_rows": source_rows,
            "silver_rows": silver_rows,
            "duplicates_removed": source_rows - silver_rows,
        }
    )

print(json.dumps(summary, indent=2))
dbutils.notebook.exit(json.dumps(summary))