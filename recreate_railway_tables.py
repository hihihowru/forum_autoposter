#!/usr/bin/env python3
"""
Drop and recreate kol_profiles and schedule_tasks tables on Railway
with the correct schema from n8n-migration-project
"""

import psycopg2

RAILWAY_DB = "postgresql://postgres:IIhZsyFLGLWQRcDrXGWsEQqPGPijfqJo@yamabiko.proxy.rlwy.net:17910/railway"

print("🔄 Recreating Railway database tables with correct schema...\n")

# Connect to Railway
conn = psycopg2.connect(RAILWAY_DB)
conn.autocommit = True
cur = conn.cursor()

# Drop existing tables
print("🗑️  Dropping existing tables...")
cur.execute("DROP TABLE IF EXISTS kol_profiles CASCADE")
print("   ✅ Dropped kol_profiles")
cur.execute("DROP TABLE IF EXISTS schedule_tasks CASCADE")
print("   ✅ Dropped schedule_tasks")

# Create kol_profiles table with correct schema
print("\n📋 Creating kol_profiles table with correct schema...")
cur.execute("""
CREATE TABLE kol_profiles (
    id SERIAL PRIMARY KEY,
    serial VARCHAR(10) NOT NULL UNIQUE,
    nickname VARCHAR(100) NOT NULL,
    member_id VARCHAR(20) NOT NULL UNIQUE,
    persona VARCHAR(50) NOT NULL,
    status VARCHAR(20),
    owner VARCHAR(50),
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    whitelist BOOLEAN,
    notes TEXT,
    post_times VARCHAR(100),
    target_audience VARCHAR(50),
    interaction_threshold DOUBLE PRECISION,
    content_types VARCHAR[],
    common_terms TEXT,
    colloquial_terms TEXT,
    tone_style TEXT,
    typing_habit TEXT,
    backstory TEXT,
    expertise TEXT,
    data_source VARCHAR(100),
    prompt_persona TEXT,
    prompt_style TEXT,
    prompt_guardrails TEXT,
    prompt_skeleton TEXT,
    prompt_cta TEXT,
    prompt_hashtags TEXT,
    signature VARCHAR(100),
    emoji_pack VARCHAR(100),
    model_id VARCHAR(50),
    template_variant VARCHAR(50),
    model_temp DOUBLE PRECISION,
    max_tokens INTEGER,
    title_openers VARCHAR[],
    title_signature_patterns VARCHAR[],
    title_tail_word VARCHAR(20),
    title_banned_words VARCHAR[],
    title_style_examples VARCHAR[],
    title_retry_max INTEGER,
    tone_formal INTEGER,
    tone_emotion INTEGER,
    tone_confidence INTEGER,
    tone_urgency INTEGER,
    tone_interaction INTEGER,
    question_ratio DOUBLE PRECISION,
    content_length VARCHAR(20),
    interaction_starters VARCHAR[],
    require_finlab_api BOOLEAN,
    allow_hashtags BOOLEAN,
    created_time TIMESTAMP,
    last_updated TIMESTAMP,
    total_posts INTEGER,
    published_posts INTEGER,
    avg_interaction_rate DOUBLE PRECISION,
    best_performing_post VARCHAR(100),
    humor_probability DOUBLE PRECISION DEFAULT 0.3,
    humor_enabled BOOLEAN DEFAULT true,
    content_style_probabilities JSONB DEFAULT '{"casual": 0.4, "humorous": 0.1, "technical": 0.3, "professional": 0.2}'::jsonb,
    analysis_depth_probabilities JSONB DEFAULT '{"basic": 0.2, "detailed": 0.5, "comprehensive": 0.3}'::jsonb,
    content_length_probabilities JSONB DEFAULT '{"long": 0.3, "short": 0.1, "medium": 0.4, "extended": 0.15, "thorough": 0.0, "comprehensive": 0.05}'::jsonb
)
""")
print("   ✅ Created kol_profiles table")

# Create indexes for kol_profiles
cur.execute("CREATE INDEX ix_kol_profiles_id ON kol_profiles (id)")
print("   ✅ Created index ix_kol_profiles_id")

# Create schedule_tasks table with correct schema
print("\n📋 Creating schedule_tasks table with correct schema...")
cur.execute("""
CREATE TABLE schedule_tasks (
    schedule_id VARCHAR PRIMARY KEY,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    schedule_name VARCHAR NOT NULL,
    schedule_description TEXT,
    session_id BIGINT,
    schedule_type VARCHAR NOT NULL,
    status VARCHAR,
    interval_seconds INTEGER,
    batch_duration_hours INTEGER,
    daily_execution_time VARCHAR,
    weekdays_only BOOLEAN,
    timezone VARCHAR,
    max_posts_per_hour INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    run_count INTEGER,
    success_count INTEGER,
    failure_count INTEGER,
    total_posts_generated INTEGER,
    generation_config JSON,
    batch_info JSON,
    error_message TEXT,
    generated_post_ids JSON,
    auto_posting BOOLEAN DEFAULT false NOT NULL,
    source_type VARCHAR,
    source_batch_id VARCHAR,
    source_experiment_id VARCHAR,
    source_feature_name VARCHAR,
    created_by VARCHAR DEFAULT 'system'
)
""")
print("   ✅ Created schedule_tasks table")

# Create index for schedule_tasks
cur.execute("CREATE INDEX ix_schedule_tasks_schedule_id ON schedule_tasks (schedule_id)")
print("   ✅ Created index ix_schedule_tasks_schedule_id")

cur.close()
conn.close()

print("\n🎉 Successfully recreated tables with correct schema!")
print("   - kol_profiles: 61 columns with all constraints and indexes")
print("   - schedule_tasks: 32 columns with all constraints and indexes")
