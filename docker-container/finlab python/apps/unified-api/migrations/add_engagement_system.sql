-- ============================================
-- Engagement Bot System Migration
-- Created: 2025-10-28
-- Purpose: Add tables for engagement bot management
-- ============================================

-- 1. Add engagement tracking columns to existing kol_profiles table
-- Note: Assumes kol_profiles table already exists with kol_serial as primary key
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS engagement_enabled BOOLEAN DEFAULT true;
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS last_engagement_at TIMESTAMP;
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS total_engagement_interactions INTEGER DEFAULT 0;
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS engagement_success_count INTEGER DEFAULT 0;
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS engagement_fail_count INTEGER DEFAULT 0;

-- Create index for engagement queries
CREATE INDEX IF NOT EXISTS idx_kol_profiles_engagement_enabled ON kol_profiles(engagement_enabled);
CREATE INDEX IF NOT EXISTS idx_kol_profiles_last_engagement ON kol_profiles(last_engagement_at);

-- 2. Create engagement_tasks table (stores engagement task configurations)
CREATE TABLE IF NOT EXISTS engagement_tasks (
    task_id SERIAL PRIMARY KEY,
    task_name VARCHAR(255) NOT NULL,
    task_description TEXT,

    -- Article source configuration
    article_source VARCHAR(50) NOT NULL CHECK (article_source IN ('manual_list', 'api_fetch', 'sql_query', 'json_file')),
    article_ids TEXT,  -- JSON array or comma-separated IDs for manual_list
    article_query TEXT,  -- SQL query or API parameters for dynamic fetch

    -- Interaction configuration
    interaction_types JSONB NOT NULL DEFAULT '[]'::JSONB,  -- ["article_reaction", "generic_comment", "comment_reaction"]
    reaction_types JSONB DEFAULT '[1, 3, 4, 5]'::JSONB,  -- Default: like, laugh, money, wow
    comment_templates JSONB DEFAULT '[]'::JSONB,  -- Array of comment templates

    -- KOL selection (uses existing KOL profiles)
    kol_serials_to_use JSONB,  -- Array of kol_serial values, null = use all with engagement_enabled=true
    max_kols_per_article INTEGER DEFAULT 5,  -- Max number of KOLs to use per article

    -- Execution configuration
    execution_mode VARCHAR(20) DEFAULT 'manual' CHECK (execution_mode IN ('manual', 'scheduled', 'immediate')),
    schedule_config JSONB,  -- Cron expression or schedule settings

    -- Rate limiting
    delay_between_interactions INTEGER DEFAULT 5,  -- Seconds between each interaction
    delay_between_articles INTEGER DEFAULT 10,  -- Seconds between processing articles

    -- Task status
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'failed')),
    last_executed_at TIMESTAMP,
    next_execution_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- Create indexes for task management
CREATE INDEX IF NOT EXISTS idx_engagement_tasks_status ON engagement_tasks(status);
CREATE INDEX IF NOT EXISTS idx_engagement_tasks_execution_mode ON engagement_tasks(execution_mode);
CREATE INDEX IF NOT EXISTS idx_engagement_tasks_next_execution ON engagement_tasks(next_execution_at);

-- 3. Create engagement_logs table (stores all interaction logs)
CREATE TABLE IF NOT EXISTS engagement_logs (
    log_id BIGSERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES engagement_tasks(task_id) ON DELETE CASCADE,
    kol_serial INTEGER REFERENCES kol_profiles(kol_serial) ON DELETE SET NULL,

    -- Article information
    article_id VARCHAR(50) NOT NULL,
    comment_index INTEGER,  -- For comment reactions

    -- Interaction details
    interaction_type VARCHAR(50) NOT NULL CHECK (interaction_type IN ('article_reaction', 'article_reaction_remove', 'comment_create', 'comment_reaction', 'comment_reaction_remove')),
    interaction_data JSONB,  -- Store emoji type, comment text, etc.

    -- Result
    success BOOLEAN NOT NULL,
    error_message TEXT,
    response_data JSONB,

    -- Timing
    executed_at TIMESTAMP DEFAULT NOW(),
    execution_duration_ms INTEGER
);

-- Create indexes for log queries
CREATE INDEX IF NOT EXISTS idx_engagement_logs_task_id ON engagement_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_engagement_logs_kol_serial ON engagement_logs(kol_serial);
CREATE INDEX IF NOT EXISTS idx_engagement_logs_article_id ON engagement_logs(article_id);
CREATE INDEX IF NOT EXISTS idx_engagement_logs_success ON engagement_logs(success);
CREATE INDEX IF NOT EXISTS idx_engagement_logs_executed_at ON engagement_logs(executed_at DESC);

-- 4. Create engagement_stats table (aggregate statistics by KOL)
CREATE TABLE IF NOT EXISTS engagement_stats (
    stat_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    kol_serial INTEGER REFERENCES kol_profiles(kol_serial) ON DELETE CASCADE,

    -- Daily statistics
    total_interactions INTEGER DEFAULT 0,
    total_reactions INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,

    -- Reaction breakdown
    reaction_like INTEGER DEFAULT 0,
    reaction_laugh INTEGER DEFAULT 0,
    reaction_money INTEGER DEFAULT 0,
    reaction_wow INTEGER DEFAULT 0,
    reaction_cry INTEGER DEFAULT 0,
    reaction_think INTEGER DEFAULT 0,
    reaction_angry INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(date, kol_serial)
);

-- Create indexes for stats queries
CREATE INDEX IF NOT EXISTS idx_engagement_stats_date ON engagement_stats(date DESC);
CREATE INDEX IF NOT EXISTS idx_engagement_stats_kol_serial ON engagement_stats(kol_serial);

-- 5. Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_engagement_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 6. Create triggers for updated_at
CREATE TRIGGER engagement_tasks_updated_at
    BEFORE UPDATE ON engagement_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_engagement_updated_at();

CREATE TRIGGER engagement_stats_updated_at
    BEFORE UPDATE ON engagement_stats
    FOR EACH ROW
    EXECUTE FUNCTION update_engagement_updated_at();

-- 7. Create view for quick engagement stats overview (using KOL profiles)
CREATE OR REPLACE VIEW engagement_overview AS
SELECT
    kp.kol_serial,
    kp.kol_email,
    kp.kol_nickname,
    kp.engagement_enabled,
    kp.total_engagement_interactions,
    kp.engagement_success_count,
    kp.engagement_fail_count,
    kp.last_engagement_at,
    COALESCE(recent.interactions_last_24h, 0) as interactions_last_24h,
    COALESCE(recent.success_last_24h, 0) as success_last_24h
FROM kol_profiles kp
LEFT JOIN (
    SELECT
        kol_serial,
        COUNT(*) as interactions_last_24h,
        SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_last_24h
    FROM engagement_logs
    WHERE executed_at >= NOW() - INTERVAL '24 hours'
    GROUP BY kol_serial
) recent ON kp.kol_serial = recent.kol_serial
WHERE kp.engagement_enabled = true
ORDER BY kp.kol_serial;

-- 8. Insert comment templates (default templates for generic comments)
INSERT INTO engagement_tasks (task_id, task_name, comment_templates, status) VALUES (0, '_default_templates',
'[
    "感謝分享！",
    "實用資訊，收藏了",
    "認同你的觀點",
    "分析得很詳細",
    "持續關注中",
    "學到了！",
    "寫得很好",
    "有道理",
    "謝謝整理",
    "支持！"
]'::JSONB, 'draft') ON CONFLICT (task_id) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Engagement system migration completed successfully!';
    RAISE NOTICE 'Enhanced kol_profiles table with engagement tracking columns';
    RAISE NOTICE 'Created tables: engagement_tasks, engagement_logs, engagement_stats';
    RAISE NOTICE 'Created view: engagement_overview';
    RAISE NOTICE 'Default comment templates inserted';
    RAISE NOTICE 'System will use existing KOL profiles for engagement bot operations';
END $$;
