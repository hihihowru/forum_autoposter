#!/usr/bin/env python3
"""
刪除錯誤的貼文記錄
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def delete_error_posts():
    """刪除錯誤的貼文記錄"""
    try:
        from src.clients.google.sheets_client import GoogleSheetsClient
        
        # 初始化 Google Sheets 客戶端
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        credentials_file = "credentials/google-service-account.json"
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 讀取貼文紀錄表
        data = sheets_client.read_sheet('貼文紀錄表')
        
        if not data or len(data) < 2:
            print("❌ 沒有找到數據")
            return
        
        print(f"📊 總行數: {len(data)}")
        
        # 找出需要刪除的錯誤貼文
        error_rows = []
        for i, row in enumerate(data[1:], 1):  # 跳過標題行
            if len(row) > 0 and row[0] and 'surge_' in str(row[0]):
                # 檢查是否為錯誤格式
                if len(row) < 34 or not row[33] or len(str(row[33])) < 10:
                    error_rows.append(i + 1)  # +1 因為跳過了標題行
                    print(f"❌ 發現錯誤貼文 (第{i+1}行): {row[0]}")
                    print(f"   內容長度: {len(str(row[33])) if len(row) > 33 else 0} 字")
        
        if not error_rows:
            print("✅ 沒有發現錯誤的貼文記錄")
            return
        
        print(f"\n🗑️ 準備刪除 {len(error_rows)} 篇錯誤貼文...")
        
        # 從後往前刪除，避免行號變化
        error_rows.sort(reverse=True)
        
        deleted_count = 0
        for row_num in error_rows:
            try:
                # 標記為已刪除（清空貼文ID和內容）
                sheets_client.update_cell('貼文紀錄表', f'A{row_num}', '')
                sheets_client.update_cell('貼文紀錄表', f'AH{row_num}', '已刪除-錯誤格式')
                print(f"✅ 已標記第 {row_num} 行為已刪除")
                deleted_count += 1
            except Exception as e:
                print(f"❌ 標記第 {row_num} 行失敗: {e}")
        
        print(f"\n🎉 刪除完成！成功刪除 {deleted_count} 篇錯誤貼文")
        
    except Exception as e:
        print(f"❌ 刪除失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    delete_error_posts()
