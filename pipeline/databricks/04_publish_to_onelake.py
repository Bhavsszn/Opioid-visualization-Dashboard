"""Publish Gold tables to OneLake-friendly parquet folders."""

PUBLISH_BASE = "dbfs:/FileStore/opioid/publish"

for table_name, path_suffix in [
    ("gold.state_year_overdoses", "state_year_overdoses"),
    ("gold.states_latest", "states_latest"),
    ("gold.quality_report", "quality_report"),
]:
    df = spark.table(table_name)
    (
        df.write.mode("overwrite")
        .format("parquet")
        .save(f"{PUBLISH_BASE}/{path_suffix}")
    )

print(f"Published Gold tables to {PUBLISH_BASE}")
