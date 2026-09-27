# Databricks notebook source
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

if not catalog or not schema:
    raise ValueError("Set both catalog and schema widgets before running this notebook.")

spark.sql(f"USE CATALOG `{catalog}`")
spark.sql(f"USE SCHEMA `{schema}`")

spark.sql("""
CREATE OR REPLACE TEMP VIEW readiness_smoke_test AS
SELECT current_timestamp() AS validated_at
""")

display(spark.sql("SELECT * FROM readiness_smoke_test"))
