#!/usr/bin/env python3
"""
公司基本資訊 API 服務
透過 Finlab API 提供公司名稱與代號查詢服務
"""

import os
import pandas as pd
import finlab
from finlab import data
import json
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException
from typing import Dict, Any, Optional, List
import uvicorn

app = FastAPI(title="公司基本資訊 API", description="透過 Finlab API 提供公司名稱與代號查詢服務")

# 全域變數儲存公司資料
company_data = None
name_to_code_dict = None
code_to_name_dict = None

@app.on_event("startup")
async def startup_event():
    """啟動時載入公司資料"""
    global company_data, name_to_code_dict, code_to_name_dict
    
    try:
        # 登入 Finlab API
        api_key = os.getenv("FINLAB_API_KEY")
        if not api_key:
            raise Exception("FINLAB_API_KEY 環境變數未設定")
        
        print("🔐 正在登入 Finlab API...")
        finlab.login(api_key)
        print("✅ Finlab API 登入成功")
        
        # 取得公司基本資訊
        print("📊 正在載入公司基本資訊...")
        raw_data = data.get('company_basic_info')
        
        if raw_data is None or raw_data.empty:
            raise Exception("無法取得公司基本資訊數據")
        
        # 提取需要的欄位
        company_data = raw_data[['stock_id', '公司簡稱', '公司名稱', '產業類別']].copy()
        company_data.columns = ['股票代號', '公司簡稱', '公司名稱', '產業類別']
        company_data = company_data.drop_duplicates(subset=['股票代號'])
        
        # 建立字典對應
        name_to_code_dict = {}
        code_to_name_dict = {}
        
        for _, row in company_data.iterrows():
            stock_id = str(row['股票代號'])
            short_name = row['公司簡稱']
            full_name = row['公司名稱']
            
            # 公司簡稱 -> 股票代號
            name_to_code_dict[short_name] = stock_id
            # 公司全名 -> 股票代號
            name_to_code_dict[full_name] = stock_id
            
            # 股票代號 -> 公司資訊
            code_to_name_dict[stock_id] = {
                '公司簡稱': short_name,
                '公司名稱': full_name,
                '產業類別': row['產業類別']
            }
        
        print(f"✅ 成功載入 {len(company_data)} 筆公司資料")
        
    except Exception as e:
        print(f"❌ 啟動失敗: {str(e)}")
        raise e

@app.get("/")
async def root():
    """根路徑 - API 資訊"""
    return {
        "message": "公司基本資訊 API",
        "version": "1.0.0",
        "total_companies": len(company_data) if company_data is not None else 0,
        "endpoints": {
            "/search": "搜尋公司 (支援公司名稱、簡稱、股票代號)",
            "/company/{code}": "根據股票代號查詢公司資訊",
            "/companies": "取得所有公司清單",
            "/stats": "取得統計資訊"
        }
    }

@app.get("/search")
async def search_company(
    q: str = Query(..., description="搜尋關鍵字 (公司名稱、簡稱或股票代號)"),
    limit: int = Query(10, description="回傳結果數量限制")
):
    """搜尋公司"""
    if company_data is None:
        raise HTTPException(status_code=500, detail="公司資料未載入")
    
    try:
        # 搜尋公司簡稱
        short_name_matches = company_data[company_data['公司簡稱'].str.contains(q, na=False)]
        # 搜尋公司全名
        full_name_matches = company_data[company_data['公司名稱'].str.contains(q, na=False)]
        # 搜尋股票代號
        code_matches = company_data[company_data['股票代號'].astype(str).str.contains(q, na=False)]
        
        # 合併結果並去重
        all_matches = pd.concat([short_name_matches, full_name_matches, code_matches]).drop_duplicates()
        
        # 限制結果數量
        if len(all_matches) > limit:
            all_matches = all_matches.head(limit)
        
        # 轉換為字典格式
        results = []
        for _, row in all_matches.iterrows():
            results.append({
                '股票代號': str(row['股票代號']),
                '公司簡稱': row['公司簡稱'],
                '公司名稱': row['公司名稱'],
                '產業類別': row['產業類別']
            })
        
        return {
            "query": q,
            "total_found": len(all_matches),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/company/{code}")
async def get_company_by_code(code: str):
    """根據股票代號查詢公司資訊"""
    if code_to_name_dict is None:
        raise HTTPException(status_code=500, detail="公司資料未載入")
    
    if code not in code_to_name_dict:
        raise HTTPException(status_code=404, detail=f"找不到股票代號 {code} 的公司")
    
    return {
        "股票代號": code,
        **code_to_name_dict[code]
    }

@app.get("/companies")
async def get_all_companies(
    page: int = Query(1, description="頁碼 (從 1 開始)"),
    page_size: int = Query(50, description="每頁數量"),
    industry: Optional[str] = Query(None, description="產業類別篩選")
):
    """取得所有公司清單"""
    if company_data is None:
        raise HTTPException(status_code=500, detail="公司資料未載入")
    
    try:
        # 篩選產業類別
        filtered_data = company_data
        if industry:
            filtered_data = company_data[company_data['產業類別'].str.contains(industry, na=False)]
        
        # 分頁處理
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        page_data = filtered_data.iloc[start_idx:end_idx]
        
        # 轉換為字典格式
        results = []
        for _, row in page_data.iterrows():
            results.append({
                '股票代號': str(row['股票代號']),
                '公司簡稱': row['公司簡稱'],
                '公司名稱': row['公司名稱'],
                '產業類別': row['產業類別']
            })
        
        return {
            "page": page,
            "page_size": page_size,
            "total": len(filtered_data),
            "total_pages": (len(filtered_data) + page_size - 1) // page_size,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """取得統計資訊"""
    if company_data is None:
        raise HTTPException(status_code=500, detail="公司資料未載入")
    
    try:
        # 產業類別統計
        industry_stats = company_data['產業類別'].value_counts().head(10).to_dict()
        
        # 市場別統計 (如果有相關資料)
        market_stats = {}
        if '市場別' in company_data.columns:
            market_stats = company_data['市場別'].value_counts().to_dict()
        
        return {
            "total_companies": len(company_data),
            "total_industries": company_data['產業類別'].nunique(),
            "top_industries": industry_stats,
            "market_distribution": market_stats,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "data_loaded": company_data is not None,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 啟動公司基本資訊 API 服務...")
    uvicorn.run(app, host="0.0.0.0", port=8011)





