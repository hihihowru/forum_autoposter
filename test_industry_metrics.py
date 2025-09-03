#!/usr/bin/env python3
"""
測試 FinLab 各產業財報指標 API
一個一個驗證可用的資料表
"""

import os
import pandas as pd
import finlab
from finlab import data
from dotenv import load_dotenv
from typing import Dict, List, Any

# 載入環境變數
load_dotenv()

def format_large_number(num):
    """格式化大數字，例如 1204532131 -> 12億453萬"""
    if pd.isna(num) or num == 0:
        return "0"
    
    num = int(num)
    
    if num >= 100000000:  # 億
        yi = num // 100000000
        wan = (num % 100000000) // 10000
        if wan > 0:
            return f"{yi}億{wan}萬"
        else:
            return f"{yi}億"
    elif num >= 10000:  # 萬
        wan = num // 10000
        return f"{wan}萬"
    else:
        return str(num)

def test_finlab_login():
    """測試 FinLab 登入"""
    print("🔐 測試 FinLab 登入...")
    
    api_key = os.getenv("FINLAB_API_KEY")
    if not api_key:
        print("❌ FINLAB_API_KEY 未設定")
        return False
    
    try:
        finlab.login(api_key)
        print("✅ FinLab 登入成功")
        return True
    except Exception as e:
        print(f"❌ FinLab 登入失敗: {e}")
        return False

def test_data_table(table_name: str, stock_id: str = "2330") -> Dict[str, Any]:
    """測試單一資料表"""
    try:
        df = data.get(table_name)
        if stock_id in df.columns:
            recent_data = df[stock_id].dropna().tail(1)
            if not recent_data.empty:
                value = recent_data.iloc[0]
                formatted_value = format_large_number(value)
                return {
                    "status": "success",
                    "table_name": table_name,
                    "stock_id": stock_id,
                    "latest_value": formatted_value,
                    "raw_value": value,
                    "date": recent_data.index[0]
                }
            else:
                return {
                    "status": "no_data",
                    "table_name": table_name,
                    "stock_id": stock_id,
                    "message": "無最新資料"
                }
        else:
            return {
                "status": "stock_not_found",
                "table_name": table_name,
                "stock_id": stock_id,
                "message": f"股票 {stock_id} 不在資料表中"
            }
    except Exception as e:
        return {
            "status": "error",
            "table_name": table_name,
            "stock_id": stock_id,
            "error": str(e)
        }

def test_semiconductor_industry():
    """測試半導體業指標"""
    print("\n🔬 測試半導體業指標 (2330 台積電)...")
    
    semiconductor_metrics = [
        'revenue:營收',
        'revenue:營收成長率',
        'financial_statement:毛利率',
        'financial_statement:營業利益率',
        'financial_statement:研發費用',
        'financial_statement:資本支出',
        'financial_statement:存貨',
        'eps:每股盈餘',
        'eps:每股盈餘成長率'
    ]
    
    results = []
    for metric in semiconductor_metrics:
        result = test_data_table(metric, "2330")
        results.append(result)
        
        if result["status"] == "success":
            print(f"✅ {metric}: {result['latest_value']}")
        elif result["status"] == "no_data":
            print(f"⚠️  {metric}: 無資料")
        elif result["status"] == "stock_not_found":
            print(f"❌ {metric}: 股票不存在")
        else:
            print(f"❌ {metric}: {result['error']}")
    
    return results

def test_electronics_components():
    """測試電子零組件業指標"""
    print("\n🔌 測試電子零組件業指標 (2327 國巨)...")
    
    components_metrics = [
        'revenue:營收',
        'revenue:營收成長率',
        'financial_statement:毛利率',
        'financial_statement:營業利益率',
        'financial_statement:存貨週轉率',
        'financial_statement:應收帳款週轉率',
        'financial_statement:研發費用',
        'financial_statement:存貨'
    ]
    
    results = []
    for metric in components_metrics:
        result = test_data_table(metric, "2327")
        results.append(result)
        
        if result["status"] == "success":
            print(f"✅ {metric}: {result['latest_value']}")
        elif result["status"] == "no_data":
            print(f"⚠️  {metric}: 無資料")
        elif result["status"] == "stock_not_found":
            print(f"❌ {metric}: 股票不存在")
        else:
            print(f"❌ {metric}: {result['error']}")
    
    return results

def test_electronics_manufacturing():
    """測試電子代工業指標"""
    print("\n🏭 測試電子代工業指標 (2317 鴻海)...")
    
    manufacturing_metrics = [
        'revenue:營收',
        'revenue:營收成長率',
        'financial_statement:毛利率',
        'financial_statement:營業利益率',
        'financial_statement:存貨週轉率',
        'financial_statement:應收帳款週轉率',
        'financial_statement:總資產週轉率',
        'financial_statement:流動比率'
    ]
    
    results = []
    for metric in manufacturing_metrics:
        result = test_data_table(metric, "2317")
        results.append(result)
        
        if result["status"] == "success":
            print(f"✅ {metric}: {result['latest_value']}")
        elif result["status"] == "no_data":
            print(f"⚠️  {metric}: 無資料")
        elif result["status"] == "stock_not_found":
            print(f"❌ {metric}: 股票不存在")
        else:
            print(f"❌ {metric}: {result['error']}")
    
    return results

def test_finance_industry():
    """測試金融業指標"""
    print("\n🏦 測試金融業指標 (2881 富邦金)...")
    
    finance_metrics = [
        'financial_statement:淨利息收入',
        'financial_statement:手續費收入',
        'financial_statement:呆帳準備',
        'financial_statement:資本適足率',
        'financial_statement:淨值報酬率',
        'financial_statement:資產報酬率',
        'eps:每股盈餘'
    ]
    
    results = []
    for metric in finance_metrics:
        result = test_data_table(metric, "2881")
        results.append(result)
        
        if result["status"] == "success":
            print(f"✅ {metric}: {result['latest_value']}")
        elif result["status"] == "no_data":
            print(f"⚠️  {metric}: 無資料")
        elif result["status"] == "stock_not_found":
            print(f"❌ {metric}: 股票不存在")
        else:
            print(f"❌ {metric}: {result['error']}")
    
    return results

def test_traditional_industry():
    """測試傳產業指標"""
    print("\n🏭 測試傳產業指標 (1301 台塑)...")
    
    traditional_metrics = [
        'revenue:營收',
        'revenue:營收成長率',
        'financial_statement:毛利率',
        'financial_statement:營業利益率',
        'financial_statement:存貨週轉率',
        'financial_statement:固定資產週轉率',
        'financial_statement:總資產週轉率'
    ]
    
    results = []
    for metric in traditional_metrics:
        result = test_data_table(metric, "1301")
        results.append(result)
        
        if result["status"] == "success":
            print(f"✅ {metric}: {result['latest_value']}")
        elif result["status"] == "no_data":
            print(f"⚠️  {metric}: 無資料")
        elif result["status"] == "stock_not_found":
            print(f"❌ {metric}: 股票不存在")
        else:
            print(f"❌ {metric}: {result['error']}")
    
    return results

def test_biotech_industry():
    """測試生技業指標"""
    print("\n🧬 測試生技業指標 (1795 美時)...")
    
    biotech_metrics = [
        'revenue:營收',
        'revenue:營收成長率',
        'financial_statement:研發費用',
        'financial_statement:毛利率',
        'financial_statement:營業利益率',
        'financial_statement:現金及約當現金',
        'financial_statement:流動比率'
    ]
    
    results = []
    for metric in biotech_metrics:
        result = test_data_table(metric, "1795")
        results.append(result)
        
        if result["status"] == "success":
            print(f"✅ {metric}: {result['latest_value']}")
        elif result["status"] == "no_data":
            print(f"⚠️  {metric}: 無資料")
        elif result["status"] == "stock_not_found":
            print(f"❌ {metric}: 股票不存在")
        else:
            print(f"❌ {metric}: {result['error']}")
    
    return results

def test_shipping_industry():
    """測試航運業指標"""
    print("\n🚢 測試航運業指標 (2603 長榮)...")
    
    shipping_metrics = [
        'revenue:營收',
        'revenue:營收成長率',
        'financial_statement:毛利率',
        'financial_statement:營業利益率',
        'financial_statement:固定資產週轉率',
        'financial_statement:總資產週轉率',
        'financial_statement:流動比率'
    ]
    
    results = []
    for metric in shipping_metrics:
        result = test_data_table(metric, "2603")
        results.append(result)
        
        if result["status"] == "success":
            print(f"✅ {metric}: {result['latest_value']}")
        elif result["status"] == "no_data":
            print(f"⚠️  {metric}: 無資料")
        elif result["status"] == "stock_not_found":
            print(f"❌ {metric}: 股票不存在")
        else:
            print(f"❌ {metric}: {result['error']}")
    
    return results

def test_construction_industry():
    """測試營建業指標"""
    print("\n🏗️ 測試營建業指標 (2542 興富發)...")
    
    construction_metrics = [
        'revenue:營收',
        'revenue:營收成長率',
        'financial_statement:毛利率',
        'financial_statement:營業利益率',
        'financial_statement:存貨',
        'financial_statement:流動比率',
        'financial_statement:負債比率'
    ]
    
    results = []
    for metric in construction_metrics:
        result = test_data_table(metric, "2542")
        results.append(result)
        
        if result["status"] == "success":
            print(f"✅ {metric}: {result['latest_value']}")
        elif result["status"] == "no_data":
            print(f"⚠️  {metric}: 無資料")
        elif result["status"] == "stock_not_found":
            print(f"❌ {metric}: 股票不存在")
        else:
            print(f"❌ {metric}: {result['error']}")
    
    return results

if __name__ == "__main__":
    print("🚀 開始測試各產業財報指標 API...")
    
    # 測試登入
    if not test_finlab_login():
        exit(1)
    
    # 測試各產業指標
    all_results = {}
    all_results['semiconductor'] = test_semiconductor_industry()
    all_results['electronics_components'] = test_electronics_components()
    all_results['electronics_manufacturing'] = test_electronics_manufacturing()
    all_results['finance'] = test_finance_industry()
    all_results['traditional'] = test_traditional_industry()
    all_results['biotech'] = test_biotech_industry()
    all_results['shipping'] = test_shipping_industry()
    all_results['construction'] = test_construction_industry()
    
    # 總結結果
    print("\n📊 測試結果總結:")
    for industry, results in all_results.items():
        success_count = sum(1 for r in results if r["status"] == "success")
        total_count = len(results)
        print(f"   {industry}: {success_count}/{total_count} 個指標可用")
    
    print("\n✅ 測試完成")


