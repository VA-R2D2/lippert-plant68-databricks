# Databricks notebook source
dbutils.widgets.text("source_table", "")

source_table = dbutils.widgets.get("source_table")

if not source_table:
    raise ValueError("Set the source_table widget before running this notebook.")

df = spark.table(source_table)
row_count = df.count()

print(f"Source table: {source_table}")
print(f"Row count: {row_count}")

display(df.limit(20))
display(spark.createDataFrame([(field.name, field.dataType.simpleString(), field.nullable) for field in df.schema.fields], ["column_name", "data_type", "nullable"]))
display(df.describe())
