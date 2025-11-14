#!/usr/bin/env python3
"""Check KOL profiles table schema"""

import os
import psycopg2

# Use public database URL
database_url = "postgresql://postgres:IIhZsyFLGLWQRcDrXGWsEQqPGPijfqJo@yamabiko.proxy.rlwy.net:17910/railway"

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    print("=" * 70)
    print("📊 Checking kol_profiles table schema...")
    print("=" * 70)

    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'kol_profiles'
        );
    """)

    exists = cursor.fetchone()[0]

    if not exists:
        print("❌ Table 'kol_profiles' does not exist!")
    else:
        print("✅ Table 'kol_profiles' exists")

        # Get column information
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'kol_profiles'
            ORDER BY ordinal_position;
        """)

        columns = cursor.fetchall()
        print("\n📋 Columns in kol_profiles:")
        print("-" * 70)
        for col_name, data_type, nullable in columns:
            print(f"  • {col_name:20} | {data_type:20} | Nullable: {nullable}")

        # Get sample data
        cursor.execute("SELECT COUNT(*) FROM kol_profiles;")
        count = cursor.fetchone()[0]
        print(f"\n📈 Total rows: {count}")

        if count > 0:
            cursor.execute("SELECT * FROM kol_profiles LIMIT 3;")
            rows = cursor.fetchall()
            print("\n📝 Sample data (first 3 rows):")
            print("-" * 70)
            for row in rows:
                print(f"  {row}")

    cursor.close()
    conn.close()
    print("=" * 70)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
