#!/usr/bin/env python3
"""
測試 Finlab 月營收 API 數據獲取
測試各種月營收相關的數據表
"""

import sys
import os
import pandas as pd
import finlab
from datetime import datetime, timedelta

# 添加src路徑
sys.path.append('./src')

def test_monthly_revenue_data():
    """測試月營收數據獲取"""
    
    print("🚀 測試 Finlab 月營收 API 數據獲取")
    print("=" * 60)
    
    try:
        # 1. 登入 Finlab API
        api_key = os.getenv("FINLAB_API_KEY")
        if not api_key:
            print("❌ 環境變數 FINLAB_API_KEY 未設定")
            return False
        
        print(f"🔑 使用 API Key: {api_key[:10]}...")
        finlab.login(api_key)
        print("✅ Finlab API 登入成功")
        
        # 2. 測試各種月營收數據表
        print("\n📊 測試月營收數據表:")
        print("-" * 40)
        
        # 定義要測試的數據表
        revenue_tables = {
            "當月營收": "monthly_revenue:當月營收",
            "上月營收": "monthly_revenue:上月營收", 
            "去年當月營收": "monthly_revenue:去年當月營收",
            "上月比較增減(%)": "monthly_revenue:上月比較增減(%)",
            "去年同月增減(%)": "monthly_revenue:去年同月增減(%)",
            "當月累計營收": "monthly_revenue:當月累計營收",
            "去年累計營收": "monthly_revenue:去年累計營收",
            "前期比較增減(%)": "monthly_revenue:前期比較增減(%)"
        }
        
        # 測試股票代號
        test_stocks = ["2330", "2454", "2317"]  # 台積電、聯發科、鴻海
        
        successful_tables = {}
        
        for table_name, table_key in revenue_tables.items():
            try:
                print(f"\n🔍 測試 {table_name}...")
                
                # 獲取數據
                data_df = finlab.data.get(table_key)
                
                if data_df is not None and not data_df.empty:
                    print(f"  ✅ 成功獲取 {table_name}")
                    print(f"  數據形狀: {data_df.shape}")
                    print(f"  索引範圍: {data_df.index[0]} 到 {data_df.index[-1]}")
                    
                    # 檢查是否有我們要的股票
                    available_stocks = [col for col in data_df.columns if col in test_stocks]
                    if available_stocks:
                        print(f"  可用股票: {available_stocks}")
                        
                        # 顯示最新數據
                        for stock in available_stocks[:2]:  # 只顯示前2個股票
                            latest_data = data_df[stock].iloc[-1]
                            print(f"    {stock} 最新數據: {latest_data}")
                    
                    successful_tables[table_name] = data_df
                else:
                    print(f"  ❌ {table_name} 數據為空")
                    
            except Exception as e:
                print(f"  ❌ 獲取 {table_name} 失敗: {e}")
        
        # 3. 分析數據結構
        print(f"\n📈 成功獲取 {len(successful_tables)} 個數據表")
        
        if successful_tables:
            # 選擇一個成功的表進行詳細分析
            sample_table = list(successful_tables.values())[0]
            print(f"\n🔍 數據結構分析 (以 {list(successful_tables.keys())[0]} 為例):")
            print(f"  索引類型: {type(sample_table.index)}")
            print(f"  索引格式: {sample_table.index[0]}")
            print(f"  列數: {len(sample_table)}")
            print(f"  欄數: {len(sample_table.columns)}")
            
            # 測試索引轉換
            try:
                if hasattr(sample_table, 'index_str_to_date'):
                    print("\n🔄 測試索引轉換為日期...")
                    date_index = sample_table.index_str_to_date()
                    print(f"  轉換後索引類型: {type(date_index)}")
                    print(f"  轉換後索引範圍: {date_index[0]} 到 {date_index[-1]}")
                else:
                    print("\n⚠️  該數據表沒有 index_str_to_date 方法")
            except Exception as e:
                print(f"  ❌ 索引轉換失敗: {e}")
        
        # 4. 投資人常用的選股指標分析
        print(f"\n💡 投資人常用的月營收選股指標分析:")
        print("-" * 40)
        
        if "去年同月增減(%)" in successful_tables:
            print("✅ 去年同月增減(%): 年成長率，反映公司長期成長性")
            print("   使用場景: 評估公司是否維持成長動能")
        
        if "上月比較增減(%)" in successful_tables:
            print("✅ 上月比較增減(%): 月成長率，反映短期營運變化")
            print("   使用場景: 評估營運趨勢是否改善")
        
        if "去年當月營收" in successful_tables:
            print("✅ 去年當月營收: 基期比較，用於計算年增率")
            print("   使用場景: 與當月營收比較，計算年成長")
        
        if "當月累計營收" in successful_tables:
            print("✅ 當月累計營收: 年度累計表現")
            print("   使用場景: 評估年度營運目標達成狀況")
        
        print("\n🎯 建議優先使用的指標:")
        print("1. 去年同月增減(%) - 年成長率，最重要")
        print("2. 上月比較增減(%) - 月成長率，趨勢指標")
        print("3. 當月營收 - 絕對值，基數大小")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_monthly_revenue_data()
    
    if success:
        print("\n🎉 月營收API測試完成！")
        print("接下來可以基於這些數據建立月營收API服務")
    else:
        print("\n❌ 月營收API測試失敗")
        print("請檢查API Key設定和網路連接")



