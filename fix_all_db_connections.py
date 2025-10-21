#!/usr/bin/env python3
"""
Script to replace all db_connection references with db_pool in main.py
"""

import re

file_path = "docker-container/finlab python/apps/unified-api/main.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all instances of "if not db_connection:" with "if not db_pool:"
content = content.replace('if not db_connection:', 'if not db_pool:')

# Replace all instances of "if db_connection:" with "if db_pool:"
content = content.replace('if db_connection:', 'if db_pool:')

# Replace "with db_connection.cursor" pattern with pool pattern
# This is more complex - we need to handle the pattern differently

# For now, let's just do the simple replacements
# The pattern "with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:"
# needs to be replaced with getting a connection from pool first

print("✅ Replaced all 'if not db_connection:' with 'if not db_pool:'")
print("✅ Replaced all 'if db_connection:' with 'if db_pool:'")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n📝 Updated {file_path}")
print("\n⚠️  WARNING: You still need to manually update cursor usage patterns!")
print("   Change: with db_connection.cursor(...) as cursor:")
print("   To:     conn = get_db_connection()")
print("           with conn.cursor(...) as cursor:")
print("           And add finally block to return connection to pool")
