#!/usr/bin/env python3
"""
備份並刪除所有排程任務
使用 API 方式進行，無需直接訪問數據庫
"""

import requests
import json
from datetime import datetime
import os

# API Base URL - Railway Production
API_BASE_URL = os.getenv('API_BASE_URL', 'https://forumautoposter-production.up.railway.app')

def backup_schedules():
    """備份所有排程任務到 JSON 檔案"""
    print("=" * 80)
    print("排程任務備份與刪除腳本")
    print("=" * 80)
    print()

    # 1. 獲取所有排程任務
    print("📥 正在獲取所有排程任務...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/schedule/tasks")
        response.raise_for_status()
        result = response.json()
        tasks = result.get('tasks', [])

        if not tasks:
            print("✅ 沒有需要備份的排程任務")
            return []

        print(f"✅ 找到 {len(tasks)} 個排程任務")

        # 2. 備份到 JSON 檔案
        backup_filename = f"schedule_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = os.path.join(os.path.dirname(__file__), backup_filename)

        print(f"💾 正在備份到 {backup_filename}...")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump({
                'backup_time': datetime.now().isoformat(),
                'total_tasks': len(tasks),
                'tasks': tasks
            }, f, ensure_ascii=False, indent=2)

        print(f"✅ 備份完成: {backup_path}")
        print()

        # 3. 顯示要刪除的任務摘要
        print("📋 排程任務摘要:")
        print(f"{'序號':<5} {'名稱':<50} {'狀態':<10} {'創建時間':<20}")
        print("=" * 90)
        for i, task in enumerate(tasks, 1):
            print(f"{i:<5} {task.get('schedule_name', 'N/A'):<50} {task.get('status', 'N/A'):<10} {task.get('created_at', 'N/A')[:19]:<20}")
        print("=" * 90)
        print()

        return tasks

    except Exception as e:
        print(f"❌ 備份失敗: {e}")
        import traceback
        traceback.print_exc()
        return []

def delete_all_schedules(tasks):
    """刪除所有排程任務"""
    if not tasks:
        print("ℹ️  沒有任務需要刪除")
        return

    print(f"🗑️  開始刪除 {len(tasks)} 個排程任務...")
    print()

    deleted_count = 0
    failed_count = 0

    for i, task in enumerate(tasks, 1):
        task_id = task.get('schedule_id')
        task_name = task.get('schedule_name', 'N/A')

        try:
            print(f"[{i}/{len(tasks)}] 刪除: {task_name} ({task_id})...", end=" ")
            response = requests.delete(f"{API_BASE_URL}/api/schedule/tasks/{task_id}")
            response.raise_for_status()
            result = response.json()

            if result.get('success'):
                print("✅")
                deleted_count += 1
            else:
                print(f"❌ {result.get('message', 'Unknown error')}")
                failed_count += 1

        except Exception as e:
            print(f"❌ {e}")
            failed_count += 1

    print()
    print("=" * 80)
    print(f"✅ 刪除完成:")
    print(f"   - 成功: {deleted_count} 個")
    print(f"   - 失敗: {failed_count} 個")
    print("=" * 80)

if __name__ == '__main__':
    print()

    # 備份
    tasks = backup_schedules()

    if tasks:
        # 確認刪除
        print("⚠️  警告: 即將刪除所有排程任務!")
        print("⚠️  備份檔案已創建，可隨時恢復")
        print()
        confirmation = input("請輸入 'DELETE' 來確認刪除，或按 Enter 取消: ").strip()

        if confirmation == 'DELETE':
            print()
            delete_all_schedules(tasks)
        else:
            print()
            print("❌ 已取消刪除操作")
            print("ℹ️  備份檔案已保留")

    print()
    print("✅ 完成")
