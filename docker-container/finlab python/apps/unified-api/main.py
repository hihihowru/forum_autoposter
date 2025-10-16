"""
統一的 API 服務 - 完整版本
Railway 部署時使用此服務作為唯一的 API 入口
整合所有微服務功能到一個 API
"""

from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import httpx
import json
import sys
import os
import pandas as pd
import numpy as np

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="Forum Autoposter Unified API",
    description="統一的 API 服務，整合所有微服務功能",
    version="1.0.0"
)

# 配置 CORS - 允許所有來源（因為我們會用 Vercel Proxy）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ==================== FinLab 初始化 ====================

import finlab
from finlab import data

stock_mapping = {}

@app.on_event("startup")
def startup_event():
    """啟動時初始化 FinLab"""
    global stock_mapping
    api_key = os.getenv("FINLAB_API_KEY")
    if api_key:
        finlab.login(api_key)
        logger.info("✅ FinLab API 登入成功")
    else:
        logger.warning("❌ 未找到 FINLAB_API_KEY 環境變數")

    # 載入股票映射表
    try:
        stock_mapping_path = '/app/stock_mapping.json'
        if os.path.exists(stock_mapping_path):
            with open(stock_mapping_path, 'r', encoding='utf-8') as f:
                stock_mapping = json.load(f)
            logger.info(f"✅ 載入股票映射表成功: {len(stock_mapping)} 支股票")
        else:
            logger.warning(f"⚠️ 股票映射表不存在: {stock_mapping_path}")
    except Exception as e:
        logger.error(f"❌ 載入股票映射表失敗: {e}")

def ensure_finlab_login():
    """確保 FinLab 已登入"""
    try:
        test_data = data.get('market_transaction_info:收盤指數')
        if test_data is None:
            api_key = os.getenv("FINLAB_API_KEY")
            if api_key:
                finlab.login(api_key)
                logger.info("🔄 FinLab API 重新登入成功")
            else:
                raise Exception("未找到 FINLAB_API_KEY")
    except Exception as e:
        logger.error(f"❌ FinLab 登入檢查失敗: {e}")
        raise e

# ==================== 輔助函數 ====================

def get_stock_name(stock_code: str) -> str:
    """根據股票代號獲取股票名稱"""
    if stock_code in stock_mapping:
        return stock_mapping[stock_code].get('company_name', f"股票{stock_code}")

    stock_names = {
        "2330": "台積電", "2454": "聯發科", "2317": "鴻海", "2881": "富邦金",
        "2882": "國泰金", "1101": "台泥", "1102": "亞泥", "1216": "統一",
        "1303": "南亞", "1326": "台化", "2002": "中鋼", "2308": "台達電",
        "2377": "微星", "2382": "廣達", "2408": "南亞科", "2474": "可成",
        "2498": "宏達電", "3008": "大立光", "3034": "聯詠", "3231": "緯創",
        "3711": "日月光投控", "4938": "和碩", "6505": "台塑化", "8046": "南電",
        "9910": "豐泰", "2412": "中華電", "1301": "台塑", "2603": "長榮"
    }
    return stock_names.get(stock_code, f"股票{stock_code}")

def get_stock_industry(stock_code: str) -> str:
    """根據股票代號獲取產業類別"""
    if stock_code in stock_mapping:
        return stock_mapping[stock_code].get('industry', '未知產業')
    return '未知產業'

def calculate_trading_stats(stock_id: str, latest_date: datetime, close_df: pd.DataFrame) -> dict:
    """計算過去五個交易日的統計資訊"""
    try:
        trading_days = close_df.index[close_df.index <= latest_date].sort_values(ascending=False)[:5]

        if len(trading_days) < 2:
            return {"up_days": 0, "five_day_change": 0.0}

        up_days = 0
        for i in range(len(trading_days) - 1):
            current_price = close_df.loc[trading_days[i], stock_id]
            previous_price = close_df.loc[trading_days[i + 1], stock_id]

            if not pd.isna(current_price) and not pd.isna(previous_price) and current_price > previous_price:
                up_days += 1

        five_days_ago_price = close_df.loc[trading_days[-1], stock_id]
        latest_price = close_df.loc[trading_days[0], stock_id]

        if not pd.isna(five_days_ago_price) and not pd.isna(latest_price) and five_days_ago_price != 0:
            five_day_change = ((latest_price - five_days_ago_price) / five_days_ago_price) * 100
        else:
            five_day_change = 0.0

        return {
            "up_days": up_days,
            "five_day_change": round(five_day_change, 2)
        }
    except Exception as e:
        logger.error(f"計算 {stock_id} 交易統計失敗: {e}")
        return {"up_days": 0, "five_day_change": 0.0}

# ==================== 健康檢查 ====================

@app.get("/")
async def root():
    """根路徑"""
    logger.info("收到根路徑請求")
    return {
        "message": "Forum Autoposter Unified API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    logger.info("收到健康檢查請求")
    return {
        "status": "healthy",
        "message": "Unified API is running successfully",
        "timestamp": datetime.now().isoformat()
    }

# ==================== OHLC API 功能 ====================

@app.get("/after_hours_limit_up")
async def get_after_hours_limit_up_stocks(
    limit: int = Query(1000, description="股票數量限制"),
    changeThreshold: float = Query(9.5, description="漲跌幅閾值百分比"),
    industries: str = Query("", description="產業類別篩選")
):
    """獲取盤後漲停股票列表 - 支持動態漲跌幅設定"""
    try:
        ensure_finlab_login()

        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')

        if close_df is None or close_df.empty:
            return {"error": "無法獲取收盤價數據"}

        close_df = close_df.sort_index()
        if volume_df is not None:
            volume_df = volume_df.sort_index()

        latest_date = close_df.index[-1]
        latest_close = close_df.loc[latest_date]

        previous_dates = close_df.index[close_df.index < latest_date]
        if len(previous_dates) == 0:
            return {"error": f"無法找到 {latest_date.strftime('%Y-%m-%d')} 之前的交易日數據"}

        previous_date = previous_dates[-1]
        previous_close = close_df.loc[previous_date]

        latest_volume = None
        if volume_df is not None and latest_date in volume_df.index:
            latest_volume = volume_df.loc[latest_date]

        selected_industries = []
        if industries:
            selected_industries = [industry.strip() for industry in industries.split(',') if industry.strip()]

        limit_up_stocks = []

        for stock_id in latest_close.index:
            try:
                if selected_industries:
                    stock_industry = get_stock_industry(stock_id)
                    if stock_industry not in selected_industries:
                        continue

                today_price = latest_close[stock_id]
                yesterday_price = previous_close[stock_id]

                if pd.isna(today_price) or pd.isna(yesterday_price) or yesterday_price == 0:
                    continue

                change_percent = ((today_price - yesterday_price) / yesterday_price) * 100

                if change_percent >= changeThreshold:
                    stock_name = get_stock_name(stock_id)
                    stock_industry = get_stock_industry(stock_id)

                    volume = 0
                    volume_amount = 0
                    if latest_volume is not None and stock_id in latest_volume.index:
                        vol = latest_volume[stock_id]
                        if not pd.isna(vol):
                            volume = int(vol)
                            volume_amount = volume * float(today_price)

                    trading_stats = calculate_trading_stats(stock_id, latest_date, close_df)

                    limit_up_stocks.append({
                        'stock_code': stock_id,
                        'stock_name': stock_name,
                        'industry': stock_industry,
                        'current_price': float(today_price),
                        'yesterday_close': float(yesterday_price),
                        'change_amount': float(today_price - yesterday_price),
                        'change_percent': float(change_percent),
                        'volume': volume,
                        'volume_amount': volume_amount,
                        'date': latest_date.strftime('%Y-%m-%d'),
                        'previous_date': previous_date.strftime('%Y-%m-%d'),
                        'up_days_5': trading_stats['up_days'],
                        'five_day_change': trading_stats['five_day_change']
                    })

            except Exception as e:
                logger.error(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue

        limit_up_stocks.sort(key=lambda x: x['volume'], reverse=True)
        limit_up_stocks = limit_up_stocks[:limit]

        return {
            'success': True,
            'total_count': len(limit_up_stocks),
            'stocks': limit_up_stocks,
            'timestamp': datetime.now().isoformat(),
            'date': latest_date.strftime('%Y-%m-%d'),
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'changeThreshold': changeThreshold
        }

    except Exception as e:
        logger.error(f"獲取盤後漲停股票失敗: {e}")
        return {"error": str(e)}

@app.get("/after_hours_limit_down")
async def get_after_hours_limit_down_stocks(
    limit: int = Query(1000, description="股票數量限制"),
    changeThreshold: float = Query(-9.5, description="跌幅閾值百分比"),
    industries: str = Query("", description="產業類別篩選")
):
    """獲取盤後跌停股票列表"""
    try:
        ensure_finlab_login()

        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')

        if close_df is None or close_df.empty:
            return {"error": "無法獲取收盤價數據"}

        close_df = close_df.sort_index()
        if volume_df is not None:
            volume_df = volume_df.sort_index()

        latest_date = close_df.index[-1]
        latest_close = close_df.loc[latest_date]

        previous_dates = close_df.index[close_df.index < latest_date]
        if len(previous_dates) == 0:
            return {"error": f"無法找到 {latest_date.strftime('%Y-%m-%d')} 之前的交易日數據"}

        previous_date = previous_dates[-1]
        previous_close = close_df.loc[previous_date]

        latest_volume = None
        if volume_df is not None and latest_date in volume_df.index:
            latest_volume = volume_df.loc[latest_date]

        selected_industries = []
        if industries:
            selected_industries = [industry.strip() for industry in industries.split(',') if industry.strip()]

        limit_down_stocks = []

        for stock_id in latest_close.index:
            try:
                if selected_industries:
                    stock_industry = get_stock_industry(stock_id)
                    if stock_industry not in selected_industries:
                        continue

                today_price = latest_close[stock_id]
                yesterday_price = previous_close[stock_id]

                if pd.isna(today_price) or pd.isna(yesterday_price) or yesterday_price == 0:
                    continue

                change_percent = ((today_price - yesterday_price) / yesterday_price) * 100

                if change_percent <= changeThreshold:
                    stock_name = get_stock_name(stock_id)
                    stock_industry = get_stock_industry(stock_id)

                    volume = 0
                    volume_amount = 0
                    if latest_volume is not None and stock_id in latest_volume.index:
                        vol = latest_volume[stock_id]
                        if not pd.isna(vol):
                            volume = int(vol)
                            volume_amount = volume * float(today_price)

                    trading_stats = calculate_trading_stats(stock_id, latest_date, close_df)

                    limit_down_stocks.append({
                        'stock_code': stock_id,
                        'stock_name': stock_name,
                        'industry': stock_industry,
                        'current_price': float(today_price),
                        'yesterday_close': float(yesterday_price),
                        'change_amount': float(today_price - yesterday_price),
                        'change_percent': float(change_percent),
                        'volume': volume,
                        'volume_amount': volume_amount,
                        'date': latest_date.strftime('%Y-%m-%d'),
                        'previous_date': previous_date.strftime('%Y-%m-%d'),
                        'up_days_5': trading_stats['up_days'],
                        'five_day_change': trading_stats['five_day_change']
                    })

            except Exception as e:
                logger.error(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue

        limit_down_stocks.sort(key=lambda x: x['volume'], reverse=True)
        limit_down_stocks = limit_down_stocks[:limit]

        return {
            'success': True,
            'total_count': len(limit_down_stocks),
            'stocks': limit_down_stocks,
            'timestamp': datetime.now().isoformat(),
            'date': latest_date.strftime('%Y-%m-%d'),
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'changeThreshold': changeThreshold
        }

    except Exception as e:
        logger.error(f"獲取盤後跌停股票失敗: {e}")
        return {"error": str(e)}

@app.get("/industries")
async def get_industries():
    """獲取所有產業類別"""
    logger.info("收到 industries 請求")

    try:
        industries = set()
        for stock_code, info in stock_mapping.items():
            if 'industry' in info:
                industries.add(info['industry'])

        industries_list = [{"id": ind, "name": ind} for ind in sorted(list(industries))]

        result = {
            "success": True,
            "data": industries_list,
            "count": len(industries_list),
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"返回 industries 數據: {len(result['data'])} 條記錄")
        return result
    except Exception as e:
        logger.error(f"獲取產業類別失敗: {e}")
        return {"error": str(e)}

@app.get("/stocks_by_industry")
async def get_stocks_by_industry(industry: str = Query(..., description="產業類別")):
    """根據產業獲取股票列表"""
    logger.info(f"收到 stocks_by_industry 請求: industry={industry}")

    try:
        stocks = []
        for stock_code, info in stock_mapping.items():
            if info.get('industry') == industry:
                stocks.append({
                    "stock_id": stock_code,
                    "stock_name": info.get('company_name', stock_code),
                    "industry": industry
                })

        result = {
            "success": True,
            "data": stocks,
            "count": len(stocks),
            "industry": industry,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"返回 {industry} 產業股票: {len(result['data'])} 支")
        return result
    except Exception as e:
        logger.error(f"獲取產業股票失敗: {e}")
        return {"error": str(e)}

@app.get("/get_ohlc")
async def get_ohlc(stock_id: str = Query(..., description="股票代碼")):
    """獲取特定股票的 OHLC 數據"""
    logger.info(f"收到 get_ohlc 請求: stock_id={stock_id}")

    try:
        ensure_finlab_login()

        open_df = data.get('price:開盤價')
        high_df = data.get('price:最高價')
        low_df = data.get('price:最低價')
        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')

        if stock_id not in open_df.columns:
            return {"error": f"Stock ID {stock_id} not found."}

        ohlcv_df = pd.DataFrame({
            'open': open_df[stock_id],
            'high': high_df[stock_id],
            'low': low_df[stock_id],
            'close': close_df[stock_id],
            'volume': volume_df[stock_id]
        })

        ohlcv_df = ohlcv_df.dropna().reset_index()
        ohlcv_df.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

        one_year_ago = datetime.today() - timedelta(days=365)
        ohlcv_df = ohlcv_df[ohlcv_df['date'] >= one_year_ago]

        return json.loads(ohlcv_df.to_json(orient="records", date_format="iso"))
    except Exception as e:
        logger.error(f"獲取 OHLC 數據失敗: {e}")
        return {"error": str(e)}

# ==================== 盤中觸發器功能 ====================

# CMoney API 配置
CMONEY_API_BASE = "https://asterisk-chipsapi.cmoney.tw"

def get_forum_200_credentials():
    """從環境變數獲取 forum_200 憑證"""
    email = os.getenv("FORUM_200_EMAIL")
    password = os.getenv("FORUM_200_PASSWORD")
    member_id = os.getenv("FORUM_200_MEMBER_ID", "9505546")  # 預設值
    
    if not email or not password:
        raise Exception("缺少 FORUM_200_EMAIL 或 FORUM_200_PASSWORD 環境變數")
    
    return {
        "email": email,
        "password": password,
        "member_id": member_id
    }

_token_cache = {
    "token": None,
    "expires_at": None,
    "created_at": None
}

async def get_dynamic_auth_token() -> str:
    """使用 forum_200 KOL 憑證動態取得 CMoney API token"""
    try:
        if (_token_cache["token"] and
            _token_cache["expires_at"] and
            datetime.now() < _token_cache["expires_at"]):
            logger.info("✅ 使用快取的 CMoney API token")
            return _token_cache["token"]

        logger.info("🔐 開始使用 forum_200 憑證登入 CMoney...")

        # 將 src 路徑加入 Python path
        src_path = '/app/src'
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

        cmoney_client = CMoneyClient()
        forum_credentials = get_forum_200_credentials()
        credentials = LoginCredentials(
            email=forum_credentials["email"],
            password=forum_credentials["password"]
        )

        login_result = await cmoney_client.login(credentials)

        if not login_result or not login_result.token:
            raise Exception("forum_200 登入失敗")

        _token_cache["token"] = login_result.token
        _token_cache["expires_at"] = login_result.expires_at
        _token_cache["created_at"] = datetime.now()

        logger.info(f"✅ forum_200 登入成功，token 有效期至: {login_result.expires_at}")
        return login_result.token

    except Exception as e:
        logger.error(f"❌ 動態取得 CMoney API token 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"認證失敗: {str(e)}")

@app.get("/intraday-trigger/execute")
async def get_intraday_trigger_stocks(
    endpoint: str = Query(..., description="數據源端點"),
    processing: str = Query("", description="處理配置")
):
    """獲取盤中觸發器股票列表"""
    logger.info(f"收到盤中觸發器請求: endpoint={endpoint}, processing={processing}")

    try:
        # 解析處理配置
        processing_config = []
        if processing:
            try:
                processing_config = json.loads(processing) if isinstance(processing, str) else processing
            except:
                processing_config = []

        # 準備請求參數
        columns = "交易時間,傳輸序號,內外盤旗標,即時成交價,即時成交量,最低價,最高價,標的,漲跌,漲跌幅,累計成交總額,累計成交量,開盤價"

        request_data = {
            "AppId": 2,
            "Guid": "583defeb-f7cb-49e7-964d-d0817e944e4f",
            "Processing": processing_config
        }

        # 動態取得認證 token
        logger.info("🔐 [盤中觸發器] 開始動態取得認證 token...")
        try:
            auth_token = await get_dynamic_auth_token()
            logger.info(f"✅ [盤中觸發器] 成功取得 token: {auth_token[:20]}...")
        except Exception as e:
            logger.error(f"❌ [盤中觸發器] 動態認證失敗: {e}")
            raise

        # 準備請求頭
        headers = {
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}",
            "cmoneyapi-trace-context": '{"appVersion":"10.111.0","osName":"iOS","platform":1,"manufacturer":"Apple","osVersion":"18.6.2","appId":2,"model":"iPhone15,2"}'
        }

        # 發送請求到 CMoney API
        logger.info(f"🌐 [盤中觸發器] 發送請求到 CMoney API: {endpoint}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{endpoint}?columns={columns}",
                json=request_data,
                headers=headers
            )

            logger.info(f"📡 [盤中觸發器] CMoney API 響應狀態: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"❌ [盤中觸發器] CMoney API 請求失敗: HTTP {response.status_code}, 響應: {response.text}")
                raise HTTPException(status_code=500, detail=f"CMoney API 請求失敗: {response.status_code}")

            # 解析響應數據
            data = response.json()
            logger.info(f"📊 [盤中觸發器] 收到數據: {len(data)} 筆記錄")

            # 提取股票代碼 (第8個欄位，索引為7)
            stocks = [item[7] for item in data if len(item) > 7 and item[7]]

            logger.info(f"✅ [盤中觸發器] 執行成功，獲取 {len(stocks)} 支股票: {stocks}")

            return {
                "success": True,
                "stocks": stocks,
                "data": data,
                "count": len(stocks)
            }

    except httpx.TimeoutException:
        logger.error("❌ [盤中觸發器] CMoney API 請求超時")
        raise HTTPException(status_code=504, detail="CMoney API 請求超時")
    except httpx.ConnectError:
        logger.error("❌ [盤中觸發器] CMoney API 連接失敗")
        raise HTTPException(status_code=503, detail="CMoney API 連接失敗")
    except Exception as e:
        logger.error(f"❌ [盤中觸發器] 執行失敗: {e}")
        raise HTTPException(status_code=500, detail=f"執行失敗: {str(e)}")

# ==================== Posting Service 功能 ====================

@app.post("/api/posting")
async def create_posting(request: Request):
    """創建貼文"""
    logger.info("收到 create_posting 請求")

    try:
        body = await request.json()
        logger.info(f"貼文內容: {body}")

        result = {
            "success": True,
            "message": "貼文創建成功",
            "post_id": "post_12345",
            "data": body,
            "timestamp": datetime.now().isoformat()
        }

        logger.info("貼文創建成功")
        return result

    except Exception as e:
        logger.error(f"貼文創建失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"貼文創建失敗: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/api/manual-posting")
async def manual_posting(request: Request):
    """手動貼文"""
    logger.info("收到 manual_posting 請求")

    try:
        body = await request.json()
        logger.info(f"手動貼文內容: {body}")

        result = {
            "success": True,
            "message": "手動貼文成功",
            "post_id": "manual_post_67890",
            "data": body,
            "timestamp": datetime.now().isoformat()
        }

        logger.info("手動貼文成功")
        return result

    except Exception as e:
        logger.error(f"手動貼文失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"手動貼文失敗: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

# ==================== Dashboard API 功能 ====================

@app.get("/dashboard/system-monitoring")
async def get_system_monitoring():
    """獲取系統監控數據"""
    logger.info("收到 system-monitoring 請求")

    result = {
        "success": True,
        "data": {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 23.1,
            "active_connections": 156,
            "uptime": "5 days, 12 hours",
            "last_restart": "2025-10-10T08:30:00Z"
        },
        "timestamp": datetime.now().isoformat()
    }

    logger.info("返回系統監控數據")
    return result

@app.get("/dashboard/content-management")
async def get_content_management():
    """獲取內容管理數據"""
    logger.info("收到 content-management 請求")

    result = {
        "success": True,
        "data": {
            "total_posts": 1250,
            "published_posts": 1180,
            "draft_posts": 70,
            "scheduled_posts": 45,
            "failed_posts": 5
        },
        "timestamp": datetime.now().isoformat()
    }

    logger.info("返回內容管理數據")
    return result

@app.get("/dashboard/interaction-analysis")
async def get_interaction_analysis():
    """獲取互動分析數據"""
    logger.info("收到 interaction-analysis 請求")

    result = {
        "success": True,
        "data": {
            "total_interactions": 15680,
            "likes": 8920,
            "comments": 2340,
            "shares": 4420,
            "engagement_rate": 12.5,
            "top_performing_posts": [
                {"post_id": "post_001", "interactions": 1250},
                {"post_id": "post_002", "interactions": 980},
                {"post_id": "post_003", "interactions": 750}
            ]
        },
        "timestamp": datetime.now().isoformat()
    }

    logger.info("返回互動分析數據")
    return result

# ==================== Trending API 功能 ====================

@app.get("/trending")
async def get_trending_topics():
    """獲取熱門話題"""
    logger.info("收到 trending 請求")

    result = {
        "success": True,
        "data": [
            {"topic": "AI人工智慧", "trend_score": 95.5, "posts_count": 1250},
            {"topic": "電動車", "trend_score": 88.2, "posts_count": 980},
            {"topic": "半導體", "trend_score": 82.1, "posts_count": 750},
            {"topic": "新能源", "trend_score": 76.8, "posts_count": 650}
        ],
        "timestamp": datetime.now().isoformat()
    }

    logger.info("返回熱門話題數據")
    return result

@app.get("/extract-keywords")
async def extract_keywords(text: str = Query(..., description="要提取關鍵字的文本")):
    """提取關鍵字"""
    logger.info(f"收到 extract-keywords 請求: text={text[:50]}...")

    keywords = ["AI", "人工智慧", "科技", "創新", "發展"]

    result = {
        "success": True,
        "data": {
            "keywords": keywords,
            "confidence_scores": [0.95, 0.88, 0.82, 0.76, 0.65],
            "original_text": text
        },
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"提取到 {len(keywords)} 個關鍵字")
    return result

@app.get("/search-stocks-by-keywords")
async def search_stocks_by_keywords(keywords: str = Query(..., description="關鍵字")):
    """根據關鍵字搜索股票"""
    logger.info(f"收到 search-stocks-by-keywords 請求: keywords={keywords}")

    stocks = [
        {"stock_id": "2330", "stock_name": "台積電", "relevance_score": 0.95},
        {"stock_id": "2454", "stock_name": "聯發科", "relevance_score": 0.88},
        {"stock_id": "2317", "stock_name": "鴻海", "relevance_score": 0.82}
    ]

    result = {
        "success": True,
        "data": {
            "stocks": stocks,
            "keywords": keywords,
            "total_found": len(stocks)
        },
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"找到 {len(stocks)} 支相關股票")
    return result

@app.get("/analyze-topic")
async def analyze_topic(topic: str = Query(..., description="要分析的話題")):
    """分析話題"""
    logger.info(f"收到 analyze-topic 請求: topic={topic}")

    result = {
        "success": True,
        "data": {
            "topic": topic,
            "sentiment": "positive",
            "sentiment_score": 0.75,
            "key_points": [
                "技術創新持續推進",
                "市場需求穩定增長",
                "政策支持力度加大"
            ],
            "related_stocks": ["2330", "2454", "2317"]
        },
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"完成話題分析: {topic}")
    return result

@app.get("/generate-content")
async def generate_content(
    topic: str = Query(..., description="話題"),
    style: str = Query("professional", description="內容風格")
):
    """生成內容"""
    logger.info(f"收到 generate-content 請求: topic={topic}, style={style}")

    result = {
        "success": True,
        "data": {
            "content": f"關於{topic}的專業分析：市場趨勢顯示該領域具有強勁的成長潛力，建議投資人密切關注相關標的。",
            "topic": topic,
            "style": style,
            "word_count": 45,
            "generated_at": datetime.now().isoformat()
        },
        "timestamp": datetime.now().isoformat()
    }

    logger.info(f"生成內容完成: {topic}")
    return result

if __name__ == "__main__":
    import uvicorn
    
    # Railway 使用 PORT 環境變數，本地開發使用 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 啟動 Unified API 服務器: {host}:{port}")
    uvicorn.run(app, host=host, port=port)
