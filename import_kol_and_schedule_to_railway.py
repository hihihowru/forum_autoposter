#!/usr/bin/env python3
"""
Import KOL profiles and schedule tasks from exported JSON files to Railway
"""

import json
import psycopg2
from psycopg2.extras import execute_values, Json

RAILWAY_DB = "postgresql://postgres:IIhZsyFLGLWQRcDrXGWsEQqPGPijfqJo@yamabiko.proxy.rlwy.net:17910/railway"

print("🚀 Importing data to Railway...\n")

# Connect to Railway
conn = psycopg2.connect(RAILWAY_DB)
cur = conn.cursor()

# Check if KOL profiles already imported
cur.execute("SELECT COUNT(*) FROM kol_profiles")
existing_kol = cur.fetchone()[0]

if existing_kol == 0:
    # Import KOL profiles
    print("📥 Importing KOL profiles...")
    with open('/tmp/kol_profiles.json', 'r') as f:
        kol_data = [json.loads(line.strip()) for line in f if line.strip()]

    print(f"   Found {len(kol_data)} KOL profiles to import")

    # Define all columns for kol_profiles
    kol_columns = [
        'id', 'serial', 'nickname', 'member_id', 'persona', 'status', 'owner',
        'email', 'password', 'whitelist', 'notes', 'post_times', 'target_audience',
        'interaction_threshold', 'content_types', 'common_terms', 'colloquial_terms',
        'tone_style', 'typing_habit', 'backstory', 'expertise', 'data_source',
        'prompt_persona', 'prompt_style', 'prompt_guardrails', 'prompt_skeleton',
        'prompt_cta', 'prompt_hashtags', 'signature', 'emoji_pack', 'model_id',
        'template_variant', 'model_temp', 'max_tokens', 'title_openers',
        'title_signature_patterns', 'title_tail_word', 'title_banned_words',
        'title_style_examples', 'title_retry_max', 'tone_formal', 'tone_emotion',
        'tone_confidence', 'tone_urgency', 'tone_interaction', 'question_ratio',
        'content_length', 'interaction_starters', 'require_finlab_api', 'allow_hashtags',
        'created_time', 'last_updated', 'total_posts', 'published_posts',
        'avg_interaction_rate', 'best_performing_post', 'humor_probability',
        'humor_enabled', 'content_style_probabilities', 'analysis_depth_probabilities',
        'content_length_probabilities'
    ]

    # Prepare data for insertion
    kol_values = []
    for row in kol_data:
        values = []
        for col in kol_columns:
            value = row.get(col)
            # Convert JSON fields to proper format
            if col in ['content_style_probabilities', 'analysis_depth_probabilities', 'content_length_probabilities']:
                if value and isinstance(value, dict):
                    value = json.dumps(value)
            values.append(value)
        kol_values.append(tuple(values))

    # Insert KOL profiles
    insert_sql = f"""
        INSERT INTO kol_profiles ({', '.join(kol_columns)})
        VALUES %s
    """
    execute_values(cur, insert_sql, kol_values)
    conn.commit()
    print(f"   ✅ Imported {len(kol_data)} KOL profiles")
else:
    print(f"📥 KOL profiles already imported ({existing_kol} records), skipping...")

# Check if schedule tasks already imported
cur.execute("SELECT COUNT(*) FROM schedule_tasks")
existing_schedule = cur.fetchone()[0]

if existing_schedule > 0:
    print(f"\n🗑️  Clearing {existing_schedule} existing schedule tasks...")
    cur.execute("DELETE FROM schedule_tasks")
    conn.commit()
    print("   ✅ Cleared existing schedule tasks")

# Import schedule tasks
print("\n📥 Importing schedule tasks...")
with open('/tmp/schedule_tasks.json', 'r') as f:
    schedule_data = [json.loads(line.strip()) for line in f if line.strip()]

print(f"   Found {len(schedule_data)} schedule tasks to import")

# Define all columns for schedule_tasks
schedule_columns = [
    'schedule_id', 'created_at', 'updated_at', 'schedule_name', 'schedule_description',
    'session_id', 'schedule_type', 'status', 'interval_seconds', 'batch_duration_hours',
    'daily_execution_time', 'weekdays_only', 'timezone', 'max_posts_per_hour',
    'started_at', 'completed_at', 'last_run', 'next_run', 'run_count',
    'success_count', 'failure_count', 'total_posts_generated', 'generation_config',
    'batch_info', 'error_message', 'generated_post_ids', 'auto_posting',
    'source_type', 'source_batch_id', 'source_experiment_id', 'source_feature_name',
    'created_by'
]

# Insert schedule tasks one by one to handle JSON properly
insert_sql = f"""
    INSERT INTO schedule_tasks ({', '.join(schedule_columns)})
    VALUES ({', '.join(['%s'] * len(schedule_columns))})
"""

imported_count = 0
for row in schedule_data:
    values = []
    for col in schedule_columns:
        value = row.get(col)
        # Convert ALL dict/list values to JSON strings, not just specific columns
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        values.append(value)

    try:
        cur.execute(insert_sql, tuple(values))
        imported_count += 1
    except Exception as e:
        print(f"   ⚠️  Error importing schedule {row.get('schedule_id')}: {e}")
        conn.rollback()  # Rollback failed transaction
        continue

conn.commit()
print(f"   ✅ Imported {imported_count} schedule tasks")

# Verify counts
cur.execute("SELECT COUNT(*) FROM kol_profiles")
kol_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM schedule_tasks")
schedule_count = cur.fetchone()[0]

cur.close()
conn.close()

print("\n🎉 Import complete!")
print(f"   - KOL profiles in Railway: {kol_count}")
print(f"   - Schedule tasks in Railway: {schedule_count}")
