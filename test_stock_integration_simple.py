#!/usr/bin/env python3
"""
簡化版股票整合測試
跳過需要 OpenAI API 的部分，專注測試股票查詢和分配功能
"""
import sys
import asyncio
import os
from pathlib import Path
from datetime import datetime

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from services.stock.topic_stock_service import create_topic_stock_service

async def test_stock_integration_simple():
    """簡化版股票整合測試"""
    
    print("🚀 簡化版股票整合測試")
    print("=" * 50)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. 初始化客戶端
        print("📋 初始化客戶端...")
        cmoney_client = CMoneyClient()
        
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
        
        # 3. 測試股票查詢服務
        print("\n🔍 測試股票查詢服務...")
        stock_service = create_topic_stock_service()
        
        # 測試前3個話題
        test_topics = topics[:3]
        topics_with_stocks = []
        
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
                
                topics_with_stocks.append({
                    'topic': topic,
                    'stock_data': stock_data,
                    'assignments': assignments
                })
            else:
                print(f"    無相關股票")
                topics_with_stocks.append({
                    'topic': topic,
                    'stock_data': stock_data,
                    'assignments': {}
                })
            
            # 添加延遲避免 API 限制
            await asyncio.sleep(1)
        
        # 4. 統計結果
        print(f"\n📊 統計結果:")
        total_topics = len(topics_with_stocks)
        topics_with_stock = sum(1 for t in topics_with_stocks if t['stock_data'].has_stocks)
        total_stocks = sum(len(t['stock_data'].stocks) for t in topics_with_stocks)
        total_assignments = sum(len(t['assignments']) for t in topics_with_stocks)
        stock_assignments = sum(sum(1 for stock in t['assignments'].values() if stock is not None) for t in topics_with_stocks)
        
        print(f"  測試話題數: {total_topics}")
        print(f"  有股票的話題: {topics_with_stock}")
        print(f"  總股票數: {total_stocks}")
        print(f"  總分配任務: {total_assignments}")
        print(f"  股票分配任務: {stock_assignments}")
        print(f"  股票話題比例: {topics_with_stock/total_topics*100:.1f}%")
        print(f"  股票分配率: {stock_assignments/total_assignments*100:.1f}%" if total_assignments > 0 else "  股票分配率: 0%")
        
        # 5. 測試特定話題（之前測試過的）
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
        
        print(f"\n✅ 簡化版測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_stock_service_only():
    """只測試股票服務功能"""
    
    print("\n🔍 只測試股票服務功能")
    print("=" * 40)
    
    try:
        stock_service = create_topic_stock_service()
        
        # 測試多個話題 ID
        test_topic_ids = [
            "136405de-3cfb-4112-8124-af4f0d42bdd8",  # 美政府入股台積電
            "4d3eab24-dc2d-4051-9656-15dc8cb90eb9",  # 大盤重返2萬4
        ]
        
        for topic_id in test_topic_ids:
            print(f"\n測試話題: {topic_id}")
            
            stock_data = await stock_service.get_topic_stocks(topic_id)
            
            print(f"  標題: {stock_data.topic_title}")
            print(f"  有股票: {stock_data.has_stocks}")
            
            if stock_data.stocks:
                print(f"  股票:")
                for stock in stock_data.stocks:
                    print(f"    - {stock.stock_id}: {stock.stock_name}")
                
                # 測試分配
                test_kols = ["200", "201", "202"]
                assignments = stock_service.assign_stocks_to_kols(stock_data.stocks, test_kols)
                
                print(f"  分配結果:")
                for kol_serial, stock in assignments.items():
                    if stock:
                        print(f"    KOL {kol_serial}: {stock.stock_id} ({stock.stock_name})")
                    else:
                        print(f"    KOL {kol_serial}: 無股票")
            else:
                print(f"  無相關股票")
            
            await asyncio.sleep(0.5)
        
        return True
        
    except Exception as e:
        print(f"❌ 股票服務測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始簡化版股票整合測試")
    print()
    
    # 執行主要測試
    success1 = asyncio.run(test_stock_integration_simple())
    
    # 執行股票服務測試
    success2 = asyncio.run(test_stock_service_only())
    
    print(f"\n{'✅ 所有測試完成!' if success1 and success2 else '❌ 部分測試失敗!'}")
    
    if success1 and success2:
        print("\n🎉 股票整合功能正常!")
        print("✅ 系統現在支援:")
        print("  - 自動查詢話題相關股票")
        print("  - 隨機分配股票給 KOL")
        print("  - 處理有股票和無股票的話題")
        print("  - 整合到話題處理流程")
        print("\n📝 下一步:")
        print("  - 設定 OpenAI API 金鑰以啟用內容生成")
        print("  - 整合 OHLC 數據獲取")
        print("  - 部署到生產環境")
    else:
        print("\n⚠️ 需要檢查以下問題:")
        print("  - CMoney API 連接")
        print("  - 話題股票查詢功能")
        print("  - 股票分配邏輯")



