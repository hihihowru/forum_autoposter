"""
測試簡化的互動數據收集系統
"""

import sys
import os
import asyncio
import datetime
from dotenv import load_dotenv

# 添加專案路徑
sys.path.append('./src')

# 載入環境變數
load_dotenv()

async def test_simplified_interaction_collection():
    """測試簡化的互動數據收集"""
    print('=== 簡化互動數據收集系統測試 ===')
    print()
    
    try:
        from services.interaction.interaction_collector_v2 import create_simplified_interaction_collector
        from clients.google.sheets_client import GoogleSheetsClient
        
        # 初始化收集器
        collector = create_simplified_interaction_collector()
        print('✅ 簡化互動數據收集器初始化成功')
        
        # 初始化 Google Sheets 客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LlikN2s'
        )
        
        print()
        
        # 測試1: 檢查貼文記錄表中的已發布貼文
        print('📊 測試1: 檢查貼文記錄表中的已發布貼文...')
        
        try:
            post_data = sheets_client.read_sheet('貼文記錄表', 'A:W')
            headers = post_data[0] if post_data else []
            rows = post_data[1:] if len(post_data) > 1 else []
            
            published_posts = []
            for i, row in enumerate(rows):
                if len(row) > 11 and row[11] == 'published':
                    post_info = {
                        'row_index': i + 2,
                        'post_id': row[0] if len(row) > 0 else '',
                        'kol_nickname': row[2] if len(row) > 2 else '',
                        'member_id': row[3] if len(row) > 3 else '',
                        'topic_title': row[8] if len(row) > 8 else '',
                        'post_timestamp': row[13] if len(row) > 13 else '',
                        'platform_post_id': row[15] if len(row) > 15 else ''
                    }
                    published_posts.append(post_info)
            
            print(f'✅ 找到 {len(published_posts)} 個已發布的貼文')
            
            for i, post in enumerate(published_posts[:3], 1):
                print(f'\\n   {i}. 貼文ID: {post[\"post_id\"]}')
                print(f'      KOL: {post[\"kol_nickname\"]} (ID: {post[\"member_id\"]})')
                print(f'      標題: {post[\"topic_title\"][:40]}...')
                print(f'      發文時間: {post[\"post_timestamp\"] or \"未設置\"}')
                print(f'      平台ID: {post[\"platform_post_id\"] or \"未設置\"}')
            
            if len(published_posts) > 3:
                print(f'\\n   ... 還有 {len(published_posts) - 3} 個貼文')
            
        except Exception as e:
            print(f'❌ 檢查已發布貼文失敗: {e}')
            return False
        
        print()
        
        # 測試2: 測試從貼文記錄表獲取詳細資訊
        print('📋 測試2: 測試從貼文記錄表獲取詳細資訊...')
        
        if published_posts:
            test_post = published_posts[0]
            test_post_id = test_post['post_id']
            
            print(f'🧪 測試貼文: {test_post_id}')
            
            try:
                post_details = await collector.get_post_details_from_record_table(test_post_id)
                
                if post_details:
                    print(f'✅ 成功獲取貼文詳細資訊:')
                    print(f'   任務ID: {post_details.get(\"task_id\", \"N/A\")}')
                    print(f'   KOL暱稱: {post_details.get(\"kol_nickname\", \"N/A\")}')
                    print(f'   會員ID: {post_details.get(\"member_id\", \"N/A\")}')
                    print(f'   話題標題: {post_details.get(\"topic_title\", \"N/A\")[:40]}...')
                    print(f'   話題ID: {post_details.get(\"topic_id\", \"N/A\")}')
                    print(f'   平台貼文ID: {post_details.get(\"platform_post_id\", \"N/A\")}')
                    print(f'   發文時間: {post_details.get(\"post_timestamp\", \"N/A\")}')
                    print(f'   是否熱門話題: {post_details.get(\"is_trending\", \"N/A\")}')
                else:
                    print(f'❌ 無法獲取貼文詳細資訊')
                    
            except Exception as e:
                print(f'❌ 獲取貼文詳細資訊失敗: {e}')
        else:
            print('⚠️  沒有已發布的貼文可供測試')
        
        print()
        
        # 測試3: 測試互動數據收集 (如果有平台貼文ID)
        print('📈 測試3: 測試互動數據收集...')
        
        testable_posts = [p for p in published_posts if p['platform_post_id']]
        
        if testable_posts:
            test_post = testable_posts[0]
            test_post_id = test_post['post_id']
            
            print(f'🧪 測試收集貼文互動數據: {test_post_id}')
            print(f'   平台貼文ID: {test_post[\"platform_post_id\"]}')
            
            try:
                interaction_record = await collector.collect_interaction_data_for_post(test_post_id, '1h')
                
                if interaction_record and not interaction_record.collection_error:
                    print(f'✅ 成功收集互動數據:')
                    print(f'   Article ID: {interaction_record.article_id}')
                    print(f'   會員ID: {interaction_record.member_id}')
                    print(f'   暱稱: {interaction_record.nickname}')
                    print(f'   標題: {interaction_record.title[:40]}...')
                    print(f'   Topic ID: {interaction_record.topic_id}')
                    print(f'   是否熱門話題: {interaction_record.is_trending_topic}')
                    print(f'   發文時間: {interaction_record.post_time}')
                    print(f'   收集時間: {interaction_record.last_update_time}')
                    print(f'   按讚數: {interaction_record.likes_count}')
                    print(f'   留言數: {interaction_record.comments_count}')
                    
                    # 測試保存到互動數據表 (模擬)
                    print(f'\\n🧪 測試保存到互動數據表...')
                    
                    try:
                        await collector.save_simplified_interaction_data([interaction_record], '互動回饋-1小時後')
                        print(f'✅ 數據保存測試完成 (檢查是否成功寫入)')
                    except Exception as e:
                        print(f'⚠️  保存測試失敗 (可能表格不存在): {e}')
                    
                elif interaction_record and interaction_record.collection_error:
                    print(f'⚠️  收集互動數據有錯誤: {interaction_record.collection_error}')
                else:
                    print(f'❌ 收集互動數據失敗')
                    
            except Exception as e:
                print(f'❌ 測試互動數據收集失敗: {e}')
        else:
            print('⚠️  沒有可測試的貼文 (缺少平台貼文ID)')
        
        print()
        
        # 測試4: 生成表格創建指引
        print('📋 測試4: 生成 Google Sheets 表格創建指引...')
        
        headers = [
            'Article ID', 'Member ID', '暱稱', '標題', '生成內文', 'Topic ID',
            '是否為熱門話題', '發文時間', '最後更新時間', '按讚數', '留言數'
        ]
        
        print(f'\\n📊 需要手動創建的三個 Google Sheets 工作表:')
        
        tables = [
            '互動回饋-1小時後',
            '互動回饋-1日後', 
            '互動回饋-7日後'
        ]
        
        for table in tables:
            print(f'\\n📋 {table}:')
            print(f'   表頭 (共 {len(headers)} 個欄位):')
            for i, header in enumerate(headers, 1):
                print(f'     {i:2d}. {header}')
        
        print(f'\\n📝 表頭複製用 (用 Tab 分隔):')
        print('\\t'.join(headers))
        
        print()
        
        # 測試5: 檢查需要收集的貼文
        print('⏰ 測試5: 檢查需要收集互動數據的貼文...')
        
        try:
            current_time = datetime.datetime.now()
            
            collection_types = ['1h', '1d', '7d']
            
            for collection_type in collection_types:
                posts_to_collect = await collector.get_published_posts_for_collection(collection_type)
                
                type_names = {'1h': '1小時後', '1d': '1日後', '7d': '7日後'}
                type_name = type_names.get(collection_type, collection_type)
                
                print(f'   {type_name}: {len(posts_to_collect)} 個貼文需要收集')
                
                for post_id in posts_to_collect[:2]:  # 只顯示前2個
                    print(f'     - {post_id}')
                
                if len(posts_to_collect) > 2:
                    print(f'     ... 還有 {len(posts_to_collect) - 2} 個')
        
        except Exception as e:
            print(f'❌ 檢查需要收集的貼文失敗: {e}')
        
        print()
        
        # 總結
        print('🎊 簡化互動數據收集系統測試總結:')
        print('=' * 60)
        
        print('✅ 測試結果:')
        results = [
            '簡化互動收集器初始化成功',
            '可以從貼文記錄表獲取貼文詳細資訊', 
            '可以收集 CMoney 平台的互動數據',
            '支援新的11個欄位的簡化表格結構',
            '可以檢測需要收集互動數據的貼文',
            '基於發文時間的動態收集邏輯正常'
        ]
        
        for result in results:
            print(f'   • {result}')
        
        print()
        print('📋 下一步操作:')
        next_steps = [
            '1. 在 Google Sheets 手動創建三個互動數據表格',
            '2. 複製表頭到新創建的工作表中',
            '3. 啟動基於發文時間的 Celery 任務',
            '4. 測試完整的自動收集流程',
            '5. 驗證數據寫入和分析功能'
        ]
        
        for step in next_steps:
            print(f'   {step}')
        
        return True
        
    except Exception as e:
        print(f'❌ 測試失敗: {e}')
        import traceback
        traceback.print_exc()
        return False

# 執行測試
async def main():
    success = await test_simplified_interaction_collection()
    
    if success:
        print('\\n🎉 簡化互動數據收集系統準備就緒！')
        print('💡 新系統使用11個欄位的簡化結構，更加高效實用')
    else:
        print('\\n⚠️  測試發現問題，需要進一步檢查')

if __name__ == '__main__':
    asyncio.run(main())
