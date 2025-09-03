#!/usr/bin/env python3
"""
緊急清理腳本
1. 刪除已自動發布的貼文
2. 將準備發布的貼文改為草稿狀態
3. 停止所有自動發布功能
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def emergency_cleanup():
    """緊急清理"""
    
    print("🚨 執行緊急清理...")
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
        
        # 分類貼文狀態
        published_posts = []      # 已發布的貼文
        ready_to_post_posts = [] # 準備發布的貼文
        other_posts = []         # 其他狀態的貼文
        
        for i, row in enumerate(rows, 1):
            if len(row) >= 16:  # 確保有足夠的欄位
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
                
                post_info = {
                    'row_index': i + 1,
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
                    'error_message': error_message,
                    'platform_post_id': platform_post_id,
                    'platform_url': platform_url,
                    'trending_topic': trending_topic
                }
                
                # 分類貼文
                if status in ['posted', '已發布', 'published'] and platform_post_id and platform_post_id != "N/A":
                    published_posts.append(post_info)
                elif status == 'ready_to_post':
                    ready_to_post_posts.append(post_info)
                else:
                    other_posts.append(post_info)
        
        # 顯示分類結果
        print(f"📊 貼文狀態分類:")
        print(f"  🚨 已發布: {len(published_posts)} 篇")
        print(f"  ⚠️ 準備發布: {len(ready_to_post_posts)} 篇")
        print(f"  ✅ 其他狀態: {len(other_posts)} 篇")
        print()
        
        # 1. 處理已發布的貼文
        if published_posts:
            print("🚨 已發布的貼文 (需要刪除):")
            print("=" * 80)
            
            for i, post in enumerate(published_posts, 1):
                print(f"{i}. 平台發文ID: {post['platform_post_id']}")
                print(f"   - 貼文ID: {post['post_id']}")
                print(f"   - KOL: {post['kol_nickname']} ({post['persona']})")
                print(f"   - 發文時間: {post['post_time']}")
                print(f"   - Google Sheets 行號: {post['row_index']}")
                print(f"   - 平台URL: {post['platform_url']}")
                print()
            
            print("💡 刪除操作建議:")
            print("1. 在 CMoney 平台刪除對應的文章")
            print("2. 在 Google Sheets 中標記狀態為 'deleted'")
            print("3. 清空平台發文ID和URL欄位")
            print()
        
        # 2. 處理準備發布的貼文
        if ready_to_post_posts:
            print("⚠️ 準備發布的貼文 (需要改為草稿):")
            print("=" * 80)
            
            for i, post in enumerate(ready_to_post_posts, 1):
                print(f"{i}. 行號 {post['row_index']}: {post['kol_nickname']}")
                print(f"   - 貼文ID: {post['post_id']}")
                print(f"   - 話題標題: {post['topic_title']}")
                print(f"   - 當前狀態: {post['status']}")
                print()
            
            print("💡 狀態更新建議:")
            print("1. 將所有 ready_to_post 狀態改為 draft")
            print("2. 等待手動審核後再決定是否發布")
            print()
        
        # 3. 生成操作清單
        print("📋 操作清單 (CSV 格式):")
        print("=" * 80)
        
        if published_posts:
            print("🗑️ 需要刪除的已發布貼文:")
            print("行號,貼文ID,KOL暱稱,人設,平台發文ID,平台URL,發文時間")
            for post in published_posts:
                print(f"{post['row_index']},{post['post_id']},{post['kol_nickname']},{post['persona']},{post['platform_post_id']},{post['platform_url']},{post['post_time']}")
            print()
        
        if ready_to_post_posts:
            print("📝 需要改為草稿的準備發布貼文:")
            print("行號,貼文ID,KOL暱稱,人設,當前狀態,建議狀態")
            for post in ready_to_post_posts:
                print(f"{post['row_index']},{post['post_id']},{post['kol_nickname']},{post['persona']},{post['status']},draft")
            print()
        
        # 4. 緊急操作建議
        print("🚨 緊急操作建議:")
        print("=" * 80)
        print("立即執行:")
        print("1. 停止所有自動發布腳本和服務")
        print("2. 在 CMoney 平台刪除已發布的文章")
        print("3. 將貼文記錄表狀態更新為 'deleted' 和 'draft'")
        print("4. 建立手動發文審核流程")
        print()
        print("後續處理:")
        print("1. 檢查並禁用所有自動發布觸發點")
        print("2. 建立發文權限控制機制")
        print("3. 實現貼文品質檢查流程")
        print("4. 建立發文前人工確認機制")
        
        print()
        print("=" * 80)
        print("✅ 緊急清理檢查完成！")
        
    except Exception as e:
        print(f"❌ 緊急清理檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    emergency_cleanup()



