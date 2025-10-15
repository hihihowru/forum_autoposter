#!/usr/bin/env python3
"""
刪除已發布的貼文
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def delete_published_posts():
    """刪除已發布的貼文"""
    
    print("🗑️ 正在檢查已發布的貼文...")
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
        
        published_posts = []
        
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
                
                # 檢查是否為已發布的貼文
                if status in ['posted', '已發布', 'published'] and platform_post_id and platform_post_id != "N/A":
                    published_posts.append({
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
        
        # 顯示已發布的貼文
        if published_posts:
            print(f"✅ 找到 {len(published_posts)} 篇已發布的貼文:")
            print("=" * 80)
            
            for i, post in enumerate(published_posts, 1):
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
            
            # 生成刪除清單
            print("🗑️ 刪除清單:")
            print("=" * 80)
            print("以下貼文需要刪除:")
            print()
            
            for i, post in enumerate(published_posts, 1):
                print(f"{i}. 平台發文ID: {post['platform_post_id']}")
                print(f"   - 貼文ID: {post['post_id']}")
                print(f"   - KOL: {post['kol_nickname']} ({post['persona']})")
                print(f"   - 發文時間: {post['post_time']}")
                print(f"   - Google Sheets 行號: {post['row_index']}")
                print(f"   - 平台URL: {post['platform_url']}")
                print()
            
            # 生成 CSV 格式的刪除清單
            print("📊 CSV 格式的刪除清單:")
            print("行號,貼文ID,KOL暱稱,人設,平台發文ID,平台URL,發文時間")
            for post in published_posts:
                print(f"{post['row_index']},{post['post_id']},{post['kol_nickname']},{post['persona']},{post['platform_post_id']},{post['platform_url']},{post['post_time']}")
            
            print()
            print("💡 刪除操作建議:")
            print("1. 先備份貼文記錄表")
            print("2. 在 CMoney 平台刪除對應的文章")
            print("3. 在 Google Sheets 中標記該行為 '已刪除' 或直接刪除")
            print("4. 更新貼文狀態為 'deleted'")
            print("5. 清空平台發文ID和URL欄位")
            print()
            print("🚨 重要提醒:")
            print("- 這些貼文已經發布到 CMoney 平台")
            print("- 需要先在平台刪除文章，再更新 Google Sheets")
            print("- 建議先備份數據，再進行刪除操作")
            
        else:
            print("✅ 沒有找到已發布的貼文")
        
        print()
        print("=" * 80)
        print("✅ 檢查完成！")
        
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    delete_published_posts()



