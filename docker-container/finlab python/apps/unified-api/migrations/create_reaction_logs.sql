-- Create reaction_logs table for tracking individual reaction attempts
CREATE TABLE IF NOT EXISTS reaction_logs (
    id SERIAL PRIMARY KEY,

    -- Article info
    article_id VARCHAR(50) NOT NULL,

    -- KOL info
    kol_serial INTEGER NOT NULL,
    kol_nickname VARCHAR(100),

    -- Reaction details
    reaction_type INTEGER DEFAULT 1, -- 1=讚, 2=噓, etc.

    -- Result
    success BOOLEAN NOT NULL,
    http_status_code INTEGER,
    error_message TEXT,

    -- Timing
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER, -- How long the API call took

    -- Hourly batch reference
    hourly_stats_id INTEGER REFERENCES hourly_reaction_stats(id) ON DELETE SET NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast queries
CREATE INDEX IF NOT EXISTS idx_reaction_logs_attempted_at ON reaction_logs(attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_reaction_logs_article_id ON reaction_logs(article_id);
CREATE INDEX IF NOT EXISTS idx_reaction_logs_kol_serial ON reaction_logs(kol_serial);
CREATE INDEX IF NOT EXISTS idx_reaction_logs_success ON reaction_logs(success);

-- Auto-delete logs older than 2 days (run this as a scheduled job or trigger)
-- DELETE FROM reaction_logs WHERE attempted_at < NOW() - INTERVAL '2 days';

COMMENT ON TABLE reaction_logs IS 'Individual reaction attempt logs, auto-deleted after 2 days';
COMMENT ON COLUMN reaction_logs.response_time_ms IS 'API response time in milliseconds';
COMMENT ON COLUMN reaction_logs.error_message IS 'Error details if success=false';
