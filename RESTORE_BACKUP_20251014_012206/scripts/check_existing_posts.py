#!/usr/bin/env python3
"""
檢查Google Sheets中的現有貼文數據
"""

import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    """檢查Google Sheets中的現有貼文數據"""
    
    try:
        # 初始化Google Sheets客戶端
        credentials_file = "credentials/google-service-account.json"
        spreadsheet_id = "148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)
        
        # 讀取貼文記錄表
        sheet_name = "貼文記錄表"
        existing_data = sheets_client.read_sheet(sheet_name)
        
        if not existing_data or len(existing_data) < 2:
            print("❌ 沒有足夠的數據")
            return
        
        # 獲取標題行
        headers = existing_data[0]
        
        print(f"📋 檢查現有貼文數據:")
        print("-" * 80)
        
        # 顯示最近的幾行數據
        for i, row in enumerate(existing_data[1:], 1):
            print(f"\n【第 {i} 篇貼文】")
            
            # 找到關鍵欄位的索引
            post_id_idx = headers.index("貼文ID") if "貼文ID" in headers else -1
            kol_nickname_idx = headers.index("KOL 暱稱") if "KOL 暱稱" in headers else -1
            content_idx = headers.index("生成內容") if "生成內容" in headers else -1
            topic_title_idx = headers.index("熱門話題標題") if "熱門話題標題" in headers else -1
            
            if post_id_idx >= 0 and len(row) > post_id_idx:
                print(f"  📝 Post ID: {row[post_id_idx]}")
            
            if kol_nickname_idx >= 0 and len(row) > kol_nickname_idx:
                print(f"  👤 KOL: {row[kol_nickname_idx]}")
            
            if topic_title_idx >= 0 and len(row) > topic_title_idx:
                print(f"  📋 話題標題: {row[topic_title_idx]}")
            
            if content_idx >= 0 and len(row) > content_idx:
                content = row[content_idx]
                print(f"  📄 生成內容:")
                print(f"    {content[:200]}{'...' if len(content) > 200 else ''}")
            
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()












