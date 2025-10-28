#!/usr/bin/env python3
"""
修復 kol_profiles 表的 ID 序列不同步問題

問題：duplicate key value violates unique constraint "kol_profiles_pkey"
原因：序列值落後於實際最大 ID

執行方式:
    方法 1 - 使用 Railway CLI:
        cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api"
        railway login
        railway run python3 scripts/fix_kol_sequence.py

    方法 2 - 手動設置 DATABASE_URL:
        export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
        python3 fix_kol_sequence.py

    方法 3 - 命令行參數:
        python3 fix_kol_sequence.py "postgresql://user:pass@host:5432/dbname"
"""

import psycopg2
import os
import sys

# 資料庫配置 - 支援多種方式獲取 DATABASE_URL
DATABASE_URL = None

# 1. 命令行參數優先
if len(sys.argv) > 1:
    DATABASE_URL = sys.argv[1]
    print(f"✅ 使用命令行參數的 DATABASE_URL")
# 2. 環境變數
elif os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"✅ 使用環境變數的 DATABASE_URL")
else:
    print("❌ 錯誤：未找到 DATABASE_URL")
    print("\n請使用以下任一方法提供 DATABASE_URL:")
    print("  1. railway run python3 scripts/fix_kol_sequence.py")
    print("  2. export DATABASE_URL='...' && python3 fix_kol_sequence.py")
    print("  3. python3 fix_kol_sequence.py 'postgresql://...'")
    sys.exit(1)

# 轉換 postgresql:// to postgres:// for psycopg2
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://", 1)

def fix_sequence():
    """修復 kol_profiles ID 序列"""
    conn = None
    try:
        # 連接資料庫
        print("🔌 連接資料庫...")
        print(f"   使用 DATABASE_URL: {DATABASE_URL[:30]}...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # 查詢當前狀況
        print("\n📊 當前狀況:")

        cursor.execute("SELECT MAX(id) FROM kol_profiles")
        max_id = cursor.fetchone()[0]
        print(f"   最大 ID: {max_id}")

        cursor.execute("SELECT last_value FROM kol_profiles_id_seq")
        seq_value = cursor.fetchone()[0]
        print(f"   序列值: {seq_value}")

        if max_id is None:
            print("\n⚠️  kol_profiles 表是空的，無需修復")
            return

        if seq_value >= max_id:
            print(f"\n✅ 序列正常！下一個 ID 將是: {seq_value + 1}")
            return

        # 修復序列
        print(f"\n🔧 修復序列... (從 {seq_value} → {max_id})")
        cursor.execute("SELECT setval('kol_profiles_id_seq', %s)", (max_id,))
        new_value = cursor.fetchone()[0]

        conn.commit()
        print(f"✅ 修復完成！下一個 ID 將是: {new_value + 1}")

        # 驗證修復
        print("\n🔍 驗證修復:")
        cursor.execute("SELECT last_value FROM kol_profiles_id_seq")
        verified_value = cursor.fetchone()[0]
        print(f"   序列值: {verified_value}")
        print(f"   最大 ID: {max_id}")

        if verified_value >= max_id:
            print("\n✅ 序列已修復！可以正常創建 KOL 了")
        else:
            print("\n❌ 修復失敗，請檢查權限")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("\n🔌 資料庫連接已關閉")

if __name__ == "__main__":
    print("=" * 80)
    print("🔧 KOL Profiles ID 序列修復工具")
    print("=" * 80)
    fix_sequence()
