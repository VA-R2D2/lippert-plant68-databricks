# Databricks notebook source
# Ingest approved sample data from an on-premises SQL API into a Unity Catalog Delta table.
# Store credentials in a Databricks secret scope; do not paste tokens or passwords into this notebook.

import requests
from pyspark.sql.functions import current_timestamp

dbutils.widgets.text("source_api_url", "")
dbutils.widgets.text("target_catalog", "")
dbutils.widgets.text("target_schema", "")
dbutils.widgets.text("target_table", "")
dbutils.widgets.text("secret_scope", "")
dbutils.widgets.text("token_secret_key", "")
dbutils.widgets.text("start_date", "")
dbutils.widgets.text("end_date", "")
dbutils.widgets.text("timezone", "")
dbutils.widgets.text("records_json_path", "data")

source_api_url = dbutils.widgets.get("source_api_url")
target_catalog = dbutils.widgets.get("target_catalog")
target_schema = dbutils.widgets.get("target_schema")
target_table = dbutils.widgets.get("target_table")
secret_scope = dbutils.widgets.get("secret_scope")
token_secret_key = dbutils.widgets.get("token_secret_key")
start_date = dbutils.widgets.get("start_date")
end_date = dbutils.widgets.get("end_date")
timezone = dbutils.widgets.get("timezone")
records_json_path = dbutils.widgets.get("records_json_path")

required = {
    "source_api_url": source_api_url,
    "target_catalog": target_catalog,
    "target_schema": target_schema,
    "target_table": target_table,
    "secret_scope": secret_scope,
    "token_secret_key": token_secret_key,
    "start_date": start_date,
    "end_date": end_date,
    "timezone": timezone,
}

missing = [name for name, value in required.items() if not value]
if missing:
    raise ValueError(f"Missing required widget values: {', '.join(missing)}")

token = dbutils.secrets.get(scope=secret_scope, key=token_secret_key)

params = {
    "startDate": start_date,
    "endDate": end_date,
    "timezone": timezone,
}

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

response = requests.get(source_api_url, headers=headers, params=params, timeout=60)
response.raise_for_status()
payload = response.json()

records = payload
for part in records_json_path.split("."):
    if part:
        records = records[part]

if not isinstance(records, list):
    raise ValueError(f"Expected records_json_path '{records_json_path}' to resolve to a JSON array.")

if not records:
    raise ValueError("The source API returned zero records for the requested sample-data window.")

df = spark.createDataFrame(records).withColumn("_ingested_at", current_timestamp())
record_count = df.count()

spark.sql(f"USE CATALOG `{target_catalog}`")
spark.sql(f"USE SCHEMA `{target_schema}`")

target_name = f"`{target_catalog}`.`{target_schema}`.`{target_table}`"

(
    df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(target_name)
)

print(f"Ingested {record_count} records into {target_name}.")
display(spark.table(target_name).limit(20))
