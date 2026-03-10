"""Databricks Bronze ingestion: raw overdose source -> bronze.overdose_raw."""

from pyspark.sql import functions as F

RAW_PATH = "dbfs:/FileStore/opioid/raw/overdoses_state_year_clean_typed.csv"

spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")

bronze_df = (
    spark.read.format("csv")
    .option("header", True)
    .option("inferSchema", True)
    .load(RAW_PATH)
    .withColumn("_ingested_at", F.current_timestamp())
    .withColumn("_source_file", F.input_file_name())
)

(
    bronze_df.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("bronze.overdose_raw")
)

print("Wrote bronze.overdose_raw")
display(bronze_df.limit(10))
