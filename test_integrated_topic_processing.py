#!/usr/bin/env python3
"""
測試整合後的話題處理流程
包含股票查詢、分配和內容生成
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
from services.stock.topic_stock_service import create_topic_stock_service

async def test_integrated_topic_processing():
    """測試整合後的話題處理流程"""
    
    print("🚀 測試整合後的話題處理流程")
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
        
        # 3. 轉換話題格式
        print("\n📝 轉換話題格式...")
        topic_data_list = []
        for topic in topics[:3]:  # 只處理前3個話題
            topic_data_list.append({
                'id': topic.id,
                'title': topic.title,
                'content': topic.name
            })
            print(f"  - {topic.id}: {topic.title}")
        
        # 4. 測試股票查詢服務
        print("\n🔍 測試股票查詢服務...")
        stock_service = create_topic_stock_service()
        
        for topic_data in topic_data_list:
            stock_data = await stock_service.get_topic_stocks(topic_data['id'])
            print(f"  話題 {topic_data['id']}:")
            print(f"    標題: {stock_data.topic_title}")
            print(f"    有股票: {stock_data.has_stocks}")
            if stock_data.stocks:
                for stock in stock_data.stocks:
                    print(f"      股票: {stock.stock_id} ({stock.stock_name})")
            else:
                print(f"      無相關股票")
        
        # 5. 測試完整的話題處理流程
        print("\n⚙️ 測試完整的話題處理流程...")
        topic_processor = create_topic_processor(sheets_client)
        
        processed_topics = await topic_processor.process_topics(topic_data_list)
        
        print(f"✅ 成功處理 {len(processed_topics)} 個話題")
        
        # 6. 分析處理結果
        print("\n📊 處理結果分析:")
        total_assignments = 0
        stock_assignments = 0
        content_generated = 0
        
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
                    else:
                        print(f"    KOL {kol_serial}: 無股票")
            
            print(f"  生成內容數量: {len(processed_topic.generated_content or {})}")
            
            # 統計
            total_assignments += len(processed_topic.assignments)
            if processed_topic.stock_assignments:
                stock_assignments += sum(1 for stock in processed_topic.stock_assignments.values() if stock is not None)
            content_generated += len(processed_topic.generated_content or {})
            
            # 顯示生成的內容示例
            if processed_topic.generated_content:
                print(f"  內容示例:")
                for kol_serial, content in list(processed_topic.generated_content.items())[:1]:  # 只顯示第一個
                    if content.success:
                        print(f"    KOL {kol_serial}:")
                        print(f"      標題: {content.title}")
                        print(f"      內容: {content.content[:100]}...")
                    else:
                        print(f"    KOL {kol_serial}: 生成失敗 - {content.error_message}")
        
        # 7. 總結統計
        print(f"\n📈 總結統計:")
        print(f"  處理話題數: {len(processed_topics)}")
        print(f"  總分配任務: {total_assignments}")
        print(f"  股票相關任務: {stock_assignments}")
        print(f"  成功生成內容: {content_generated}")
        print(f"  股票分配率: {stock_assignments/total_assignments*100:.1f}%" if total_assignments > 0 else "  股票分配率: 0%")
        
        # 8. 測試股票分配邏輯
        print(f"\n🎯 測試股票分配邏輯:")
        if processed_topics:
            first_topic = processed_topics[0]
            if first_topic.stock_data.get('has_stocks', False):
                print(f"  話題有股票，已隨機分配給 KOL")
                for kol_serial, stock in first_topic.stock_assignments.items():
                    if stock:
                        print(f"    KOL {kol_serial} 分配到: {stock.stock_id} ({stock.stock_name})")
            else:
                print(f"  話題沒有股票，所有 KOL 都沒有分配到股票")
        
        print(f"\n✅ 整合測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_specific_topic():
    """測試特定話題的處理"""
    
    print("\n🔍 測試特定話題處理")
    print("=" * 40)
    
    # 使用之前測試過的話題 ID
    test_topic_id = "136405de-3cfb-4112-8124-af4f0d42bdd8"
    
    try:
        # 初始化服務
        stock_service = create_topic_stock_service()
        
        # 查詢股票資訊
        stock_data = await stock_service.get_topic_stocks(test_topic_id)
        
        print(f"話題 ID: {stock_data.topic_id}")
        print(f"話題標題: {stock_data.topic_title}")
        print(f"有股票: {stock_data.has_stocks}")
        
        if stock_data.stocks:
            print("股票列表:")
            for stock in stock_data.stocks:
                print(f"  - {stock.stock_id}: {stock.stock_name}")
            
            # 測試股票分配
            test_kols = ["200", "201", "202"]
            assignments = stock_service.assign_stocks_to_kols(stock_data.stocks, test_kols)
            
            print("\n股票分配結果:")
            for kol_serial, stock in assignments.items():
                if stock:
                    print(f"  KOL {kol_serial}: {stock.stock_id} ({stock.stock_name})")
                else:
                    print(f"  KOL {kol_serial}: 無股票")
        else:
            print("無相關股票")
        
        return True
        
    except Exception as e:
        print(f"❌ 特定話題測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始整合測試")
    print()
    
    # 執行主要測試
    success1 = asyncio.run(test_integrated_topic_processing())
    
    # 執行特定話題測試
    success2 = asyncio.run(test_specific_topic())
    
    print(f"\n{'✅ 所有測試完成!' if success1 and success2 else '❌ 部分測試失敗!'}")
    
    if success1 and success2:
        print("\n🎉 整合成功! 系統現在支援:")
        print("  ✅ 自動查詢話題相關股票")
        print("  ✅ 隨機分配股票給 KOL")
        print("  ✅ 根據股票資訊生成內容")
        print("  ✅ 整合到現有的話題處理流程")
        print("  ✅ 支援有股票和無股票的話題")
    else:
        print("\n⚠️ 需要檢查以下問題:")
        print("  - CMoney API 連接")
        print("  - Google Sheets 權限")
        print("  - 話題股票查詢功能")
        print("  - 內容生成服務")



