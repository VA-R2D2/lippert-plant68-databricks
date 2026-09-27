# Databricks notebook source
print("Databricks workspace smoke test started.")
display(spark.sql("SELECT current_timestamp() AS validated_at"))
