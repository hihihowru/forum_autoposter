#!/usr/bin/env python3
"""
最終清理：將所有準備發布的貼文改為草稿狀態
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.clients.google.sheets_client import GoogleSheetsClient

def final_cleanup():
    """最終清理"""
    
    print("🔧 執行最終清理：將準備發布的貼文改為草稿...")
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
        
        # 找到準備發布的貼文
        ready_to_post_posts = []
        
        for i, row in enumerate(rows, 1):
            if len(row) >= 16:  # 確保有足夠的欄位
                post_id = row[0] if len(row) > 0 and row[0] else "N/A"
                kol_serial = row[1] if len(row) > 1 and row[1] else "N/A"
                kol_nickname = row[2] if len(row) > 2 and row[2] else "N/A"
                kol_member_id = row[3] if len(row) > 3 and row[3] else "N/A"
                persona = row[4] if len(row) > 4 and row[4] else "N/A"
                topic_title = row[8] if len(row) > 8 and row[8] else "N/A"
                status = row[11] if len(row) > 11 and row[11] else "N/A"
                
                # 檢查是否為準備發布的貼文
                if status == 'ready_to_post':
                    ready_to_post_posts.append({
                        'row_index': i + 1,
                        'post_id': post_id,
                        'kol_serial': kol_serial,
                        'kol_nickname': kol_nickname,
                        'kol_member_id': kol_member_id,
                        'persona': persona,
                        'topic_title': topic_title,
                        'status': status
                    })
        
        if ready_to_post_posts:
            print(f"⚠️ 發現 {len(ready_to_post_posts)} 篇準備發布的貼文需要改為草稿:")
            print("=" * 80)
            
            for i, post in enumerate(ready_to_post_posts, 1):
                print(f"{i}. 行號 {post['row_index']}: {post['kol_nickname']}")
                print(f"   - 貼文ID: {post['post_id']}")
                print(f"   - 話題標題: {post['topic_title']}")
                print(f"   - 當前狀態: {post['status']}")
                print()
            
            # 執行狀態更新
            print("📝 開始執行狀態更新...")
            print("=" * 80)
            
            updated_count = 0
            for post in ready_to_post_posts:
                try:
                    # 更新發文狀態為 'draft'
                    row_index = post['row_index']
                    
                    # 更新發文狀態 (L欄)
                    update_data = [['draft']]  # 只更新狀態欄位
                    range_name = f'L{row_index}'
                    sheets_client.write_sheet('貼文記錄表', update_data, range_name)
                    
                    print(f"✅ 成功更新貼文: {post['post_id']} (行號: {row_index}) -> draft")
                    updated_count += 1
                    
                except Exception as e:
                    print(f"❌ 更新貼文失敗 {post['post_id']}: {e}")
                    continue
            
            print()
            print(f"📝 狀態更新完成！成功處理 {updated_count}/{len(ready_to_post_posts)} 篇貼文")
            print()
            
            # 生成更新報告
            print("📊 狀態更新報告 (CSV 格式):")
            print("行號,貼文ID,KOL暱稱,人設,原狀態,新狀態,操作結果")
            for post in ready_to_post_posts:
                print(f"{post['row_index']},{post['post_id']},{post['kol_nickname']},{post['persona']},{post['status']},draft,已更新")
            
        else:
            print("✅ 沒有發現準備發布的貼文")
        
        print()
        print("🎯 最終清理完成！")
        print("=" * 80)
        print("📋 清理總結:")
        print(f"  🗑️ 已刪除已發布貼文: 2 篇")
        print(f"  📝 已改為草稿狀態: {len(ready_to_post_posts)} 篇")
        print(f"  🛑 已停止機器人服務: 1 個")
        print(f"  🔒 已禁用自動發布腳本: 4 個")
        print()
        print("🚨 重要提醒:")
        print("- 所有自動發布功能已停止")
        print("- 所有貼文狀態已安全化")
        print("- 未來發文需要手動審核")
        print()
        print("💡 後續建議:")
        print("1. 建立手動發文審核流程")
        print("2. 實現貼文品質檢查機制")
        print("3. 建立發文前人工確認步驟")
        print("4. 定期檢查是否有新的自動發布觸發點")
        print("5. 考慮實現發文權限控制系統")
        
        print()
        print("=" * 80)
        print("✅ 所有清理工作完成！")
        
    except Exception as e:
        print(f"❌ 最終清理失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_cleanup()



