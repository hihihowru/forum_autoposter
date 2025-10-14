#!/usr/bin/env python3
"""
更新互動回饋即時總表結構，新增 donation 和 emoji 相關欄位
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))
sys.path.append(os.path.join(project_root, '..', 'src'))

from clients.google.sheets_client import GoogleSheetsClient

def main():
    print("🔧 更新互動回饋即時總表結構:")
    print("-----------------------------------------")
    print()
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file="credentials/google-service-account.json",
        spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    try:
        # 讀取現有數據
        current_data = sheets_client.read_sheet('互動回饋即時總表', 'A1:O10')
        
        if not current_data or len(current_data) == 0:
            print("❌ 沒有找到現有數據")
            return
        
        # 新的標題行（新增 donation 和 emoji 相關欄位）
        new_headers = [
            'article_id', 'member_id', 'nickname', 'title', 'content', 'topic_id', 
            'is_trending_topic', 'post_time', 'last_update_time', 'likes_count', 
            'comments_count', 'total_interactions', 'engagement_rate', 'growth_rate', 
            'collection_error', 'donation_count', 'donation_amount', 'emoji_type', 
            'emoji_counts', 'total_emoji_count'
        ]
        
        print(f"📋 新標題行: {new_headers}")
        print(f"📊 新增欄位數: {len(new_headers) - len(current_data[0])}")
        
        # 準備新的數據行
        new_data = [new_headers]
        
        # 處理現有數據行，添加新欄位的預設值
        for row in current_data[1:]:
            new_row = row.copy()
            # 添加新欄位的預設值
            new_row.extend(['0', '0', '', '', '0'])  # donation_count, donation_amount, emoji_type, emoji_counts, total_emoji_count
            new_data.append(new_row)
        
        # 寫入新的數據結構
        sheets_client.write_sheet('互動回饋即時總表', new_data, 'A1:T1000')
        
        print("✅ 成功更新互動回饋即時總表結構")
        print(f"📊 新欄位:")
        print(f"  - donation_count: 捐贈次數")
        print(f"  - donation_amount: 捐贈金額")
        print(f"  - emoji_type: emoji 類型")
        print(f"  - emoji_counts: 各 emoji 數量 (JSON 格式)")
        print(f"  - total_emoji_count: 總 emoji 數量")
        
    except Exception as e:
        print(f"❌ 更新失敗: {e}")

if __name__ == "__main__":
    main()
























