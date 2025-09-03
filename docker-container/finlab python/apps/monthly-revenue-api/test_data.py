#!/usr/bin/env python3
"""
測試月營收數據獲取
"""

import os
import finlab
from finlab import data

def test_monthly_revenue_data():
    """測試月營收數據獲取"""
    
    # 設定 API key
    api_key = "AOl10aUjuRAwxdHjbO25jGoH7c8LOhXqKz/HgT9WlcCPkBwL8Qp6PDlqpd59YuR7#vip_m%"
    
    try:
        # 登入
        print("🔑 登入 Finlab API...")
        finlab.login(api_key)
        print("✅ 登入成功")
        
        # 測試各種月營收數據
        print("\n📊 測試月營收數據獲取...")
        
        # 1. 當月營收
        print("\n1. 測試當月營收...")
        current_revenue = data.get('monthly_revenue:當月營收')
        print(f"   數據形狀: {current_revenue.shape}")
        print(f"   索引範圍: {current_revenue.index[0]} 到 {current_revenue.index[-1]}")
        print(f"   股票數量: {len(current_revenue.columns)}")
        
        # 檢查台積電
        if '2330' in current_revenue.columns:
            print(f"   台積電最新營收: {current_revenue['2330'].iloc[-1]}")
            print(f"   台積電營收範圍: {current_revenue['2330'].index[0]} 到 {current_revenue['2330'].index[-1]}")
        else:
            print("   ⚠️  台積電(2330)不在數據中")
        
        # 2. 去年同月增減(%)
        print("\n2. 測試去年同月增減(%)...")
        yoy_growth = data.get('monthly_revenue:去年同月增減(%)')
        print(f"   數據形狀: {yoy_growth.shape}")
        
        if '2330' in yoy_growth.columns:
            latest_yoy = yoy_growth['2330'].iloc[-1]
            print(f"   台積電最新年增率: {latest_yoy}%")
        else:
            print("   ⚠️  台積電(2330)不在數據中")
        
        # 3. 上月比較增減(%)
        print("\n3. 測試上月比較增減(%)...")
        mom_growth = data.get('monthly_revenue:上月比較增減(%)')
        print(f"   數據形狀: {mom_growth.shape}")
        
        if '2330' in mom_growth.columns:
            latest_mom = mom_growth['2330'].iloc[-1]
            print(f"   台積電最新月增率: {latest_mom}%")
        else:
            print("   ⚠️  台積電(2330)不在數據中")
        
        # 4. 測試索引轉換
        print("\n4. 測試索引轉換...")
        try:
            date_index = current_revenue.index_str_to_date()
            print(f"   轉換後索引類型: {type(date_index)}")
            print(f"   轉換後索引範圍: {date_index[0]} 到 {date_index[-1]}")
        except Exception as e:
            print(f"   ⚠️  索引轉換失敗: {e}")
        
        print("\n🎉 月營收數據測試完成！")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_monthly_revenue_data()



