#!/usr/bin/env python3
"""
Migrate KOL profiles and schedule tasks from n8n-migration-project to Railway
"""

import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database connections
# Docker container is exposing port 5432 to localhost:5432
# So we can connect to it the same way, it will use the Docker container's database
LOCAL_DOCKER_DB = "postgresql://postgres:password@localhost:5432/posting_management"
RAILWAY_DB = "postgresql://postgres:IIhZsyFLGLWQRcDrXGWsEQqPGPijfqJo@yamabiko.proxy.rlwy.net:17910/railway"

print("🔍 Checking database connections...")

def export_kol_profiles():
    """Export KOL profiles from local Docker database"""
    print("📤 Exporting KOL profiles from n8n-migration-project...")

    conn = psycopg2.connect(LOCAL_DOCKER_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM kol_profiles ORDER BY serial")
    kol_profiles = cur.fetchall()

    # Convert to list of dicts
    profiles = [dict(row) for row in kol_profiles]

    print(f"✅ Exported {len(profiles)} KOL profiles")

    cur.close()
    conn.close()

    return profiles

def export_schedule_tasks():
    """Export schedule tasks from local Docker database"""
    print("📤 Exporting schedule tasks from n8n-migration-project...")

    conn = psycopg2.connect(LOCAL_DOCKER_DB)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM schedule_tasks ORDER BY created_at DESC")
    tasks = cur.fetchall()

    # Convert to list of dicts
    tasks_list = [dict(row) for row in tasks]

    print(f"✅ Exported {len(tasks_list)} schedule tasks")

    cur.close()
    conn.close()

    return tasks_list

def import_kol_profiles_to_railway(profiles):
    """Import KOL profiles to Railway database"""
    print("📥 Importing KOL profiles to Railway...")

    conn = psycopg2.connect(RAILWAY_DB)
    cur = conn.cursor()

    # Clear existing KOL profiles
    cur.execute("DELETE FROM kol_profiles")
    print("🗑️  Cleared existing KOL profiles")

    # Insert new profiles
    insert_sql = """
        INSERT INTO kol_profiles (
            id, serial, nickname, member_id, persona, status, owner, email, password,
            whitelist, notes, post_times, target_audience, interaction_threshold,
            content_types, common_terms, colloquial_terms, tone_style, typing_habit,
            backstory, expertise, data_source, prompt_persona, prompt_style,
            prompt_guardrails, prompt_skeleton, prompt_cta, prompt_hashtags,
            signature, emoji_pack, model_id, template_variant, model_temp,
            max_tokens, title_openers, title_signature_patterns, title_tail_word,
            title_banned_words, title_style_examples, title_retry_max, tone_formal,
            tone_emotion, tone_confidence, tone_urgency, tone_interaction,
            question_ratio, content_length, interaction_starters, require_finlab_api,
            allow_hashtags, created_time, last_updated, total_posts, published_posts,
            avg_interaction_rate, best_performing_post, humor_probability,
            humor_enabled, content_style_probabilities, analysis_depth_probabilities,
            content_length_probabilities
        ) VALUES (
            %(id)s, %(serial)s, %(nickname)s, %(member_id)s, %(persona)s, %(status)s,
            %(owner)s, %(email)s, %(password)s, %(whitelist)s, %(notes)s, %(post_times)s,
            %(target_audience)s, %(interaction_threshold)s, %(content_types)s,
            %(common_terms)s, %(colloquial_terms)s, %(tone_style)s, %(typing_habit)s,
            %(backstory)s, %(expertise)s, %(data_source)s, %(prompt_persona)s,
            %(prompt_style)s, %(prompt_guardrails)s, %(prompt_skeleton)s, %(prompt_cta)s,
            %(prompt_hashtags)s, %(signature)s, %(emoji_pack)s, %(model_id)s,
            %(template_variant)s, %(model_temp)s, %(max_tokens)s, %(title_openers)s,
            %(title_signature_patterns)s, %(title_tail_word)s, %(title_banned_words)s,
            %(title_style_examples)s, %(title_retry_max)s, %(tone_formal)s,
            %(tone_emotion)s, %(tone_confidence)s, %(tone_urgency)s, %(tone_interaction)s,
            %(question_ratio)s, %(content_length)s, %(interaction_starters)s,
            %(require_finlab_api)s, %(allow_hashtags)s, %(created_time)s,
            %(last_updated)s, %(total_posts)s, %(published_posts)s,
            %(avg_interaction_rate)s, %(best_performing_post)s, %(humor_probability)s,
            %(humor_enabled)s, %(content_style_probabilities)s,
            %(analysis_depth_probabilities)s, %(content_length_probabilities)s
        )
    """

    cur.executemany(insert_sql, profiles)
    conn.commit()

    print(f"✅ Imported {len(profiles)} KOL profiles to Railway")

    cur.close()
    conn.close()

def import_schedule_tasks_to_railway(tasks):
    """Import schedule tasks to Railway database"""
    print("📥 Importing schedule tasks to Railway...")

    conn = psycopg2.connect(RAILWAY_DB)
    cur = conn.cursor()

    # Clear existing schedule tasks
    cur.execute("DELETE FROM schedule_tasks")
    print("🗑️  Cleared existing schedule tasks")

    # Insert new tasks
    insert_sql = """
        INSERT INTO schedule_tasks (
            schedule_id, created_at, updated_at, schedule_name, schedule_description,
            session_id, schedule_type, status, interval_seconds, batch_duration_hours,
            daily_execution_time, weekdays_only, timezone, max_posts_per_hour,
            started_at, completed_at, last_run, next_run, run_count, success_count,
            failure_count, total_posts_generated, generation_config, batch_info,
            error_message, generated_post_ids, auto_posting, source_type,
            source_batch_id, source_experiment_id, source_feature_name, created_by
        ) VALUES (
            %(schedule_id)s, %(created_at)s, %(updated_at)s, %(schedule_name)s,
            %(schedule_description)s, %(session_id)s, %(schedule_type)s, %(status)s,
            %(interval_seconds)s, %(batch_duration_hours)s, %(daily_execution_time)s,
            %(weekdays_only)s, %(timezone)s, %(max_posts_per_hour)s, %(started_at)s,
            %(completed_at)s, %(last_run)s, %(next_run)s, %(run_count)s,
            %(success_count)s, %(failure_count)s, %(total_posts_generated)s,
            %(generation_config)s, %(batch_info)s, %(error_message)s,
            %(generated_post_ids)s, %(auto_posting)s, %(source_type)s,
            %(source_batch_id)s, %(source_experiment_id)s, %(source_feature_name)s,
            %(created_by)s
        )
    """

    # Process tasks to handle JSON fields
    processed_tasks = []
    for task in tasks:
        task_dict = dict(task)

        # Convert JSON fields to strings if they're dicts/lists
        for json_field in ['generation_config', 'batch_info', 'generated_post_ids']:
            if task_dict.get(json_field) and isinstance(task_dict[json_field], (dict, list)):
                task_dict[json_field] = json.dumps(task_dict[json_field])

        processed_tasks.append(task_dict)

    cur.executemany(insert_sql, processed_tasks)
    conn.commit()

    print(f"✅ Imported {len(tasks)} schedule tasks to Railway")

    cur.close()
    conn.close()

def main():
    """Main migration function"""
    print("🚀 Starting migration from n8n-migration-project to Railway...\n")

    try:
        # Export data
        kol_profiles = export_kol_profiles()
        schedule_tasks = export_schedule_tasks()

        print()

        # Import to Railway
        import_kol_profiles_to_railway(kol_profiles)
        import_schedule_tasks_to_railway(schedule_tasks)

        print("\n🎉 Migration complete!")
        print(f"   - {len(kol_profiles)} KOL profiles migrated")
        print(f"   - {len(schedule_tasks)} schedule tasks migrated")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
