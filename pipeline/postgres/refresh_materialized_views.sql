-- Optional materialized view for low-latency latest lookup

CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_states_latest AS
SELECT DISTINCT ON (state)
  state,
  year,
  deaths,
  population,
  crude_rate,
  age_adjusted_rate,
  updated_at
FROM analytics.state_year_overdoses
ORDER BY state, year DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_states_latest_state ON analytics.mv_states_latest (state);

-- Refresh strategy: call after sync job completes
-- REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_states_latest;
