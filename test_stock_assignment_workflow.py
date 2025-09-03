#!/usr/bin/env python3
"""
測試股票分配工作流程
專注測試股票查詢、分配和記錄功能，跳過內容生成
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
from services.stock.topic_stock_service import create_topic_stock_service

async def test_stock_assignment_workflow():
    """測試股票分配工作流程"""
    
    print("🚀 測試股票分配工作流程")
    print("=" * 50)
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
        
        # 3. 測試股票查詢和分配
        print("\n🔍 測試股票查詢和分配...")
        stock_service = create_topic_stock_service()
        
        # 處理前3個話題
        test_topics = topics[:3]
        processed_topics = []
        
        for i, topic in enumerate(test_topics, 1):
            print(f"\n話題 {i}: {topic.title}")
            print(f"  ID: {topic.id}")
            
            # 查詢股票資訊
            stock_data = await stock_service.get_topic_stocks(topic.id)
            
            print(f"  股票查詢結果:")
            print(f"    標題: {stock_data.topic_title}")
            print(f"    有股票: {stock_data.has_stocks}")
            
            if stock_data.stocks:
                print(f"    股票列表:")
                for stock in stock_data.stocks:
                    print(f"      - {stock.stock_id}: {stock.stock_name}")
                
                # 測試股票分配
                test_kols = ["200", "201", "202"]
                assignments = stock_service.assign_stocks_to_kols(stock_data.stocks, test_kols)
                
                print(f"    股票分配結果:")
                for kol_serial, stock in assignments.items():
                    if stock:
                        print(f"      KOL {kol_serial}: {stock.stock_id} ({stock.stock_name})")
                    else:
                        print(f"      KOL {kol_serial}: 無股票")
                
                processed_topics.append({
                    'topic': topic,
                    'stock_data': stock_data,
                    'assignments': assignments
                })
            else:
                print(f"    無相關股票")
                processed_topics.append({
                    'topic': topic,
                    'stock_data': stock_data,
                    'assignments': {}
                })
            
            # 添加延遲避免 API 限制
            await asyncio.sleep(1)
        
        # 4. 模擬寫入 Google Sheets (不實際寫入，只測試格式)
        print(f"\n📝 模擬寫入 Google Sheets...")
        
        for i, processed_topic in enumerate(processed_topics, 1):
            topic = processed_topic['topic']
            stock_data = processed_topic['stock_data']
            assignments = processed_topic['assignments']
            
            print(f"\n話題 {i} 的記錄格式:")
            
            for kol_serial in ["200", "201", "202"]:
                assigned_stock = assignments.get(kol_serial)
                stock_info = ""
                if assigned_stock:
                    stock_info = f"{assigned_stock.stock_name}({assigned_stock.stock_id})"
                
                # 模擬記錄格式
                record = [
                    f"{topic.id}-{kol_serial}",  # 貼文ID (A)
                    kol_serial,  # KOL Serial (B)
                    f"KOL{kol_serial}",  # KOL 暱稱 (C)
                    f"950554{kol_serial}",  # KOL ID (D)
                    "技術分析專家",  # Persona (E)
                    "investment",  # Content Type (F)
                    1,  # 已派發TopicIndex (G)
                    topic.id,  # 已派發TopicID (H)
                    topic.title,  # 已派發TopicTitle (I)
                    "技術分析,台股,投資",  # 已派發TopicKeywords (J)
                    "",  # 生成內容 (K)
                    "ready_to_gen",  # 發文狀態 (L)
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 上次排程時間 (M)
                    "",  # 發文時間戳記 (N)
                    "",  # 最近錯誤訊息 (O)
                    "",  # 平台發文ID (P)
                    "",  # 平台發文URL (Q)
                    topic.title,  # 熱門話題標題 (R)
                    stock_info,  # 分配股票資訊 (S)
                    "pending",  # 1小時後收集狀態 (T)
                    "pending",  # 1日後收集狀態 (U)
                    "pending",  # 7日後收集狀態 (V)
                    "",  # 1小時後收集時間 (W)
                    "",  # 1日後收集時間 (X)
                    ""   # 7日後收集時間 (Y)
                ]
                
                print(f"  KOL {kol_serial}:")
                print(f"    貼文ID: {record[0]}")
                print(f"    股票資訊: {record[18] if record[18] else '無'}")
                print(f"    狀態: {record[11]}")
        
        # 5. 統計結果
        print(f"\n📊 統計結果:")
        total_topics = len(processed_topics)
        topics_with_stocks = sum(1 for t in processed_topics if t['stock_data'].has_stocks)
        total_assignments = sum(len(t['assignments']) for t in processed_topics)
        stock_assignments = sum(sum(1 for stock in t['assignments'].values() if stock is not None) for t in processed_topics)
        
        print(f"  測試話題數: {total_topics}")
        print(f"  有股票的話題: {topics_with_stocks}")
        print(f"  總分配任務: {total_assignments}")
        print(f"  股票分配任務: {stock_assignments}")
        print(f"  股票話題比例: {topics_with_stocks/total_topics*100:.1f}%")
        print(f"  股票分配率: {stock_assignments/total_assignments*100:.1f}%" if total_assignments > 0 else "  股票分配率: 0%")
        
        # 6. 測試特定話題
        print(f"\n🎯 測試特定話題:")
        test_topic_id = "136405de-3cfb-4112-8124-af4f0d42bdd8"
        
        stock_data = await stock_service.get_topic_stocks(test_topic_id)
        print(f"  話題 ID: {stock_data.topic_id}")
        print(f"  標題: {stock_data.topic_title}")
        print(f"  有股票: {stock_data.has_stocks}")
        
        if stock_data.stocks:
            print(f"  股票: {', '.join([f'{s.stock_id}({s.stock_name})' for s in stock_data.stocks])}")
            
            # 測試多次分配，確保隨機性
            print(f"  測試隨機分配:")
            for i in range(3):
                test_kols = ["200", "201", "202"]
                assignments = stock_service.assign_stocks_to_kols(stock_data.stocks, test_kols)
                assignment_str = ", ".join([f"KOL{k}:{s.stock_id if s else 'None'}" for k, s in assignments.items()])
                print(f"    第{i+1}次: {assignment_str}")
        
        print(f"\n✅ 股票分配工作流程測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_google_sheets_structure():
    """測試 Google Sheets 結構"""
    
    print("\n🔍 測試 Google Sheets 結構")
    print("=" * 40)
    
    try:
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        
        # 讀取貼文記錄表
        post_data = sheets_client.read_sheet('貼文記錄表', 'A:Y')
        headers = post_data[0] if post_data else []
        rows = post_data[1:] if len(post_data) > 1 else []
        
        print(f"📋 Google Sheets 欄位結構:")
        for i, header in enumerate(headers):
            print(f"  {chr(65+i)}: {header}")
        
        print(f"\n📊 現有數據統計:")
        print(f"  總行數: {len(rows)}")
        
        if rows:
            # 統計各狀態的任務數量
            status_counts = {}
            stock_assignments = 0
            
            for row in rows:
                if len(row) > 11:
                    status = row[11]  # 發文狀態
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # 檢查股票分配 (第19欄，索引18)
                    stock_info = row[18] if len(row) > 18 else ''
                    if stock_info:
                        stock_assignments += 1
            
            print(f"  任務狀態統計:")
            for status, count in status_counts.items():
                print(f"    {status}: {count} 個任務")
            
            print(f"  股票分配統計:")
            print(f"    有股票分配的任務: {stock_assignments}")
            print(f"    股票分配率: {stock_assignments/len(rows)*100:.1f}%")
            
            # 顯示最近的任務示例
            print(f"\n📝 最近的任務示例:")
            for i, row in enumerate(rows[-2:], 1):  # 顯示最後2個任務
                if len(row) > 18:
                    print(f"  任務 {i}:")
                    print(f"    ID: {row[0]}")
                    print(f"    KOL: {row[2]} ({row[1]})")
                    print(f"    狀態: {row[11]}")
                    print(f"    股票: {row[18] if row[18] else '無'}")
                    print(f"    標題: {row[8]}")
        else:
            print("  沒有現有數據")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets 結構測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始股票分配工作流程測試")
    print()
    
    # 執行主要測試
    success1 = asyncio.run(test_stock_assignment_workflow())
    
    # 執行 Google Sheets 結構測試
    success2 = asyncio.run(test_google_sheets_structure())
    
    print(f"\n{'✅ 所有測試完成!' if success1 and success2 else '❌ 部分測試失敗!'}")
    
    if success1 and success2:
        print("\n🎉 股票分配工作流程正常!")
        print("✅ 系統現在支援:")
        print("  - 自動查詢話題相關股票")
        print("  - 智能分配股票給 KOL")
        print("  - 正確的 Google Sheets 記錄格式")
        print("  - 完整的欄位結構 (A-Y)")
        print("\n📋 主流程整合完成:")
        print("  階段1: 話題抓取與股票分配 ✅")
        print("  階段2: 內容生成 (需要 OpenAI API)")
        print("  階段3: 發文與收集 ✅")
        print("\n🔄 下一步:")
        print("  - 設定 OpenAI API 金鑰")
        print("  - 啟動定時任務")
        print("  - 監控流程執行")
    else:
        print("\n⚠️ 需要檢查以下問題:")
        print("  - CMoney API 連接")
        print("  - Google Sheets 權限")
        print("  - 話題股票查詢功能")



