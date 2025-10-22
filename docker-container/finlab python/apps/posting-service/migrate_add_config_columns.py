"""
Database migration script to add trigger_config and schedule_config columns
"""

import psycopg2
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection - use environment variable or default
DATABASE_URL = os.getenv("DATABASE_PRIVATE_URL") or os.getenv("DATABASE_URL") or "postgresql://postgres:password@postgres-db:5432/posting_management"

def run_migration():
    """Add trigger_config and schedule_config columns to schedule_tasks table"""
    conn = None
    try:
        logger.info("🔄 Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='schedule_tasks'
            AND column_name IN ('trigger_config', 'schedule_config')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"📋 Existing config columns: {existing_columns}")

        # Add trigger_config if not exists
        if 'trigger_config' not in existing_columns:
            logger.info("➕ Adding trigger_config column...")
            cursor.execute("""
                ALTER TABLE schedule_tasks
                ADD COLUMN trigger_config JSONB
            """)
            logger.info("✅ trigger_config column added")
        else:
            logger.info("⏭️  trigger_config column already exists")

        # Add schedule_config if not exists
        if 'schedule_config' not in existing_columns:
            logger.info("➕ Adding schedule_config column...")
            cursor.execute("""
                ALTER TABLE schedule_tasks
                ADD COLUMN schedule_config JSONB
            """)
            logger.info("✅ schedule_config column added")
        else:
            logger.info("⏭️  schedule_config column already exists")

        conn.commit()
        logger.info("🎉 Migration completed successfully!")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logger.info("🔌 Database connection closed")

if __name__ == "__main__":
    run_migration()
