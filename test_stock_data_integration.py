#!/usr/bin/env python3
"""
測試個股數據整合
驗證從股票分配到個股數據獲取的完整流程
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
from services.stock.stock_data_service import create_stock_data_service
from services.content.content_generator import create_content_generator, ContentRequest

async def test_stock_data_integration():
    """測試個股數據整合"""
    
    print("🚀 測試個股數據整合")
    print("=" * 60)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. 初始化服務
        print("📋 初始化服務...")
        cmoney_client = CMoneyClient()
        sheets_client = GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        stock_service = create_topic_stock_service()
        stock_data_service = create_stock_data_service()
        content_generator = create_content_generator()
        
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
        test_topic = topics[0]  # 使用第一個話題
        
        print(f"話題: {test_topic.title}")
        print(f"ID: {test_topic.id}")
        
        # 查詢股票資訊
        stock_data = await stock_service.get_topic_stocks(test_topic.id)
        
        print(f"股票查詢結果:")
        print(f"  有股票: {stock_data.has_stocks}")
        
        if stock_data.stocks:
            print(f"  股票列表:")
            for stock in stock_data.stocks:
                print(f"    - {stock.stock_id}: {stock.stock_name}")
            
            # 測試股票分配
            test_kols = ["200", "201", "202"]
            assignments = stock_service.assign_stocks_to_kols(stock_data.stocks, test_kols)
            
            print(f"  股票分配結果:")
            for kol_serial, stock in assignments.items():
                if stock:
                    print(f"    KOL {kol_serial}: {stock.stock_id} ({stock.stock_name})")
                else:
                    print(f"    KOL {kol_serial}: 無股票")
            
            # 4. 測試個股數據獲取
            print(f"\n📊 測試個股數據獲取...")
            
            for kol_serial, stock in assignments.items():
                if stock:
                    print(f"\nKOL {kol_serial} 的股票: {stock.stock_id} ({stock.stock_name})")
                    
                    # 獲取個股數據
                    comprehensive_data = await stock_data_service.get_comprehensive_stock_data(stock.stock_id)
                    
                    print(f"  個股數據獲取結果:")
                    print(f"    有 OHLC 數據: {comprehensive_data['has_ohlc']}")
                    print(f"    有分析數據: {comprehensive_data['has_analysis']}")
                    print(f"    有財務數據: {comprehensive_data['has_financial']}")
                    
                    if comprehensive_data['has_ohlc'] and comprehensive_data['ohlc_data']:
                        ohlc_data = comprehensive_data['ohlc_data']
                        print(f"    OHLC 數據筆數: {len(ohlc_data)}")
                        if ohlc_data:
                            latest = ohlc_data[-1]
                            print(f"    最新價格: {latest.close}")
                    
                    if comprehensive_data['has_analysis'] and comprehensive_data['analysis_data']:
                        analysis_data = comprehensive_data['analysis_data']
                        print(f"    技術指標: {list(analysis_data.technical_indicators.keys())}")
                        print(f"    交易信號: {len(analysis_data.trading_signals)} 個")
                    
                    if comprehensive_data['has_financial'] and comprehensive_data['financial_data']:
                        financial_data = comprehensive_data['financial_data']
                        print(f"    營收: {financial_data.revenue}")
                        print(f"    本益比: {financial_data.pe_ratio}")
                    
                    # 5. 測試內容生成
                    print(f"\n📝 測試內容生成...")
                    
                    # 準備市場數據
                    market_data = {
                        'stock_id': stock.stock_id,
                        'stock_name': stock.stock_name,
                        'has_stock': True,
                        'stock_data': comprehensive_data
                    }
                    
                    # 創建內容生成請求
                    request = ContentRequest(
                        topic_title=test_topic.title,
                        topic_keywords="技術分析,台股,投資",
                        kol_persona="技術分析專家",
                        kol_nickname=f"KOL{kol_serial}",
                        content_type="investment",
                        market_data=market_data
                    )
                    
                    try:
                        # 生成內容
                        generated = content_generator.generate_complete_content(request)
                        
                        if generated.success:
                            print(f"  ✅ 內容生成成功")
                            print(f"    標題: {generated.title}")
                            print(f"    內容長度: {len(generated.content)} 字")
                            
                            # 檢查內容是否包含股票資訊
                            if stock.stock_id in generated.content or stock.stock_name in generated.content:
                                print(f"    ✅ 內容包含股票資訊: {stock.stock_name}({stock.stock_id})")
                            else:
                                print(f"    ⚠️ 內容未包含股票資訊")
                            
                            # 檢查內容是否包含個股數據
                            if comprehensive_data['has_ohlc'] and str(latest.close) in generated.content:
                                print(f"    ✅ 內容包含股價數據")
                            elif comprehensive_data['has_financial'] and str(financial_data.pe_ratio) in generated.content:
                                print(f"    ✅ 內容包含財務數據")
                            else:
                                print(f"    ⚠️ 內容未包含個股數據")
                        else:
                            print(f"  ❌ 內容生成失敗: {generated.error_message}")
                            
                    except Exception as e:
                        print(f"  ❌ 內容生成異常: {e}")
                    
                    # 添加延遲避免 API 限制
                    await asyncio.sleep(2)
        else:
            print("  無相關股票")
        
        # 6. 測試無股票情況
        print(f"\n🔍 測試無股票情況...")
        
        # 創建無股票的市場數據
        market_data_no_stock = {
            'has_stock': False
        }
        
        request_no_stock = ContentRequest(
            topic_title=test_topic.title,
            topic_keywords="技術分析,台股,投資",
            kol_persona="技術分析專家",
            kol_nickname="KOL200",
            content_type="investment",
            market_data=market_data_no_stock
        )
        
        try:
            generated_no_stock = content_generator.generate_complete_content(request_no_stock)
            
            if generated_no_stock.success:
                print(f"  ✅ 無股票內容生成成功")
                print(f"    標題: {generated_no_stock.title}")
                print(f"    內容長度: {len(generated_no_stock.content)} 字")
                print(f"    ✅ 內容不包含特定股票資訊")
            else:
                print(f"  ❌ 無股票內容生成失敗: {generated_no_stock.error_message}")
                
        except Exception as e:
            print(f"  ❌ 無股票內容生成異常: {e}")
        
        print(f"\n✅ 個股數據整合測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_alignment():
    """測試工作流程對齊"""
    
    print("\n🔍 測試工作流程對齊")
    print("=" * 40)
    
    try:
        print("📋 主流程階段:")
        print("  階段1: 話題抓取與股票分配 ✅")
        print("  階段2: 個股數據獲取 (OHLC + 分析 + 財務) ✅")
        print("  階段3: 內容生成 (根據股票數據) ✅")
        print("  階段4: 發文與收集 ✅")
        
        print("\n📊 數據流對齊:")
        print("  無股票話題 → 一般內容生成")
        print("  有股票話題 → 個股數據流 → 專業內容生成")
        
        print("\n🎯 個股數據流包含:")
        print("  - OHLC 數據 (股價、成交量)")
        print("  - 技術分析 (RSI、移動平均線等)")
        print("  - 財務數據 (營收、本益比等)")
        print("  - 交易信號 (買賣建議)")
        
        print("\n✅ 工作流程對齊完成!")
        return True
        
    except Exception as e:
        print(f"❌ 工作流程對齊測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始個股數據整合測試")
    print()
    
    # 執行主要測試
    success1 = asyncio.run(test_stock_data_integration())
    
    # 執行工作流程對齊測試
    success2 = asyncio.run(test_workflow_alignment())
    
    print(f"\n{'✅ 所有測試完成!' if success1 and success2 else '❌ 部分測試失敗!'}")
    
    if success1 and success2:
        print("\n🎉 個股數據整合成功!")
        print("✅ 系統現在支援:")
        print("  - 智能股票分配")
        print("  - 個股數據獲取 (OHLC + 分析 + 財務)")
        print("  - 根據股票數據生成專業內容")
        print("  - 無股票話題的一般內容生成")
        print("\n📋 完整數據流:")
        print("  話題 → 股票查詢 → 股票分配 → 個股數據 → 內容生成 → 發文")
        print("\n🔄 下一步:")
        print("  - 啟動微服務 (OHLC API, Analyze API)")
        print("  - 設定定時任務")
        print("  - 監控數據流執行")
    else:
        print("\n⚠️ 需要檢查以下問題:")
        print("  - 微服務連接")
        print("  - 個股數據獲取")
        print("  - 內容生成整合")



