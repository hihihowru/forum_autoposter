#!/usr/bin/env python3
"""
手動更新貼文記錄狀態
"""

import sys
import os
from datetime import datetime

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))

from src.clients.google.sheets_client import GoogleSheetsClient

def main():
    print("📋 手動更新貼文記錄狀態:")
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
        status_index = None
        timestamp_index = None
        platform_id_index = None
        platform_url_index = None
        articleid_index = None
        
        for i, header in enumerate(headers):
            if header == "貼文ID":
                post_id_index = i
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
        print(f"  發文狀態: {status_index}")
        print(f"  發文時間戳記: {timestamp_index}")
        print(f"  平台發文ID: {platform_id_index}")
        print(f"  平台發文URL: {platform_url_index}")
        print(f"  articleid: {articleid_index}")
        print()
        
        # 手動更新數據
        update_data = {
            "19cab017-cdcf-41ec-b07b-c43fdc427c80-203": {
                "status": "已發文",
                "timestamp": "2025-09-02 15:30:45",
                "platform_id": "173477844",
                "platform_url": "https://www.cmoney.tw/forum/article/173477844",
                "articleid": "173477844"
            },
            "19cab017-cdcf-41ec-b07b-c43fdc427c80-204": {
                "status": "已發文",
                "timestamp": "2025-09-02 15:31:12",
                "platform_id": "173477845",
                "platform_url": "https://www.cmoney.tw/forum/article/173477845",
                "articleid": "173477845"
            }
        }
        
        # 更新每篇貼文
        for i, row in enumerate(post_data[1:], 2):
            if len(row) > post_id_index:
                post_id = row[post_id_index]
                if post_id in update_data:
                    update_info = update_data[post_id]
                    
                    # 準備更新的行數據
                    updated_row = row.copy()
                    
                    # 確保行數據長度足夠
                    while len(updated_row) < len(headers):
                        updated_row.append("")
                    
                    # 更新欄位
                    if status_index is not None:
                        updated_row[status_index] = update_info["status"]
                    if timestamp_index is not None:
                        updated_row[timestamp_index] = update_info["timestamp"]
                    if platform_id_index is not None:
                        updated_row[platform_id_index] = update_info["platform_id"]
                    if platform_url_index is not None:
                        updated_row[platform_url_index] = update_info["platform_url"]
                    if articleid_index is not None:
                        updated_row[articleid_index] = update_info["articleid"]
                    
                    # 寫入更新後的行
                    range_name = f"A{i}:AN{i}"
                    sheets_client.write_sheet("貼文記錄表", [updated_row], range_name)
                    
                    print(f"✅ 已更新 {post_id}")
                    print(f"  發文狀態: {update_info['status']}")
                    print(f"  發文時間: {update_info['timestamp']}")
                    print(f"  平台發文ID: {update_info['platform_id']}")
                    print(f"  平台發文URL: {update_info['platform_url']}")
                    print(f"  articleid: {update_info['articleid']}")
                    print()
        
        print("🎉 所有貼文記錄已更新完成！")
        
    except Exception as e:
        print(f"❌ 更新失敗: {e}")

if __name__ == "__main__":
    main()












