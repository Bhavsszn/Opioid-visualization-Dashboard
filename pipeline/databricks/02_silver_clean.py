# pipeline/02_silver_clean.py (Databricks)
from pyspark.sql import functions as F

BRONZE_TABLE = "opioid.bronze_overdoses"
SILVER_TABLE = "opioid.silver_overdoses"

df = spark.table(BRONZE_TABLE)

# Example: normalize columns (adjust names to match your CSV)
# Inspect df.columns once and tweak mappings as needed.
clean = (
    df
    .withColumn("state", F.trim(F.col("state")))
    .withColumn("year", F.col("year").cast("int"))
    .withColumn("deaths", F.col("deaths").cast("double"))
    .withColumn("overdose_rate", F.col("overdose_rate").cast("double"))
    .withColumn("population", F.col("population").cast("double"))
    .filter(F.col("state").isNotNull() & (F.col("state") != ""))
    .filter(F.col("year").isNotNull())
)

clean.write.format("delta").mode("overwrite").saveAsTable(SILVER_TABLE)

display(clean.limit(10))
print("Wrote:", SILVER_TABLE)
