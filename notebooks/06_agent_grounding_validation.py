# Databricks notebook source
# Validate the approved SOPs and playbooks selected for agent grounding.
dbutils.widgets.text("reference_document_table", "")

reference_document_table = dbutils.widgets.get("reference_document_table")

if not reference_document_table:
    raise ValueError("Set reference_document_table to a table or view with approved reference-document metadata.")

df = spark.table(reference_document_table)
required_columns = {"document_name", "owner", "source_uri", "approval_status"}
missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(f"Reference document table is missing required columns: {', '.join(sorted(missing_columns))}")

approved_df = df.filter("approval_status = 'approved'")

print(f"Total reference documents: {df.count()}")
print(f"Approved reference documents: {approved_df.count()}")

display(approved_df.select("document_name", "owner", "source_uri", "approval_status"))
