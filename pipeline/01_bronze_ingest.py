# pipeline/01_bronze_ingest.py (Databricks)
from pyspark.sql import functions as F

# CHANGE THIS to where your raw CSV lives
RAW_PATH = "dbfs:/FileStore/opioid/raw/overdoses_state_year_clean_typed.csv"

bronze = (
    spark.read.option("header", True).option("inferSchema", True).csv(RAW_PATH)
      .withColumn("ingested_at", F.current_timestamp())
)

# Write bronze Delta table
BRONZE_TABLE = "opioid.bronze_overdoses"
spark.sql("CREATE SCHEMA IF NOT EXISTS opioid")
bronze.write.format("delta").mode("overwrite").saveAsTable(BRONZE_TABLE)

display(bronze.limit(10))
print("✅ Wrote:", BRONZE_TABLE)
