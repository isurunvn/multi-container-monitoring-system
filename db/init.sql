CREATE TABLE IF NOT EXISTS checks (
  id SERIAL PRIMARY KEY,
  container_id TEXT NOT NULL,
  fetched_time TIMESTAMPTZ NOT NULL,
  local_time TIMESTAMPTZ NOT NULL,
  drift_seconds INTEGER NOT NULL,
  http_status INTEGER NOT NULL,
  body_contains_expected BOOLEAN NOT NULL,
  ok BOOLEAN NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_checks_created_at ON checks (created_at DESC);
