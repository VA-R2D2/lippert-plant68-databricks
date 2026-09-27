# Databricks notebook source
dbutils.widgets.text("source_table", "")

source_table = dbutils.widgets.get("source_table")

if not source_table:
    raise ValueError("Set the source_table widget before running this notebook.")

df = spark.table(source_table)

display(df.limit(20))
display(df.describe())
print(f"Row count: {df.count()}")
