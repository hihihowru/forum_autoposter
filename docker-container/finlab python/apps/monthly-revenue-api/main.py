import os
import json
import pandas as pd
import finlab
from finlab import data
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException
from typing import Optional, Dict, Any, List

app = FastAPI(
    title="月營收 API",
    description="提供個股月營收相關數據的API服務",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    """服務啟動時登入 Finlab API"""
    api_key = os.getenv("FINLAB_API_KEY")
    if api_key:
        try:
            finlab.login(api_key)
            print("✅ Finlab API 登入成功")
        except Exception as e:
            print(f"❌ Finlab API 登入失敗: {e}")
    else:
        print("⚠️  環境變數 FINLAB_API_KEY 未設定")

@app.get("/")
def root():
    """API 根路徑"""
    return {
        "message": "月營收 API 服務",
        "version": "1.0.0",
        "endpoints": {
            "/monthly_revenue/{stock_id}": "獲取指定股票的月營收數據",
            "/revenue_summary/{stock_id}": "獲取指定股票的營收摘要",
            "/top_performers": "獲取營收表現最佳的股票",
            "/health": "健康檢查"
        }
    }

@app.get("/monthly_revenue/{stock_id}")
def get_monthly_revenue(
    stock_id: str,
    months: int = Query(12, description="返回的月份數量，預設12個月")
):
    """獲取指定股票的月營收數據"""
    try:
        # 獲取各種月營收數據
        current_revenue = data.get('monthly_revenue:當月營收')
        last_month_revenue = data.get('monthly_revenue:上月營收')
        last_year_revenue = data.get('monthly_revenue:去年當月營收')
        mom_growth = data.get('monthly_revenue:上月比較增減(%)')
        yoy_growth = data.get('monthly_revenue:去年同月增減(%)')
        cumulative_revenue = data.get('monthly_revenue:當月累計營收')
        last_year_cumulative = data.get('monthly_revenue:去年累計營收')
        cumulative_growth = data.get('monthly_revenue:前期比較增減(%)')
        
        # 檢查股票是否存在
        if stock_id not in current_revenue.columns:
            raise HTTPException(status_code=404, detail=f"股票代號 {stock_id} 未找到")
        
        # 獲取數據並轉換索引為日期
        try:
            current_revenue = current_revenue.index_str_to_date()
            last_month_revenue = last_month_revenue.index_str_to_date()
            last_year_revenue = last_year_revenue.index_str_to_date()
            mom_growth = mom_growth.index_str_to_date()
            yoy_growth = yoy_growth.index_str_to_date()
            cumulative_revenue = cumulative_revenue.index_str_to_date()
            last_year_cumulative = last_year_cumulative.index_str_to_date()
            cumulative_growth = cumulative_growth.index_str_to_date()
        except Exception as e:
            print(f"⚠️  索引轉換失敗，使用原始索引: {e}")
        
        # 組成完整的月營收數據
        revenue_data = []
        dates = current_revenue.index
        
        # 限制返回的月份數量
        if months < len(dates):
            dates = dates[-months:]
        
        for date in dates:
            try:
                month_data = {
                    "月份": date.strftime("%Y-%m") if hasattr(date, 'strftime') else str(date),
                    "當月營收": int(current_revenue.loc[date, stock_id]) if pd.notna(current_revenue.loc[date, stock_id]) else None,
                    "上月營收": int(last_month_revenue.loc[date, stock_id]) if pd.notna(last_month_revenue.loc[date, stock_id]) else None,
                    "去年當月營收": int(last_year_revenue.loc[date, stock_id]) if pd.notna(last_year_revenue.loc[date, stock_id]) else None,
                    "上月比較增減(%)": round(float(mom_growth.loc[date, stock_id]), 2) if pd.notna(mom_growth.loc[date, stock_id]) else None,
                    "去年同月增減(%)": round(float(yoy_growth.loc[date, stock_id]), 2) if pd.notna(yoy_growth.loc[date, stock_id]) else None,
                    "當月累計營收": int(cumulative_revenue.loc[date, stock_id]) if pd.notna(cumulative_revenue.loc[date, stock_id]) else None,
                    "去年累計營收": int(last_year_cumulative.loc[date, stock_id]) if pd.notna(last_year_cumulative.loc[date, stock_id]) else None,
                    "前期比較增減(%)": round(float(cumulative_growth.loc[date, stock_id]), 2) if pd.notna(cumulative_growth.loc[date, stock_id]) else None
                }
                revenue_data.append(month_data)
            except Exception as e:
                print(f"⚠️  處理日期 {date} 的數據時發生錯誤: {e}")
                continue
        
        return {
            "stock_id": stock_id,
            "data": revenue_data,
            "total_months": len(revenue_data)
        }
        
    except Exception as e:
        print(f"❌ 獲取股票 {stock_id} 月營收數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取月營收數據失敗: {str(e)}")

@app.get("/revenue_summary/{stock_id}")
def get_revenue_summary(stock_id: str):
    """獲取指定股票的營收摘要"""
    try:
        # 獲取最新月份的數據
        current_revenue = data.get('monthly_revenue:當月營收')
        yoy_growth = data.get('monthly_revenue:去年同月增減(%)')
        mom_growth = data.get('monthly_revenue:上月比較增減(%)')
        cumulative_revenue = data.get('monthly_revenue:當月累計營收')
        
        # 檢查股票是否存在
        if stock_id not in current_revenue.columns:
            raise HTTPException(status_code=404, detail=f"股票代號 {stock_id} 未找到")
        
        # 轉換索引
        try:
            current_revenue = current_revenue.index_str_to_date()
            yoy_growth = yoy_growth.index_str_to_date()
            mom_growth = mom_growth.index_str_to_date()
            cumulative_revenue = cumulative_revenue.index_str_to_date()
        except Exception as e:
            print(f"⚠️  索引轉換失敗: {e}")
        
        # 獲取最新數據
        latest_date = current_revenue.index[-1]
        latest_revenue = current_revenue.loc[latest_date, stock_id]
        latest_yoy = yoy_growth.loc[latest_date, stock_id] if pd.notna(yoy_growth.loc[latest_date, stock_id]) else 0
        latest_mom = mom_growth.loc[latest_date, stock_id] if pd.notna(mom_growth.loc[latest_date, stock_id]) else 0
        latest_cumulative = cumulative_revenue.loc[latest_date, stock_id] if pd.notna(cumulative_revenue.loc[latest_date, stock_id]) else 0
        
        # 生成投資建議
        investment_advice = _generate_investment_advice(latest_yoy, latest_mom)
        
        summary = {
            "stock_id": stock_id,
            "最新月份": latest_date.strftime("%Y-%m") if hasattr(latest_date, 'strftime') else str(latest_date),
            "當月營收": int(latest_revenue) if pd.notna(latest_revenue) else None,
            "年增率": f"{latest_yoy:.2f}%" if latest_yoy is not None else "N/A",
            "月增率": f"{latest_mom:.2f}%" if latest_mom is not None else "N/A",
            "累計營收": int(latest_cumulative) if pd.notna(latest_cumulative) else None,
            "投資建議": investment_advice
        }
        
        return summary
        
    except Exception as e:
        print(f"❌ 獲取股票 {stock_id} 營收摘要失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取營收摘要失敗: {str(e)}")

@app.get("/top_performers")
def get_top_performers(
    metric: str = Query("去年同月增減(%)", description="排序指標"),
    top_n: int = Query(5, description="返回的股票數量")
):
    """獲取營收表現最佳的股票"""
    try:
        # 檢查指標是否支援
        supported_metrics = ["去年同月增減(%)", "上月比較增減(%)", "當月營收"]
        if metric not in supported_metrics:
            raise HTTPException(status_code=400, detail=f"不支援的指標: {metric}，支援的指標: {supported_metrics}")
        
        # 獲取對應的數據
        if metric == "去年同月增減(%)":
            data_df = data.get('monthly_revenue:去年同月增減(%)')
        elif metric == "上月比較增減(%)":
            data_df = data.get('monthly_revenue:上月比較增減(%)')
        elif metric == "當月營收":
            data_df = data.get('monthly_revenue:當月營收')
        
        # 轉換索引
        try:
            data_df = data_df.index_str_to_date()
        except Exception as e:
            print(f"⚠️  索引轉換失敗: {e}")
        
        # 獲取最新數據
        latest_date = data_df.index[-1]
        latest_data = data_df.loc[latest_date]
        
        # 排序並獲取前N名
        performers = []
        for stock_id, value in latest_data.items():
            if pd.notna(value):
                performers.append({
                    "stock_id": stock_id,
                    "月份": latest_date.strftime("%Y-%m") if hasattr(latest_date, 'strftime') else str(latest_date),
                    metric: round(float(value), 2) if metric != "當月營收" else int(value),
                    "當月營收": int(data.get('monthly_revenue:當月營收').loc[latest_date, stock_id]) if pd.notna(data.get('monthly_revenue:當月營收').loc[latest_date, stock_id]) else None
                })
        
        # 根據指標排序
        reverse = metric != "當月營收"  # 增減率降序，營收升序
        performers.sort(key=lambda x: x[metric], reverse=reverse)
        
        return performers[:top_n]
        
    except Exception as e:
        print(f"❌ 獲取營收表現最佳股票失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取排行榜失敗: {str(e)}")

def _generate_investment_advice(yoy_growth: float, mom_growth: float) -> str:
    """根據營收數據生成投資建議"""
    if yoy_growth is None or mom_growth is None:
        return "數據不足，無法提供建議"
    
    if yoy_growth > 20 and mom_growth > 10:
        return "營收表現優異，年增率強勁，建議關注"
    elif yoy_growth > 10 and mom_growth > 5:
        return "營收穩定成長，趨勢向上，可考慮布局"
    elif yoy_growth > 0 and mom_growth > 0:
        return "營收略有成長，需觀察後續表現"
    elif yoy_growth < -10 or mom_growth < -5:
        return "營收下滑明顯，建議觀望"
    else:
        return "營收表現平平，建議等待更好時機"

@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("🚀 啟動月營收 API 服務...")
    uvicorn.run(app, host="0.0.0.0", port=8003)











