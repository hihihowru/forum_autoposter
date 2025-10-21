#!/usr/bin/env python3
"""
Migration script to add trigger_config and schedule_config columns to schedule_tasks table
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False

    print("🔄 Connecting to database...")

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("✅ Connected to database")

        # Check if columns already exist
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'schedule_tasks'
              AND column_name IN ('trigger_config', 'schedule_config')
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]

        if 'trigger_config' in existing_columns and 'schedule_config' in existing_columns:
            print("✅ Columns already exist, no migration needed")
            return True

        print(f"📝 Existing columns: {existing_columns}")
        print("🔄 Adding missing columns...")

        # Add columns
        cursor.execute("""
            ALTER TABLE schedule_tasks
            ADD COLUMN IF NOT EXISTS trigger_config JSONB DEFAULT '{}',
            ADD COLUMN IF NOT EXISTS schedule_config JSONB DEFAULT '{}'
        """)

        conn.commit()
        print("✅ Columns added successfully")

        # Verify columns were added
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'schedule_tasks'
              AND column_name IN ('trigger_config', 'schedule_config')
        """)

        result = cursor.fetchall()
        print("\n📊 Verification:")
        for row in result:
            print(f"  - {row['column_name']}: {row['data_type']}")

        cursor.close()
        conn.close()

        print("\n✅ Migration completed successfully")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
