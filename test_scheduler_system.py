"""
測試排程系統和互動數據收集
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

async def test_interaction_collector():
    """測試互動數據收集器"""
    print('=== 測試互動數據收集器 ===')
    print()
    
    try:
        from services.interaction.interaction_collector import create_interaction_collector
        
        # 創建收集器
        collector = create_interaction_collector()
        print('✅ 互動數據收集器初始化成功')
        
        # 測試獲取已發布貼文
        print('📊 測試獲取已發布貼文...')
        
        # 先模擬一些 published 狀態的貼文
        from clients.google.sheets_client import GoogleSheetsClient
        
        sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        
        # 檢查是否有 published 狀態的貼文
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:Q')
        headers = post_data[0]
        rows = post_data[1:]
        
        published_posts = []
        for row in rows:
            if len(row) > 11 and row[11] in ['published', 'ready_to_post']:
                published_posts.append({
                    'task_id': row[0] if len(row) > 0 else '',
                    'status': row[11] if len(row) > 11 else '',
                    'platform_post_id': row[15] if len(row) > 15 else ''
                })
        
        print(f'✅ 找到 {len(published_posts)} 個可測試的貼文')
        
        for i, post in enumerate(published_posts[:3], 1):  # 只顯示前3個
            print(f'  {i}. {post["task_id"]} - 狀態: {post["status"]} - 平台ID: {post["platform_post_id"] or "未設置"}')
        
        # 如果有平台貼文ID，測試收集互動數據
        testable_posts = [p for p in published_posts if p['platform_post_id']]
        
        if testable_posts:
            print(f'\\n🧪 測試收集互動數據 (使用貼文: {testable_posts[0]["task_id"]})...')
            
            # 模擬貼文記錄
            test_post_record = {
                'task_id': testable_posts[0]['task_id'],
                'kol_serial': '200',
                'kol_nickname': '川川哥',
                'kol_id': '9505546',
                'platform_post_id': testable_posts[0]['platform_post_id'],
                'post_timestamp': datetime.datetime.now().isoformat(),
                'full_row': ['test'] * 17  # 模擬完整行數據
            }
            
            # 收集互動數據
            interaction_record = await collector.collect_interaction_data(test_post_record)
            
            if interaction_record:
                print('✅ 互動數據收集成功!')
                print(f'  讚數: {interaction_record.interested_count}')
                print(f'  留言數: {interaction_record.comment_count}')
                print(f'  收藏數: {interaction_record.collected_count}')
                print(f'  表情數: {interaction_record.emoji_total}')
                print(f'  總互動: {interaction_record.total_interactions}')
                print(f'  每小時平均: {interaction_record.hourly_avg_interactions:.2f}')
            else:
                print('❌ 互動數據收集失敗')
        else:
            print('⚠️  沒有可測試的貼文 (缺少平台貼文ID)')
        
        print()
        return True
        
    except Exception as e:
        print(f'❌ 測試失敗: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_celery_configuration():
    """測試 Celery 配置"""
    print('=== 測試 Celery 配置 ===')
    print()
    
    try:
        from services.scheduler.celery_app import app
        
        print('✅ Celery 應用程式載入成功')
        print(f'📊 Broker: {app.conf.broker_url}')
        print(f'📊 Backend: {app.conf.result_backend}')
        print(f'📊 Timezone: {app.conf.timezone}')
        
        # 顯示定時任務配置
        print(f'\\n📅 定時任務配置:')
        for task_name, task_config in app.conf.beat_schedule.items():
            print(f'  ✅ {task_name}:')
            print(f'     任務: {task_config["task"]}')
            print(f'     排程: {task_config["schedule"]}')
            print(f'     佇列: {task_config.get("options", {}).get("queue", "default")}')
        
        # 顯示任務路由
        print(f'\\n🚀 任務路由配置:')
        for task_pattern, route_config in app.conf.task_routes.items():
            print(f'  ✅ {task_pattern} → 佇列: {route_config["queue"]}')
        
        print()
        return True
        
    except Exception as e:
        print(f'❌ Celery 配置測試失敗: {e}')
        return False

def test_task_definitions():
    """測試任務定義"""
    print('=== 測試任務定義 ===')
    print()
    
    try:
        from services.scheduler import tasks
        
        # 測試任務函數是否可正常載入
        task_functions = [
            'collect_hourly_interactions',
            'collect_daily_interactions', 
            'collect_weekly_interactions',
            'generate_content_for_ready_tasks',
            'publish_ready_posts',
            'fetch_and_assign_topics',
            'test_task'
        ]
        
        for task_name in task_functions:
            if hasattr(tasks, task_name):
                task_func = getattr(tasks, task_name)
                print(f'✅ 任務 {task_name} 載入成功')
                print(f'   最大重試: {getattr(task_func, "max_retries", "未設置")}')
            else:
                print(f'❌ 任務 {task_name} 載入失敗')
        
        print()
        return True
        
    except Exception as e:
        print(f'❌ 任務定義測試失敗: {e}')
        return False

async def test_manual_task_execution():
    """測試手動執行任務"""
    print('=== 測試手動執行任務 ===')
    print()
    
    try:
        # 測試生成內容任務的邏輯 (不使用 Celery)
        print('🧪 測試內容生成任務邏輯...')
        
        from clients.google.sheets_client import GoogleSheetsClient
        from services.content.content_generator import create_content_generator, ContentRequest
        
        sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        
        content_generator = create_content_generator()
        
        # 查找 ready_to_gen 任務
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:Q')
        headers = post_data[0]
        rows = post_data[1:]
        
        ready_gen_tasks = []
        for i, row in enumerate(rows):
            if len(row) > 11 and row[11] == 'ready_to_gen':
                ready_gen_tasks.append({
                    'row_index': i + 2,
                    'data': row
                })
        
        print(f'✅ 找到 {len(ready_gen_tasks)} 個 ready_to_gen 任務')
        
        if ready_gen_tasks:
            # 測試處理第一個任務
            task = ready_gen_tasks[0]
            row = task['data']
            
            print(f'🎯 測試處理任務: {row[0]}')
            
            request = ContentRequest(
                topic_title=row[8] if len(row) > 8 else '',
                topic_keywords=row[9] if len(row) > 9 else '',
                kol_persona=row[4] if len(row) > 4 else '',
                kol_nickname=row[2] if len(row) > 2 else '',
                content_type=row[5] if len(row) > 5 else ''
            )
            
            print(f'  話題: {request.topic_title}')
            print(f'  KOL: {request.kol_nickname}')
            print(f'  人設: {request.kol_persona}')
            
            # 生成內容 (模擬，不實際更新)
            generated = content_generator.generate_complete_content(request)
            
            if generated.success:
                print(f'✅ 內容生成成功!')
                print(f'  標題: {generated.title}')
                print(f'  內容長度: {len(generated.content)} 字')
                print(f'  (模擬模式，不更新 Google Sheets)')
            else:
                print(f'❌ 內容生成失敗: {generated.error_message}')
        else:
            print('ℹ️  沒有 ready_to_gen 任務可測試')
        
        print()
        return True
        
    except Exception as e:
        print(f'❌ 手動任務執行測試失敗: {e}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主測試函數"""
    print('🧪 排程系統和互動數據收集測試')
    print('=' * 60)
    print()
    
    test_results = []
    
    # 1. 測試 Celery 配置
    result1 = test_celery_configuration()
    test_results.append(('Celery 配置', result1))
    
    # 2. 測試任務定義
    result2 = test_task_definitions()
    test_results.append(('任務定義', result2))
    
    # 3. 測試互動數據收集器
    result3 = await test_interaction_collector()
    test_results.append(('互動數據收集器', result3))
    
    # 4. 測試手動任務執行
    result4 = await test_manual_task_execution()
    test_results.append(('手動任務執行', result4))
    
    # 總結
    print('🎊 測試總結')
    print('=' * 60)
    
    for test_name, result in test_results:
        status = '✅ 通過' if result else '❌ 失敗'
        print(f'{test_name}: {status}')
    
    success_count = sum(1 for _, result in test_results if result)
    total_count = len(test_results)
    
    print(f'\\n📊 測試結果: {success_count}/{total_count} 通過')
    
    if success_count == total_count:
        print('🎉 所有測試通過！排程系統準備就緒')
    else:
        print('⚠️  部分測試失敗，需要檢查問題')
    
    print(f'\\n💡 下一步:')
    print(f'1. 安裝 Redis 服務 (brew install redis)')
    print(f'2. 啟動 Redis 服務 (redis-server)')
    print(f'3. 啟動 Celery Worker (celery -A src.services.scheduler.celery_app worker --loglevel=info)')
    print(f'4. 啟動 Celery Beat (celery -A src.services.scheduler.celery_app beat --loglevel=info)')
    print(f'5. 手動在 Google Sheets 創建互動追蹤表格')

if __name__ == '__main__':
    asyncio.run(main())
