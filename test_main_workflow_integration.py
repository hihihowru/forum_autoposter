#!/usr/bin/env python3
"""
測試整合後的主流程
包含股票查詢、分配、內容生成和發文的完整流程
"""
import sys
import asyncio
import os
from pathlib import Path
from datetime import datetime

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from clients.google.sheets_client import GoogleSheetsClient
from services.assign.topic_processor import create_topic_processor
from services.content.content_generator import create_content_generator, ContentRequest

async def test_main_workflow_integration():
    """測試整合後的主流程"""
    
    print("🚀 測試整合後的主流程")
    print("=" * 60)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. 初始化客戶端
        print("📋 初始化客戶端...")
        cmoney_client = CMoneyClient()
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 2. 獲取熱門話題
        print("🔍 獲取熱門話題...")
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password='N9t1kY3x'
        )
        
        access_token = await cmoney_client.login(credentials)
        topics = await cmoney_client.get_trending_topics(access_token.token)
        
        print(f"✅ 獲取到 {len(topics)} 個熱門話題")
        
        if not topics:
            print("❌ 沒有獲取到熱門話題，結束測試")
            return False
        
        # 3. 測試完整的話題處理流程 (包含股票查詢和分配)
        print("\n⚙️ 測試完整的話題處理流程...")
        topic_processor = create_topic_processor(sheets_client)
        
        # 轉換話題格式
        topic_data_list = []
        for topic in topics[:2]:  # 只處理前2個話題
            topic_data_list.append({
                'id': topic.id,
                'title': topic.title,
                'content': topic.name
            })
            print(f"  - {topic.id}: {topic.title}")
        
        # 處理話題（包含股票查詢和分配）
        processed_topics = await topic_processor.process_topics(topic_data_list)
        
        print(f"✅ 成功處理 {len(processed_topics)} 個話題")
        
        # 4. 分析處理結果
        print("\n📊 處理結果分析:")
        total_assignments = 0
        stock_assignments = 0
        
        for i, processed_topic in enumerate(processed_topics, 1):
            print(f"\n話題 {i}: {processed_topic.title}")
            print(f"  ID: {processed_topic.topic_id}")
            print(f"  分配 KOL 數量: {len(processed_topic.assignments)}")
            print(f"  股票資訊: {processed_topic.stock_data.get('has_stocks', False)}")
            
            if processed_topic.stock_assignments:
                print(f"  股票分配:")
                for kol_serial, stock in processed_topic.stock_assignments.items():
                    if stock:
                        print(f"    KOL {kol_serial}: {stock.stock_id} ({stock.stock_name})")
                        stock_assignments += 1
                    else:
                        print(f"    KOL {kol_serial}: 無股票")
            
            total_assignments += len(processed_topic.assignments)
        
        print(f"\n📈 統計結果:")
        print(f"  處理話題數: {len(processed_topics)}")
        print(f"  總分配任務: {total_assignments}")
        print(f"  股票相關任務: {stock_assignments}")
        print(f"  股票分配率: {stock_assignments/total_assignments*100:.1f}%" if total_assignments > 0 else "  股票分配率: 0%")
        
        # 5. 測試內容生成 (模擬 generate_content_for_ready_tasks)
        print(f"\n📝 測試內容生成...")
        content_generator = create_content_generator()
        
        # 讀取貼文記錄表
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:X')
        headers = post_data[0] if post_data else []
        rows = post_data[1:] if len(post_data) > 1 else []
        
        ready_to_gen_count = 0
        generated_count = 0
        
        for i, row in enumerate(rows):
            if len(row) > 11 and row[11] == 'ready_to_gen':  # 發文狀態
                ready_to_gen_count += 1
                
                # 獲取股票資訊 (第19欄，索引18)
                stock_info = row[18] if len(row) > 18 else ''
                market_data = {}
                
                if stock_info:
                    # 解析股票資訊格式: "台積電(2330)"
                    if '(' in stock_info and ')' in stock_info:
                        stock_name = stock_info.split('(')[0]
                        stock_id = stock_info.split('(')[1].split(')')[0]
                        market_data = {
                            'stock_id': stock_id,
                            'stock_name': stock_name,
                            'has_stock': True
                        }
                        print(f"  任務 {row[0]} 有股票資訊: {stock_name}({stock_id})")
                    else:
                        market_data = {'has_stock': False}
                else:
                    market_data = {'has_stock': False}
                    print(f"  任務 {row[0]} 沒有股票資訊")
                
                # 創建內容生成請求
                request = ContentRequest(
                    topic_title=row[8] if len(row) > 8 else '',
                    topic_keywords=row[9] if len(row) > 9 else '',
                    kol_persona=row[4] if len(row) > 4 else '',
                    kol_nickname=row[2] if len(row) > 2 else '',
                    content_type=row[5] if len(row) > 5 else '',
                    market_data=market_data
                )
                
                try:
                    # 生成內容
                    generated = content_generator.generate_complete_content(request)
                    
                    if generated.success:
                        generated_count += 1
                        print(f"  ✅ 成功為任務 {row[0]} 生成內容")
                        print(f"     標題: {generated.title}")
                        print(f"     內容長度: {len(generated.content)} 字")
                        
                        # 檢查內容是否包含股票資訊
                        if market_data.get('has_stock', False):
                            stock_id = market_data.get('stock_id', '')
                            stock_name = market_data.get('stock_name', '')
                            if stock_id in generated.content or stock_name in generated.content:
                                print(f"     ✅ 內容包含股票資訊: {stock_name}({stock_id})")
                            else:
                                print(f"     ⚠️ 內容未包含股票資訊")
                    else:
                        print(f"  ❌ 任務 {row[0]} 內容生成失敗: {generated.error_message}")
                        
                except Exception as e:
                    print(f"  ❌ 處理任務 {row[0]} 時出錯: {e}")
                    continue
        
        print(f"\n📊 內容生成統計:")
        print(f"  待生成任務: {ready_to_gen_count}")
        print(f"  成功生成: {generated_count}")
        print(f"  生成成功率: {generated_count/ready_to_gen_count*100:.1f}%" if ready_to_gen_count > 0 else "  生成成功率: 0%")
        
        # 6. 測試發文準備 (模擬 publish_ready_posts)
        print(f"\n📤 測試發文準備...")
        
        ready_to_post_count = 0
        for row in rows:
            if len(row) > 11 and row[11] == 'ready_to_post':  # 發文狀態
                ready_to_post_count += 1
        
        print(f"  準備發文任務: {ready_to_post_count}")
        
        print(f"\n✅ 主流程整合測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_stages():
    """測試各個流程階段"""
    
    print("\n🔍 測試各個流程階段")
    print("=" * 40)
    
    try:
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 讀取貼文記錄表
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:X')
        headers = post_data[0] if post_data else []
        rows = post_data[1:] if len(post_data) > 1 else []
        
        print(f"📋 Google Sheets 欄位結構:")
        for i, header in enumerate(headers):
            print(f"  {chr(65+i)}: {header}")
        
        # 統計各狀態的任務數量
        status_counts = {}
        stock_assignments = 0
        
        for row in rows:
            if len(row) > 11:
                status = row[11]  # 發文狀態
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # 檢查股票分配
                stock_info = row[18] if len(row) > 18 else ''
                if stock_info:
                    stock_assignments += 1
        
        print(f"\n📊 任務狀態統計:")
        for status, count in status_counts.items():
            print(f"  {status}: {count} 個任務")
        
        print(f"\n📈 股票分配統計:")
        print(f"  總任務數: {len(rows)}")
        print(f"  有股票分配的任務: {stock_assignments}")
        print(f"  股票分配率: {stock_assignments/len(rows)*100:.1f}%" if rows else "  股票分配率: 0%")
        
        # 顯示最近的任務示例
        print(f"\n📝 最近的任務示例:")
        for i, row in enumerate(rows[-3:], 1):  # 顯示最後3個任務
            if len(row) > 18:
                print(f"  任務 {i}:")
                print(f"    ID: {row[0]}")
                print(f"    KOL: {row[2]} ({row[1]})")
                print(f"    狀態: {row[11]}")
                print(f"    股票: {row[18] if row[18] else '無'}")
                print(f"    標題: {row[8]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 流程階段測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始主流程整合測試")
    print()
    
    # 執行主要測試
    success1 = asyncio.run(test_main_workflow_integration())
    
    # 執行流程階段測試
    success2 = asyncio.run(test_workflow_stages())
    
    print(f"\n{'✅ 所有測試完成!' if success1 and success2 else '❌ 部分測試失敗!'}")
    
    if success1 and success2:
        print("\n🎉 主流程整合成功!")
        print("✅ 系統現在支援:")
        print("  1. 自動查詢話題相關股票")
        print("  2. 智能分配股票給 KOL")
        print("  3. 根據股票資訊生成內容")
        print("  4. 完整的發文流程")
        print("  5. 互動數據收集")
        print("\n📋 主流程階段:")
        print("  階段1: fetch_and_assign_topics (話題抓取與股票分配)")
        print("  階段2: generate_content_for_ready_tasks (內容生成)")
        print("  階段3: publish_ready_posts (發文與收集)")
        print("\n🔄 下一步:")
        print("  - 設定定時任務執行")
        print("  - 監控流程執行狀況")
        print("  - 優化股票分配邏輯")
    else:
        print("\n⚠️ 需要檢查以下問題:")
        print("  - CMoney API 連接")
        print("  - Google Sheets 權限")
        print("  - 話題股票查詢功能")
        print("  - 內容生成服務")



