"""
Database Migration: Add trigger_type column to post_records table
"""
import psycopg2
import os

database_url = os.getenv("DATABASE_URL", "")
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgres://", 1)

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Add trigger_type column if it doesn't exist
    cursor.execute("""
        ALTER TABLE post_records 
        ADD COLUMN IF NOT EXISTS trigger_type VARCHAR(100);
    """)
    
    conn.commit()
    print("✅ Migration successful: trigger_type column added to post_records table")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()
