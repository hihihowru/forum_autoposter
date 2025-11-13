#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查資料庫中的所有資料表
"""

import os
import psycopg2
import urllib.parse

database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:IIhZsyFLGLWQRcDrXGWsEQqPGPijfqJo@postgres.railway.internal:5432/railway')
parsed_url = urllib.parse.urlparse(database_url)

conn = psycopg2.connect(
    host=parsed_url.hostname,
    port=parsed_url.port or 5432,
    database=parsed_url.path[1:],
    user=parsed_url.username,
    password=parsed_url.password
)

cursor = conn.cursor()

# List all tables
cursor.execute('''
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
''')

tables = cursor.fetchall()

print('=' * 70)
print('All Tables in Database')
print('=' * 70)

for table in tables:
    table_name = table[0]

    # Get row count
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]

    # Get column info
    cursor.execute(f'''
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
        LIMIT 5
    ''')
    columns = cursor.fetchall()
    col_names = [c[0] for c in columns]

    status = '✅ HAS DATA' if count > 0 else '❌ EMPTY'

    print(f'\n📊 {table_name}')
    print(f'   Status: {status} ({count} rows)')
    print(f'   Columns: {", ".join(col_names)}{"..." if len(columns) >= 5 else ""}')

cursor.close()
conn.close()

print('\n' + '=' * 70)
