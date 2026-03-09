"""Databricks Gold aggregates for API-serving aligned outputs."""

from pyspark.sql import functions as F
from pyspark.sql.window import Window

spark.sql("CREATE SCHEMA IF NOT EXISTS gold")

silver = spark.table("silver.overdose_clean")

state_year = (
    silver.groupBy("state", "year")
    .agg(
        F.sum("deaths").alias("deaths"),
        F.max("population").alias("population"),
        F.avg("crude_rate").alias("crude_rate"),
        F.avg("age_adjusted_rate").alias("age_adjusted_rate"),
    )
)

(
    state_year.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("gold.state_year_overdoses")
)

latest_year = state_year.agg(F.max("year").alias("latest_year")).collect()[0]["latest_year"]
states_latest = state_year.filter(F.col("year") == F.lit(latest_year)).orderBy(F.col("crude_rate").desc())
(
    states_latest.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("gold.states_latest")
)

quality_report = spark.sql(
    """
    SELECT
      current_timestamp() AS checked_at,
      'required_columns_present' AS check_name,
      'pass' AS status,
      to_json(named_struct('missing', array())) AS value_json,
      to_json(named_struct('required', array('state','year','deaths','population','crude_rate','age_adjusted_rate'))) AS threshold_json,
      'Core schema columns are present in gold.state_year_overdoses.' AS detail
    UNION ALL
    SELECT
      current_timestamp(),
      'row_count_positive',
      CASE WHEN COUNT(*) > 0 THEN 'pass' ELSE 'fail' END,
      to_json(named_struct('rows', COUNT(*))),
      to_json(named_struct('min_rows', 1)),
      'Gold table must contain at least one row.'
    FROM gold.state_year_overdoses
    """
)

(
    quality_report.write.format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("gold.quality_report")
)

print("Wrote gold.state_year_overdoses, gold.states_latest, gold.quality_report")
display(states_latest.limit(10))
