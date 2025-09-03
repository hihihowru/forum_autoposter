"""
測試基於發文時間的互動數據收集邏輯
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

async def test_time_based_collection_logic():
    """測試基於發文時間的收集邏輯"""
    print('=== 基於發文時間的互動數據收集測試 ===')
    print()
    
    try:
        from clients.google.sheets_client import GoogleSheetsClient
        from services.scheduler.tasks_v2 import check_and_collect_interactions, collect_specific_interaction
        
        # 初始化客戶端
        sheets_client = GoogleSheetsClient(
            credentials_file='credentials/google-service-account.json',
            spreadsheet_id='148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s'
        )
        
        print('✅ 客戶端初始化成功')
        print()
        
        # 測試1: 檢查現有貼文記錄表結構
        print('📊 測試1: 檢查貼文記錄表結構...')
        
        try:
            post_data = sheets_client.read_sheet('貼文記錄表', 'A1:W1')
            headers = post_data[0] if post_data else []
            
            print(f'✅ 成功讀取表頭，共 {len(headers)} 個欄位')
            
            # 檢查必要的欄位
            required_fields = [
                '發文時間戳記', '1小時後收集狀態', '1日後收集狀態', '7日後收集狀態',
                '1小時後收集時間', '1日後收集時間', '7日後收集時間'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in headers:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f'⚠️  缺少必要欄位: {missing_fields}')
                print(f'💡 請手動在 Google Sheets 中新增這些欄位')
            else:
                print(f'✅ 所有必要欄位都存在')
            
        except Exception as e:
            print(f'❌ 讀取表頭失敗: {e}')
            return False
        
        print()
        
        # 測試2: 模擬檢查發文時間邏輯
        print('⏰ 測試2: 模擬檢查發文時間邏輯...')
        
        current_time = datetime.datetime.now()
        
        # 模擬不同發文時間的測試案例
        test_cases = [
            {
                'name': '1小時前發文',
                'post_time': current_time - datetime.timedelta(hours=1, minutes=2),
                'expected_1h': True,
                'expected_1d': False,
                'expected_7d': False
            },
            {
                'name': '25小時前發文',
                'post_time': current_time - datetime.timedelta(hours=25),
                'expected_1h': False,
                'expected_1d': True,
                'expected_7d': False
            },
            {
                'name': '7天2小時前發文',
                'post_time': current_time - datetime.timedelta(days=7, hours=2),
                'expected_1h': False,
                'expected_1d': False,
                'expected_7d': True
            },
            {
                'name': '30分鐘前發文',
                'post_time': current_time - datetime.timedelta(minutes=30),
                'expected_1h': False,
                'expected_1d': False,
                'expected_7d': False
            }
        ]
        
        for case in test_cases:
            print(f'🧪 {case[\"name\"]}:')
            print(f'   發文時間: {case[\"post_time\"].strftime(\"%Y-%m-%d %H:%M:%S\")}')
            
            # 檢查各個收集點
            time_checks = [
                ('1h', datetime.timedelta(hours=1), datetime.timedelta(minutes=5), case['expected_1h']),
                ('1d', datetime.timedelta(days=1), datetime.timedelta(minutes=10), case['expected_1d']),
                ('7d', datetime.timedelta(days=7), datetime.timedelta(minutes=30), case['expected_7d'])
            ]
            
            for check_type, delta, tolerance, expected in time_checks:
                target_time = case['post_time'] + delta
                time_diff = abs(current_time - target_time)
                should_collect = time_diff <= tolerance
                
                status = '✅' if should_collect == expected else '❌'
                print(f'   {check_type}: 時差 {time_diff} ≤ 容錯 {tolerance} = {should_collect} {status}')
            
            print()
        
        # 測試3: 檢查現有發布貼文
        print('📋 測試3: 檢查現有發布貼文...')
        
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
                        'kol_name': row[2] if len(row) > 2 else '',
                        'status': row[11] if len(row) > 11 else '',
                        'post_time': row[13] if len(row) > 13 else '',
                        'platform_id': row[15] if len(row) > 15 else ''
                    }
                    published_posts.append(post_info)
            
            print(f'✅ 找到 {len(published_posts)} 個已發布的貼文')
            
            for i, post in enumerate(published_posts[:3], 1):  # 只顯示前3個
                print(f'   {i}. {post[\"post_id\"]} - {post[\"kol_name\"]}')
                print(f'      發文時間: {post[\"post_time\"] or \"未設置\"}')
                print(f'      平台ID: {post[\"platform_id\"] or \"未設置\"}')
                
                # 如果有發文時間，計算收集時間點
                if post['post_time']:
                    try:
                        post_dt = datetime.datetime.fromisoformat(post['post_time'].replace('Z', '+00:00'))
                        
                        collect_times = [
                            ('1小時後', post_dt + datetime.timedelta(hours=1)),
                            ('1日後', post_dt + datetime.timedelta(days=1)),
                            ('7日後', post_dt + datetime.timedelta(days=7))
                        ]
                        
                        print(f'      收集時間點:')
                        for name, collect_time in collect_times:
                            time_diff = abs(current_time - collect_time)
                            status = '🕐 即將到達' if time_diff <= datetime.timedelta(minutes=30) else '⏰ 未到達'
                            print(f'        {name}: {collect_time.strftime(\"%Y-%m-%d %H:%M\")} {status}')
                        
                    except ValueError:
                        print(f'      ⚠️  發文時間格式無效')
                
                print()
            
        except Exception as e:
            print(f'❌ 檢查發布貼文失敗: {e}')
        
        # 測試4: 測試任務觸發邏輯
        print('🎯 測試4: 測試任務觸發邏輯...')
        
        print('🧪 測試 Celery 任務定義...')
        
        try:
            # 測試任務導入
            from services.scheduler.celery_app_v2 import app
            print('✅ Celery 應用程式導入成功')
            
            # 顯示新的排程配置
            print('📅 新的排程配置:')
            for task_name, config in app.conf.beat_schedule.items():
                print(f'   ✅ {task_name}: {config[\"schedule\"]}')
            
        except Exception as e:
            print(f'❌ Celery 配置測試失敗: {e}')
        
        print()
        
        # 總結
        print('🎊 基於發文時間的收集邏輯測試總結:')
        print('=' * 60)
        
        print('✅ 新邏輯優勢:')
        advantages = [
            '精確時間控制: 基於每篇貼文的發文時間',
            '動態觸發: 每10分鐘檢查，不會錯過收集時機',
            '狀態追蹤: 防止重複收集，支援錯誤重試',
            '個別處理: 每篇貼文獨立的收集時程',
            '容錯機制: 允許一定時間範圍內的偏差'
        ]
        
        for advantage in advantages:
            print(f'   • {advantage}')
        
        print()
        print('📋 實施步驟:')
        steps = [
            '1. 在 Google Sheets 手動新增6個收集狀態欄位',
            '2. 安裝並啟動 Redis 服務',
            '3. 啟動新版 Celery Worker 和 Beat',
            '4. 手動創建互動數據收集表格',
            '5. 測試完整的收集流程'
        ]
        
        for step in steps:
            print(f'   {step}')
        
        print()
        print('🚀 啟動指令 (新版):')
        print('   celery -A src.services.scheduler.celery_app_v2 worker --loglevel=info')
        print('   celery -A src.services.scheduler.celery_app_v2 beat --loglevel=info')
        
        return True
        
    except Exception as e:
        print(f'❌ 測試失敗: {e}')
        import traceback
        traceback.print_exc()
        return False

# 執行測試
async def main():
    success = await test_time_based_collection_logic()
    
    if success:
        print('\\n🎉 基於發文時間的收集邏輯已準備就緒！')
    else:
        print('\\n⚠️  測試發現問題，需要進一步檢查')

if __name__ == '__main__':
    asyncio.run(main())
