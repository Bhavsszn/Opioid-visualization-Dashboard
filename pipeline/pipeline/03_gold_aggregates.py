# pipeline/03_gold_aggregates.py (Databricks)
from pyspark.sql import functions as F
from pyspark.sql.window import Window

SILVER_TABLE = "opioid.silver_overdoses"

GOLD_STATE_YEAR = "opioid.gold_state_year"
GOLD_STATE_LATEST = "opioid.gold_state_latest"

df = spark.table(SILVER_TABLE)

# Gold: state-year metrics (already basically this, but ensure uniqueness + ordering)
state_year = (
    df.groupBy("state", "year")
      .agg(
          F.sum("deaths").alias("deaths"),
          F.avg("overdose_rate").alias("overdose_rate"),
          F.max("population").alias("population")
      )
)

state_year.write.format("delta").mode("overwrite").saveAsTable(GOLD_STATE_YEAR)

# Gold: latest year per state
w = Window.partitionBy("state").orderBy(F.col("year").desc())
latest = (
    state_year
    .withColumn("rn", F.row_number().over(w))
    .filter(F.col("rn") == 1)
    .drop("rn")
)

latest.write.format("delta").mode("overwrite").saveAsTable(GOLD_STATE_LATEST)

display(latest.orderBy("state").limit(10))
print("✅ Wrote:", GOLD_STATE_YEAR, "and", GOLD_STATE_LATEST)
