#!/usr/bin/env python3
"""Check if articles were saved to Railway database"""

import psycopg2
import json

# Use public database URL
database_url = "postgresql://postgres:IIhZsyFLGLWQRcDrXGWsEQqPGPijfqJo@yamabiko.proxy.rlwy.net:17910/railway"

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    print("=" * 70)
    print("📊 Checking hourly_reaction_stats table...")
    print("=" * 70)

    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'hourly_reaction_stats'
        );
    """)
    exists = cursor.fetchone()[0]

    if not exists:
        print("❌ Table 'hourly_reaction_stats' does not exist!")
    else:
        print("✅ Table 'hourly_reaction_stats' exists")

        # Get row count
        cursor.execute("SELECT COUNT(*) FROM hourly_reaction_stats;")
        count = cursor.fetchone()[0]
        print(f"\n📈 Total rows: {count}")

        if count > 0:
            # Get latest record
            cursor.execute("""
                SELECT
                    id,
                    hour_start,
                    hour_end,
                    total_articles,
                    total_attempts,
                    successful_likes,
                    unique_articles,
                    kol_serials,
                    article_ids,
                    created_at
                FROM hourly_reaction_stats
                ORDER BY hour_start DESC
                LIMIT 1;
            """)

            row = cursor.fetchone()
            if row:
                print("\n📝 Latest record:")
                print("-" * 70)
                print(f"  ID: {row[0]}")
                print(f"  Hour Start: {row[1]}")
                print(f"  Hour End: {row[2]}")
                print(f"  Total Articles: {row[3]}")
                print(f"  Total Attempts: {row[4]}")
                print(f"  Successful Likes: {row[5]}")
                print(f"  Unique Articles: {row[6]}")
                print(f"  KOL Serials: {row[7]}")

                # Parse article_ids JSON
                article_ids = json.loads(row[8]) if row[8] else []
                print(f"  Article IDs (count): {len(article_ids)}")
                if len(article_ids) > 0:
                    print(f"  First 5 Article IDs: {article_ids[:5]}")

                print(f"  Created At: {row[9]}")

            # Show all records
            cursor.execute("""
                SELECT
                    hour_start,
                    total_articles,
                    successful_likes,
                    unique_articles
                FROM hourly_reaction_stats
                ORDER BY hour_start DESC
                LIMIT 10;
            """)

            rows = cursor.fetchall()
            if rows:
                print("\n📋 Recent 10 records:")
                print("-" * 70)
                print(f"{'Hour Start':<20} {'Articles':<10} {'Likes':<10} {'Unique':<10}")
                print("-" * 70)
                for row in rows:
                    print(f"{str(row[0]):<20} {row[1]:<10} {row[2]:<10} {row[3]:<10}")

    cursor.close()
    conn.close()
    print("=" * 70)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
