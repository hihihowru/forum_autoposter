-- ============================================
-- Reaction Bot Database Schema Migration
-- Created: 2025-11-10
-- Purpose: Add tables for auto-like reaction bot feature
-- ============================================

-- Table 1: reaction_bot_config
-- Stores bot configuration settings
CREATE TABLE IF NOT EXISTS reaction_bot_config (
    id SERIAL PRIMARY KEY,
    enabled BOOLEAN DEFAULT false,
    reaction_percentage INT DEFAULT 100, -- 100 = 1x reactions, 200 = 2x reactions
    selected_kol_serials JSON DEFAULT '[]', -- Array of KOL serials: [201, 202, 203]
    distribution_algorithm VARCHAR(50) DEFAULT 'poisson', -- 'poisson', 'uniform', 'weighted'
    min_delay_seconds FLOAT DEFAULT 0.5, -- Minimum delay between reactions
    max_delay_seconds FLOAT DEFAULT 2.0, -- Maximum delay between reactions
    max_reactions_per_kol_per_hour INT DEFAULT 100, -- Rate limiting
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert default config
INSERT INTO reaction_bot_config (enabled, reaction_percentage, selected_kol_serials)
VALUES (false, 100, '[]')
ON CONFLICT DO NOTHING;

-- Table 2: reaction_bot_logs
-- Stores bot activity logs
CREATE TABLE IF NOT EXISTS reaction_bot_logs (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR(50) NOT NULL,
    kol_serial INT NOT NULL,
    reaction_type VARCHAR(20) DEFAULT 'like', -- 'like', 'comment', 'share'
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    response_data JSON, -- Store API response
    timestamp TIMESTAMP DEFAULT NOW(),

    -- Indexes for performance
    INDEX idx_reaction_bot_logs_article_id (article_id),
    INDEX idx_reaction_bot_logs_kol_serial (kol_serial),
    INDEX idx_reaction_bot_logs_timestamp (timestamp DESC)
);

-- Table 3: reaction_bot_batches
-- Tracks batch processing of article IDs
CREATE TABLE IF NOT EXISTS reaction_bot_batches (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL, -- e.g., "batch_2025-11-10_14-00-00"
    article_count INT DEFAULT 0,
    total_reactions INT DEFAULT 0,
    reactions_sent INT DEFAULT 0,
    reactions_failed INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_reaction_bot_batches_batch_id (batch_id),
    INDEX idx_reaction_bot_batches_status (status),
    INDEX idx_reaction_bot_batches_created_at (created_at DESC)
);

-- Table 4: reaction_bot_article_queue
-- Queue of articles waiting for reactions
CREATE TABLE IF NOT EXISTS reaction_bot_article_queue (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100),
    article_id VARCHAR(50) NOT NULL,
    assigned_reactions INT DEFAULT 0, -- Number of reactions assigned to this article
    reactions_sent INT DEFAULT 0, -- Number of reactions actually sent
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,

    -- Foreign key to batch
    CONSTRAINT fk_batch FOREIGN KEY (batch_id) REFERENCES reaction_bot_batches(batch_id) ON DELETE CASCADE,

    INDEX idx_reaction_bot_article_queue_batch_id (batch_id),
    INDEX idx_reaction_bot_article_queue_article_id (article_id),
    INDEX idx_reaction_bot_article_queue_status (status)
);

-- Table 5: reaction_bot_stats
-- Daily statistics summary
CREATE TABLE IF NOT EXISTS reaction_bot_stats (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    total_batches INT DEFAULT 0,
    total_articles_processed INT DEFAULT 0,
    total_reactions_sent INT DEFAULT 0,
    total_reactions_failed INT DEFAULT 0,
    avg_reactions_per_article FLOAT DEFAULT 0.0,
    success_rate FLOAT DEFAULT 0.0, -- Percentage of successful reactions
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_reaction_bot_stats_date (date DESC)
);

-- Trigger: Update reaction_bot_config updated_at on modification
CREATE OR REPLACE FUNCTION update_reaction_bot_config_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_reaction_bot_config_updated_at
BEFORE UPDATE ON reaction_bot_config
FOR EACH ROW
EXECUTE FUNCTION update_reaction_bot_config_updated_at();

-- Function: Calculate daily stats (to be called by cron job)
CREATE OR REPLACE FUNCTION calculate_reaction_bot_daily_stats(target_date DATE)
RETURNS VOID AS $$
DECLARE
    v_total_batches INT;
    v_total_articles INT;
    v_total_reactions_sent INT;
    v_total_reactions_failed INT;
    v_avg_reactions FLOAT;
    v_success_rate FLOAT;
BEGIN
    -- Count batches
    SELECT COUNT(*) INTO v_total_batches
    FROM reaction_bot_batches
    WHERE DATE(created_at) = target_date;

    -- Count articles
    SELECT COUNT(*) INTO v_total_articles
    FROM reaction_bot_article_queue
    WHERE DATE(created_at) = target_date;

    -- Count successful reactions
    SELECT COUNT(*) INTO v_total_reactions_sent
    FROM reaction_bot_logs
    WHERE DATE(timestamp) = target_date AND success = true;

    -- Count failed reactions
    SELECT COUNT(*) INTO v_total_reactions_failed
    FROM reaction_bot_logs
    WHERE DATE(timestamp) = target_date AND success = false;

    -- Calculate average reactions per article
    IF v_total_articles > 0 THEN
        v_avg_reactions := v_total_reactions_sent::FLOAT / v_total_articles;
    ELSE
        v_avg_reactions := 0.0;
    END IF;

    -- Calculate success rate
    IF (v_total_reactions_sent + v_total_reactions_failed) > 0 THEN
        v_success_rate := (v_total_reactions_sent::FLOAT / (v_total_reactions_sent + v_total_reactions_failed)) * 100;
    ELSE
        v_success_rate := 0.0;
    END IF;

    -- Insert or update stats
    INSERT INTO reaction_bot_stats (
        date,
        total_batches,
        total_articles_processed,
        total_reactions_sent,
        total_reactions_failed,
        avg_reactions_per_article,
        success_rate
    )
    VALUES (
        target_date,
        v_total_batches,
        v_total_articles,
        v_total_reactions_sent,
        v_total_reactions_failed,
        v_avg_reactions,
        v_success_rate
    )
    ON CONFLICT (date) DO UPDATE SET
        total_batches = EXCLUDED.total_batches,
        total_articles_processed = EXCLUDED.total_articles_processed,
        total_reactions_sent = EXCLUDED.total_reactions_sent,
        total_reactions_failed = EXCLUDED.total_reactions_failed,
        avg_reactions_per_article = EXCLUDED.avg_reactions_per_article,
        success_rate = EXCLUDED.success_rate;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON reaction_bot_config TO app_user;
-- GRANT SELECT, INSERT ON reaction_bot_logs TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON reaction_bot_batches TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON reaction_bot_article_queue TO app_user;
-- GRANT SELECT ON reaction_bot_stats TO app_user;

COMMENT ON TABLE reaction_bot_config IS 'Reaction bot configuration settings';
COMMENT ON TABLE reaction_bot_logs IS 'Individual reaction activity logs';
COMMENT ON TABLE reaction_bot_batches IS 'Batch processing tracker';
COMMENT ON TABLE reaction_bot_article_queue IS 'Queue of articles waiting for reactions';
COMMENT ON TABLE reaction_bot_stats IS 'Daily statistics summary';
