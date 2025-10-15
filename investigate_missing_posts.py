#!/usr/bin/env python3
"""
檢查貼文記錄消失的原因和可能的恢復方案
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def investigate_missing_posts():
    """調查貼文記錄消失的原因"""
    
    print("🔍 調查貼文記錄消失的原因...")
    print("=" * 80)
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    try:
        # 讀取貼文記錄表
        data = sheets_client.read_sheet('貼文記錄表', 'A:R')
        
        if not data:
            print("❌ 無法讀取貼文記錄表")
            return
        
        headers = data[0] if data else []
        rows = data[1:] if len(data) > 1 else []
        
        print(f"📊 當前貼文記錄表狀態:")
        print(f"  📋 表頭欄位數: {len(headers)}")
        print(f"  📝 數據行數: {len(rows)}")
        print()
        
        # 檢查表頭
        print("📋 表頭欄位:")
        for i, header in enumerate(headers):
            print(f"  {i+1}. {header}")
        print()
        
        # 檢查現有數據
        if rows:
            print("📝 現有貼文記錄:")
            for i, row in enumerate(rows[:10], 1):  # 只顯示前10筆
                if len(row) >= 3:
                    post_id = row[0] if row[0] else "N/A"
                    kol_nickname = row[2] if len(row) > 2 else "N/A"
                    status = row[11] if len(row) > 11 else "N/A"
                    print(f"  {i}. {post_id} - {kol_nickname} - {status}")
        else:
            print("⚠️ 沒有找到任何貼文記錄")
        
        print()
        print("🔍 可能的原因分析:")
        print("=" * 80)
        
        # 檢查可能的清理腳本
        cleanup_scripts = [
            "complete_cleanup.py",
            "scripts/clear_posts.py", 
            "scripts/force_clear_posts.py",
            "clear_and_rebuild.py",
            "emergency_cleanup.py",
            "final_cleanup.py"
        ]
        
        print("🧹 可能執行的清理腳本:")
        for script in cleanup_scripts:
            if os.path.exists(script):
                print(f"  ✅ {script} - 存在")
            else:
                print(f"  ❌ {script} - 不存在")
        
        print()
        print("💡 恢復建議:")
        print("=" * 80)
        
        if len(rows) == 0:
            print("🚨 情況：完全沒有貼文記錄")
            print("📋 建議：")
            print("  1. 檢查是否有Google Sheets的版本歷史")
            print("  2. 檢查是否有備份文件")
            print("  3. 重新生成貼文記錄")
        elif len(rows) < 10:
            print("⚠️ 情況：貼文記錄數量很少")
            print("📋 建議：")
            print("  1. 檢查最近的清理操作")
            print("  2. 確認是否需要重新生成")
            print("  3. 檢查是否有部分數據被誤刪")
        else:
            print("✅ 情況：貼文記錄正常")
            print("📋 建議：")
            print("  1. 檢查篩選條件是否正確")
            print("  2. 確認查看的是正確的工作表")
        
        print()
        print("🔄 下一步行動:")
        print("=" * 80)
        print("1. 檢查Google Sheets的版本歷史")
        print("2. 確認是否有備份文件")
        print("3. 重新生成貼文記錄")
        print("4. 檢查清理腳本的執行記錄")
        
    except Exception as e:
        print(f"❌ 調查失敗: {e}")
        import traceback
        traceback.print_exc()

def check_google_sheets_history():
    """檢查Google Sheets的版本歷史"""
    print("\n📚 檢查Google Sheets版本歷史...")
    print("=" * 80)
    print("請手動檢查Google Sheets的版本歷史：")
    print("1. 打開Google Sheets")
    print("2. 點擊「檔案」>「版本歷史」")
    print("3. 查看是否有之前的版本")
    print("4. 如果有，可以恢復到之前的版本")

def suggest_recovery_actions():
    """建議恢復行動"""
    print("\n🔄 建議的恢復行動:")
    print("=" * 80)
    print("1. 立即檢查Google Sheets版本歷史")
    print("2. 如果有備份，恢復到清理前的狀態")
    print("3. 如果沒有備份，重新生成貼文記錄")
    print("4. 未來避免執行清理腳本，除非確定要清空數據")

if __name__ == "__main__":
    investigate_missing_posts()
    check_google_sheets_history()
    suggest_recovery_actions()
