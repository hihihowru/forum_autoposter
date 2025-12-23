"""
Migration: Add Investment Blog Tables

Run this script to create the investment_blog_sync_state and investment_blog_articles tables.

Usage:
    DATABASE_URL="postgresql://..." python migrations/add_investment_blog_tables.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from datetime import datetime

# Get database URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/posting_management")

def run_migration():
    """Create investment blog tables"""

    print(f"🔄 Connecting to database...")
    print(f"   URL: {DATABASE_URL[:50]}...")

    engine = create_engine(DATABASE_URL)

    # SQL to create tables
    create_sync_state_table = """
    CREATE TABLE IF NOT EXISTS investment_blog_sync_state (
        id SERIAL PRIMARY KEY,
        author_id VARCHAR NOT NULL UNIQUE,
        last_seen_article_id VARCHAR,
        last_sync_at TIMESTAMP,
        articles_synced_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_investment_blog_sync_state_author_id
    ON investment_blog_sync_state(author_id);
    """

    create_articles_table = """
    CREATE TABLE IF NOT EXISTS investment_blog_articles (
        id VARCHAR PRIMARY KEY,
        author_id VARCHAR NOT NULL,
        title VARCHAR NOT NULL,
        content TEXT,
        stock_tags JSONB,
        preview_img_url VARCHAR,
        total_views INTEGER DEFAULT 0,
        cmoney_updated_at BIGINT,
        cmoney_created_at BIGINT,
        status VARCHAR DEFAULT 'pending',
        posted_at TIMESTAMP,
        posted_by VARCHAR,
        cmoney_post_id VARCHAR,
        cmoney_post_url VARCHAR,
        post_error TEXT,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_investment_blog_articles_author_id
    ON investment_blog_articles(author_id);

    CREATE INDEX IF NOT EXISTS idx_investment_blog_articles_status
    ON investment_blog_articles(status);

    CREATE INDEX IF NOT EXISTS idx_investment_blog_articles_created_at
    ON investment_blog_articles(cmoney_created_at DESC);
    """

    try:
        with engine.connect() as conn:
            # Create sync state table
            print("📋 Creating investment_blog_sync_state table...")
            conn.execute(text(create_sync_state_table))
            conn.commit()
            print("✅ investment_blog_sync_state table created")

            # Create articles table
            print("📋 Creating investment_blog_articles table...")
            conn.execute(text(create_articles_table))
            conn.commit()
            print("✅ investment_blog_articles table created")

            # Verify tables exist
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name IN ('investment_blog_sync_state', 'investment_blog_articles')
            """))
            tables = [row[0] for row in result]
            print(f"\n✅ Migration complete! Tables created: {tables}")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise


def check_tables():
    """Check if tables exist and show row counts"""
    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as conn:
            # Check sync state
            result = conn.execute(text("SELECT COUNT(*) FROM investment_blog_sync_state"))
            sync_count = result.scalar()
            print(f"📊 investment_blog_sync_state: {sync_count} rows")

            # Check articles
            result = conn.execute(text("SELECT COUNT(*) FROM investment_blog_articles"))
            articles_count = result.scalar()
            print(f"📊 investment_blog_articles: {articles_count} rows")

            # Show status breakdown
            result = conn.execute(text("""
                SELECT status, COUNT(*) as count
                FROM investment_blog_articles
                GROUP BY status
            """))
            print("\n📊 Articles by status:")
            for row in result:
                print(f"   {row[0]}: {row[1]}")

    except Exception as e:
        print(f"❌ Error checking tables: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Investment Blog Migration")
    parser.add_argument("--check", action="store_true", help="Check tables instead of migrating")
    args = parser.parse_args()

    if args.check:
        check_tables()
    else:
        run_migration()
