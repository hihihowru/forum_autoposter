#!/usr/bin/env python3
"""
檢查貼文記錄狀態
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    print("📋 檢查貼文記錄狀態:")
    print("-----------------------------------------")
    print("---------------------------------------")
    print()
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file="credentials/google-service-account.json",
        spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    try:
        # 讀取貼文記錄表
        post_data = sheets_client.read_sheet("貼文記錄表")
        
        if len(post_data) <= 1:
            print("❌ 沒有找到貼文數據")
            return
        
        headers = post_data[0]
        
        # 查找關鍵欄位索引
        post_id_index = None
        kol_nickname_index = None
        status_index = None
        timestamp_index = None
        platform_id_index = None
        platform_url_index = None
        articleid_index = None
        
        for i, header in enumerate(headers):
            if header == "貼文ID":
                post_id_index = i
            elif header == "KOL 暱稱":
                kol_nickname_index = i
            elif header == "發文狀態":
                status_index = i
            elif header == "發文時間戳記":
                timestamp_index = i
            elif header == "平台發文ID":
                platform_id_index = i
            elif header == "平台發文URL":
                platform_url_index = i
            elif header == "articleid":
                articleid_index = i
        
        print(f"📊 關鍵欄位索引:")
        print(f"  貼文ID: {post_id_index}")
        print(f"  KOL 暱稱: {kol_nickname_index}")
        print(f"  發文狀態: {status_index}")
        print(f"  發文時間戳記: {timestamp_index}")
        print(f"  平台發文ID: {platform_id_index}")
        print(f"  平台發文URL: {platform_url_index}")
        print(f"  articleid: {articleid_index}")
        print()
        
        # 檢查每篇貼文
        print(f"📊 貼文記錄:")
        for i, row in enumerate(post_data[1:], 1):
            if len(row) > max(post_id_index or 0, kol_nickname_index or 0):
                post_id = row[post_id_index] if post_id_index is not None else "未知"
                kol_name = row[kol_nickname_index] if kol_nickname_index is not None else "未知"
                status = row[status_index] if status_index is not None and len(row) > status_index else "未知"
                timestamp = row[timestamp_index] if timestamp_index is not None and len(row) > timestamp_index else "未知"
                platform_id = row[platform_id_index] if platform_id_index is not None and len(row) > platform_id_index else "未知"
                platform_url = row[platform_url_index] if platform_url_index is not None and len(row) > platform_url_index else "未知"
                articleid = row[articleid_index] if articleid_index is not None and len(row) > articleid_index else "未知"
                
                print(f"【第 {i} 篇貼文】")
                print(f"  📝 Post ID: {post_id}")
                print(f"  👤 KOL: {kol_name}")
                print(f"  📊 發文狀態: {status}")
                print(f"  ⏰ 發文時間戳記: {timestamp}")
                print(f"  🆔 平台發文ID: {platform_id}")
                print(f"  🔗 平台發文URL: {platform_url}")
                print(f"  📋 articleid: {articleid}")
                print("----------------------------------------")
                print()
            
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")

if __name__ == "__main__":
    main()












