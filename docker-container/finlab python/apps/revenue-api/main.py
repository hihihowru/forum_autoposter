import os
import json
import pandas as pd
import finlab
from finlab import data
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException
from typing import Dict, Any, Optional

app = FastAPI()

@app.on_event("startup")
def startup_event():
    """啟動時登入 FinLab"""
    api_key = os.getenv("FINLAB_API_KEY")
    if api_key:
        finlab.login(api_key)

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

@app.get("/revenue/{stock_id}")
def get_revenue_data(stock_id: str, periods: int = Query(3, description="取得最近幾個月的資料")):
    """取得股票營收資料"""
    try:
        # 取得各種營收資料
        current_revenue = data.get('monthly_revenue:當月營收')
        prev_revenue = data.get('monthly_revenue:上月營收')
        last_year_revenue = data.get('monthly_revenue:去年當月營收')
        mom_change = data.get('monthly_revenue:上月比較增減(%)')
        yoy_change = data.get('monthly_revenue:去年同月增減(%)')
        cumulative_revenue = data.get('monthly_revenue:當月累計營收')
        last_year_cumulative = data.get('monthly_revenue:去年累計營收')
        period_change = data.get('monthly_revenue:前期比較增減(%)')
        
        if stock_id not in current_revenue.columns:
            raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
        
        # 取得最近幾期的資料
        result = {
            "stock_id": stock_id,
            "data": []
        }
        
        for i in range(periods):
            try:
                # 取得各期資料
                current = current_revenue[stock_id].dropna().iloc[-(i+1)]
                prev = prev_revenue[stock_id].dropna().iloc[-(i+1)]
                last_year = last_year_revenue[stock_id].dropna().iloc[-(i+1)]
                mom = mom_change[stock_id].dropna().iloc[-(i+1)]
                yoy = yoy_change[stock_id].dropna().iloc[-(i+1)]
                cumulative = cumulative_revenue[stock_id].dropna().iloc[-(i+1)]
                last_year_cum = last_year_cumulative[stock_id].dropna().iloc[-(i+1)]
                period = period_change[stock_id].dropna().iloc[-(i+1)]
                
                period_data = {
                    "period": current_revenue.index[-(i+1)],
                    "current_revenue": {
                        "value": int(current),
                        "formatted": format_large_number(current)
                    },
                    "previous_revenue": {
                        "value": int(prev),
                        "formatted": format_large_number(prev)
                    },
                    "last_year_revenue": {
                        "value": int(last_year),
                        "formatted": format_large_number(last_year)
                    },
                    "growth_rates": {
                        "month_over_month": round(float(mom), 2),
                        "year_over_year": round(float(yoy), 2),
                        "period_change": round(float(period), 2)
                    },
                    "cumulative": {
                        "current": {
                            "value": int(cumulative),
                            "formatted": format_large_number(cumulative)
                        },
                        "last_year": {
                            "value": int(last_year_cum),
                            "formatted": format_large_number(last_year_cum)
                        }
                    }
                }
                
                result["data"].append(period_data)
                
            except IndexError:
                break
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/revenue/{stock_id}/summary")
def get_revenue_summary(stock_id: str):
    """取得股票營收摘要"""
    try:
        # 取得最新營收資料
        current_revenue = data.get('monthly_revenue:當月營收')
        yoy_change = data.get('monthly_revenue:去年同月增減(%)')
        cumulative_revenue = data.get('monthly_revenue:當月累計營收')
        period_change = data.get('monthly_revenue:前期比較增減(%)')
        
        if stock_id not in current_revenue.columns:
            raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
        
        # 取得最新資料
        latest_revenue = current_revenue[stock_id].dropna().iloc[-1]
        latest_yoy = yoy_change[stock_id].dropna().iloc[-1]
        latest_cumulative = cumulative_revenue[stock_id].dropna().iloc[-1]
        latest_period = period_change[stock_id].dropna().iloc[-1]
        
        # 取得前3期資料計算趨勢
        recent_revenues = current_revenue[stock_id].dropna().tail(3)
        trend = "上升" if recent_revenues.iloc[-1] > recent_revenues.iloc[0] else "下降"
        
        result = {
            "stock_id": stock_id,
            "latest_period": current_revenue.index[-1],
            "current_revenue": {
                "value": int(latest_revenue),
                "formatted": format_large_number(latest_revenue)
            },
            "growth": {
                "year_over_year": round(float(latest_yoy), 2),
                "period_change": round(float(latest_period), 2)
            },
            "cumulative_revenue": {
                "value": int(latest_cumulative),
                "formatted": format_large_number(latest_cumulative)
            },
            "trend": trend,
            "analysis": {
                "revenue_trend": f"營收趨勢{trend}",
                "growth_status": "強勁成長" if latest_yoy > 20 else "穩定成長" if latest_yoy > 0 else "下滑"
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/revenue/{stock_id}/growth")
def get_revenue_growth(stock_id: str, periods: int = Query(6, description="取得最近幾個月的成長率")):
    """取得股票營收成長率資料"""
    try:
        mom_change = data.get('monthly_revenue:上月比較增減(%)')
        yoy_change = data.get('monthly_revenue:去年同月增減(%)')
        period_change = data.get('monthly_revenue:前期比較增減(%)')
        
        if stock_id not in mom_change.columns:
            raise HTTPException(status_code=404, detail=f"Stock ID {stock_id} not found")
        
        result = {
            "stock_id": stock_id,
            "growth_data": []
        }
        
        for i in range(min(periods, len(mom_change[stock_id].dropna()))):
            try:
                period_data = {
                    "period": mom_change.index[-(i+1)],
                    "month_over_month": round(float(mom_change[stock_id].dropna().iloc[-(i+1)]), 2),
                    "year_over_year": round(float(yoy_change[stock_id].dropna().iloc[-(i+1)]), 2),
                    "period_change": round(float(period_change[stock_id].dropna().iloc[-(i+1)]), 2)
                }
                result["growth_data"].append(period_data)
            except IndexError:
                break
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "healthy", "service": "revenue-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)


