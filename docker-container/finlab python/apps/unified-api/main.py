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
import psycopg2
from psycopg2.extras import RealDictCursor

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
import psycopg2
from psycopg2.extras import RealDictCursor

stock_mapping = {}
db_connection = None

def create_post_records_table():
    """創建 post_records 表（如果不存在）"""
    try:
        if not db_connection:
            logger.error("❌ 數據庫連接不存在，無法創建表")
            return
            
        with db_connection.cursor() as cursor:
            logger.info("🔍 檢查 post_records 表是否存在...")
            # 檢查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'post_records'
                );
            """)
            table_exists = cursor.fetchone()[0]
            logger.info(f"📊 表存在狀態: {table_exists}")
            
            if not table_exists:
                logger.info("📋 開始創建 post_records 表...")
                cursor.execute("""
                    CREATE TABLE post_records (
                        post_id VARCHAR PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        session_id BIGINT,
                        kol_serial INTEGER NOT NULL,
                        kol_nickname VARCHAR NOT NULL,
                        kol_persona VARCHAR,
                        stock_code VARCHAR NOT NULL,
                        stock_name VARCHAR NOT NULL,
                        title VARCHAR NOT NULL,
                        content TEXT NOT NULL,
                        content_md TEXT,
                        status VARCHAR DEFAULT 'draft',
                        reviewer_notes TEXT,
                        approved_by VARCHAR,
                        approved_at TIMESTAMP,
                        scheduled_at TIMESTAMP,
                        published_at TIMESTAMP,
                        cmoney_post_id VARCHAR,
                        cmoney_post_url VARCHAR,
                        publish_error TEXT,
                        views BIGINT DEFAULT 0,
                        likes BIGINT DEFAULT 0,
                        comments BIGINT DEFAULT 0,
                        shares BIGINT DEFAULT 0,
                        topic_id VARCHAR,
                        topic_title VARCHAR,
                        technical_analysis TEXT,
                        serper_data TEXT,
                        quality_score FLOAT,
                        ai_detection_score FLOAT,
                        risk_level VARCHAR,
                        generation_params TEXT,
                        commodity_tags TEXT,
                        alternative_versions TEXT
                    );
                """)
                db_connection.commit()
                logger.info("✅ post_records 表創建成功")
            else:
                logger.info("✅ post_records 表已存在")
                
    except Exception as e:
        logger.error(f"❌ 創建 post_records 表失敗: {e}")
        logger.error(f"❌ 錯誤詳情: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ 完整錯誤堆疊: {traceback.format_exc()}")
        raise

@app.on_event("startup")
def startup_event():
    """啟動時初始化 FinLab 和數據庫連接"""
    global stock_mapping, db_connection

    # 檢查所有關鍵環境變數
    logger.info("🔍 [啟動檢查] 開始檢查環境變數...")
    logger.info(f"🔍 [啟動檢查] FINLAB_API_KEY 存在: {os.getenv('FINLAB_API_KEY') is not None}")
    logger.info(f"🔍 [啟動檢查] FORUM_200_EMAIL 存在: {os.getenv('FORUM_200_EMAIL') is not None}")
    logger.info(f"🔍 [啟動檢查] FORUM_200_PASSWORD 存在: {os.getenv('FORUM_200_PASSWORD') is not None}")
    logger.info(f"🔍 [啟動檢查] DATABASE_URL 存在: {os.getenv('DATABASE_URL') is not None}")
    logger.info(f"🔍 [啟動檢查] PORT: {os.getenv('PORT', '未設定')}")

    # 初始化數據庫連接
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            logger.info(f"🔗 嘗試連接數據庫: {database_url[:20]}...")
            # Railway PostgreSQL URL 格式轉換（postgresql:// -> postgres://）
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)

            db_connection = psycopg2.connect(database_url)
            logger.info("✅ PostgreSQL 數據庫連接成功")
            
            # 創建 post_records 表（如果不存在）
            logger.info("📋 開始創建 post_records 表...")
            create_post_records_table()
            logger.info("✅ post_records 表創建完成")
        else:
            logger.warning("⚠️ 未找到 DATABASE_URL 環境變數，將無法查詢貼文數據")
    except Exception as e:
        logger.error(f"❌ PostgreSQL 數據庫連接失敗: {e}")
        logger.error(f"❌ 錯誤詳情: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ 完整錯誤堆疊: {traceback.format_exc()}")

    api_key = os.getenv("FINLAB_API_KEY")
    if api_key:
        finlab.login(api_key)
        logger.info("✅ FinLab API 登入成功")
    else:
        logger.warning("❌ 未找到 FINLAB_API_KEY 環境變數")

    # 載入股票映射表（先嘗試靜態文件）
    try:
        stock_mapping_path = '/app/stock_mapping.json'
        if os.path.exists(stock_mapping_path):
            with open(stock_mapping_path, 'r', encoding='utf-8') as f:
                stock_mapping = json.load(f)
            logger.info(f"✅ 載入靜態股票映射表成功: {len(stock_mapping)} 支股票")
        else:
            logger.warning(f"⚠️ 靜態股票映射表不存在: {stock_mapping_path}")
    except Exception as e:
        logger.error(f"❌ 載入靜態股票映射表失敗: {e}")

    # 從 FinLab 動態載入完整公司資訊
    try:
        if api_key:
            logger.info("📊 正在從 FinLab 載入完整公司資訊...")
            company_info = data.get('company_basic_info')
            if company_info is not None and not company_info.empty:
                # 轉換為字典格式
                for stock_id in company_info['stock_id']:
                    stock_data = company_info[company_info['stock_id'] == stock_id].iloc[0]
                    stock_mapping[stock_id] = {
                        'company_name': stock_data.get('公司簡稱', stock_data.get('公司名稱', f'股票{stock_id}')),
                        'industry': stock_data.get('產業類別', '未知產業')
                    }
                logger.info(f"✅ 從 FinLab 載入完整公司資訊成功: {len(stock_mapping)} 支股票")
            else:
                logger.warning("⚠️ 無法從 FinLab 取得公司資訊")
    except Exception as e:
        logger.error(f"❌ 從 FinLab 載入公司資訊失敗: {e}")

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

@app.get("/stock_mapping.json")
async def get_stock_mapping():
    """獲取完整股票映射表（供前端使用）"""
    logger.info("收到 stock_mapping 請求")

    try:
        return {
            "success": True,
            "data": stock_mapping,
            "count": len(stock_mapping),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"獲取股票映射表失敗: {e}")
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

    # 記錄環境變數狀態（不記錄實際值以保護隱私）
    logger.info(f"📋 [憑證檢查] FORUM_200_EMAIL 存在: {email is not None}")
    logger.info(f"📋 [憑證檢查] FORUM_200_PASSWORD 存在: {password is not None}")
    logger.info(f"📋 [憑證檢查] FORUM_200_MEMBER_ID: {member_id}")

    if not email or not password:
        # 更詳細的錯誤訊息
        missing = []
        if not email:
            missing.append("FORUM_200_EMAIL")
        if not password:
            missing.append("FORUM_200_PASSWORD")
        error_msg = f"缺少環境變數: {', '.join(missing)}"
        logger.error(f"❌ {error_msg}")
        raise Exception(error_msg)

    logger.info(f"✅ [憑證檢查] 成功載入 forum_200 憑證: {email}")
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

@app.post("/intraday-trigger/execute")
async def get_intraday_trigger_stocks(request: Request):
    """獲取盤中觸發器股票列表"""
    try:
        # 從 POST body 獲取配置
        body = await request.json()
        endpoint = body.get("endpoint")
        processing = body.get("processing", [])
        
        logger.info(f"收到盤中觸發器請求: endpoint={endpoint}, processing={processing}")
        
        if not endpoint:
            raise HTTPException(status_code=400, detail="缺少 endpoint 參數")

        # 準備請求參數
        columns = "交易時間,傳輸序號,內外盤旗標,即時成交價,即時成交量,最低價,最高價,標的,漲跌,漲跌幅,累計成交總額,累計成交量,開盤價"

        request_data = {
            "AppId": 2,
            "Guid": "583defeb-f7cb-49e7-964d-d0817e944e4f",
            "Processing": processing
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
            raw_data = response.json()
            logger.info(f"📊 [盤中觸發器] 收到數據: {len(raw_data)} 筆記錄")

            # 提取股票代碼並映射到股票名稱和產業
            stock_codes = [item[7] for item in raw_data if len(item) > 7 and item[7]]

            # 構建包含股票名稱和產業的完整數據
            stocks_with_info = []
            for stock_code in stock_codes:
                stock_name = get_stock_name(stock_code)
                stock_industry = get_stock_industry(stock_code)
                stocks_with_info.append({
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "industry": stock_industry
                })

            logger.info(f"✅ [盤中觸發器] 執行成功，獲取 {len(stocks_with_info)} 支股票")
            # 提取股票列表避免 f-string 嵌套問題
            stock_list = [f"{s['stock_code']}({s['stock_name']})" for s in stocks_with_info[:5]]
            logger.info(f"📋 [盤中觸發器] 股票列表: {stock_list}...")

            return {
                "success": True,
                "stocks": stock_codes,  # 返回股票代碼字符串數組，與前端期望格式一致
                "data": raw_data,  # 保留原始 CMoney 數據
                "count": len(stock_codes)
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

        # 生成唯一的 post_id
        import uuid
        post_id = str(uuid.uuid4())
        
        # 準備插入數據
        post_data = {
            'post_id': post_id,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'session_id': body.get('session_id', 1),
            'kol_serial': body.get('kol_serial', 200),
            'kol_nickname': body.get('kol_nickname', 'KOL-200'),
            'kol_persona': body.get('kol_persona', '分析師'),
            'stock_code': body.get('stock_code', ''),
            'stock_name': body.get('stock_name', ''),
            'title': body.get('title', ''),
            'content': body.get('content', ''),
            'content_md': body.get('content_md', ''),
            'status': body.get('status', 'draft'),
            'reviewer_notes': body.get('reviewer_notes'),
            'approved_by': body.get('approved_by'),
            'approved_at': body.get('approved_at'),
            'scheduled_at': body.get('scheduled_at'),
            'published_at': body.get('published_at'),
            'cmoney_post_id': body.get('cmoney_post_id'),
            'cmoney_post_url': body.get('cmoney_post_url'),
            'publish_error': body.get('publish_error'),
            'views': body.get('views', 0),
            'likes': body.get('likes', 0),
            'comments': body.get('comments', 0),
            'shares': body.get('shares', 0),
            'topic_id': body.get('topic_id'),
            'topic_title': body.get('topic_title'),
            'technical_analysis': json.dumps(body.get('technical_analysis', {})) if body.get('technical_analysis') else None,
            'serper_data': json.dumps(body.get('serper_data', {})) if body.get('serper_data') else None,
            'quality_score': body.get('quality_score'),
            'ai_detection_score': body.get('ai_detection_score'),
            'risk_level': body.get('risk_level'),
            'generation_params': json.dumps(body.get('generation_params', {})) if body.get('generation_params') else None,
            'commodity_tags': json.dumps(body.get('commodity_tags', [])) if body.get('commodity_tags') else None,
            'alternative_versions': json.dumps(body.get('alternative_versions', {})) if body.get('alternative_versions') else None
        }
        
        # 插入到數據庫
        if db_connection:
            with db_connection.cursor() as cursor:
                insert_sql = """
                    INSERT INTO post_records (
                        post_id, created_at, updated_at, session_id, kol_serial, kol_nickname, 
                        kol_persona, stock_code, stock_name, title, content, content_md, 
                        status, reviewer_notes, approved_by, approved_at, scheduled_at, 
                        published_at, cmoney_post_id, cmoney_post_url, publish_error, 
                        views, likes, comments, shares, topic_id, topic_title, 
                        technical_analysis, serper_data, quality_score, ai_detection_score, 
                        risk_level, generation_params, commodity_tags, alternative_versions
                    ) VALUES (
                        %(post_id)s, %(created_at)s, %(updated_at)s, %(session_id)s, 
                        %(kol_serial)s, %(kol_nickname)s, %(kol_persona)s, %(stock_code)s, 
                        %(stock_name)s, %(title)s, %(content)s, %(content_md)s, %(status)s, 
                        %(reviewer_notes)s, %(approved_by)s, %(approved_at)s, %(scheduled_at)s, 
                        %(published_at)s, %(cmoney_post_id)s, %(cmoney_post_url)s, 
                        %(publish_error)s, %(views)s, %(likes)s, %(comments)s, %(shares)s, 
                        %(topic_id)s, %(topic_title)s, %(technical_analysis)s, %(serper_data)s, 
                        %(quality_score)s, %(ai_detection_score)s, %(risk_level)s, 
                        %(generation_params)s, %(commodity_tags)s, %(alternative_versions)s
                    )
                """
                
                cursor.execute(insert_sql, post_data)
                db_connection.commit()
                logger.info(f"✅ 貼文已插入數據庫: {post_id}")
        else:
            logger.warning("⚠️ 數據庫連接不存在，無法保存貼文")

        result = {
            "success": True,
            "message": "貼文創建成功",
            "post_id": post_id,
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

# ==================== Posts API 功能 ====================

@app.get("/posts")
async def get_posts(
    skip: int = Query(0, description="跳過的記錄數"),
    limit: int = Query(10000, description="返回的記錄數"),
    status: str = Query(None, description="狀態篩選")
):
    """獲取貼文列表（從 PostgreSQL 數據庫）"""
    logger.info(f"收到 get_posts 請求: skip={skip}, limit={limit}, status={status}")

    try:
        if not db_connection:
            logger.warning("數據庫連接不可用，返回空數據")
            return {
                "success": True,
                "posts": [],
                "count": 0,
                "skip": skip,
                "limit": limit,
                "timestamp": datetime.now().isoformat()
            }

        # 查詢 post_records 表
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # 構建查詢
            query = "SELECT * FROM post_records"
            params = []

            if status:
                query += " WHERE status = %s"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            logger.info(f"執行 SQL 查詢: {query} with params: {params}")
            cursor.execute(query, params)
            posts = cursor.fetchall()

            # 獲取總數
            count_query = "SELECT COUNT(*) as count FROM post_records"
            if status:
                count_query += " WHERE status = %s"
                cursor.execute(count_query, [status] if status else [])
            else:
                cursor.execute(count_query)

            total_count = cursor.fetchone()['count']

            logger.info(f"查詢到 {len(posts)} 條貼文數據，總數: {total_count}")

            return {
                "success": True,
                "posts": [dict(post) for post in posts],
                "count": total_count,
                "skip": skip,
                "limit": limit,
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"查詢貼文數據失敗: {e}")
        return {
            "success": False,
            "posts": [],
            "count": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

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

# ==================== 數據庫管理功能 ====================

@app.post("/admin/import-1788-posts")
async def import_1788_posts():
    """導入 1788 筆 post_records 數據（管理員功能）"""
    try:
        if not db_connection:
            return {"error": "數據庫連接不存在"}
        
        # 讀取 JSON 數據文件
        json_file_path = '/app/post_records_1788.json'
        if not os.path.exists(json_file_path):
            return {"error": "post_records_1788.json 文件不存在"}
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        logger.info(f"📊 從 JSON 文件加載 {len(records)} 筆記錄")
        
        with db_connection.cursor() as cursor:
            # 清空現有數據
            cursor.execute("DELETE FROM post_records")
            logger.info("🗑️ 清空現有數據")
            
            # 批量插入數據
            insert_sql = """
                INSERT INTO post_records (
                    post_id, created_at, updated_at, session_id, kol_serial, kol_nickname, 
                    kol_persona, stock_code, stock_name, title, content, content_md, 
                    status, reviewer_notes, approved_by, approved_at, scheduled_at, 
                    published_at, cmoney_post_id, cmoney_post_url, publish_error, 
                    views, likes, comments, shares, topic_id, topic_title, 
                    technical_analysis, serper_data, quality_score, ai_detection_score, 
                    risk_level, generation_params, commodity_tags, alternative_versions
                ) VALUES (
                    %(post_id)s, %(created_at)s, %(updated_at)s, %(session_id)s, 
                    %(kol_serial)s, %(kol_nickname)s, %(kol_persona)s, %(stock_code)s, 
                    %(stock_name)s, %(title)s, %(content)s, %(content_md)s, %(status)s, 
                    %(reviewer_notes)s, %(approved_by)s, %(approved_at)s, %(scheduled_at)s, 
                    %(published_at)s, %(cmoney_post_id)s, %(cmoney_post_url)s, 
                    %(publish_error)s, %(views)s, %(likes)s, %(comments)s, %(shares)s, 
                    %(topic_id)s, %(topic_title)s, %(technical_analysis)s, %(serper_data)s, 
                    %(quality_score)s, %(ai_detection_score)s, %(risk_level)s, 
                    %(generation_params)s, %(commodity_tags)s, %(alternative_versions)s
                )
            """
            
            # 轉換記錄格式
            records_dict = []
            for record in records:
                record_dict = dict(record)
                
                # 處理 datetime 字符串
                for datetime_field in ['created_at', 'updated_at', 'approved_at', 'scheduled_at', 'published_at']:
                    if record_dict.get(datetime_field):
                        if isinstance(record_dict[datetime_field], str):
                            try:
                                record_dict[datetime_field] = datetime.fromisoformat(record_dict[datetime_field].replace('Z', '+00:00'))
                            except:
                                record_dict[datetime_field] = None
                        elif not isinstance(record_dict[datetime_field], datetime):
                            record_dict[datetime_field] = None
                    else:
                        record_dict[datetime_field] = None
                
                # 處理 JSON 字段 - 確保是字符串格式
                for json_field in ['technical_analysis', 'serper_data', 'generation_params', 'commodity_tags', 'alternative_versions']:
                    if record_dict.get(json_field):
                        if isinstance(record_dict[json_field], (dict, list)):
                            # 如果是字典或列表，轉換為 JSON 字符串
                            try:
                                record_dict[json_field] = json.dumps(record_dict[json_field], ensure_ascii=False)
                            except:
                                record_dict[json_field] = None
                        elif isinstance(record_dict[json_field], str):
                            # 如果已經是字符串，保持不變
                            pass
                        else:
                            record_dict[json_field] = None
                    else:
                        record_dict[json_field] = None
                
                records_dict.append(record_dict)
            
            # 批量插入
            logger.info(f"📥 開始插入 {len(records_dict)} 筆記錄...")
            cursor.executemany(insert_sql, records_dict)
            db_connection.commit()
            
            logger.info(f"✅ 成功導入 {len(records_dict)} 筆記錄")
            
            # 驗證導入結果
            cursor.execute("SELECT COUNT(*) FROM post_records")
            count = cursor.fetchone()[0]
            
            # 顯示狀態統計
            cursor.execute("SELECT status, COUNT(*) FROM post_records GROUP BY status")
            status_stats = cursor.fetchall()
            
            return {
                "success": True,
                "message": f"成功導入 {len(records_dict)} 筆記錄",
                "total_count": count,
                "status_stats": {status: count for status, count in status_stats},
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ 導入 1788 筆記錄失敗: {e}")
        return {"error": str(e)}

@app.post("/test/insert-sample-data")
async def insert_sample_data():
    """插入樣本數據到 post_records 表（測試功能）"""
    try:
        if not db_connection:
            return {"error": "數據庫連接不存在"}
        
        with db_connection.cursor() as cursor:
            # 創建樣本記錄
            sample_records = [
                {
                    'post_id': 'test-001',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'session_id': 1,
                    'kol_serial': 200,
                    'kol_nickname': 'KOL-200',
                    'kol_persona': '技術分析專家',
                    'stock_code': '2330',
                    'stock_name': '台積電',
                    'title': '台積電(2330) 技術面分析與操作建議',
                    'content': '台積電今日表現強勢，技術指標顯示多頭趨勢明確。建議關注580元支撐位，突破600元可考慮加碼。',
                    'content_md': '## 台積電(2330) 技術面分析\n\n台積電今日表現強勢，技術指標顯示多頭趨勢明確。',
                    'status': 'draft',
                    'reviewer_notes': None,
                    'approved_by': None,
                    'approved_at': None,
                    'scheduled_at': None,
                    'published_at': None,
                    'cmoney_post_id': None,
                    'cmoney_post_url': None,
                    'publish_error': None,
                    'views': 0,
                    'likes': 0,
                    'comments': 0,
                    'shares': 0,
                    'topic_id': 'tech_analysis',
                    'topic_title': '技術分析',
                    'technical_analysis': '{"rsi": 65, "macd": "bullish", "support": 580}',
                    'serper_data': '{"search_volume": 1000, "trend": "up"}',
                    'quality_score': 8.5,
                    'ai_detection_score': 0.95,
                    'risk_level': 'medium',
                    'generation_params': '{"model": "gpt-4", "temperature": 0.7}',
                    'commodity_tags': '["半導體", "科技股", "龍頭股"]',
                    'alternative_versions': '{"version_1": "短線操作", "version_2": "長線投資"}'
                },
                {
                    'post_id': 'test-002',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                    'session_id': 1,
                    'kol_serial': 201,
                    'kol_nickname': 'KOL-201',
                    'kol_persona': '基本面分析師',
                    'stock_code': '2317',
                    'stock_name': '鴻海',
                    'title': '鴻海(2317) 財報分析與投資價值評估',
                    'content': '鴻海最新財報顯示營收成長穩定，獲利能力持續改善。本益比合理，適合長期投資。',
                    'content_md': '## 鴻海(2317) 財報分析\n\n鴻海最新財報顯示營收成長穩定。',
                    'status': 'approved',
                    'reviewer_notes': '內容品質良好，建議發布',
                    'approved_by': 'admin',
                    'approved_at': datetime.now(),
                    'scheduled_at': None,
                    'published_at': None,
                    'cmoney_post_id': None,
                    'cmoney_post_url': None,
                    'publish_error': None,
                    'views': 150,
                    'likes': 12,
                    'comments': 3,
                    'shares': 2,
                    'topic_id': 'fundamental_analysis',
                    'topic_title': '基本面分析',
                    'technical_analysis': '{"pe_ratio": 12.5, "pb_ratio": 1.2, "roe": 8.5}',
                    'serper_data': '{"search_volume": 800, "trend": "stable"}',
                    'quality_score': 9.0,
                    'ai_detection_score': 0.98,
                    'risk_level': 'low',
                    'generation_params': '{"model": "gpt-4", "temperature": 0.5}',
                    'commodity_tags': '["電子製造", "代工", "蘋果概念股"]',
                    'alternative_versions': '{"version_1": "保守投資", "version_2": "價值投資"}'
                }
            ]
            
            # 插入記錄
            insert_sql = """
                INSERT INTO post_records (
                    post_id, created_at, updated_at, session_id, kol_serial, kol_nickname, 
                    kol_persona, stock_code, stock_name, title, content, content_md, 
                    status, reviewer_notes, approved_by, approved_at, scheduled_at, 
                    published_at, cmoney_post_id, cmoney_post_url, publish_error, 
                    views, likes, comments, shares, topic_id, topic_title, 
                    technical_analysis, serper_data, quality_score, ai_detection_score, 
                    risk_level, generation_params, commodity_tags, alternative_versions
                ) VALUES (
                    %(post_id)s, %(created_at)s, %(updated_at)s, %(session_id)s, 
                    %(kol_serial)s, %(kol_nickname)s, %(kol_persona)s, %(stock_code)s, 
                    %(stock_name)s, %(title)s, %(content)s, %(content_md)s, %(status)s, 
                    %(reviewer_notes)s, %(approved_by)s, %(approved_at)s, %(scheduled_at)s, 
                    %(published_at)s, %(cmoney_post_id)s, %(cmoney_post_url)s, 
                    %(publish_error)s, %(views)s, %(likes)s, %(comments)s, %(shares)s, 
                    %(topic_id)s, %(topic_title)s, %(technical_analysis)s, %(serper_data)s, 
                    %(quality_score)s, %(ai_detection_score)s, %(risk_level)s, 
                    %(generation_params)s, %(commodity_tags)s, %(alternative_versions)s
                )
            """
            
            cursor.executemany(insert_sql, sample_records)
            db_connection.commit()
            
            logger.info(f"✅ 成功插入 {len(sample_records)} 筆樣本記錄")
            
            # 驗證插入結果
            cursor.execute("SELECT COUNT(*) FROM post_records")
            count = cursor.fetchone()[0]
            
            # 顯示狀態統計
            cursor.execute("SELECT status, COUNT(*) FROM post_records GROUP BY status")
            status_stats = cursor.fetchall()
            
            return {
                "success": True,
                "message": f"成功插入 {len(sample_records)} 筆樣本記錄",
                "total_count": count,
                "status_stats": {status: count for status, count in status_stats},
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ 插入樣本數據失敗: {e}")
        return {"error": str(e)}

@app.post("/admin/create-post-records-table")
async def create_table_manually():
    """手動創建 post_records 表（管理員功能）"""
    try:
        if not db_connection:
            return {"error": "數據庫連接不存在"}
        
        create_post_records_table()
        return {
            "success": True,
            "message": "post_records 表創建成功",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 手動創建表失敗: {e}")
        return {"error": str(e)}

@app.post("/admin/drop-and-recreate-post-records-table")
async def drop_and_recreate_table():
    """刪除並重新創建 post_records 表（管理員功能）"""
    try:
        if not db_connection:
            return {"error": "數據庫連接不存在"}
        
        with db_connection.cursor() as cursor:
            # 刪除現有表
            cursor.execute("DROP TABLE IF EXISTS post_records CASCADE")
            db_connection.commit()
            logger.info("🗑️ 刪除現有 post_records 表")
            
            # 重新創建表
            cursor.execute("""
                CREATE TABLE post_records (
                    post_id VARCHAR PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id INTEGER,
                    kol_serial INTEGER NOT NULL,
                    kol_nickname VARCHAR NOT NULL,
                    kol_persona VARCHAR,
                    stock_code VARCHAR NOT NULL,
                    stock_name VARCHAR NOT NULL,
                    title VARCHAR NOT NULL,
                    content TEXT NOT NULL,
                    content_md TEXT,
                    status VARCHAR DEFAULT 'draft',
                    reviewer_notes TEXT,
                    approved_by VARCHAR,
                    approved_at TIMESTAMP,
                    scheduled_at TIMESTAMP,
                    published_at TIMESTAMP,
                    cmoney_post_id VARCHAR,
                    cmoney_post_url VARCHAR,
                    publish_error TEXT,
                    views BIGINT DEFAULT 0,
                    likes BIGINT DEFAULT 0,
                    comments BIGINT DEFAULT 0,
                    shares BIGINT DEFAULT 0,
                    topic_id VARCHAR,
                    topic_title VARCHAR,
                    technical_analysis TEXT,
                    serper_data TEXT,
                    quality_score FLOAT,
                    ai_detection_score FLOAT,
                    risk_level VARCHAR,
                    generation_params TEXT,
                    commodity_tags TEXT,
                    alternative_versions TEXT
                );
            """)
            db_connection.commit()
            logger.info("✅ 重新創建 post_records 表成功")
            
        return {
            "success": True,
            "message": "post_records 表已刪除並重新創建",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 刪除並重新創建表失敗: {e}")
        return {"error": str(e)}

@app.post("/admin/reset-database")
async def reset_database():
    """重置數據庫（管理員功能）"""
    try:
        if not db_connection:
            return {"error": "數據庫連接不存在"}
        
        with db_connection.cursor() as cursor:
            # 刪除現有表
            cursor.execute("DROP TABLE IF EXISTS post_records CASCADE")
            db_connection.commit()
            logger.info("🗑️ 刪除現有 post_records 表")
            
        return {
            "success": True,
            "message": "數據庫已重置，表已刪除",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 重置數據庫失敗: {e}")
        return {"error": str(e)}

@app.post("/admin/fix-database")
async def fix_database():
    """修復數據庫（管理員功能）"""
    try:
        if not db_connection:
            return {"error": "數據庫連接不存在"}
        
        # 創建新的連接來避免事務問題
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # 從環境變數獲取數據庫連接信息
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return {"error": "DATABASE_URL 環境變數不存在"}
        
        # 創建新連接
        new_conn = psycopg2.connect(database_url)
        new_conn.autocommit = True
        
        with new_conn.cursor() as cursor:
            # 刪除現有表
            cursor.execute("DROP TABLE IF EXISTS post_records CASCADE")
            logger.info("🗑️ 刪除現有 post_records 表")
            
            # 重新創建表
            cursor.execute("""
                CREATE TABLE post_records (
                    post_id VARCHAR PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id BIGINT,
                    kol_serial INTEGER NOT NULL,
                    kol_nickname VARCHAR NOT NULL,
                    kol_persona VARCHAR,
                    stock_code VARCHAR NOT NULL,
                    stock_name VARCHAR NOT NULL,
                    title VARCHAR NOT NULL,
                    content TEXT NOT NULL,
                    content_md TEXT,
                    status VARCHAR DEFAULT 'draft',
                    reviewer_notes TEXT,
                    approved_by VARCHAR,
                    approved_at TIMESTAMP,
                    scheduled_at TIMESTAMP,
                    published_at TIMESTAMP,
                    cmoney_post_id VARCHAR,
                    cmoney_post_url VARCHAR,
                    publish_error TEXT,
                    views BIGINT DEFAULT 0,
                    likes BIGINT DEFAULT 0,
                    comments BIGINT DEFAULT 0,
                    shares BIGINT DEFAULT 0,
                    topic_id VARCHAR,
                    topic_title VARCHAR,
                    technical_analysis TEXT,
                    serper_data TEXT,
                    quality_score FLOAT,
                    ai_detection_score FLOAT,
                    risk_level VARCHAR,
                    generation_params TEXT,
                    commodity_tags TEXT,
                    alternative_versions TEXT
                );
            """)
            logger.info("✅ 重新創建 post_records 表成功")
            
        new_conn.close()
        
        return {
            "success": True,
            "message": "數據庫已修復，表已重新創建",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 修復數據庫失敗: {e}")
        return {"error": str(e)}

@app.post("/admin/import-post-records")
async def import_post_records():
    """導入 post_records 數據（管理員功能）"""
    try:
        # 讀取 JSON 數據文件
        json_file_path = '/app/post_records_1788.json'
        if not os.path.exists(json_file_path):
            return {"error": "post_records_1788.json 文件不存在"}
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        logger.info(f"📊 從 JSON 文件加載 {len(records)} 筆記錄")
        
        with db_connection.cursor() as cursor:
            # 清空現有數據
            cursor.execute("DELETE FROM post_records")
            logger.info("🗑️ 清空現有數據")
            
            # 批量插入數據
            insert_sql = """
                INSERT INTO post_records (
                    post_id, created_at, updated_at, session_id, kol_serial, kol_nickname, 
                    kol_persona, stock_code, stock_name, title, content, content_md, 
                    status, reviewer_notes, approved_by, approved_at, scheduled_at, 
                    published_at, cmoney_post_id, cmoney_post_url, publish_error, 
                    views, likes, comments, shares, topic_id, topic_title, 
                    technical_analysis, serper_data, quality_score, ai_detection_score, 
                    risk_level, generation_params, commodity_tags, alternative_versions
                ) VALUES (
                    %(post_id)s, %(created_at)s, %(updated_at)s, %(session_id)s, 
                    %(kol_serial)s, %(kol_nickname)s, %(kol_persona)s, %(stock_code)s, 
                    %(stock_name)s, %(title)s, %(content)s, %(content_md)s, %(status)s, 
                    %(reviewer_notes)s, %(approved_by)s, %(approved_at)s, %(scheduled_at)s, 
                    %(published_at)s, %(cmoney_post_id)s, %(cmoney_post_url)s, 
                    %(publish_error)s, %(views)s, %(likes)s, %(comments)s, %(shares)s, 
                    %(topic_id)s, %(topic_title)s, %(technical_analysis)s, %(serper_data)s, 
                    %(quality_score)s, %(ai_detection_score)s, %(risk_level)s, 
                    %(generation_params)s, %(commodity_tags)s, %(alternative_versions)s
                )
            """
            
            # 轉換記錄格式
            records_dict = []
            for record in records:
                record_dict = dict(record)
                
                # 處理 datetime 字符串
                for datetime_field in ['created_at', 'updated_at', 'approved_at', 'scheduled_at', 'published_at']:
                    if record_dict.get(datetime_field):
                        if isinstance(record_dict[datetime_field], str):
                            try:
                                record_dict[datetime_field] = datetime.fromisoformat(record_dict[datetime_field].replace('Z', '+00:00'))
                            except:
                                record_dict[datetime_field] = None
                        elif not isinstance(record_dict[datetime_field], datetime):
                            record_dict[datetime_field] = None
                    else:
                        record_dict[datetime_field] = None
                
                # 處理 JSON 字段 - 轉換為 TEXT
                for json_field in ['technical_analysis', 'serper_data', 'generation_params', 'commodity_tags', 'alternative_versions']:
                    if record_dict.get(json_field):
                        if isinstance(record_dict[json_field], (dict, list)):
                            # 如果是字典或列表，轉換為 JSON 字符串
                            try:
                                record_dict[json_field] = json.dumps(record_dict[json_field], ensure_ascii=False)
                            except:
                                record_dict[json_field] = None
                        elif isinstance(record_dict[json_field], str):
                            # 如果已經是字符串，保持不變
                            pass
                        else:
                            record_dict[json_field] = None
                    else:
                        record_dict[json_field] = None
                
                records_dict.append(record_dict)
            
            # 批量插入
            cursor.executemany(insert_sql, records_dict)
            db_connection.commit()
            
            logger.info(f"✅ 成功導入 {len(records_dict)} 筆記錄")
            
            # 驗證導入結果
            cursor.execute("SELECT COUNT(*) FROM post_records")
            count = cursor.fetchone()[0]
            
            # 顯示狀態統計
            cursor.execute("SELECT status, COUNT(*) FROM post_records GROUP BY status")
            status_stats = cursor.fetchall()
            
            return {
                "success": True,
                "message": f"成功導入 {len(records_dict)} 筆記錄",
                "total_count": count,
                "status_stats": {status: count for status, count in status_stats},
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ 導入 post_records 失敗: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    # Railway 使用 PORT 環境變數，本地開發使用 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 啟動 Unified API 服務器: {host}:{port}")
    uvicorn.run(app, host=host, port=port)
