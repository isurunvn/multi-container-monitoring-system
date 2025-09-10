-- Multi-Container Monitoring Database Schema
-- Consolidated schema with enhanced logging and monitoring capabilities

-- Main checks table with enhanced monitoring columns
CREATE TABLE IF NOT EXISTS checks (
    id SERIAL PRIMARY KEY,
    target VARCHAR(50) NOT NULL,
    status VARCHAR(10) NOT NULL,
    http_status INTEGER,
    time_drift_seconds INTEGER,
    response_time_ms INTEGER,
    fetched_time TIMESTAMPTZ,
    local_time TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Metrics table for structured metric storage
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    tags JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Performance summary view for monitoring dashboard
CREATE OR REPLACE VIEW performance_summary AS
SELECT 
    target,
    COUNT(*) as total_checks,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) as successful_checks,
    ROUND(
        (SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)) * 100, 
        2
    ) as availability_percent,
    AVG(response_time_ms) as avg_response_time_ms,
    MAX(time_drift_seconds) as max_time_drift,
    MIN(created_at) as first_check,
    MAX(created_at) as last_check
FROM checks 
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY target;

-- System health dashboard view
CREATE OR REPLACE VIEW system_health AS
SELECT 
    'overall' as metric_type,
    ROUND(AVG(
        CASE WHEN status = 'PASS' THEN 100 ELSE 0 END
    ), 2) as availability_percent,
    COUNT(*) as total_checks_last_hour,
    AVG(response_time_ms) as avg_response_time_ms,
    MAX(time_drift_seconds) as max_drift_seconds
FROM checks 
WHERE created_at > NOW() - INTERVAL '1 hour';

-- Hourly monitoring summary view
CREATE OR REPLACE VIEW hourly_summary AS
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    target,
    COUNT(*) as checks_per_hour,
    AVG(response_time_ms) as avg_response_time_ms,
    MAX(time_drift_seconds) as max_drift,
    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) as failures
FROM checks 
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', created_at), target
ORDER BY hour DESC;

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_checks_target_time ON checks (target, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_checks_status_time ON checks (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON metrics (metric_name, timestamp DESC);

-- Initialize system
INSERT INTO metrics (metric_name, metric_value, tags)
SELECT 'system_initialized', 1, '{"component": "database", "version": "consolidated"}'::jsonb
WHERE NOT EXISTS (SELECT 1 FROM metrics LIMIT 1);
