"""
發文管理API - 簡化版
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from src.database import get_db
from src.services.posting_service import PostingService
from src.models.posting_models import PostingSession
import os
import pandas as pd
import finlab
import finlab.data as fdata
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 載入環境變數
load_dotenv('/Users/williamchen/Documents/n8n-migration-project/.env')

logger = logging.getLogger(__name__)

router = APIRouter()

# 導入股票名稱映射
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stock_names_mapping import STOCK_NAMES

def get_stock_name(stock_id: str) -> str:
    """根據股票代號獲取股票名稱"""
    return STOCK_NAMES.get(stock_id, f"股票{stock_id}")

async def _get_real_limit_up_stocks_from_finlab(target_date: str = None, min_change_percent: float = 9.5) -> List[Dict[str, Any]]:
    """
    使用 Finlab API 獲取真實的漲停股票數據
    
    Args:
        target_date: 目標日期，格式為 "YYYY-MM-DD"，預設為最新交易日
        
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
        yesterday_close = close_price.loc[close_price.index[close_price.index < target_datetime][-1]]
        
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
                
                # 檢查是否有有效數據
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
        return []

async def _get_real_limit_down_stocks_from_finlab(target_date: str = None, min_change_percent: float = 9.5) -> List[Dict[str, Any]]:
    """
    使用 Finlab API 獲取真實的跌停股票數據
    
    Args:
        target_date: 目標日期，格式為 "YYYY-MM-DD"，預設為最新交易日
        min_change_percent: 最小跌幅百分比，預設為 9.5%
        
    Returns:
        跌停股票列表
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
        yesterday_close = close_price.loc[close_price.index[close_price.index < target_datetime][-1]]
        
        # 獲取今日成交金額
        today_volume_amount = None
        if volume_amount is not None and target_datetime in volume_amount.index:
            today_volume_amount = volume_amount.loc[target_datetime]
        
        logger.info(f"目標日期: {target_datetime.strftime('%Y-%m-%d')}")
        logger.info(f"前一交易日: {yesterday_close.name.strftime('%Y-%m-%d')}")
        
        # 計算跌幅
        limit_down_stocks = []
        
        for stock_id in close_price.columns:
            try:
                # 獲取今日和昨日收盤價
                today_price = today_close[stock_id]
                yesterday_price = yesterday_close[stock_id]
                
                # 檢查是否有有效數據
                if pd.isna(today_price) or pd.isna(yesterday_price) or yesterday_price == 0:
                    continue
                
                # 計算跌幅
                change_percent = ((today_price - yesterday_price) / yesterday_price) * 100
                
                # 檢查是否跌停（跌幅超過 min_change_percent%）
                if change_percent <= -min_change_percent:
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
                    
                    limit_down_stocks.append(stock_data)
                    
            except Exception as e:
                logger.warning(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue
        
        # 按成交金額排序
        limit_down_stocks.sort(key=lambda x: x.get('volume_amount', 0), reverse=True)
        
        # 添加成交量排名
        for i, stock in enumerate(limit_down_stocks, 1):
            stock['volume_rank'] = i
        
        logger.info(f"找到 {len(limit_down_stocks)} 檔跌停股票")
        return limit_down_stocks
        
    except Exception as e:
        logger.error(f"獲取跌停股票時發生錯誤: {e}")
        return []

async def _get_sector_stocks_from_finlab(
    selected_sectors: List[str], 
    volume_threshold: float = None, 
    volume_percentile: float = None
) -> List[Dict[str, Any]]:
    """
    使用 Finlab API 獲取指定產業的股票數據
    
    Args:
        selected_sectors: 選定的產業列表
        volume_threshold: 成交金額絕對閾值
        volume_percentile: 成交金額相對百分位
        
    Returns:
        產業股票列表
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
        
        logger.info(f"成功獲取收盤價數據，共 {len(close_price)} 個交易日，{len(close_price.columns)} 檔股票")
        if volume_amount is not None:
            logger.info(f"成功獲取成交金額數據，共 {len(volume_amount)} 個交易日，{len(volume_amount.columns)} 檔股票")
        
        # 使用最新交易日
        target_datetime = close_price.index[-1]
        today_close = close_price.loc[target_datetime]
        
        # 獲取今日成交金額
        today_volume_amount = None
        if volume_amount is not None and target_datetime in volume_amount.index:
            today_volume_amount = volume_amount.loc[target_datetime]
        
        logger.info(f"目標日期: {target_datetime.strftime('%Y-%m-%d')}")
        logger.info(f"選定產業: {selected_sectors}")
        
        # 台股33個產業分類（MECE標準）- 代表性股票映射
        sector_stock_mapping = {
            # 電子工業（8大類）
            'semiconductor': ['2330', '2454', '2303', '2379', '2317', '3034', '3711'],  # 半導體業
            'computer_peripheral': ['2357', '2377', '2382', '2474', '3231'],  # 電腦及週邊設備業
            'optoelectronics': ['2409', '3481', '3008', '4934', '4952'],  # 光電業
            'communications': ['2412', '3045', '4904', '5388', '6285'],  # 通信網路業
            'electronic_components': ['2327', '2474', '3231', '3019', '3035'],  # 電子零組件業
            'electronic_distribution': ['2347', '2352', '2383', '2449', '2450'],  # 電子通路業
            'information_services': ['2453', '2454', '2474', '3231', '3019'],  # 資訊服務業
            'other_electronics': ['2317', '2352', '2382', '2474', '3231'],  # 其他電子業
            
            # 傳統產業
            'steel_iron': ['2002', '2014', '2027', '2028', '2030'],  # 鋼鐵工業
            'petrochemical': ['1301', '1303', '1326', '6505', '6509'],  # 塑膠工業
            'textile': ['1476', '1477', '1440', '1449', '1451'],  # 紡織纖維
            'food': ['1216', '1227', '1231', '1232', '1233'],  # 食品工業
            'construction': ['2501', '2504', '2505', '2506', '2509'],  # 建材營造
            'shipping': ['2603', '2605', '2609', '2610', '2615'],  # 航運業
            'aviation': ['2618', '2619', '2620', '2621', '2622'],  # 航空業
            'tourism': ['2707', '2712', '2727', '2731', '2739'],  # 觀光餐旅
            'retail': ['2912', '2915', '2923', '2929', '2936'],  # 貿易百貨
            'finance': ['2881', '2882', '2883', '2884', '2885'],  # 金融保險
            'securities': ['6005', '6015', '6024', '6026', '6027'],  # 證券業
            'biotech': ['4743', '4142', '4105', '4107', '4108'],  # 生技醫療
            'pharmaceutical': ['4105', '4107', '4108', '4119', '4128'],  # 製藥業
            'chemical': ['1717', '1718', '1722', '1723', '1727'],  # 化學工業
            'glass_ceramics': ['1802', '1806', '1808', '1809', '1810'],  # 玻璃陶瓷
            'paper': ['1904', '1905', '1906', '1907', '1909'],  # 造紙工業
            'rubber': ['2101', '2102', '2103', '2104', '2105'],  # 橡膠工業
            'automotive': ['2201', '2204', '2206', '2207', '2208'],  # 汽車工業
            'machinery': ['1503', '1504', '1506', '1507', '1509'],  # 電機機械
            'electrical': ['1503', '1504', '1506', '1507', '1509'],  # 電器電纜
            'cable': ['1605', '1608', '1609', '1611', '1612'],  # 電器電纜
            
            # 新興產業
            'green_energy': ['3711', '3708', '3706', '3704', '3705'],  # 綠能環保
            'digital_cloud': ['2453', '2454', '2474', '3231', '3019'],  # 數位雲端
            'sports_leisure': ['9914', '9917', '9921', '9924', '9925'],  # 運動休閒
            'home_living': ['9933', '9934', '9935', '9937', '9938'],  # 居家生活
            'other': ['1101', '1102', '1103', '1104', '1108']  # 其他
        }
        
        # 收集所有選定產業的股票
        target_stocks = []
        for sector in selected_sectors:
            if sector in sector_stock_mapping:
                target_stocks.extend(sector_stock_mapping[sector])
        
        # 去重
        target_stocks = list(set(target_stocks))
        
        logger.info(f"目標股票數量: {len(target_stocks)}")
        
        # 獲取股票數據
        sector_stocks = []
        
        for stock_id in target_stocks:
            try:
                # 檢查股票是否存在於數據中
                if stock_id not in close_price.columns:
                    continue
                
                # 獲取今日收盤價
                today_price = today_close[stock_id]
                
                # 檢查是否有有效數據
                if pd.isna(today_price) or today_price == 0:
                    continue
                
                # 獲取成交金額資訊
                volume_amount_value = 0
                if today_volume_amount is not None and stock_id in today_volume_amount.index:
                    amount = today_volume_amount[stock_id]
                    if not pd.isna(amount):
                        volume_amount_value = round(amount, 0)
                
                # 轉換為前端期望的格式
                stock_data = {
                    "stock_code": stock_id,
                    "stock_name": get_stock_name(stock_id),
                    "current_price": round(today_price, 2),
                    "limit_up_price": round(today_price, 2),
                    "volume": volume_amount_value,  # 成交金額
                    "volume_rank": 0,  # 暫時設為0，可以後續計算
                    "market_cap": 0,  # 暫時設為0
                    "sector": selected_sectors[0] if selected_sectors else "未知",  # 使用第一個選定產業
                    "limit_up_reason": "產業選擇",  # 標記為產業選擇
                    "news_sentiment": 0.8,  # 暫時設為預設值
                    "technical_score": 0.9,  # 暫時設為預設值
                    "yesterday_close": round(today_price, 2),  # 暫時設為今日價格
                    "change_amount": 0,  # 暫時設為0
                    "change_percent": 0,  # 暫時設為0
                    "volume_amount": volume_amount_value,
                    "volume_amount_billion": round(volume_amount_value / 100000000, 4) if volume_amount_value > 0 else 0
                }
                
                sector_stocks.append(stock_data)
                    
            except Exception as e:
                logger.warning(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue
        
        # 根據成交金額篩選
        if volume_threshold:
            sector_stocks = [s for s in sector_stocks if s.get('volume_amount', 0) >= volume_threshold]
            logger.info(f"成交金額篩選後剩餘 {len(sector_stocks)} 檔股票")
        
        if volume_percentile and len(sector_stocks) > 0:
            # 按成交金額排序，取前N%
            sorted_stocks = sorted(sector_stocks, key=lambda x: x.get('volume_amount', 0), reverse=True)
            cutoff_index = int(len(sorted_stocks) * (volume_percentile / 100))
            sector_stocks = sorted_stocks[:cutoff_index]
            logger.info(f"百分位篩選後剩餘 {len(sector_stocks)} 檔股票")
        
        # 按成交金額排序
        sector_stocks.sort(key=lambda x: x.get('volume_amount', 0), reverse=True)
        
        # 添加成交量排名
        for i, stock in enumerate(sector_stocks, 1):
            stock['volume_rank'] = i
        
        logger.info(f"找到 {len(sector_stocks)} 檔產業股票")
        return sector_stocks
        
    except Exception as e:
        logger.error(f"獲取產業股票時發生錯誤: {e}")
        return []

# 依賴注入函數
def get_posting_service(db: Session = Depends(get_db)) -> PostingService:
    """獲取發文管理服務實例"""
    return PostingService(db)

# ==================== 模板管理 ====================

@router.post("/templates", response_model=dict)
async def create_template(
    template_data: dict,
    service: PostingService = Depends(get_posting_service)
):
    """創建發文模板"""
    try:
        return await service.create_template(template_data)
    except Exception as e:
        logger.error(f"創建發文模板失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates", response_model=List[dict])
async def get_templates(
    service: PostingService = Depends(get_posting_service)
):
    """獲取發文模板列表"""
    try:
        return await service.get_templates()
    except Exception as e:
        logger.error(f"獲取發文模板列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 會話管理 ====================

@router.post("/sessions", response_model=dict)
async def create_session(
    session_data: dict,
    service: PostingService = Depends(get_posting_service)
):
    """創建發文會話"""
    try:
        # 直接創建會話，不依賴Pydantic模型
        session = PostingSession(
            session_name=session_data.get('name', 'New Session'),
            trigger_type=session_data.get('trigger_type', 'custom_stocks'),
            trigger_data=session_data.get('trigger_data', {}),
            config=session_data.get('config', {}),
            status='active'
        )
        service.db.add(session)
        service.db.commit()
        service.db.refresh(session)
        
        return {
            "id": session.id,
            "session_name": session.session_name,
            "trigger_type": session.trigger_type,
            "trigger_data": session.trigger_data,
            "config": session.config,
            "status": session.status,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None
        }
    except Exception as e:
        logger.error(f"創建發文會話失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[dict])
async def get_sessions(
    service: PostingService = Depends(get_posting_service)
):
    """獲取發文會話列表"""
    try:
        return await service.get_sessions()
    except Exception as e:
        logger.error(f"獲取發文會話列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_post_content(kol_info: dict, stock_code: str, stock_name: str, prompt_template: str, trigger_data: dict) -> str:
    """生成發文內容"""
    try:
        # 如果沒有自定義prompt，使用默認模板
        if not prompt_template:
            prompt_template = f"""你是一位專業的股票分析師，暱稱是「{kol_info['nickname']}」，人設是「{kol_info['persona']}」。

請分析股票 {stock_name}({stock_code})，保持你的專業風格和人設特色。"""
        
        # 替換prompt中的變量
        stock_info = f"{stock_name}({stock_code})"
        prompt = prompt_template.replace("{stock_info}", stock_info)
        
        # TODO: 調用AI服務生成內容
        # 這裡暫時返回模擬內容
        if kol_info['persona'] == '技術派':
            content = f"{stock_name}({stock_code}) 從技術面來看，MACD出現黃金交叉，均線呈現多頭排列，成交量放大，技術指標顯示強勢突破信號。"
        elif kol_info['persona'] == '總經派':
            content = f"{stock_name}({stock_code}) 從基本面分析來看，營收成長超預期，財務指標穩健，長期投資價值顯現。"
        elif kol_info['persona'] == '消息派':
            content = f"{stock_name}({stock_code}) 聽說有內線消息，但具體內容還不能說太多，大家自己判斷。"
        else:
            content = f"{stock_name}({stock_code}) 從多個角度分析，這支股票值得關注。"
        
        return content
        
    except Exception as e:
        logger.error(f"生成內容失敗: {e}")
        return f"{stock_name}({stock_code}) 分析內容生成失敗。"

@router.post("/sessions/{session_id}/generate")
async def generate_posts(
    session_id: int,
    service: PostingService = Depends(get_posting_service)
):
    """生成發文"""
    try:
        # 獲取會話配置
        session = await service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="會話不存在")
        
        # 獲取會話配置
        config = session.get('config', {})
        kol_config = config.get('kol', {})
        kol_prompts = config.get('kolPrompts', [])
        trigger_data = config.get('trigger_data', {})
        
        # 獲取選中的KOL
        selected_kols = kol_config.get('selected_kols', [])
        if not selected_kols:
            raise HTTPException(status_code=400, detail="未選擇KOL")
        
        # 獲取股票數據
        stock_codes = trigger_data.get('stock_codes', [])
        stock_names = trigger_data.get('stock_names', [])
        
        if not stock_codes:
            raise HTTPException(status_code=400, detail="未選擇股票")
        
        # 生成發文
        generated_posts = []
        failed_count = 0
        
        for i, kol_serial in enumerate(selected_kols):
            try:
                # 獲取KOL信息
                kol_info = await service.get_kol_by_serial(kol_serial)
                if not kol_info:
                    logger.warning(f"KOL {kol_serial} 不存在")
                    failed_count += 1
                    continue
                
                # 獲取對應的prompt配置
                prompt_config = next((p for p in kol_prompts if p['kol_serial'] == kol_serial), None)
                prompt_template = prompt_config.get('custom_prompt', prompt_config.get('default_prompt', '')) if prompt_config else ''
                
                # 為每個股票生成發文
                for j, (stock_code, stock_name) in enumerate(zip(stock_codes, stock_names)):
                    # 生成內容
                    post_content = await generate_post_content(
                        kol_info, 
                        stock_code, 
                        stock_name, 
                        prompt_template,
                        trigger_data
                    )
                    
                    # 創建發文記錄
                    post_data = {
                        "session_id": session_id,
                        "title": f"{kol_info['nickname']}的分析 - {stock_name}({stock_code})",
                        "content": post_content,
                        "status": "pending_review",
                        "kol_serial": kol_serial,
                        "kol_nickname": kol_info['nickname'],
                        "kol_persona": kol_info['persona'],
                        "stock_codes": [stock_code],
                        "stock_names": [stock_name],
                        "stock_data": {},
                        "generation_config": config,
                        "prompt_template": prompt_template,
                        "technical_indicators": [],
                        "quality_score": 0.85,
                        "ai_detection_score": 0.15,
                        "risk_level": "low",
                        "views": 0,
                        "likes": 0,
                        "comments": 0,
                        "shares": 0
                    }
                    
                    # 保存到數據庫
                    post = await service.create_post(post_data)
                    generated_posts.append(post)
                    
            except Exception as e:
                logger.error(f"為KOL {kol_serial} 生成發文失敗: {e}")
                failed_count += 1
        
        result = {
            "success": True,
            "generated_count": len(generated_posts),
            "failed_count": failed_count,
            "posts": generated_posts,
            "errors": []
        }
        
        return result
        
    except Exception as e:
        logger.error(f"生成發文失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 發文管理 ====================

@router.post("/posts", response_model=dict)
async def create_post(
    post_data: dict,
    service: PostingService = Depends(get_posting_service)
):
    """創建發文"""
    try:
        return await service.create_post(post_data)
    except Exception as e:
        logger.error(f"創建發文失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts")
async def get_posts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    service: PostingService = Depends(get_posting_service)
):
    """獲取發文列表"""
    try:
        return await service.get_posts(skip, limit, status)
    except Exception as e:
        logger.error(f"獲取發文列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/posts/{post_id}/status")
async def update_post_status(
    post_id: int,
    status: str,
    service: PostingService = Depends(get_posting_service)
):
    """更新發文狀態"""
    try:
        return await service.update_post_status(post_id, status)
    except Exception as e:
        logger.error(f"更新發文狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/posts/{post_id}/content")
async def update_post_content(
    post_id: int,
    title: str,
    content: str,
    service: PostingService = Depends(get_posting_service)
):
    """更新發文內容"""
    try:
        return await service.update_post_content(post_id, title, content)
    except Exception as e:
        logger.error(f"更新發文內容失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Prompt模板管理 ====================

@router.post("/prompt-templates", response_model=dict)
async def create_prompt_template(
    template_data: dict,
    service: PostingService = Depends(get_posting_service)
):
    """創建Prompt模板"""
    try:
        return await service.create_prompt_template(template_data)
    except Exception as e:
        logger.error(f"創建Prompt模板失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompt-templates", response_model=List[dict])
async def get_prompt_templates(
    data_source: Optional[str] = None,
    service: PostingService = Depends(get_posting_service)
):
    """獲取Prompt模板列表"""
    try:
        return await service.get_prompt_templates(data_source)
    except Exception as e:
        logger.error(f"獲取Prompt模板列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== KOL管理 ====================

@router.get("/kols", response_model=List[dict])
async def get_kols(
    service: PostingService = Depends(get_posting_service)
):
    """獲取KOL列表"""
    try:
        return await service.get_kols()
    except Exception as e:
        logger.error(f"獲取KOL列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 觸發器數據 ====================

@router.get("/debug/env")
async def debug_env():
    """調試環境變量"""
    finlab_key = os.getenv('FINLAB_API_KEY')
    return {
        "FINLAB_API_KEY": "SET" if finlab_key else "NOT SET",
        "key_length": len(finlab_key) if finlab_key else 0
    }

@router.post("/triggers/after-hours-limit-up")
async def get_after_hours_limit_up_stocks(
    trigger_config: dict,
    service: PostingService = Depends(get_posting_service)
):
    """獲取盤後漲跌股票數據（支援漲跌幅和成交量篩選）"""
    try:
        # 檢查環境變量
        finlab_key = os.getenv('FINLAB_API_KEY')
        if not finlab_key:
            logger.error("未找到 FINLAB_API_KEY 環境變數")
            return {
                "success": False,
                "error": "FINLAB_API_KEY not found",
                "total_count": 0,
                "stocks": []
            }
        
        # 從配置中獲取參數
        volume_threshold = trigger_config.get('volume_threshold')
        volume_percentile = trigger_config.get('volume_percentile')
        high_volume_only = trigger_config.get('limit_up_after_hours_high_volume', False)
        low_volume_only = trigger_config.get('limit_up_after_hours_low_volume', False)
        
        # 獲取漲跌幅設定
        change_threshold = trigger_config.get('changeThreshold', {})
        change_type = change_threshold.get('type', 'up')  # 'up' or 'down'
        change_percentage = change_threshold.get('percentage', 9.5)  # 預設9.5%
        
        # 獲取產業選擇設定
        sector_selection = trigger_config.get('sectorSelection', {})
        selected_sectors = sector_selection.get('selectedSectors', [])
        sector_volume_threshold = sector_selection.get('volumeThreshold')
        sector_volume_percentile = sector_selection.get('volumePercentile')
        
        # 根據觸發器類型獲取股票
        trigger_key = trigger_config.get('triggerKey', 'limit_up_after_hours')
        
        if trigger_key == 'sector_selection':
            # 產業選擇觸發器
            stocks = await _get_sector_stocks_from_finlab(
                selected_sectors, 
                sector_volume_threshold, 
                sector_volume_percentile
            )
        elif trigger_key == 'limit_up_after_hours':
            # 盤後漲觸發器
            logger.info(f"調用盤後漲觸發器，漲幅閾值: {change_percentage}% (type: {type(change_percentage)})")
            try:
                # 確保 change_percentage 是 float 類型
                min_change_percent = float(change_percentage)
                logger.info(f"轉換後的漲幅閾值: {min_change_percent}")
                stocks = await _get_real_limit_up_stocks_from_finlab(min_change_percent=min_change_percent)
                logger.info(f"盤後漲觸發器返回 {len(stocks)} 支股票")
            except Exception as e:
                logger.error(f"盤後漲觸發器調用失敗: {e}")
                import traceback
                logger.error(f"詳細錯誤: {traceback.format_exc()}")
                stocks = []
        elif trigger_key == 'limit_down_after_hours':
            # 盤後跌觸發器
            stocks = await _get_real_limit_down_stocks_from_finlab(change_percentage)
        else:
            # 預設使用上漲股票
            stocks = await _get_real_limit_up_stocks_from_finlab(change_percentage)
        
        if not stocks:
            logger.warning(f"未找到任何{change_type == 'up' and '上漲' or '下跌'}股票")
            return {
                "success": True,
                "total_count": 0,
                "filter_config": {
                    "volume_threshold": volume_threshold,
                    "volume_percentile": volume_percentile,
                    "high_volume_only": high_volume_only,
                    "low_volume_only": low_volume_only,
                    "change_threshold": change_threshold
                },
                "stocks": [],
                "summary": {
                    "high_volume_count": 0,
                    "low_volume_count": 0,
                    "avg_volume": 0,
                    "avg_volume_rank": 0
                }
            }
        
        # 先返回所有股票，不進行預篩選
        # 篩選邏輯將在前端根據用戶需求進行
        filtered_stocks = stocks
        
        # 計算統計摘要
        volume_amounts = [s.get('volume_amount', 0) for s in filtered_stocks]
        avg_volume = sum(volume_amounts) / len(volume_amounts) if volume_amounts else 0
        
        # 計算高/低成交量數量
        sorted_all = sorted(stocks, key=lambda x: x.get('volume_amount', 0), reverse=True)
        high_volume_cutoff = int(len(sorted_all) * 0.7)  # 前70%為高成交量
        high_volume_count = len([s for s in filtered_stocks if s in sorted_all[:high_volume_cutoff]])
        low_volume_count = len(filtered_stocks) - high_volume_count
        
        return {
            "success": True,
            "total_count": len(filtered_stocks),
            "filter_config": {
                "volume_threshold": volume_threshold,
                "volume_percentile": volume_percentile,
                "high_volume_only": high_volume_only,
                "low_volume_only": low_volume_only,
                "change_threshold": change_threshold
            },
            "stocks": filtered_stocks,
            "summary": {
                "high_volume_count": high_volume_count,
                "low_volume_count": low_volume_count,
                "avg_volume": avg_volume,
                "avg_volume_rank": 0  # 暫時設為0，可以後續計算
            }
        }
        
    except Exception as e:
        logger.error(f"獲取盤後漲停股票數據失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 分析數據 ====================

@router.get("/analytics/posts/{post_id}", response_model=List[dict])
async def get_post_analytics(
    post_id: int,
    days: int = 7,
    service: PostingService = Depends(get_posting_service)
):
    """獲取發文分析數據"""
    try:
        return await service.get_post_analytics(post_id, days)
    except Exception as e:
        logger.error(f"獲取發文分析數據失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/summary")
async def get_analytics_summary(
    days: int = 30,
    service: PostingService = Depends(get_posting_service)
):
    """獲取分析摘要"""
    try:
        return await service.get_analytics_summary(days)
    except Exception as e:
        logger.error(f"獲取分析摘要失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))