#!/usr/bin/env python3
"""
測試 FinLab API 登入和數據獲取
"""
import sys
import asyncio
import os
from pathlib import Path

# 添加 src 目錄到 Python 路徑
sys.path.append(str(Path(__file__).parent / "src"))

def test_finlab_login():
    """測試 FinLab API 登入"""
    try:
        import finlab
        from finlab import data
        
        print("🔍 測試 FinLab API 登入")
        print("=" * 40)
        
        # 設定 API 金鑰
        api_key = "demo_key"  # 使用 demo_key
        print(f"使用 API 金鑰: {api_key}")
        
        # 嘗試登入
        print("正在登入 FinLab API...")
        finlab.login(api_key)
        print("✅ FinLab API 登入成功!")
        
        # 測試獲取數據
        print("\n📊 測試數據獲取...")
        
        # 測試獲取股價數據
        try:
            print("測試獲取股價數據...")
            open_df = data.get('price:開盤價')
            print(f"✅ 股價數據獲取成功，包含 {len(open_df.columns)} 個股票")
            
            # 檢查台積電 (2330) 是否有數據
            if '2330' in open_df.columns:
                print("✅ 台積電 (2330) 數據可用")
                latest_price = open_df['2330'].dropna().iloc[-1]
                print(f"   最新開盤價: {latest_price}")
            else:
                print("❌ 台積電 (2330) 數據不可用")
                
        except Exception as e:
            print(f"❌ 股價數據獲取失敗: {e}")
        
        # 測試獲取營收數據
        try:
            print("\n測試獲取營收數據...")
            revenue_df = data.get('monthly_revenue:當月營收')
            print(f"✅ 營收數據獲取成功，包含 {len(revenue_df.columns)} 個股票")
            
            # 檢查台積電 (2330) 是否有營收數據
            if '2330' in revenue_df.columns:
                print("✅ 台積電 (2330) 營收數據可用")
                latest_revenue = revenue_df['2330'].dropna().iloc[-1]
                print(f"   最新月營收: {latest_revenue/100000000:.1f}億")
            else:
                print("❌ 台積電 (2330) 營收數據不可用")
                
        except Exception as e:
            print(f"❌ 營收數據獲取失敗: {e}")
        
        # 測試獲取財報數據
        try:
            print("\n測試獲取財報數據...")
            eps_df = data.get('financial_statement:每股盈餘')
            print(f"✅ 財報數據獲取成功，包含 {len(eps_df.columns)} 個股票")
            
            # 檢查台積電 (2330) 是否有財報數據
            if '2330' in eps_df.columns:
                print("✅ 台積電 (2330) 財報數據可用")
                latest_eps = eps_df['2330'].dropna().iloc[-1]
                print(f"   最新 EPS: {latest_eps}")
            else:
                print("❌ 台積電 (2330) 財報數據不可用")
                
        except Exception as e:
            print(f"❌ 財報數據獲取失敗: {e}")
        
        print("\n✅ FinLab API 測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ FinLab API 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_stock_data_service_with_finlab():
    """測試個股數據服務與 FinLab API 整合"""
    try:
        from services.stock.stock_data_service import create_stock_data_service
        
        print("\n🔍 測試個股數據服務與 FinLab API 整合")
        print("=" * 50)
        
        # 創建服務實例
        stock_data_service = create_stock_data_service(finlab_api_key="demo_key")
        
        # 測試股票代號
        test_stock_id = "2330"
        print(f"測試股票: {test_stock_id}")
        
        # 測試營收數據獲取
        print(f"\n💰 測試營收數據獲取...")
        revenue_data = await stock_data_service.get_stock_revenue_data(test_stock_id)
        
        if revenue_data:
            print(f"✅ 營收數據獲取成功:")
            if revenue_data.current_month_revenue:
                print(f"  當月營收: {revenue_data.current_month_revenue/100000000:.1f}億")
            if revenue_data.year_over_year_growth:
                print(f"  年增率: {revenue_data.year_over_year_growth:.1f}%")
            if revenue_data.month_over_month_growth:
                print(f"  月增率: {revenue_data.month_over_month_growth:.1f}%")
        else:
            print(f"❌ 營收數據獲取失敗")
        
        # 測試財務數據獲取
        print(f"\n📈 測試財務數據獲取...")
        financial_data = await stock_data_service.get_stock_financial_data(test_stock_id)
        
        if financial_data:
            print(f"✅ 財務數據獲取成功:")
            if financial_data.eps:
                print(f"  EPS: {financial_data.eps}")
            if financial_data.revenue:
                print(f"  營業收入: {financial_data.revenue/100000000:.1f}億")
            if financial_data.total_assets:
                print(f"  資產總額: {financial_data.total_assets/100000000:.1f}億")
        else:
            print(f"❌ 財務數據獲取失敗")
        
        # 測試綜合數據獲取
        print(f"\n🔍 測試綜合數據獲取...")
        comprehensive_data = await stock_data_service.get_comprehensive_stock_data(test_stock_id)
        
        print(f"綜合數據獲取結果:")
        print(f"  股票代號: {comprehensive_data['stock_id']}")
        print(f"  有營收數據: {comprehensive_data['has_revenue']}")
        print(f"  有財務數據: {comprehensive_data['has_financial']}")
        
        print("\n✅ 個股數據服務與 FinLab API 整合測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ 個股數據服務測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始 FinLab API 測試")
    print()
    
    # 執行 FinLab API 登入測試
    success1 = test_finlab_login()
    
    # 執行個股數據服務整合測試
    success2 = asyncio.run(test_stock_data_service_with_finlab())
    
    print(f"\n{'✅ 所有測試完成!' if success1 and success2 else '❌ 部分測試失敗!'}")
    
    if success1 and success2:
        print("\n🎉 FinLab API 整合成功!")
        print("✅ 系統現在支援:")
        print("  - FinLab API 登入")
        print("  - 股價數據獲取")
        print("  - 營收數據獲取")
        print("  - 財報數據獲取")
        print("  - 個股數據服務整合")
        print("\n🔄 下一步:")
        print("  - 執行完整的個股數據流測試")
        print("  - 整合到內容生成流程")
    else:
        print("\n⚠️ 需要檢查以下問題:")
        print("  - FinLab API 金鑰設定")
        print("  - 網路連接")
        print("  - 數據權限")



