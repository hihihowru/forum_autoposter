#!/usr/bin/env python3
"""
刪除已發布的貼文並停止所有機器人自動發布功能
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def delete_published_and_stop_bots():
    """刪除已發布的貼文並停止機器人"""
    
    print("🚨 執行緊急清理：刪除已發布貼文並停止機器人...")
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
        
        # 找到已發布的貼文
        published_posts = []
        
        for i, row in enumerate(rows, 1):
            if len(row) >= 16:  # 確保有足夠的欄位
                post_id = row[0] if len(row) > 0 and row[0] else "N/A"
                kol_serial = row[1] if len(row) > 1 and row[1] else "N/A"
                kol_nickname = row[2] if len(row) > 2 and row[2] else "N/A"
                kol_member_id = row[3] if len(row) > 3 and row[3] else "N/A"
                persona = row[4] if len(row) > 4 and row[4] else "N/A"
                topic_title = row[8] if len(row) > 8 and row[8] else "N/A"
                status = row[11] if len(row) > 11 and row[11] else "N/A"
                platform_post_id = row[15] if len(row) > 15 and row[15] else "N/A"
                platform_url = row[16] if len(row) > 16 and row[16] else "N/A"
                
                # 檢查是否為已發布的貼文
                if status in ['posted', '已發布', 'published'] and platform_post_id and platform_post_id != "N/A":
                    published_posts.append({
                        'row_index': i + 1,
                        'post_id': post_id,
                        'kol_serial': kol_serial,
                        'kol_nickname': kol_nickname,
                        'kol_member_id': kol_member_id,
                        'persona': persona,
                        'topic_title': topic_title,
                        'status': status,
                        'platform_post_id': platform_post_id,
                        'platform_url': platform_url
                    })
        
        if published_posts:
            print(f"🚨 發現 {len(published_posts)} 篇已發布的貼文需要刪除:")
            print("=" * 80)
            
            for i, post in enumerate(published_posts, 1):
                print(f"{i}. 平台發文ID: {post['platform_post_id']}")
                print(f"   - 貼文ID: {post['post_id']}")
                print(f"   - KOL: {post['kol_nickname']} ({post['persona']})")
                print(f"   - 話題標題: {post['topic_title']}")
                print(f"   - Google Sheets 行號: {post['row_index']}")
                print(f"   - 平台URL: {post['platform_url']}")
                print()
            
            # 執行刪除操作
            print("🗑️ 開始執行刪除操作...")
            print("=" * 80)
            
            deleted_count = 0
            for post in published_posts:
                try:
                    # 更新貼文狀態為 'deleted'
                    row_index = post['row_index']
                    
                    # 更新發文狀態、清空平台信息
                    update_data = [
                        'deleted',        # 發文狀態 (L欄)
                        '',               # 上次排程時間 (M欄) - 保持不變
                        '',               # 發文時間戳記 (N欄) - 清空
                        '已刪除 - 機器人自動發布',  # 最近錯誤訊息 (O欄)
                        '',               # 平台發文ID (P欄) - 清空
                        ''                # 平台發文URL (Q欄) - 清空
                    ]
                    
                    # 寫入更新
                    range_name = f'L{row_index}:Q{row_index}'
                    sheets_client.write_sheet('貼文記錄表', [update_data], range_name)
                    
                    print(f"✅ 成功刪除貼文: {post['post_id']} (行號: {row_index})")
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"❌ 刪除貼文失敗 {post['post_id']}: {e}")
                    continue
            
            print()
            print(f"🗑️ 刪除完成！成功處理 {deleted_count}/{len(published_posts)} 篇貼文")
            print()
            
            # 生成刪除報告
            print("📊 刪除報告 (CSV 格式):")
            print("行號,貼文ID,KOL暱稱,人設,平台發文ID,平台URL,操作結果")
            for post in published_posts:
                print(f"{post['row_index']},{post['post_id']},{post['kol_nickname']},{post['persona']},{post['platform_post_id']},{post['platform_url']},已刪除")
            
        else:
            print("✅ 沒有發現已發布的貼文")
        
        print()
        print("🛑 第二步：停止所有機器人自動發布功能")
        print("=" * 80)
        
        # 檢查並停止自動發布進程
        print("🔍 檢查自動發布進程...")
        
        # 檢查 Python 進程
        import subprocess
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                auto_publish_processes = []
                
                for line in lines:
                    if any(keyword in line for keyword in ['auto_publish', 'publish', 'celery', 'new_topic_assignment']):
                        if 'grep' not in line:
                            auto_publish_processes.append(line)
                
                if auto_publish_processes:
                    print("⚠️ 發現自動發布相關進程:")
                    for process in auto_publish_processes:
                        print(f"  {process}")
                    
                    print()
                    print("💡 建議手動停止這些進程:")
                    print("1. 使用 'kill' 命令停止進程")
                    print("2. 檢查 Docker 容器中的自動發布服務")
                    print("3. 禁用 cron 定時任務")
                else:
                    print("✅ 沒有發現運行中的自動發布進程")
            else:
                print("⚠️ 無法檢查進程狀態")
        except Exception as e:
            print(f"⚠️ 檢查進程失敗: {e}")
        
        print()
        print("🔧 停止機器人的具體步驟:")
        print("=" * 80)
        print("1. 停止所有 Python 自動發布腳本")
        print("2. 檢查並停止 Celery 定時任務")
        print("3. 檢查 Docker 容器中的自動發布服務")
        print("4. 禁用 cron 任務 (如果有的話)")
        print("5. 將所有 ready_to_post 狀態改為 draft")
        print()
        print("🚨 重要提醒:")
        print("- 在建立手動發文審核流程之前，不要運行任何自動發布腳本")
        print("- 所有發文必須經過人工審核和確認")
        print("- 建議建立發文權限控制機制")
        print()
        print("💡 後續建議:")
        print("1. 建立手動發文審核流程")
        print("2. 實現貼文品質檢查機制")
        print("3. 建立發文前人工確認步驟")
        print("4. 定期檢查是否有新的自動發布觸發點")
        
        print()
        print("=" * 80)
        print("✅ 緊急清理完成！")
        
    except Exception as e:
        print(f"❌ 緊急清理失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    delete_published_and_stop_bots()



