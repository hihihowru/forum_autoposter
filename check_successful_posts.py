#!/usr/bin/env python3
"""
檢查成功發文的貼文記錄
列出所有已發布的貼文ID和相關信息，方便識別有品質問題的貼文
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.clients.google.sheets_client import GoogleSheetsClient

def check_successful_posts():
    """檢查成功發文的貼文記錄"""
    
    try:
        # 初始化 Google Sheets 客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        print("🔍 正在檢查成功發文的貼文記錄...")
        print("=" * 80)
        
        # 讀取貼文記錄表
        data = sheets_client.read_sheet('貼文記錄表', 'A:R')
        
        if not data or len(data) < 2:
            print("❌ 貼文記錄表為空或格式錯誤")
            return
        
        headers = data[0]
        rows = data[1:]
        
        print(f"📊 總記錄數: {len(rows)}")
        print()
        
        # 統計不同狀態的貼文數量
        status_counts = {}
        successful_posts = []
        
        for i, row in enumerate(rows, 1):
            if len(row) >= 16:  # 確保有足夠的欄位
                # 提取關鍵信息
                post_id = row[0] if len(row) > 0 and row[0] else "N/A"
                kol_serial = row[1] if len(row) > 1 and row[1] else "N/A"
                kol_nickname = row[2] if len(row) > 2 and row[2] else "N/A"
                kol_member_id = row[3] if len(row) > 3 and row[3] else "N/A"
                persona = row[4] if len(row) > 4 and row[4] else "N/A"
                topic_title = row[8] if len(row) > 8 and row[8] else "N/A"
                content = row[10] if len(row) > 10 and row[10] else "N/A"
                status = row[11] if len(row) > 11 and row[11] else "N/A"
                scheduled_time = row[12] if len(row) > 12 and row[12] else "N/A"
                post_time = row[13] if len(row) > 13 and row[13] else "N/A"
                error_message = row[14] if len(row) > 14 and row[14] else "N/A"
                platform_post_id = row[15] if len(row) > 15 and row[15] else "N/A"
                platform_url = row[16] if len(row) > 16 and row[16] else "N/A"
                trending_topic = row[17] if len(row) > 17 and row[17] else "N/A"
                
                # 統計狀態
                if status not in status_counts:
                    status_counts[status] = 0
                status_counts[status] += 1
                
                # 檢查是否為成功發文的貼文
                if status in ['posted', '已發布', 'published'] and platform_post_id:
                    successful_posts.append({
                        'row_index': i + 1,  # Google Sheets 行號（從2開始）
                        'post_id': post_id,
                        'kol_serial': kol_serial,
                        'kol_nickname': kol_nickname,
                        'kol_member_id': kol_member_id,
                        'persona': persona,
                        'topic_title': topic_title,
                        'content_preview': content[:50] + "..." if len(content) > 50 else content,
                        'status': status,
                        'scheduled_time': scheduled_time,
                        'post_time': post_time,
                        'platform_post_id': platform_post_id,
                        'platform_url': platform_url,
                        'trending_topic': trending_topic
                    })
        
        # 顯示狀態統計
        print("📈 貼文狀態統計:")
        print("-" * 40)
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count} 篇")
        print()
        
        # 顯示成功發文的貼文
        print(f"✅ 成功發文的貼文數量: {len(successful_posts)}")
        print("=" * 80)
        
        if successful_posts:
            print("📋 成功發文的貼文列表:")
            print()
            
            for i, post in enumerate(successful_posts, 1):
                print(f"【第 {i} 篇】")
                print(f"  📍 Google Sheets 行號: {post['row_index']}")
                print(f"  🆔 貼文ID: {post['post_id']}")
                print(f"  👤 KOL: {post['kol_nickname']} (Serial: {post['kol_serial']}, ID: {post['kol_member_id']})")
                print(f"  🎭 人設: {post['persona']}")
                print(f"  📝 話題標題: {post['topic_title']}")
                print(f"  📄 內容預覽: {post['content_preview']}")
                print(f"  📊 狀態: {post['status']}")
                print(f"  ⏰ 排程時間: {post['scheduled_time']}")
                print(f"  🚀 發文時間: {post['post_time']}")
                print(f"  🔗 平台發文ID: {post['platform_post_id']}")
                print(f"  🌐 平台URL: {post['platform_url']}")
                print(f"  🔥 熱門話題: {post['trending_topic']}")
                print()
                print("-" * 80)
                print()
            
            # 生成刪除建議
            print("🗑️ 刪除建議:")
            print("=" * 80)
            print("基於您提到的品質問題，建議檢查以下貼文:")
            print()
            
            for i, post in enumerate(successful_posts, 1):
                print(f"{i}. 貼文ID: {post['post_id']}")
                print(f"   - KOL: {post['kol_nickname']} ({post['persona']})")
                print(f"   - 平台發文ID: {post['platform_post_id']}")
                print(f"   - 平台URL: {post['platform_url']}")
                print(f"   - Google Sheets 行號: {post['row_index']}")
                print()
            
            print("💡 刪除操作建議:")
            print("1. 先備份貼文記錄表")
            print("2. 在 CMoney 平台刪除對應的文章")
            print("3. 在 Google Sheets 中標記該行為 '已刪除' 或直接刪除")
            print("4. 更新貼文狀態為 'deleted'")
            print()
            
            # 生成 CSV 格式的刪除清單
            print("📊 CSV 格式的刪除清單:")
            print("行號,貼文ID,KOL暱稱,人設,平台發文ID,平台URL")
            for post in successful_posts:
                print(f"{post['row_index']},{post['post_id']},{post['kol_nickname']},{post['persona']},{post['platform_post_id']},{post['platform_url']}")
            
        else:
            print("❌ 沒有找到成功發文的貼文")
        
        print()
        print("=" * 80)
        print("✅ 檢查完成！")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_successful_posts()
