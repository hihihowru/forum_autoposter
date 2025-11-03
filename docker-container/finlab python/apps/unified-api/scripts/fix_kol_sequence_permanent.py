#!/usr/bin/env python3
"""
永久修復 kol_profiles 表的 ID 序列不同步問題

問題：duplicate key value violates unique constraint "kol_profiles_pkey"
原因：序列值落後於實際最大 ID
解決：修復序列 + 創建觸發器自動防止未來再發生

執行方式:
    railway run python3 scripts/fix_kol_sequence_permanent.py
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
    print("  1. railway run python3 scripts/fix_kol_sequence_permanent.py")
    print("  2. export DATABASE_URL='...' && python3 fix_kol_sequence_permanent.py")
    print("  3. python3 fix_kol_sequence_permanent.py 'postgresql://...'")
    sys.exit(1)

# 轉換 postgresql:// to postgres:// for psycopg2
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://", 1)

def fix_sequence_permanent():
    """永久修復 kol_profiles ID 序列"""
    conn = None
    try:
        # 連接資料庫
        print("\n" + "=" * 80)
        print("🔧 KOL Profiles ID 序列永久修復工具")
        print("=" * 80)
        print("\n🔌 連接資料庫...")
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

        # Step 1: 修復當前序列
        print(f"\n🔧 Step 1: 修復當前序列... (從 {seq_value} → {max_id})")
        cursor.execute("SELECT setval('kol_profiles_id_seq', %s)", (max_id,))
        new_value = cursor.fetchone()[0]
        print(f"✅ 序列已更新到: {new_value}")

        # Step 2: 創建觸發器函數
        print("\n🔧 Step 2: 創建觸發器函數...")
        cursor.execute("""
            CREATE OR REPLACE FUNCTION sync_kol_profiles_sequence()
            RETURNS TRIGGER AS $$
            BEGIN
                PERFORM setval('kol_profiles_id_seq', (SELECT COALESCE(MAX(id), 0) FROM kol_profiles));
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("✅ 觸發器函數已創建")

        # Step 3: 創建觸發器
        print("\n🔧 Step 3: 創建觸發器...")

        # 先刪除舊觸發器（如果存在）
        cursor.execute("DROP TRIGGER IF EXISTS sync_kol_sequence_trigger ON kol_profiles")

        # 創建新觸發器
        cursor.execute("""
            CREATE TRIGGER sync_kol_sequence_trigger
                AFTER INSERT ON kol_profiles
                FOR EACH STATEMENT
                EXECUTE FUNCTION sync_kol_profiles_sequence();
        """)
        print("✅ 觸發器已創建")

        # 提交變更
        conn.commit()
        print("\n💾 變更已提交")

        # 驗證修復
        print("\n🔍 驗證修復結果:")

        cursor.execute("SELECT last_value FROM kol_profiles_id_seq")
        verified_value = cursor.fetchone()[0]
        print(f"   序列值: {verified_value}")
        print(f"   最大 ID: {max_id}")

        # 檢查觸發器是否存在
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_trigger
            WHERE tgname = 'sync_kol_sequence_trigger'
        """)
        trigger_exists = cursor.fetchone()[0]
        print(f"   觸發器存在: {'✅ 是' if trigger_exists > 0 else '❌ 否'}")

        # 最終結果
        print("\n" + "=" * 80)
        if verified_value >= max_id and trigger_exists > 0:
            print("✅ 永久修復成功！")
            print("\n🎉 現在可以正常創建 KOL 了！")
            print(f"   - 下一個 ID 將是: {verified_value + 1}")
            print(f"   - 觸發器已啟用，未來不會再出現此問題")
            print(f"   - 即使手動插入帶 ID 的記錄，觸發器也會自動修復序列")
        else:
            print("❌ 修復未完成，請檢查權限或重試")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        if conn:
            conn.rollback()
            print("🔙 變更已回滾")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("\n🔌 資料庫連接已關閉")

if __name__ == "__main__":
    fix_sequence_permanent()
