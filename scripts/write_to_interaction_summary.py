#!/usr/bin/env python3
"""
將貼文資訊寫入互動回饋即時總表
"""

import sys
import os
from datetime import datetime

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'src'))
sys.path.append(os.path.join(project_root, '..', 'src'))

from clients.google.sheets_client import GoogleSheetsClient

def main():
    print("📊 將貼文資訊寫入互動回饋即時總表:")
    print("-----------------------------------------")
    print()
    
    # 初始化 Google Sheets 客戶端
    sheets_client = GoogleSheetsClient(
        credentials_file="credentials/google-service-account.json",
        spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
    )
    
    try:
        # 1. 從貼文記錄表獲取已發文的文章
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:AN')
        if not post_data or len(post_data) <= 1:
            print("❌ 沒有找到已發文的貼文記錄")
            return
        
        headers = post_data[0]
        posts = post_data[1:]
        
        # 找到關鍵欄位索引
        post_id_index = None
        kol_serial_index = None
        kol_nickname_index = None
        kol_id_index = None
        topic_id_index = None
        topic_title_index = None
        content_index = None
        platform_post_id_index = None
        platform_post_url_index = None
        post_time_index = None
        
        for i, header in enumerate(headers):
            if header == "貼文ID":
                post_id_index = i
            elif header == "KOL Serial":
                kol_serial_index = i
            elif header == "KOL 暱稱":
                kol_nickname_index = i
            elif header == "KOL ID":
                kol_id_index = i
            elif header == "已派發TopicID":
                topic_id_index = i
            elif header == "熱門話題標題":
                topic_title_index = i
            elif header == "生成內容":
                content_index = i
            elif header == "平台發文ID":
                platform_post_id_index = i
            elif header == "平台發文URL":
                platform_post_url_index = i
            elif header == "發文時間戳記":
                post_time_index = i
        
        # 2. 從同學會帳號管理表獲取 member_id
        kol_data = sheets_client.read_sheet('同學會帳號管理', 'A:AZ')
        kol_headers = kol_data[0] if kol_data else []
        kol_records = kol_data[1:] if len(kol_data) > 1 else []
        
        # 建立 KOL Serial 到 member_id 的映射
        kol_mapping = {}
        for record in kol_records:
            if len(record) >= 5:
                serial = record[0] if len(record) > 0 else ""
                member_id = record[4] if len(record) > 4 else ""
                if serial and member_id:
                    kol_mapping[serial] = member_id
        
        # 3. 準備互動回饋數據
        interaction_records = []
        
        for post in posts:
            if len(post) > max(post_id_index or 0, platform_post_id_index or 0):
                post_id = post[post_id_index] if post_id_index is not None else ""
                kol_serial = post[kol_serial_index] if kol_serial_index is not None else ""
                kol_nickname = post[kol_nickname_index] if kol_nickname_index is not None else ""
                kol_id = post[kol_id_index] if kol_id_index is not None else ""
                topic_id = post[topic_id_index] if topic_id_index is not None else ""
                topic_title = post[topic_title_index] if topic_title_index is not None else ""
                content = post[content_index] if content_index is not None else ""
                platform_post_id = post[platform_post_id_index] if platform_post_id_index is not None else ""
                platform_post_url = post[platform_post_url_index] if platform_post_url_index is not None else ""
                post_time = post[post_time_index] if post_time_index is not None else ""
                
                if platform_post_id and platform_post_id.strip():
                    print(f"📝 處理文章 {platform_post_id} ({kol_nickname})...")
                    
                    # 獲取 member_id
                    member_id = kol_mapping.get(kol_serial, "")
                    
                    # 準備互動回饋記錄
                    interaction_record = [
                        platform_post_id,  # article_id
                        member_id,  # member_id
                        kol_nickname,  # nickname
                        f"貼文 {platform_post_id}",  # title
                        content[:100] if content else "",  # content (截取前100字)
                        topic_id,  # topic_id
                        "TRUE" if topic_title else "FALSE",  # is_trending_topic
                        post_time,  # post_time
                        datetime.now().isoformat(),  # last_update_time
                        "0",  # likes_count (初始值)
                        "0",  # comments_count (初始值)
                        "0",  # total_interactions (初始值)
                        "0.0",  # engagement_rate (初始值)
                        "0.0",  # growth_rate (初始值)
                        "",  # collection_error
                        "0",  # donation_count (初始值)
                        "0",  # donation_amount (初始值)
                        "",  # emoji_type (初始值)
                        "{}",  # emoji_counts (JSON 格式，初始值)
                        "0"  # total_emoji_count (初始值)
                    ]
                    
                    interaction_records.append(interaction_record)
        
        # 4. 清空互動回饋即時總表並寫入新數據
        if interaction_records:
            print(f"📋 準備寫入 {len(interaction_records)} 條記錄到互動回饋即時總表...")
            
            # 讀取標題行
            header_data = sheets_client.read_sheet('互動回饋即時總表', 'A1:O1')
            if header_data and len(header_data) > 0:
                # 清空工作表（保留標題行）
                sheets_client.write_sheet('互動回饋即時總表', header_data, 'A1:O1000')
                
                # 寫入新數據
                sheets_client.append_sheet('互動回饋即時總表', interaction_records)
                
                print("✅ 成功寫入互動回饋即時總表")
                print(f"📊 寫入記錄數: {len(interaction_records)}")
                
                # 顯示寫入的數據
                for record in interaction_records:
                    print(f"  - {record[2]} ({record[0]}): {record[3]}")
            else:
                print("❌ 無法讀取標題行")
        else:
            print("⚠️ 沒有找到可寫入的貼文記錄")
            
    except Exception as e:
        print(f"❌ 寫入失敗: {e}")

if __name__ == "__main__":
    main()
