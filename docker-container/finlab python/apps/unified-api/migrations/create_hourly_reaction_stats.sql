-- 小時統計表：記錄每小時的互動統計
CREATE TABLE IF NOT EXISTS hourly_reaction_stats (
    id SERIAL PRIMARY KEY,
    hour_start TIMESTAMP NOT NULL,
    hour_end TIMESTAMP NOT NULL,
    total_new_articles INT DEFAULT 0,
    total_like_attempts INT DEFAULT 0,
    successful_likes INT DEFAULT 0,
    unique_articles_liked INT DEFAULT 0,
    like_success_rate DECIMAL(5, 2) DEFAULT 0.00,
    kol_pool_serials INT[] DEFAULT '{}',
    article_ids TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(hour_start)
);

-- 建立索引加速查詢
CREATE INDEX IF NOT EXISTS idx_hourly_stats_hour_start ON hourly_reaction_stats(hour_start DESC);
CREATE INDEX IF NOT EXISTS idx_hourly_stats_created_at ON hourly_reaction_stats(created_at DESC);
