#!/usr/bin/env python3
"""
清理舊的排程任務腳本

此腳本會刪除所有現有的排程任務記錄，讓你可以重新開始測試：
- 觸發器 (triggers)
- 最大股票數 (max_stocks)
- 股票篩選條件 (stock filters)
- KOL分配方式 (kol_assignment)

使用方法:
    python cleanup_old_schedules.py

注意: 此腳本會永久刪除所有排程任務，請謹慎使用！
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

def get_database_url():
    """從環境變數獲取資料庫 URL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ 找不到 DATABASE_URL 環境變數")
        print("請設定: export DATABASE_URL='postgresql://...'")
        return None
    return database_url

def cleanup_schedules(dry_run=True):
    """
    清理所有排程任務

    Args:
        dry_run: 如果為 True，只顯示要刪除的任務，不實際刪除
    """
    database_url = get_database_url()
    if not database_url:
        return False

    try:
        print(f"🔌 正在連接資料庫...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 查詢所有排程任務
        print(f"\n📊 正在查詢現有排程任務...")
        cursor.execute("""
            SELECT
                schedule_id,
                schedule_name,
                status,
                schedule_type,
                created_at,
                run_count,
                success_count,
                failure_count
            FROM schedule_tasks
            ORDER BY created_at DESC
        """)

        tasks = cursor.fetchall()

        if not tasks:
            print("✅ 資料庫中沒有排程任務")
            return True

        print(f"\n📋 找到 {len(tasks)} 個排程任務:\n")
        print(f"{'ID':<36} {'名稱':<30} {'狀態':<10} {'類型':<15} {'執行次數':<10} {'成功':<8} {'失敗':<8}")
        print("=" * 130)

        for task in tasks:
            task_id = task['schedule_id']
            name = task['schedule_name'] or 'N/A'
            status = task['status'] or 'N/A'
            schedule_type = task['schedule_type'] or 'N/A'
            run_count = task['run_count'] or 0
            success_count = task['success_count'] or 0
            failure_count = task['failure_count'] or 0

            print(f"{task_id:<36} {name:<30} {status:<10} {schedule_type:<15} {run_count:<10} {success_count:<8} {failure_count:<8}")

        print("=" * 130)

        if dry_run:
            print(f"\n⚠️  DRY RUN 模式 - 不會實際刪除任務")
            print(f"ℹ️  要真正刪除，請執行: python cleanup_old_schedules.py --confirm")
        else:
            # 詢問確認
            print(f"\n⚠️  警告: 這將永久刪除所有 {len(tasks)} 個排程任務!")
            confirmation = input("請輸入 'DELETE' 來確認刪除: ")

            if confirmation != 'DELETE':
                print("❌ 取消刪除操作")
                return False

            # 執行刪除
            print(f"\n🗑️  正在刪除所有排程任務...")
            cursor.execute("DELETE FROM schedule_tasks")
            deleted_count = cursor.rowcount
            conn.commit()

            print(f"✅ 成功刪除 {deleted_count} 個排程任務")
            print(f"🎉 資料庫已清空，可以開始全新的測試！")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ 清理失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys

    print("=" * 80)
    print("排程任務清理腳本")
    print("=" * 80)
    print()

    # 檢查是否有 --confirm 參數
    confirm_mode = '--confirm' in sys.argv

    if confirm_mode:
        print("🔥 確認模式 - 將實際刪除排程任務")
    else:
        print("👀 預覽模式 - 只顯示要刪除的任務")

    print()

    # 執行清理
    success = cleanup_schedules(dry_run=not confirm_mode)

    if success:
        print("\n✅ 清理操作完成")
        sys.exit(0)
    else:
        print("\n❌ 清理操作失敗")
        sys.exit(1)
