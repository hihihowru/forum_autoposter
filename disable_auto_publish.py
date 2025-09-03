#!/usr/bin/env python3
"""
禁用所有自動發布功能
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def disable_auto_publish():
    """禁用所有自動發布功能"""
    
    print("🚨 正在禁用所有自動發布功能...")
    print("=" * 80)
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
        spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
    )
    
    try:
        # 讀取貼文記錄表
        data = sheets_client.read_sheet('貼文記錄表', 'A:R')
        
        if not data or len(data) < 2:
            print("❌ 貼文記錄表為空或格式錯誤")
            return
        
        headers = data[0]
        rows = data[1:]
        
        print(f"📊 總記錄數: {len(rows)}")
        print()
        
        # 檢查所有 ready_to_post 狀態的貼文
        ready_to_post_count = 0
        ready_to_post_rows = []
        
        for i, row in enumerate(rows, 1):
            if len(row) >= 16:  # 確保有足夠的欄位
                post_id = row[0] if len(row) > 0 and row[0] else "N/A"
                kol_nickname = row[2] if len(row) > 2 and row[2] else "N/A"
                status = row[11] if len(row) > 11 and row[11] else "N/A"
                topic_title = row[8] if len(row) > 8 and row[8] else "N/A"
                
                # 檢查是否為 ready_to_post 狀態
                if status == 'ready_to_post':
                    ready_to_post_count += 1
                    ready_to_post_rows.append({
                        'row_index': i + 1,
                        'post_id': post_id,
                        'kol_nickname': kol_nickname,
                        'topic_title': topic_title
                    })
        
        print(f"⚠️ 發現 {ready_to_post_count} 篇準備發文的貼文 (ready_to_post)")
        print()
        
        if ready_to_post_rows:
            print("📋 準備發文的貼文列表:")
            print("-" * 60)
            
            for post in ready_to_post_rows:
                print(f"行號 {post['row_index']}: {post['kol_nickname']} - {post['topic_title'][:30]}...")
            
            print()
            print("🚨 這些貼文可能會被自動發布！")
            print()
            
            # 建議操作
            print("💡 建議操作:")
            print("1. 將所有 ready_to_post 狀態改為 draft (草稿)")
            print("2. 禁用所有自動發布腳本")
            print("3. 建立手動發文審核流程")
            print("4. 檢查定時任務配置")
            
            # 生成狀態更新建議
            print()
            print("📊 狀態更新建議 (CSV 格式):")
            print("行號,貼文ID,KOL暱稱,當前狀態,建議狀態")
            for post in ready_to_post_rows:
                print(f"{post['row_index']},{post['post_id']},{post['kol_nickname']},ready_to_post,draft")
        
        else:
            print("✅ 沒有發現準備發文的貼文")
        
        print()
        print("🔧 禁用自動發布的具體步驟:")
        print("=" * 80)
        print("1. 停止所有 Python 自動發布腳本")
        print("2. 檢查並停止 Celery 定時任務")
        print("3. 檢查 Docker 容器中的自動發布服務")
        print("4. 禁用 cron 任務 (如果有的話)")
        print("5. 將貼文狀態改為 draft，等待手動審核")
        print()
        print("🚨 重要提醒:")
        print("- 在建立手動發文審核流程之前，不要運行任何自動發布腳本")
        print("- 所有發文必須經過人工審核和確認")
        print("- 建議建立發文權限控制機制")
        
        print()
        print("=" * 80)
        print("✅ 檢查完成！")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    disable_auto_publish()



