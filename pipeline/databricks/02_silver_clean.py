"""Databricks Silver cleaning: bronze.overdose_raw -> silver.overdose_clean."""

from pyspark.sql import functions as F

spark.sql("CREATE SCHEMA IF NOT EXISTS silver")

raw = spark.table("bronze.overdose_raw")

clean = (
    raw.select(
        F.trim(F.col("state")).alias("state"),
        F.col("year").cast("int").alias("year"),
        F.col("deaths").cast("double").alias("deaths"),
        F.col("population").cast("double").alias("population"),
        F.col("crude_rate").cast("double").alias("crude_rate"),
        F.col("age_adjusted_rate").cast("double").alias("age_adjusted_rate"),
        F.col("_ingested_at"),
    )
    .filter(F.col("state").isNotNull() & (F.col("state") != ""))
    .filter(F.col("year").isNotNull())
    .dropDuplicates(["state", "year"])
)

(
    clean.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("silver.overdose_clean")
)

print("Wrote silver.overdose_clean")
display(clean.orderBy("year", "state").limit(10))
