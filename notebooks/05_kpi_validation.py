# Databricks notebook source
# Use this template after KPI formulas and expected sample results are approved.
dbutils.widgets.text("source_table", "")
dbutils.widgets.text("kpi_name", "")
dbutils.widgets.text("kpi_sql_expression", "")
dbutils.widgets.text("expected_result", "")

source_table = dbutils.widgets.get("source_table")
kpi_name = dbutils.widgets.get("kpi_name")
kpi_sql_expression = dbutils.widgets.get("kpi_sql_expression")
expected_result = dbutils.widgets.get("expected_result")

required = {
    "source_table": source_table,
    "kpi_name": kpi_name,
    "kpi_sql_expression": kpi_sql_expression,
    "expected_result": expected_result,
}

missing = [name for name, value in required.items() if not value]
if missing:
    raise ValueError(f"Missing required widget values: {', '.join(missing)}")

query = f"SELECT {kpi_sql_expression} AS actual_result FROM {source_table}"
actual = spark.sql(query).collect()[0]["actual_result"]

print(f"KPI: {kpi_name}")
print(f"Expected result: {expected_result}")
print(f"Actual result: {actual}")

display(spark.sql(query))
