#!/usr/bin/env python3
"""
月營收 API 服務
提供個股月營收相關數據的API接口
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException
from typing import Optional, Dict, Any, List
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="月營收 API",
    description="提供個股月營收相關數據的API服務",
    version="1.0.0"
)

class MonthlyRevenueService:
    """月營收數據服務"""
    
    def __init__(self):
        self.revenue_data = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """初始化模擬數據（暫時使用，等待真實API整合）"""
        logger.info("初始化月營收模擬數據...")
        
        # 模擬月營收數據結構
        # 格式: {stock_id: {date: {metric: value}}}
        sample_stocks = ["2330", "2454", "2317", "2412", "2881"]  # 台積電、聯發科、鴻海、中華電、富邦金
        
        # 生成過去12個月的日期
        dates = []
        current_date = datetime.now()
        for i in range(12):
            date = current_date - timedelta(days=30*i)
            month_str = date.strftime("%Y-%m")
            dates.append(month_str)
        
        dates.reverse()  # 從舊到新
        
        for stock_id in sample_stocks:
            self.revenue_data[stock_id] = {}
            
            for i, date in enumerate(dates):
                # 模擬營收數據（單位：百萬元）
                base_revenue = {
                    "2330": 50000,  # 台積電
                    "2454": 15000,  # 聯發科
                    "2317": 8000,   # 鴻海
                    "2412": 3000,   # 中華電
                    "2881": 2000    # 富邦金
                }[stock_id]
                
                # 加入一些隨機變化
                import random
                random.seed(hash(stock_id + date))  # 確保可重現性
                
                # 模擬月營收
                monthly_revenue = base_revenue + random.randint(-2000, 3000)
                
                # 模擬年增率 (-20% 到 +50%)
                yoy_growth = random.uniform(-0.2, 0.5)
                
                # 模擬月增率 (-15% 到 +25%)
                mom_growth = random.uniform(-0.15, 0.25)
                
                # 去年同月營收
                last_year_revenue = int(monthly_revenue / (1 + yoy_growth))
                
                # 上月營收
                last_month_revenue = int(monthly_revenue / (1 + mom_growth))
                
                # 累計營收（簡單累加）
                cumulative_revenue = monthly_revenue * (i + 1)
                last_year_cumulative = last_year_revenue * (i + 1)
                
                self.revenue_data[stock_id][date] = {
                    "當月營收": monthly_revenue,
                    "上月營收": last_month_revenue,
                    "去年當月營收": last_year_revenue,
                    "上月比較增減(%)": round(mom_growth * 100, 2),
                    "去年同月增減(%)": round(yoy_growth * 100, 2),
                    "當月累計營收": cumulative_revenue,
                    "去年累計營收": last_year_cumulative,
                    "前期比較增減(%)": round(((cumulative_revenue - last_year_cumulative) / last_year_cumulative) * 100, 2)
                }
        
        logger.info(f"已初始化 {len(sample_stocks)} 檔股票的月營收數據")
    
    def get_monthly_revenue(self, stock_id: str, months: int = 12) -> Dict[str, Any]:
        """獲取指定股票的月營收數據"""
        if stock_id not in self.revenue_data:
            raise HTTPException(status_code=404, detail=f"股票代號 {stock_id} 未找到")
        
        stock_data = self.revenue_data[stock_id]
        dates = sorted(stock_data.keys())
        
        # 限制返回的月份數量
        if months < len(dates):
            dates = dates[-months:]
        
        result = {
            "stock_id": stock_id,
            "data": []
        }
        
        for date in dates:
            month_data = stock_data[date].copy()
            month_data["月份"] = date
            result["data"].append(month_data)
        
        return result
    
    def get_revenue_summary(self, stock_id: str) -> Dict[str, Any]:
        """獲取指定股票的營收摘要"""
        if stock_id not in self.revenue_data:
            raise HTTPException(status_code=404, detail=f"股票代號 {stock_id} 未找到")
        
        stock_data = self.revenue_data[stock_id]
        dates = sorted(stock_data.keys())
        
        if not dates:
            raise HTTPException(status_code=404, detail=f"股票 {stock_id} 沒有營收數據")
        
        latest_date = dates[-1]
        latest_data = stock_data[latest_date]
        
        # 計算趨勢指標
        if len(dates) >= 2:
            prev_month = dates[-2]
            prev_data = stock_data[prev_month]
            
            # 營收趨勢
            revenue_trend = "上升" if latest_data["當月營收"] > prev_data["當月營收"] else "下降"
            
            # 成長動能
            if latest_data["去年同月增減(%)"] > 0:
                growth_momentum = "強勁" if latest_data["去年同月增減(%)"] > 20 else "穩定"
            else:
                growth_momentum = "疲弱"
        else:
            revenue_trend = "未知"
            growth_momentum = "未知"
        
        summary = {
            "stock_id": stock_id,
            "最新月份": latest_date,
            "當月營收": latest_data["當月營收"],
            "年增率": f"{latest_data['去年同月增減(%)']:.2f}%",
            "月增率": f"{latest_data['上月比較增減(%)']:.2f}%",
            "累計營收": latest_data["當月累計營收"],
            "營收趨勢": revenue_trend,
            "成長動能": growth_momentum,
            "投資建議": self._generate_investment_advice(latest_data)
        }
        
        return summary
    
    def _generate_investment_advice(self, data: Dict[str, Any]) -> str:
        """根據營收數據生成投資建議"""
        yoy_growth = data["去年同月增減(%)"]
        mom_growth = data["上月比較增減(%)"]
        
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
    
    def get_top_performers(self, metric: str = "去年同月增減(%)", top_n: int = 5) -> List[Dict[str, Any]]:
        """獲取營收表現最佳的股票"""
        if metric not in ["去年同月增減(%)", "上月比較增減(%)", "當月營收"]:
            raise HTTPException(status_code=400, detail=f"不支援的指標: {metric}")
        
        performers = []
        
        for stock_id, stock_data in self.revenue_data.items():
            dates = sorted(stock_data.keys())
            if dates:
                latest_date = dates[-1]
                latest_data = stock_data[latest_date]
                
                performers.append({
                    "stock_id": stock_id,
                    "月份": latest_date,
                    metric: latest_data[metric],
                    "當月營收": latest_data["當月營收"]
                })
        
        # 根據指標排序
        reverse = metric != "當月營收"  # 增減率降序，營收升序
        performers.sort(key=lambda x: x[metric], reverse=reverse)
        
        return performers[:top_n]

# 初始化服務
revenue_service = MonthlyRevenueService()

@app.get("/")
def root():
    """API 根路徑"""
    return {
        "message": "月營收 API 服務",
        "version": "1.0.0",
        "endpoints": {
            "/monthly_revenue/{stock_id}": "獲取指定股票的月營收數據",
            "/revenue_summary/{stock_id}": "獲取指定股票的營收摘要",
            "/top_performers": "獲取營收表現最佳的股票"
        }
    }

@app.get("/monthly_revenue/{stock_id}")
def get_monthly_revenue(
    stock_id: str,
    months: int = Query(12, description="返回的月份數量，預設12個月")
):
    """獲取指定股票的月營收數據"""
    try:
        return revenue_service.get_monthly_revenue(stock_id, months)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取股票 {stock_id} 月營收數據失敗: {e}")
        raise HTTPException(status_code=500, detail="內部服務錯誤")

@app.get("/revenue_summary/{stock_id}")
def get_revenue_summary(stock_id: str):
    """獲取指定股票的營收摘要"""
    try:
        return revenue_service.get_revenue_summary(stock_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取股票 {stock_id} 營收摘要失敗: {e}")
        raise HTTPException(status_code=500, detail="內部服務錯誤")

@app.get("/top_performers")
def get_top_performers(
    metric: str = Query("去年同月增減(%)", description="排序指標"),
    top_n: int = Query(5, description="返回的股票數量")
):
    """獲取營收表現最佳的股票"""
    try:
        return revenue_service.get_top_performers(metric, top_n)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取營收表現最佳股票失敗: {e}")
        raise HTTPException(status_code=500, detail="內部服務錯誤")

@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    logger.info("啟動月營收 API 服務...")
    uvicorn.run(app, host="0.0.0.0", port=8002)













