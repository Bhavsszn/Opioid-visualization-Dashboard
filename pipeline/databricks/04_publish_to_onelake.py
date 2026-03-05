# pipeline/databricks/04_publish_to_onelake.py
# Goal: export GOLD tables to a folder that Fabric can import (Parquet is easiest).

from pyspark.sql import functions as F

GOLD_STATE_YEAR = "opioid.gold_state_year"
GOLD_STATE_LATEST = "opioid.gold_state_latest"

# Choose a publish path you can move into OneLake later.
# If you have ADLS Gen2, use abfss://... (best).
# If not, for a portfolio demo use DBFS and manually upload the files into Fabric Lakehouse Files.
PUBLISH_BASE = "dbfs:/FileStore/opioid/publish"  # change later to abfss://... if you have ADLS

state_year = spark.table(GOLD_STATE_YEAR)
state_latest = spark.table(GOLD_STATE_LATEST)

# Write partitioned parquet for efficient BI reads
(state_year
 .repartition("year")
 .write.mode("overwrite")
 .format("parquet")
 .save(f"{PUBLISH_BASE}/gold_state_year_parquet"))

(state_latest
 .write.mode("overwrite")
 .format("parquet")
 .save(f"{PUBLISH_BASE}/gold_state_latest_parquet"))

print("✅ Published parquet to:")
print(f"{PUBLISH_BASE}/gold_state_year_parquet")
print(f"{PUBLISH_BASE}/gold_state_latest_parquet")
