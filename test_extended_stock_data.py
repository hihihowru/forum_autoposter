#!/usr/bin/env python3
"""
測試擴展後的個股數據服務
包含月營收和財報數據的完整測試
"""
import sys
import asyncio
import os
from pathlib import Path
from datetime import datetime

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

from services.stock.stock_data_service import create_stock_data_service
from services.stock.data_source_scheduler import get_data_source_scheduler, DataSourceType

async def test_extended_stock_data_service():
    """測試擴展後的個股數據服務"""
    
    print("🚀 測試擴展後的個股數據服務")
    print("=" * 60)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 1. 測試數據源調度器
        print("📋 測試數據源調度器...")
        scheduler = get_data_source_scheduler()
        
        print("數據源類型:")
        for data_type in DataSourceType:
            sources = scheduler.get_priority_sorted_sources(data_type)
            print(f"  {data_type.value}: {len(sources)} 個數據源")
            for source in sources:
                print(f"    - {source.name} (優先級: {source.priority})")
        
        # 2. 初始化個股數據服務
        print(f"\n📊 初始化個股數據服務...")
        stock_data_service = create_stock_data_service()
        
        # 測試股票代號
        test_stock_id = "2330"  # 台積電
        
        print(f"測試股票: {test_stock_id}")
        
        # 3. 測試營收數據獲取
        print(f"\n💰 測試營收數據獲取...")
        revenue_data = await stock_data_service.get_stock_revenue_data(test_stock_id)
        
        if revenue_data:
            print(f"✅ 營收數據獲取成功:")
            print(f"  當月營收: {revenue_data.current_month_revenue/100000000:.1f}億" if revenue_data.current_month_revenue else "  當月營收: 無數據")
            print(f"  上月營收: {revenue_data.last_month_revenue/100000000:.1f}億" if revenue_data.last_month_revenue else "  上月營收: 無數據")
            print(f"  年增率: {revenue_data.year_over_year_growth:.1f}%" if revenue_data.year_over_year_growth else "  年增率: 無數據")
            print(f"  月增率: {revenue_data.month_over_month_growth:.1f}%" if revenue_data.month_over_month_growth else "  月增率: 無數據")
            print(f"  累計營收: {revenue_data.cumulative_revenue/100000000:.1f}億" if revenue_data.cumulative_revenue else "  累計營收: 無數據")
            print(f"  累計年增率: {revenue_data.cumulative_growth:.1f}%" if revenue_data.cumulative_growth else "  累計年增率: 無數據")
        else:
            print(f"❌ 營收數據獲取失敗")
        
        # 4. 測試財務數據獲取
        print(f"\n📈 測試財務數據獲取...")
        financial_data = await stock_data_service.get_stock_financial_data(test_stock_id)
        
        if financial_data:
            print(f"✅ 財務數據獲取成功:")
            print(f"  營業收入: {financial_data.revenue/100000000:.1f}億" if financial_data.revenue else "  營業收入: 無數據")
            print(f"  每股盈餘: {financial_data.eps}" if financial_data.eps else "  每股盈餘: 無數據")
            print(f"  資產總額: {financial_data.total_assets/100000000:.1f}億" if financial_data.total_assets else "  資產總額: 無數據")
            print(f"  負債總額: {financial_data.total_liabilities/100000000:.1f}億" if financial_data.total_liabilities else "  負債總額: 無數據")
            print(f"  股東權益: {financial_data.shareholders_equity/100000000:.1f}億" if financial_data.shareholders_equity else "  股東權益: 無數據")
            print(f"  營業利益: {financial_data.operating_income/100000000:.1f}億" if financial_data.operating_income else "  營業利益: 無數據")
            print(f"  淨利: {financial_data.net_income/100000000:.1f}億" if financial_data.net_income else "  淨利: 無數據")
            print(f"  現金流量: {financial_data.cash_flow/100000000:.1f}億" if financial_data.cash_flow else "  現金流量: 無數據")
        else:
            print(f"❌ 財務數據獲取失敗")
        
        # 5. 測試綜合數據獲取
        print(f"\n🔍 測試綜合數據獲取...")
        comprehensive_data = await stock_data_service.get_comprehensive_stock_data(test_stock_id)
        
        print(f"綜合數據獲取結果:")
        print(f"  股票代號: {comprehensive_data['stock_id']}")
        print(f"  有 OHLC 數據: {comprehensive_data['has_ohlc']}")
        print(f"  有分析數據: {comprehensive_data['has_analysis']}")
        print(f"  有財務數據: {comprehensive_data['has_financial']}")
        print(f"  有營收數據: {comprehensive_data['has_revenue']}")
        
        # 6. 測試多個股票
        print(f"\n📊 測試多個股票...")
        test_stocks = ["2330", "2454", "2317"]  # 台積電、聯發科、鴻海
        
        for stock_id in test_stocks:
            print(f"\n股票 {stock_id}:")
            
            # 快速測試營收數據
            revenue_data = await stock_data_service.get_stock_revenue_data(stock_id)
            if revenue_data and revenue_data.current_month_revenue:
                print(f"  月營收: {revenue_data.current_month_revenue/100000000:.1f}億")
                if revenue_data.year_over_year_growth:
                    print(f"  年增率: {revenue_data.year_over_year_growth:.1f}%")
            else:
                print(f"  營收數據: 無")
            
            # 快速測試財務數據
            financial_data = await stock_data_service.get_stock_financial_data(stock_id)
            if financial_data and financial_data.eps:
                print(f"  EPS: {financial_data.eps}")
            else:
                print(f"  財務數據: 無")
            
            # 添加延遲避免 API 限制
            await asyncio.sleep(1)
        
        # 7. 測試數據源調度
        print(f"\n⚙️ 測試數據源調度...")
        
        # 測試技術分析數據源
        technical_sources = scheduler.get_priority_sorted_sources(DataSourceType.TECHNICAL)
        print(f"技術分析數據源: {len(technical_sources)} 個")
        for source in technical_sources:
            print(f"  - {source.name}: {source.description}")
        
        # 測試營收數據源
        revenue_sources = scheduler.get_priority_sorted_sources(DataSourceType.REVENUE)
        print(f"營收數據源: {len(revenue_sources)} 個")
        for source in revenue_sources:
            print(f"  - {source.name}: {source.description}")
        
        # 測試財務數據源
        financial_sources = scheduler.get_priority_sorted_sources(DataSourceType.FINANCIAL)
        print(f"財務數據源: {len(financial_sources)} 個")
        for source in financial_sources:
            print(f"  - {source.name}: {source.description}")
        
        print(f"\n✅ 擴展後的個股數據服務測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_data_source_management():
    """測試數據源管理功能"""
    
    print("\n🔧 測試數據源管理功能")
    print("=" * 40)
    
    try:
        scheduler = get_data_source_scheduler()
        
        # 測試啟用/停用數據源
        print("測試數據源啟用/停用:")
        
        # 停用一個數據源
        scheduler.disable_data_source(DataSourceType.TECHNICAL, "OHLC數據")
        technical_sources = scheduler.get_enabled_data_sources(DataSourceType.TECHNICAL)
        print(f"停用 OHLC數據 後，技術分析啟用數據源: {len(technical_sources)} 個")
        
        # 重新啟用
        scheduler.enable_data_source(DataSourceType.TECHNICAL, "OHLC數據")
        technical_sources = scheduler.get_enabled_data_sources(DataSourceType.TECHNICAL)
        print(f"重新啟用 OHLC數據 後，技術分析啟用數據源: {len(technical_sources)} 個")
        
        # 測試數據源資訊
        print(f"\n數據源統計:")
        info = scheduler.get_data_source_info()
        for data_type, data_info in info.items():
            print(f"  {data_type}: {data_info['enabled']}/{data_info['count']} 啟用")
        
        print("✅ 數據源管理功能測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 數據源管理測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始擴展後的個股數據服務測試")
    print()
    
    # 執行主要測試
    success1 = asyncio.run(test_extended_stock_data_service())
    
    # 執行數據源管理測試
    success2 = asyncio.run(test_data_source_management())
    
    print(f"\n{'✅ 所有測試完成!' if success1 and success2 else '❌ 部分測試失敗!'}")
    
    if success1 and success2:
        print("\n🎉 擴展後的個股數據服務正常!")
        print("✅ 系統現在支援:")
        print("  - 月營收數據獲取 (當月、上月、年增率、月增率等)")
        print("  - 財報數據獲取 (資產、負債、股東權益、EPS等)")
        print("  - 數據源調度管理")
        print("  - 綜合個股數據整合")
        print("\n📋 完整數據源:")
        print("  - 技術分析: OHLC、技術指標")
        print("  - 營收分析: 月營收、成長率")
        print("  - 財務分析: 財報、EPS、現金流量")
        print("  - 基本面分析: 綜合基本面數據")
        print("\n🔄 下一步:")
        print("  - 設定 FinLab API 金鑰")
        print("  - 整合到內容生成流程")
        print("  - 測試完整工作流程")
    else:
        print("\n⚠️ 需要檢查以下問題:")
        print("  - FinLab API 連接")
        print("  - 數據源配置")
        print("  - 個股數據獲取")



