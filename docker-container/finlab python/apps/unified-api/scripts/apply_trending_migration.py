#!/usr/bin/env python3
"""
Apply trending topics migration
Adds has_trending_topic, topic_id, topic_title, topic_content columns to posts table
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def apply_migration():
    """Apply the trending topics migration"""

    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not found")
        print("Please set DATABASE_URL in your environment or .env file")
        sys.exit(1)

    print(f"✅ DATABASE_URL found")

    # Parse DATABASE_URL
    result = urlparse(database_url)

    try:
        # Connect to database
        print("🔌 Connecting to database...")
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port,
            database=result.path[1:],  # Remove leading '/'
            user=result.username,
            password=result.password
        )

        print(f"✅ Connected to database: {result.path[1:]}")

        # Read migration SQL
        migration_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "migrations",
            "add_trending_topics_support.sql"
        )

        print(f"📄 Reading migration file: {migration_path}")

        with open(migration_path, 'r', encoding='utf-8') as f:
            migration_sql = f.read()

        # Execute migration
        print("🚀 Executing migration...")
        cursor = conn.cursor()

        # Split by semicolon and execute each statement
        statements = [s.strip() for s in migration_sql.split(';') if s.strip()]

        for i, statement in enumerate(statements, 1):
            if statement.strip():
                print(f"  [{i}/{len(statements)}] Executing: {statement[:60]}...")
                try:
                    cursor.execute(statement)
                    conn.commit()
                    print(f"  ✅ Success")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"  ⚠️  Already exists (skipped)")
                        conn.rollback()
                    else:
                        print(f"  ❌ Error: {e}")
                        conn.rollback()
                        raise

        # Verify columns were added
        print("\n🔍 Verifying migration...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'post_records'
            AND column_name IN ('has_trending_topic', 'topic_id', 'topic_title', 'topic_content')
            ORDER BY column_name
        """)

        columns = cursor.fetchall()

        if len(columns) == 4:
            print("✅ Migration successful! Added columns:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]}, nullable: {col[2]})")
        else:
            print(f"⚠️  Warning: Expected 4 columns, found {len(columns)}")
            for col in columns:
                print(f"   - {col[0]}")

        # Check indexes
        print("\n🔍 Checking indexes...")
        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'post_records'
            AND indexname IN ('idx_posts_has_trending_topic', 'idx_posts_topic_id')
            ORDER BY indexname
        """)

        indexes = cursor.fetchall()
        print(f"✅ Found {len(indexes)} indexes:")
        for idx in indexes:
            print(f"   - {idx[0]}")

        cursor.close()
        conn.close()

        print("\n🎉 Migration completed successfully!")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    apply_migration()
