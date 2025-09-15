#!/usr/bin/env python3
"""
修復後的盤後漲觸發器 API
修復了收盤價數據處理和查詢按鈕的問題
"""

import os
import logging
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import finlab
from finlab import data as fdata

logger = logging.getLogger(__name__)

def get_stock_name(stock_id: str) -> str:
    """獲取股票名稱"""
    try:
        # 這裡可以實現獲取股票名稱的邏輯
        # 暫時返回股票代號
        return stock_id
    except Exception:
        return stock_id

async def _get_real_limit_up_stocks_from_finlab_fixed(target_date: str = None, min_change_percent: float = 9.5) -> List[Dict[str, Any]]:
    """
    修復後的盤後漲觸發器 - 使用 Finlab API 獲取真實的漲停股票數據
    
    修復內容：
    1. 確保數據按日期排序
    2. 改善前一交易日數據獲取的邏輯
    3. 增加更好的錯誤處理
    4. 修復查詢按鈕的數據獲取功能
    
    Args:
        target_date: 目標日期，格式為 "YYYY-MM-DD"，預設為最新交易日
        min_change_percent: 最小漲幅百分比，預設為 9.5%
        
    Returns:
        漲停股票列表
    """
    try:
        # 確保 finlab 已登入
        finlab_key = os.getenv('FINLAB_API_KEY')
        if not finlab_key:
            logger.error("未找到 FINLAB_API_KEY 環境變數")
            return []
        
        finlab.login(finlab_key)
        logger.info("Finlab API 登入成功")
        
        # 獲取收盤價數據
        logger.info("正在獲取收盤價數據...")
        close_price = fdata.get('price:收盤價')
        
        # 獲取成交金額數據
        logger.info("正在獲取成交金額數據...")
        volume_amount = fdata.get('price:成交金額')
        
        if close_price is None or close_price.empty:
            logger.error("無法獲取收盤價數據")
            return []
        
        if volume_amount is None or volume_amount.empty:
            logger.warning("無法獲取成交金額數據，將不包含成交金額資訊")
            volume_amount = None
        
        # 修復1：確保數據按日期排序
        close_price = close_price.sort_index()
        if volume_amount is not None:
            volume_amount = volume_amount.sort_index()
        
        logger.info(f"成功獲取收盤價數據，共 {len(close_price)} 個交易日，{len(close_price.columns)} 檔股票")
        if volume_amount is not None:
            logger.info(f"成功獲取成交金額數據，共 {len(volume_amount)} 個交易日，{len(volume_amount.columns)} 檔股票")
        
        # 確定目標日期
        if target_date is None:
            # 使用最新交易日
            target_datetime = close_price.index[-1]
        else:
            target_datetime = pd.to_datetime(target_date)
        
        # 檢查目標日期是否存在於數據中
        if target_datetime not in close_price.index:
            logger.error(f"目標日期 {target_date} 不存在於數據中")
            logger.info(f"可用的最新日期: {close_price.index[-1].strftime('%Y-%m-%d')}")
            return []
        
        # 獲取目標日期和前一日的收盤價
        today_close = close_price.loc[target_datetime]
        
        # 修復2：改善前一交易日數據獲取的邏輯
        previous_dates = close_price.index[close_price.index < target_datetime]
        if len(previous_dates) == 0:
            logger.error(f"無法找到 {target_datetime.strftime('%Y-%m-%d')} 之前的交易日數據")
            return []
        
        yesterday_close = close_price.loc[previous_dates[-1]]
        
        # 獲取今日成交金額
        today_volume_amount = None
        if volume_amount is not None and target_datetime in volume_amount.index:
            today_volume_amount = volume_amount.loc[target_datetime]
        
        logger.info(f"目標日期: {target_datetime.strftime('%Y-%m-%d')}")
        logger.info(f"前一交易日: {yesterday_close.name.strftime('%Y-%m-%d')}")
        
        # 計算漲幅
        limit_up_stocks = []
        
        for stock_id in close_price.columns:
            try:
                # 獲取今日和昨日收盤價
                today_price = today_close[stock_id]
                yesterday_price = yesterday_close[stock_id]
                
                # 修復3：改善數據驗證
                if pd.isna(today_price) or pd.isna(yesterday_price) or yesterday_price == 0:
                    continue
                
                # 計算漲幅
                change_percent = ((today_price - yesterday_price) / yesterday_price) * 100
                
                # 檢查是否漲停（漲幅超過 min_change_percent%）
                if change_percent >= min_change_percent:
                    stock_name = get_stock_name(stock_id)
                    
                    # 獲取成交金額資訊
                    volume_amount_value = 0
                    if today_volume_amount is not None and stock_id in today_volume_amount.index:
                        amount = today_volume_amount[stock_id]
                        if not pd.isna(amount):
                            volume_amount_value = round(amount, 0)
                    
                    # 轉換為前端期望的格式
                    stock_data = {
                        "stock_code": stock_id,
                        "stock_name": stock_name,
                        "current_price": round(today_price, 2),
                        "limit_up_price": round(today_price, 2),
                        "volume": volume_amount_value,  # 成交金額
                        "volume_rank": 0,  # 暫時設為0，可以後續計算
                        "market_cap": 0,  # 暫時設為0
                        "sector": "未知",  # 暫時設為未知
                        "limit_up_reason": "技術面突破",  # 暫時設為預設值
                        "news_sentiment": 0.8,  # 暫時設為預設值
                        "technical_score": 0.9,  # 暫時設為預設值
                        "yesterday_close": round(yesterday_price, 2),
                        "change_amount": round(today_price - yesterday_price, 2),
                        "change_percent": round(change_percent, 2),
                        "volume_amount": volume_amount_value,
                        "volume_amount_billion": round(volume_amount_value / 100000000, 4) if volume_amount_value > 0 else 0
                    }
                    
                    limit_up_stocks.append(stock_data)
                    
            except Exception as e:
                logger.warning(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue
        
        # 按成交金額排序
        limit_up_stocks.sort(key=lambda x: x.get('volume_amount', 0), reverse=True)
        
        # 添加成交量排名
        for i, stock in enumerate(limit_up_stocks, 1):
            stock['volume_rank'] = i
        
        logger.info(f"找到 {len(limit_up_stocks)} 檔漲停股票")
        return limit_up_stocks
        
    except Exception as e:
        logger.error(f"獲取漲停股票時發生錯誤: {e}")
        import traceback
        logger.error(f"詳細錯誤: {traceback.format_exc()}")
        return []

# 測試函數
async def test_fixed_trigger():
    """測試修復後的觸發器"""
    logger.info("開始測試修復後的盤後漲觸發器...")
    
    # 測試獲取漲停股票
    stocks = await _get_real_limit_up_stocks_from_finlab_fixed(min_change_percent=9.5)
    
    if stocks:
        logger.info(f"✅ 成功獲取 {len(stocks)} 檔漲停股票")
        for i, stock in enumerate(stocks[:3], 1):  # 顯示前3檔
            logger.info(f"  {i}. {stock['stock_name']}({stock['stock_code']}) - 漲幅: {stock['change_percent']:.2f}%")
    else:
        logger.warning("⚠️ 未找到漲停股票")
    
    return stocks

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_fixed_trigger())

