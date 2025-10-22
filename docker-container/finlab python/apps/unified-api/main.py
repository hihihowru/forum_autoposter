"""
統一的 API 服務 - 完整版本
Railway 部署時使用此服務作為唯一的 API 入口
整合所有微服務功能到一個 API

🔥 FORCE REBUILD: 2025-10-20-19:50 - Railway cache bust to deploy latest fixes

Recent Updates:
- 2025-10-20 19:50: FORCE REBUILD - Railway stuck on old cache (abd60928)
  * Log cleanup (2dff92db) - 65% verbosity reduction
  * API key strip (d1fa8165) - Fix trailing newline causing "Invalid header"
  * Stock info passing (3e22a469) - Fix generic fallback content
  * Fallback fix (f016e43d) - Stock names in templates
- 2025-10-20: Fixed posting-service imports with robust multi-strategy path resolution
- 2025-10-20: Enabled alternative_versions generation for ALL posting_types
- 2025-01-18: Fixed Railway healthcheck - added /health endpoint alongside /api/health
- 2025-01-18: Separated 6 intraday triggers into individual GET endpoints
- 2025-01-18: Standardized all API endpoints with /api prefix
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
import pytz
import traceback

# Timezone utility - Always use Taipei time (GMT+8)
def get_current_time():
    """Returns current time in Asia/Taipei timezone"""
    return datetime.now(pytz.timezone('Asia/Taipei'))

def convert_post_datetimes_to_taipei(post_dict):
    """
    Convert naive UTC datetime fields in post dictionary to Taipei timezone strings.
    Also parse JSON fields from TEXT to dict/list.

    This fixes the issue where database TIMESTAMP columns (without timezone) are returned
    as naive datetime objects, which get serialized as UTC but displayed incorrectly.

    Args:
        post_dict: Dictionary containing post data from database

    Returns:
        Dictionary with datetime fields converted to Taipei timezone ISO strings
        and JSON fields parsed from TEXT to dict/list
    """
    taipei_tz = pytz.timezone('Asia/Taipei')
    utc_tz = pytz.utc

    # Datetime fields that need conversion
    datetime_fields = ['created_at', 'updated_at', 'published_at', 'scheduled_time']

    result = dict(post_dict)

    # Convert datetime fields
    for field in datetime_fields:
        if field in result and result[field] is not None:
            dt = result[field]

            # If datetime is naive (no tzinfo), assume it's UTC
            if isinstance(dt, datetime) and dt.tzinfo is None:
                # Add UTC timezone
                dt_utc = utc_tz.localize(dt)
                # Convert to Taipei timezone
                dt_taipei = dt_utc.astimezone(taipei_tz)
                # Store as ISO format string
                result[field] = dt_taipei.isoformat()
            elif isinstance(dt, datetime):
                # Already has timezone info, just convert to Taipei
                dt_taipei = dt.astimezone(taipei_tz)
                result[field] = dt_taipei.isoformat()

    # 🔥 FIX: Parse JSON fields from TEXT to dict/list
    json_fields = ['technical_analysis', 'serper_data', 'generation_params', 'commodity_tags', 'alternative_versions']

    for field in json_fields:
        if field in result and result[field] is not None:
            if isinstance(result[field], str):
                try:
                    parsed = json.loads(result[field])
                    result[field] = parsed
                    # Removed excessive debug logging (was causing 500 logs/sec Railway limit)
                except Exception as e:
                    logger.error(f"❌ Failed to parse {field}: {e}")
                    result[field] = None

    # 🔥 FIX: Rename generation_params to generation_config for frontend compatibility
    if 'generation_params' in result:
        result['generation_config'] = result.pop('generation_params')
        # Removed excessive debug logging (was causing 500 logs/sec Railway limit)

    return result

def _get_sorting_label(stock_sorting: dict) -> str:
    """Generate display label for stock sorting"""
    if not stock_sorting or not stock_sorting.get('method') or stock_sorting.get('method') == 'none':
        return "隨機排序"

    method_labels = {
        'price_change_pct': '漲跌幅',
        'volume': '成交量',
        'five_day_return': '五日漲幅',
        'ten_day_return': '十日漲幅',
        'twenty_day_return': '二十日漲幅',
        'market_cap': '市值',
        'turnover_rate': '周轉率'
    }

    method = stock_sorting.get('method', 'none')
    direction = stock_sorting.get('direction', 'desc')

    label = method_labels.get(method, method)
    arrow = '↓' if direction == 'desc' else '↑'

    return f"{label}{arrow}"

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔇 Suppress verbose external library logging (saves ~10 lines per post)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("openai._base_client").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# 創建 FastAPI 應用
app = FastAPI(
    title="Forum Autoposter Unified API",
    description="統一的 API 服務，整合所有微服務功能。訪問 /docs 查看 Swagger UI 文檔",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
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
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# ==================== GPT 內容生成器初始化 ====================

# 添加 posting-service 到 Python 路徑
# 使用多種方式確保正確找到 posting-service 目錄
def setup_posting_service_path():
    """Setup posting-service path with multiple fallback strategies"""
    # Strategy 1: Relative to current file (local development)
    path1 = os.path.join(os.path.dirname(__file__), 'posting-service')

    # Strategy 2: Relative to current working directory
    path2 = os.path.join(os.getcwd(), 'posting-service')

    # Strategy 3: Absolute path (Docker WORKDIR)
    path3 = '/app/posting-service'

    for path in [path1, path2, path3]:
        if os.path.exists(path) and os.path.isdir(path):
            if path not in sys.path:
                sys.path.insert(0, path)
            logger.info(f"📁 posting-service 路徑已設置: {path}")
            return path

    logger.error(f"❌ 找不到 posting-service 目錄! 嘗試的路徑: {[path1, path2, path3]}")
    return None

posting_service_path = setup_posting_service_path()

# 導入 GPT 內容生成器
try:
    import openai
    from gpt_content_generator import GPTContentGenerator
    gpt_generator = GPTContentGenerator()
    logger.info("✅ GPT 內容生成器初始化成功")
except Exception as e:
    logger.warning(f"⚠️  GPT 內容生成器導入失敗: {e}，將使用模板生成")
    gpt_generator = None

# 導入個人化模組
try:
    from personalization_module import enhanced_personalization_processor
    logger.info("✅ 個人化模組初始化成功")
except Exception as e:
    logger.warning(f"⚠️  個人化模組導入失敗: {e}，將跳過個人化處理")
    enhanced_personalization_processor = None

stock_mapping = {}
db_pool = None  # Connection pool instead of single connection

def get_db_connection():
    """Get a connection from the pool"""
    if db_pool is None:
        raise Exception("Database pool not initialized")
    return db_pool.getconn()

def return_db_connection(conn):
    """Return a connection to the pool"""
    if db_pool and conn:
        db_pool.putconn(conn)

def create_post_records_table():
    """創建 post_records 表（如果不存在）"""
    conn = None
    try:
        if not db_pool:
            logger.error("❌ 數據庫連接池不存在，無法創建表")
            return

        conn = get_db_connection()

        with conn.cursor() as cursor:
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
                conn.commit()
                logger.info("✅ post_records 表創建成功")
            else:
                logger.info("✅ post_records 表已存在")

    except Exception as e:
        logger.error(f"❌ 創建 post_records 表失敗: {e}")
        logger.error(f"❌ 錯誤詳情: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ 完整錯誤堆疊: {traceback.format_exc()}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            return_db_connection(conn)

def create_schedule_tasks_table():
    """創建 schedule_tasks 表（如果不存在）"""
    conn = None
    try:
        if not db_pool:
            logger.error("❌ 數據庫連接池不存在，無法創建表")
            return

        conn = get_db_connection()

        with conn.cursor() as cursor:
            logger.info("🔍 檢查 schedule_tasks 表是否存在...")
            # 檢查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'schedule_tasks'
                );
            """)
            table_exists = cursor.fetchone()[0]
            logger.info(f"📊 表存在狀態: {table_exists}")

            if not table_exists:
                logger.info("📋 開始創建 schedule_tasks 表...")
                cursor.execute("""
                    CREATE TABLE schedule_tasks (
                        schedule_id VARCHAR PRIMARY KEY,
                        schedule_name VARCHAR NOT NULL,
                        schedule_description TEXT,
                        status VARCHAR DEFAULT 'active',
                        schedule_type VARCHAR NOT NULL,
                        interval_seconds INTEGER DEFAULT 300,
                        auto_posting BOOLEAN DEFAULT FALSE,
                        max_posts_per_hour INTEGER DEFAULT 2,
                        schedule_config TEXT,
                        trigger_config TEXT,
                        batch_info TEXT,
                        generation_config TEXT,
                        next_run TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        run_count INTEGER DEFAULT 0,
                        success_count INTEGER DEFAULT 0,
                        failure_count INTEGER DEFAULT 0,
                        success_rate FLOAT DEFAULT 0.0,
                        last_run TIMESTAMP,
                        last_error TEXT
                    );
                """)
                conn.commit()
                logger.info("✅ schedule_tasks 表創建成功")
            else:
                logger.info("✅ schedule_tasks 表已存在")

    except Exception as e:
        logger.error(f"❌ 創建 schedule_tasks 表失敗: {e}")
        logger.error(f"❌ 錯誤詳情: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ 完整錯誤堆疊: {traceback.format_exc()}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            return_db_connection(conn)

@app.on_event("startup")
def startup_event():
    """啟動時初始化 FinLab 和數據庫連接"""
    global stock_mapping, db_pool

    # 檢查所有關鍵環境變數
    logger.info("🔍 [啟動檢查] 開始檢查環境變數...")
    logger.info(f"🔍 [啟動檢查] FINLAB_API_KEY 存在: {os.getenv('FINLAB_API_KEY') is not None}")
    logger.info(f"🔍 [啟動檢查] FORUM_200_EMAIL 存在: {os.getenv('FORUM_200_EMAIL') is not None}")
    logger.info(f"🔍 [啟動檢查] FORUM_200_PASSWORD 存在: {os.getenv('FORUM_200_PASSWORD') is not None}")
    logger.info(f"🔍 [啟動檢查] DATABASE_URL 存在: {os.getenv('DATABASE_URL') is not None}")
    logger.info(f"🔍 [啟動檢查] PORT: {os.getenv('PORT', '未設定')}")

    # 初始化數據庫連接 - Don't crash startup if DB fails
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            logger.info(f"🔗 嘗試連接數據庫: {database_url[:20]}...")
            # Railway PostgreSQL URL 格式轉換（postgresql:// -> postgres:// for psycopg2）
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgres://", 1)

            # 添加連接參數以解決 Railway 連接問題
            import urllib.parse
            parsed_url = urllib.parse.urlparse(database_url)

            # 構建連接參數
            connect_kwargs = {
                'host': parsed_url.hostname,
                'port': parsed_url.port or 5432,
                'database': parsed_url.path[1:],  # 移除前導斜線
                'user': parsed_url.username,
                'password': parsed_url.password,
                'connect_timeout': 30,  # 30秒連接超時
                'sslmode': 'require',   # Railway 需要 SSL
                'keepalives_idle': 600, # 保持連接活躍
                'keepalives_interval': 30,
                'keepalives_count': 3
            }

            # Create connection pool (1-10 concurrent connections)
            # Use minconn=1 for faster startup
            logger.info(f"🔗 創建數據庫連接池...")
            db_pool = pool.SimpleConnectionPool(
                minconn=1,  # Minimum 1 connection (faster startup)
                maxconn=10,  # Maximum 10 concurrent connections
                **connect_kwargs
            )
            logger.info("✅ PostgreSQL 連接池創建成功 (1-10 connections)")

            # Don't test pool during startup - let first request validate
            logger.info("✅ 數據庫連接池初始化完成 (延遲測試到首次使用)")

            # Create tables using pool
            try:
                logger.info("📋 開始創建 post_records 表...")
                create_post_records_table()
                logger.info("✅ post_records 表創建完成")

                logger.info("📋 開始創建 schedule_tasks 表...")
                create_schedule_tasks_table()
                logger.info("✅ schedule_tasks 表創建完成")
            except Exception as table_error:
                logger.error(f"❌ 創建表失敗: {table_error}")
                # Don't fail startup if table creation fails
        else:
            logger.warning("⚠️ 未找到 DATABASE_URL 環境變數，將無法查詢貼文數據")
            db_pool = None
    except Exception as e:
        logger.error(f"❌ PostgreSQL 數據庫連接失敗: {e}")
        logger.error(f"❌ 錯誤詳情: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ 完整錯誤堆疊: {traceback.format_exc()}")
        db_pool = None  # Ensure pool is None on failure

    # FinLab API 登入 - Don't crash startup if FinLab login fails
    try:
        api_key = os.getenv("FINLAB_API_KEY")
        if api_key:
            logger.info("🔑 嘗試登入 FinLab API...")
            finlab.login(api_key)
            logger.info("✅ FinLab API 登入成功")
        else:
            logger.warning("⚠️ 未找到 FINLAB_API_KEY 環境變數")
    except Exception as e:
        logger.error(f"❌ FinLab API 登入失敗: {e}")
        logger.error(f"❌ 錯誤詳情: {type(e).__name__}: {str(e)}")
        # Don't crash - app can still serve other endpoints

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
        "timestamp": get_current_time().isoformat()
    }

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """健康檢查端點 - 支持 /health 和 /api/health 兩個路徑"""
    logger.info("收到健康檢查請求")

    # 檢查數據庫連接狀態
    db_status = "disconnected"
    if db_pool:
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            db_status = "connected"
        except Exception as e:
            logger.warning(f"數據庫健康檢查失敗: {e}")
            db_status = "error"
        finally:
            if conn:
                return_db_connection(conn)

    # 檢查 FinLab API 狀態
    finlab_status = "connected" if os.getenv("FINLAB_API_KEY") else "disconnected"

    return {
        "status": "healthy",
        "message": "Unified API is running successfully",
        "timestamp": get_current_time().isoformat(),
        "services": {
            "finlab": finlab_status,
            "database": db_status
        },
        "endpoints": {
            "total": 35,
            "working": 30 if db_status == "connected" else 24,
            "database_dependent": 11
        }
    }

@app.get("/api/debug/import-status")
async def debug_import_status():
    """Debug endpoint to expose module import status and errors"""
    import traceback

    result = {
        "timestamp": get_current_time().isoformat(),
        "python_version": sys.version,
        "sys_path": sys.path,
        "posting_service_path": os.path.join(os.path.dirname(__file__), 'posting-service'),
        "modules": {}
    }

    # Check if posting-service directory exists
    posting_service_dir = os.path.join(os.path.dirname(__file__), 'posting-service')
    result["posting_service_exists"] = os.path.exists(posting_service_dir)

    if os.path.exists(posting_service_dir):
        result["posting_service_files"] = os.listdir(posting_service_dir)

    # Check GPT generator
    result["modules"]["gpt_generator"] = {
        "imported": gpt_generator is not None,
        "instance": str(type(gpt_generator)) if gpt_generator else None
    }

    # Check personalization processor
    result["modules"]["personalization_processor"] = {
        "imported": enhanced_personalization_processor is not None,
        "instance": str(type(enhanced_personalization_processor)) if enhanced_personalization_processor else None
    }

    # Try importing modules individually to see exact errors
    errors = {}

    # Test openai import
    try:
        import openai as test_openai
        errors["openai"] = {"status": "success", "version": getattr(test_openai, '__version__', 'unknown')}
    except Exception as e:
        errors["openai"] = {"status": "failed", "error": str(e), "traceback": traceback.format_exc()}

    # Test gpt_content_generator import
    try:
        from gpt_content_generator import GPTContentGenerator as TestGPT
        errors["gpt_content_generator"] = {"status": "success"}
    except Exception as e:
        errors["gpt_content_generator"] = {"status": "failed", "error": str(e), "traceback": traceback.format_exc()}

    # Test kol_database_service import
    try:
        from kol_database_service import KOLProfile, KOLDatabaseService
        errors["kol_database_service"] = {"status": "success"}
    except Exception as e:
        errors["kol_database_service"] = {"status": "failed", "error": str(e), "traceback": traceback.format_exc()}

    # Test random_content_generator import
    try:
        from random_content_generator import RandomContentGenerator
        errors["random_content_generator"] = {"status": "success"}
    except Exception as e:
        errors["random_content_generator"] = {"status": "failed", "error": str(e), "traceback": traceback.format_exc()}

    # Test personalization_module import
    try:
        from personalization_module import enhanced_personalization_processor as test_processor
        errors["personalization_module"] = {"status": "success", "has_instance": test_processor is not None}
    except Exception as e:
        errors["personalization_module"] = {"status": "failed", "error": str(e), "traceback": traceback.format_exc()}

    result["import_tests"] = errors

    return result

@app.get("/api/debug/openai-config")
async def debug_openai_config():
    """Debug endpoint to check OpenAI API configuration"""
    import traceback

    result = {
        "timestamp": get_current_time().isoformat(),
        "environment": {
            "OPENAI_API_KEY_exists": os.getenv("OPENAI_API_KEY") is not None,
            "OPENAI_API_KEY_length": len(os.getenv("OPENAI_API_KEY", "")) if os.getenv("OPENAI_API_KEY") else 0,
            "OPENAI_API_KEY_prefix": os.getenv("OPENAI_API_KEY", "")[:10] + "..." if os.getenv("OPENAI_API_KEY") else None,
            "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "not set")
        },
        "gpt_generator": {
            "initialized": gpt_generator is not None,
            "has_api_key": gpt_generator.api_key is not None if gpt_generator else False,
            "api_key_length": len(gpt_generator.api_key) if gpt_generator and gpt_generator.api_key else 0,
            "model": gpt_generator.model if gpt_generator else None
        }
    }

    # Test OpenAI API connection
    if gpt_generator and gpt_generator.api_key:
        try:
            # Try a simple API call
            import openai
            openai.api_key = gpt_generator.api_key

            # Test with a minimal completion
            response = openai.chat.completions.create(
                model=gpt_generator.model,
                messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
                max_tokens=10
            )

            result["api_test"] = {
                "status": "success",
                "response": response.choices[0].message.content,
                "model_used": response.model
            }
        except Exception as e:
            result["api_test"] = {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()[:500]
            }
    else:
        result["api_test"] = {
            "status": "skipped",
            "reason": "No API key or GPT generator not initialized"
        }

    return result

@app.post("/api/database/migrate/add-schedule-columns")
async def migrate_add_schedule_columns():
    """
    Migration: Add trigger_config and schedule_config columns to schedule_tasks table
    This is a one-time migration endpoint
    """
    logger.info("收到數據庫遷移請求: add-schedule-columns")

    conn = None
    try:
        if not db_pool:
            return {
                "success": False,
                "error": "Database connection not available"
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if columns already exist
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'schedule_tasks'
                  AND column_name IN ('trigger_config', 'schedule_config')
            """)
            existing_columns = [row['column_name'] for row in cursor.fetchall()]

            if 'trigger_config' in existing_columns and 'schedule_config' in existing_columns:
                logger.info("✅ Columns already exist, no migration needed")
                return {
                    "success": True,
                    "message": "Columns already exist, no migration needed",
                    "existing_columns": existing_columns
                }

            logger.info(f"📝 Existing columns: {existing_columns}")
            logger.info("🔄 Adding missing columns...")

            # Add columns
            cursor.execute("""
                ALTER TABLE schedule_tasks
                ADD COLUMN IF NOT EXISTS trigger_config JSONB DEFAULT '{}',
                ADD COLUMN IF NOT EXISTS schedule_config JSONB DEFAULT '{}'
            """)

            conn.commit()
            logger.info("✅ Columns added successfully")

            # Verify columns were added
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'schedule_tasks'
                  AND column_name IN ('trigger_config', 'schedule_config')
            """)

            result = cursor.fetchall()
            logger.info(f"📊 Verification: {result}")

            return {
                "success": True,
                "message": "Migration completed successfully",
                "columns_added": [dict(row) for row in result]
            }

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        if conn:
            conn.rollback()
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.get("/api/database/test")
async def test_database():
    """測試數據庫連接並執行查詢"""
    logger.info("收到數據庫測試請求")

    result = {
        "connection_status": "disconnected",
        "test_query_success": False,
        "tables": [],
        "kol_count": 0,
        "post_count": 0,
        "schedule_count": 0,
        "errors": [],
        "timestamp": get_current_time().isoformat()
    }

    conn = None
    try:
        if not db_pool:
            result["errors"].append("Database pool not initialized")
            return result

        conn = get_db_connection()

        # Test 1: Basic connection test
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            result["connection_status"] = "connected"
            result["test_query_success"] = True
        except Exception as e:
            result["errors"].append(f"Connection test failed: {str(e)}")
            return result

        # Test 2: List all tables
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                result["tables"] = [table[0] for table in tables]
        except Exception as e:
            result["errors"].append(f"Failed to list tables: {str(e)}")

        # Test 3: Count records in key tables
        try:
            with conn.cursor() as cursor:
                # Count KOLs
                cursor.execute("SELECT COUNT(*) FROM kol_profiles")
                result["kol_count"] = cursor.fetchone()[0]

                # Count posts
                cursor.execute("SELECT COUNT(*) FROM post_records")
                result["post_count"] = cursor.fetchone()[0]

                # Count schedules
                cursor.execute("SELECT COUNT(*) FROM posting_schedules")
                result["schedule_count"] = cursor.fetchone()[0]
        except Exception as e:
            result["errors"].append(f"Failed to count records: {str(e)}")

        result["success"] = len(result["errors"]) == 0

    except Exception as e:
        result["errors"].append(f"Database test error: {str(e)}")
    finally:
        if conn:
            return_db_connection(conn)

    return result

@app.post("/api/database/migrate-trigger-type")
async def migrate_trigger_type():
    """
    Database Migration: Add trigger_type column to post_records table

    This endpoint should be called ONCE after deploying the trigger_type fix.
    It adds the missing trigger_type column to the post_records table.
    """
    logger.info("🔧 開始數據庫遷移: 添加 trigger_type 列")

    conn = None
    try:
        if not db_pool:
            return {
                "success": False,
                "error": "Database pool not initialized",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        conn.rollback()  # Clear any failed transactions

        with conn.cursor() as cursor:
            # Add trigger_type column if it doesn't exist
            cursor.execute("""
                ALTER TABLE post_records
                ADD COLUMN IF NOT EXISTS trigger_type VARCHAR(100);
            """)

            # Add generation_mode column if it doesn't exist
            cursor.execute("""
                ALTER TABLE post_records
                ADD COLUMN IF NOT EXISTS generation_mode VARCHAR(50) DEFAULT 'manual';
            """)

            conn.commit()

        logger.info("✅ 數據庫遷移成功: trigger_type 和 generation_mode 列已添加")
        return {
            "success": True,
            "message": "Migration successful: trigger_type and generation_mode columns added to post_records table",
            "timestamp": get_current_time().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 數據庫遷移失敗: {e}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/api/admin/reconnect-database")
async def reconnect_database():
    """重新連接數據庫（管理員功能）"""
    global db_connection
    logger.info("收到重新連接數據庫請求")
    
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return {
                "success": False,
                "error": "DATABASE_URL not found",
                "timestamp": get_current_time().isoformat()
            }
        
        # 關閉現有連接
        if db_pool:
            try:
                db_connection.close()
                logger.info("已關閉現有數據庫連接")
            except:
                pass
        
        # 重新連接
        import urllib.parse
        parsed_url = urllib.parse.urlparse(database_url)
        
        connect_kwargs = {
            'host': parsed_url.hostname,
            'port': parsed_url.port or 5432,
            'database': parsed_url.path[1:],
            'user': parsed_url.username,
            'password': parsed_url.password,
            'connect_timeout': 30,
            'sslmode': 'require',
            'keepalives_idle': 600,
            'keepalives_interval': 30,
            'keepalives_count': 3
        }
        
        db_connection = psycopg2.connect(**connect_kwargs)
        
        # 測試連接
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        logger.info("✅ 數據庫重新連接成功")
        
        return {
            "success": True,
            "message": "Database reconnected successfully",
            "timestamp": get_current_time().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 數據庫重新連接失敗: {e}")
        db_connection = None
        return {
            "success": False,
            "error": str(e),
            "timestamp": get_current_time().isoformat()
        }

# ==================== OHLC API 功能 ====================

@app.get("/api/after_hours_limit_up")
async def get_after_hours_limit_up_stocks(
    limit: int = Query(1000, description="股票數量限制"),
    changeThreshold: float = Query(9.5, description="漲跌幅閾值百分比"),
    industries: str = Query("", description="產業類別篩選"),
    sortBy: str = Query(None, description="排序方式: five_day_loss, five_day_gain, volume_desc, etc.")
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
            'timestamp': get_current_time().isoformat(),
            'date': latest_date.strftime('%Y-%m-%d'),
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'changeThreshold': changeThreshold
        }

    except Exception as e:
        logger.error(f"獲取盤後漲停股票失敗: {e}")
        return {"error": str(e)}

@app.get("/api/after_hours_limit_down")
async def get_after_hours_limit_down_stocks(
    limit: int = Query(1000, description="股票數量限制"),
    changeThreshold: float = Query(-9.5, description="跌幅閾值百分比"),
    industries: str = Query("", description="產業類別篩選"),
    sortBy: str = Query(None, description="排序方式: five_day_loss, five_day_gain, volume_desc, etc.")
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
            'timestamp': get_current_time().isoformat(),
            'date': latest_date.strftime('%Y-%m-%d'),
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'changeThreshold': changeThreshold
        }

    except Exception as e:
        logger.error(f"獲取盤後跌停股票失敗: {e}")
        return {"error": str(e)}

@app.get("/api/after_hours_volume_amount_high")
async def get_after_hours_volume_amount_high(
    limit: int = Query(50, description="返回的股票數量"),
    changeThreshold: float = Query(0.0, description="漲跌幅閾值（%）")
):
    """獲取盤後成交金額高的股票（成交金額絕對值排序，由大到小）"""
    logger.info(f"收到 get_after_hours_volume_amount_high 請求: limit={limit}, changeThreshold={changeThreshold}")

    try:
        ensure_finlab_login()

        # 獲取股票數據
        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')

        if close_df is None or close_df.empty:
            return {"error": "無法獲取股票數據"}

        close_df = close_df.sort_index()
        volume_df = volume_df.sort_index() if volume_df is not None else None
        
        latest_date = close_df.index[-1]
        previous_date = close_df.index[-2]
        
        latest_close = close_df.loc[latest_date]
        previous_close = close_df.loc[previous_date]
        
        latest_volume = None
        if volume_df is not None and latest_date in volume_df.index:
            latest_volume = volume_df.loc[latest_date]
        
        volume_amount_stocks = []
        
        for stock_id in latest_close.index:
            try:
                today_price = latest_close[stock_id]
                yesterday_price = previous_close[stock_id]
                
                if pd.isna(today_price) or pd.isna(yesterday_price):
                    continue
                
                change_percent = ((today_price - yesterday_price) / yesterday_price) * 100
                
                # 檢查漲跌幅閾值
                if abs(change_percent) < changeThreshold:
                    continue

                # 計算成交金額和成交量
                volume_amount = 0
                volume = 0
                if latest_volume is not None and stock_id in latest_volume.index:
                    vol = latest_volume[stock_id]
                    if not pd.isna(vol):
                        volume = int(vol)
                        volume_amount = volume * float(today_price)

                # 計算五日統計
                stats = calculate_trading_stats(stock_id, latest_date, close_df)

                volume_amount_stocks.append({
                    'stock_id': stock_id,
                    'stock_name': get_stock_name(stock_id),
                    'industry': get_stock_industry(stock_id),
                    'current_price': float(today_price),
                    'change_amount': float(today_price - yesterday_price),
                    'change_percent': float(change_percent),
                    'volume': volume,
                    'volume_amount': volume_amount,
                    'up_days_5': stats['up_days'],
                    'five_day_change': stats['five_day_change'],
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'previous_date': previous_date.strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                logger.warning(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue
        
        # 按成交金額排序（由大到小）
        volume_amount_stocks.sort(key=lambda x: x['volume_amount'], reverse=True)
        volume_amount_stocks = volume_amount_stocks[:limit]
        
        return {
            'success': True,
            'total_count': len(volume_amount_stocks),
            'stocks': volume_amount_stocks,
            'timestamp': get_current_time().isoformat(),
            'date': latest_date.strftime('%Y-%m-%d'),
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'sort_by': 'volume_amount_high'
        }
        
    except Exception as e:
        logger.error(f"獲取盤後成交金額高股票失敗: {e}")
        return {"error": str(e)}

@app.get("/api/after_hours_volume_amount_low")
async def get_after_hours_volume_amount_low(
    limit: int = Query(50, description="返回的股票數量"),
    changeThreshold: float = Query(0.0, description="漲跌幅閾值（%）")
):
    """獲取盤後成交金額低的股票（成交金額絕對值排序，由小到大）"""
    logger.info(f"收到 get_after_hours_volume_amount_low 請求: limit={limit}, changeThreshold={changeThreshold}")

    try:
        ensure_finlab_login()

        # 獲取股票數據
        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')

        if close_df is None or close_df.empty:
            return {"error": "無法獲取股票數據"}

        close_df = close_df.sort_index()
        volume_df = volume_df.sort_index() if volume_df is not None else None
        
        latest_date = close_df.index[-1]
        previous_date = close_df.index[-2]
        
        latest_close = close_df.loc[latest_date]
        previous_close = close_df.loc[previous_date]
        
        latest_volume = None
        if volume_df is not None and latest_date in volume_df.index:
            latest_volume = volume_df.loc[latest_date]
        
        volume_amount_stocks = []
        
        for stock_id in latest_close.index:
            try:
                today_price = latest_close[stock_id]
                yesterday_price = previous_close[stock_id]
                
                if pd.isna(today_price) or pd.isna(yesterday_price):
                    continue
                
                change_percent = ((today_price - yesterday_price) / yesterday_price) * 100
                
                # 檢查漲跌幅閾值
                if abs(change_percent) < changeThreshold:
                    continue

                # 計算成交金額和成交量
                volume_amount = 0
                volume = 0
                if latest_volume is not None and stock_id in latest_volume.index:
                    vol = latest_volume[stock_id]
                    if not pd.isna(vol):
                        volume = int(vol)
                        volume_amount = volume * float(today_price)

                # 計算五日統計
                stats = calculate_trading_stats(stock_id, latest_date, close_df)

                volume_amount_stocks.append({
                    'stock_id': stock_id,
                    'stock_name': get_stock_name(stock_id),
                    'industry': get_stock_industry(stock_id),
                    'current_price': float(today_price),
                    'change_amount': float(today_price - yesterday_price),
                    'change_percent': float(change_percent),
                    'volume': volume,
                    'volume_amount': volume_amount,
                    'up_days_5': stats['up_days'],
                    'five_day_change': stats['five_day_change'],
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'previous_date': previous_date.strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                logger.warning(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue
        
        # 按成交金額排序（由小到大）
        volume_amount_stocks.sort(key=lambda x: x['volume_amount'])
        volume_amount_stocks = volume_amount_stocks[:limit]
        
        return {
            'success': True,
            'total_count': len(volume_amount_stocks),
            'stocks': volume_amount_stocks,
            'timestamp': get_current_time().isoformat(),
            'date': latest_date.strftime('%Y-%m-%d'),
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'sort_by': 'volume_amount_low'
        }
        
    except Exception as e:
        logger.error(f"獲取盤後成交金額低股票失敗: {e}")
        return {"error": str(e)}

@app.get("/api/after_hours_volume_change_rate_high")
async def get_after_hours_volume_change_rate_high(
    limit: int = Query(50, description="返回的股票數量"),
    changeThreshold: float = Query(0.0, description="漲跌幅閾值（%）")
):
    """獲取盤後成交金額變化率高的股票（成交金額變化率排序，由大到小）"""
    logger.info(f"收到 get_after_hours_volume_change_rate_high 請求: limit={limit}, changeThreshold={changeThreshold}")

    try:
        ensure_finlab_login()

        # 獲取股票數據
        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')

        if close_df is None or close_df.empty:
            return {"error": "無法獲取股票數據"}

        close_df = close_df.sort_index()
        volume_df = volume_df.sort_index() if volume_df is not None else None
        
        latest_date = close_df.index[-1]
        previous_date = close_df.index[-2]
        day_before_date = close_df.index[-3]
        
        latest_close = close_df.loc[latest_date]
        previous_close = close_df.loc[previous_date]
        
        latest_volume = None
        previous_volume = None
        if volume_df is not None:
            if latest_date in volume_df.index:
                latest_volume = volume_df.loc[latest_date]
            if previous_date in volume_df.index:
                previous_volume = volume_df.loc[previous_date]
        
        volume_change_stocks = []
        
        for stock_id in latest_close.index:
            try:
                today_price = latest_close[stock_id]
                yesterday_price = previous_close[stock_id]
                
                if pd.isna(today_price) or pd.isna(yesterday_price):
                    continue
                
                change_percent = ((today_price - yesterday_price) / yesterday_price) * 100
                
                # 檢查漲跌幅閾值
                if abs(change_percent) < changeThreshold:
                    continue
                
                # 計算成交金額變化率
                today_volume_amount = 0
                yesterday_volume_amount = 0
                volume_change_rate = 0
                
                if latest_volume is not None and stock_id in latest_volume.index:
                    vol = latest_volume[stock_id]
                    if not pd.isna(vol):
                        today_volume_amount = int(vol) * float(today_price)
                
                if previous_volume is not None and stock_id in previous_volume.index:
                    vol = previous_volume[stock_id]
                    if not pd.isna(vol):
                        yesterday_volume_amount = int(vol) * float(yesterday_price)
                
                if yesterday_volume_amount > 0:
                    volume_change_rate = ((today_volume_amount - yesterday_volume_amount) / yesterday_volume_amount) * 100
                
                # 計算五日統計
                stats = calculate_trading_stats(stock_id, latest_date, close_df)

                # 計算成交量
                today_volume = 0
                if latest_volume is not None and stock_id in latest_volume.index and not pd.isna(latest_volume[stock_id]):
                    today_volume = int(latest_volume[stock_id])

                volume_change_stocks.append({
                    'stock_id': stock_id,
                    'stock_name': get_stock_name(stock_id),
                    'industry': get_stock_industry(stock_id),
                    'current_price': float(today_price),
                    'change_amount': float(today_price - yesterday_price),
                    'change_percent': float(change_percent),
                    'volume': today_volume,
                    'volume_amount': today_volume_amount,
                    'volume_change_rate': float(volume_change_rate),
                    'up_days_5': stats['up_days'],
                    'five_day_change': stats['five_day_change'],
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'previous_date': previous_date.strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                logger.warning(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue
        
        # 按成交金額變化率排序（由大到小）
        volume_change_stocks.sort(key=lambda x: x['volume_change_rate'], reverse=True)
        volume_change_stocks = volume_change_stocks[:limit]
        
        return {
            'success': True,
            'total_count': len(volume_change_stocks),
            'stocks': volume_change_stocks,
            'timestamp': get_current_time().isoformat(),
            'date': latest_date.strftime('%Y-%m-%d'),
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'sort_by': 'volume_change_rate_high'
        }
        
    except Exception as e:
        logger.error(f"獲取盤後成交金額變化率高股票失敗: {e}")
        return {"error": str(e)}

@app.get("/api/after_hours_volume_change_rate_low")
async def get_after_hours_volume_change_rate_low(
    limit: int = Query(50, description="返回的股票數量"),
    changeThreshold: float = Query(0.0, description="漲跌幅閾值（%）")
):
    """獲取盤後成交金額變化率低的股票（成交金額變化率排序，由小到大）"""
    logger.info(f"收到 get_after_hours_volume_change_rate_low 請求: limit={limit}, changeThreshold={changeThreshold}")

    try:
        ensure_finlab_login()

        # 獲取股票數據
        close_df = data.get('price:收盤價')
        volume_df = data.get('price:成交股數')

        if close_df is None or close_df.empty:
            return {"error": "無法獲取股票數據"}

        close_df = close_df.sort_index()
        volume_df = volume_df.sort_index() if volume_df is not None else None
        
        latest_date = close_df.index[-1]
        previous_date = close_df.index[-2]
        day_before_date = close_df.index[-3]
        
        latest_close = close_df.loc[latest_date]
        previous_close = close_df.loc[previous_date]
        
        latest_volume = None
        previous_volume = None
        if volume_df is not None:
            if latest_date in volume_df.index:
                latest_volume = volume_df.loc[latest_date]
            if previous_date in volume_df.index:
                previous_volume = volume_df.loc[previous_date]
        
        volume_change_stocks = []
        
        for stock_id in latest_close.index:
            try:
                today_price = latest_close[stock_id]
                yesterday_price = previous_close[stock_id]
                
                if pd.isna(today_price) or pd.isna(yesterday_price):
                    continue
                
                change_percent = ((today_price - yesterday_price) / yesterday_price) * 100
                
                # 檢查漲跌幅閾值
                if abs(change_percent) < changeThreshold:
                    continue
                
                # 計算成交金額變化率
                today_volume_amount = 0
                yesterday_volume_amount = 0
                volume_change_rate = 0
                
                if latest_volume is not None and stock_id in latest_volume.index:
                    vol = latest_volume[stock_id]
                    if not pd.isna(vol):
                        today_volume_amount = int(vol) * float(today_price)
                
                if previous_volume is not None and stock_id in previous_volume.index:
                    vol = previous_volume[stock_id]
                    if not pd.isna(vol):
                        yesterday_volume_amount = int(vol) * float(yesterday_price)
                
                if yesterday_volume_amount > 0:
                    volume_change_rate = ((today_volume_amount - yesterday_volume_amount) / yesterday_volume_amount) * 100
                
                # 計算五日統計
                stats = calculate_trading_stats(stock_id, latest_date, close_df)

                # 計算成交量
                today_volume = 0
                if latest_volume is not None and stock_id in latest_volume.index and not pd.isna(latest_volume[stock_id]):
                    today_volume = int(latest_volume[stock_id])

                volume_change_stocks.append({
                    'stock_id': stock_id,
                    'stock_name': get_stock_name(stock_id),
                    'industry': get_stock_industry(stock_id),
                    'current_price': float(today_price),
                    'change_amount': float(today_price - yesterday_price),
                    'change_percent': float(change_percent),
                    'volume': today_volume,
                    'volume_amount': today_volume_amount,
                    'volume_change_rate': float(volume_change_rate),
                    'up_days_5': stats['up_days'],
                    'five_day_change': stats['five_day_change'],
                    'date': latest_date.strftime('%Y-%m-%d'),
                    'previous_date': previous_date.strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                logger.warning(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue
        
        # 按成交金額變化率排序（由小到大）
        volume_change_stocks.sort(key=lambda x: x['volume_change_rate'])
        volume_change_stocks = volume_change_stocks[:limit]
        
        return {
            'success': True,
            'total_count': len(volume_change_stocks),
            'stocks': volume_change_stocks,
            'timestamp': get_current_time().isoformat(),
            'date': latest_date.strftime('%Y-%m-%d'),
            'previous_date': previous_date.strftime('%Y-%m-%d'),
            'sort_by': 'volume_change_rate_low'
        }
        
    except Exception as e:
        logger.error(f"獲取盤後成交金額變化率低股票失敗: {e}")
        return {"error": str(e)}

@app.get("/api/stock_mapping.json")
async def get_stock_mapping():
    """獲取完整股票映射表（供前端使用）"""
    logger.info("收到 stock_mapping 請求")

    try:
        return {
            "success": True,
            "data": stock_mapping,
            "count": len(stock_mapping),
            "timestamp": get_current_time().isoformat()
        }
    except Exception as e:
        logger.error(f"獲取股票映射表失敗: {e}")
        return {"error": str(e)}

@app.get("/api/industries")
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
            "timestamp": get_current_time().isoformat()
        }

        logger.info(f"返回 industries 數據: {len(result['data'])} 條記錄")
        return result
    except Exception as e:
        logger.error(f"獲取產業類別失敗: {e}")
        return {"error": str(e)}

@app.get("/api/stocks_by_industry")
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
            "timestamp": get_current_time().isoformat()
        }

        logger.info(f"返回 {industry} 產業股票: {len(result['data'])} 支")
        return result
    except Exception as e:
        logger.error(f"獲取產業股票失敗: {e}")
        return {"error": str(e)}

@app.get("/api/get_ohlc")
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
        # Check token cache validity
        if _token_cache["token"] and _token_cache["expires_at"]:
            current_time = get_current_time()
            expires_at = _token_cache["expires_at"]

            # Handle timezone-naive datetime from cmoney_client
            if expires_at.tzinfo is None:
                # Assume naive datetime is in local timezone (Taipei)
                taipei_tz = pytz.timezone('Asia/Taipei')
                expires_at = taipei_tz.localize(expires_at)

            if current_time < expires_at:
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
        _token_cache["created_at"] = get_current_time()

        logger.info(f"✅ forum_200 登入成功，token 有效期至: {login_result.expires_at}")
        return login_result.token

    except Exception as e:
        logger.error(f"❌ 動態取得 CMoney API token 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"認證失敗: {str(e)}")

@app.post("/api/intraday-trigger/execute")
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

# Helper function for intraday triggers
async def execute_cmoney_intraday_trigger(processing: list, trigger_name: str):
    """執行 CMoney 盤中觸發器的通用函數"""
    try:
        endpoint = "https://asterisk-chipsapi.cmoney.tw/AdditionInformationRevisit/api/GetAll/StockCalculation"
        columns = "交易時間,傳輸序號,內外盤旗標,即時成交價,即時成交量,最低價,最高價,標的,漲跌,漲跌幅,累計成交總額,累計成交量,開盤價"

        request_data = {
            "AppId": 2,
            "Guid": "583defeb-f7cb-49e7-964d-d0817e944e4f",
            "Processing": processing
        }

        # 動態取得認證 token
        auth_token = await get_dynamic_auth_token()

        headers = {
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}",
            "cmoneyapi-trace-context": '{"appVersion":"10.111.0","osName":"iOS","platform":1,"manufacturer":"Apple","osVersion":"18.6.2","appId":2,"model":"iPhone15,2"}'
        }

        # 發送請求到 CMoney API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{endpoint}?columns={columns}",
                json=request_data,
                headers=headers
            )

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"CMoney API 請求失敗: {response.status_code}")

            raw_data = response.json()
            # CMoney API columns: 交易時間,傳輸序號,內外盤旗標,即時成交價,即時成交量,最低價,最高價,標的,漲跌,漲跌幅,累計成交總額,累計成交量,開盤價
            # Index mapping: 0=交易時間, 1=傳輸序號, 2=內外盤旗標, 3=即時成交價, 4=即時成交量, 5=最低價, 6=最高價, 7=標的, 8=漲跌, 9=漲跌幅, 10=累計成交總額, 11=累計成交量, 12=開盤價

            stocks_with_info = []
            for item in raw_data:
                if len(item) >= 13 and item[7]:  # Ensure we have all fields
                    stock_code = item[7]

                    # Calculate 5-day trading statistics
                    # Note: Historical data not available in intraday context, using defaults
                    stats = {"up_days": 0, "five_day_change": 0.0}

                    stocks_with_info.append({
                        "stock_code": stock_code,
                        "stock_name": get_stock_name(stock_code),
                        "industry": get_stock_industry(stock_code),
                        "current_price": float(item[3]) if item[3] else 0.0,  # 即時成交價
                        "open_price": float(item[12]) if item[12] else 0.0,  # 開盤價
                        "high_price": float(item[6]) if item[6] else 0.0,  # 最高價
                        "low_price": float(item[5]) if item[5] else 0.0,  # 最低價
                        "change_amount": float(item[8]) if item[8] else 0.0,  # 漲跌
                        "change_percent": float(item[9]) if item[9] else 0.0,  # 漲跌幅
                        "volume": int(item[11]) if item[11] else 0,  # 累計成交量
                        "volume_amount": float(item[10]) if item[10] else 0.0,  # 累計成交總額
                        "trade_time": item[0] if item[0] else "",  # 交易時間
                        # Add 5-day statistics
                        "up_days_5": stats['up_days'],  # 五日上漲天數
                        "five_day_change": stats['five_day_change']  # 五日漲跌幅
                    })

            logger.info(f"✅ [{trigger_name}] 獲取 {len(stocks_with_info)} 支股票")

            return {
                "success": True,
                "total_count": len(stocks_with_info),
                "stocks": stocks_with_info,
                "timestamp": get_current_time().isoformat(),
                "trigger_type": trigger_name
            }

    except Exception as e:
        logger.error(f"❌ [{trigger_name}] 執行失敗: {e}")
        raise HTTPException(status_code=500, detail=f"{trigger_name} 執行失敗: {str(e)}")

# 6 個獨立的盤中觸發器端點

@app.get("/api/intraday/gainers-by-amount")
async def get_intraday_gainers_by_amount(limit: int = Query(20, description="返回股票數量")):
    """
    盤中觸發器：漲幅排序+成交額

    按成交額排序，篩選出漲幅最大的股票（未漲停）
    適用場景：找出當日強勢上漲且成交活躍的股票
    """
    processing = [
        {"ParameterJson":"{ \"TargetPropertyNamePath\" : [ \"TotalTransactionAmount\"]}","ProcessType":"DescOrder"},
        {"ProcessType":"EqualValueFilter","ParameterJson":"{\"TargetPropertyNamePath\": [\"Commodity\", \"IsChipsKPopularStocksSortSubject\"], \"Value\": true}"},
        {"ProcessType":"LessThanColumnsFilter","ParameterJson":"{\"TargetPropertyNamePath\": [\"StrikePrice\"], \"ComparePropertyNamePath\": [\"Commodity\" , \"LimitUp\"]}"},
        {"ProcessType":"MoreThanValueFilter","ParameterJson":"{\"TargetPropertyNamePath\": [\"ChangeRange\"], \"Value\": 0 }"},
        {"ParameterJson":"{\"TargetPropertyNamePath\": [\"ChangeRange\"]}","ProcessType":"DescOrder"},
        {"ProcessType":"ThenDescOrder","ParameterJson":"{\"TargetPropertyNamePath\": [\"TotalVolume\"]}"},
        {"ParameterJson":"{\"TargetPropertyNamePath\": [\"CommKey\"]}","ProcessType":"ThenAscOrder"},
        {"ProcessType":"TakeCount","ParameterJson":f"{{\"Count\":{limit}}}"}
    ]
    return await execute_cmoney_intraday_trigger(processing, "漲幅排序+成交額")

@app.get("/api/intraday/volume-leaders")
async def get_intraday_volume_leaders(limit: int = Query(20, description="返回股票數量")):
    """
    盤中觸發器：成交量排序

    按成交量排序，找出當日成交量最大的熱門股票
    適用場景：找出市場關注度最高、交易最活躍的股票
    """
    processing = [
        {"ProcessType":"EqualValueFilter","ParameterJson":"{\"TargetPropertyNamePath\": [\"Commodity\", \"IsChipsKPopularStocksSortSubject\"], \"Value\": true}"},
        {"ProcessType":"DescOrder","ParameterJson":"{\"TargetPropertyNamePath\" :[\"TotalVolume\"]}"},
        {"ProcessType":"ThenDescOrder","ParameterJson":"{\"TargetPropertyNamePath\" :[\"ChangeRange\"]}"},
        {"ParameterJson":"{\"TargetPropertyNamePath\" :[\"CommKey\"]}","ProcessType":"ThenAscOrder"},
        {"ParameterJson":f"{{\"Count\":{limit}}}","ProcessType":"TakeCount"}
    ]
    return await execute_cmoney_intraday_trigger(processing, "成交量排序")

@app.get("/api/intraday/amount-leaders")
async def get_intraday_amount_leaders(limit: int = Query(20, description="返回股票數量")):
    """
    盤中觸發器：成交額排序

    按成交額排序，找出當日成交金額最大的股票
    適用場景：找出資金流入最多、大戶關注的股票
    """
    processing = [
        {"ProcessType":"EqualValueFilter","ParameterJson":"{\"TargetPropertyNamePath\":[\"Commodity\", \"IsChipsKPopularStocksSortSubject\"], \"Value\": true}"},
        {"ProcessType":"DescOrder","ParameterJson":"{\"TargetPropertyNamePath\":[\"TotalTransactionAmount\"]}"},
        {"ParameterJson":"{\"TargetPropertyNamePath\":[\"TotalVolume\" ]}","ProcessType":"ThenDescOrder"},
        {"ProcessType":"ThenDescOrder","ParameterJson":"{\"TargetPropertyNamePath\":[\"ChangeRange\"]}"},
        {"ProcessType":"TakeCount","ParameterJson":f"{{\"Count\":{limit}}}"}
    ]
    return await execute_cmoney_intraday_trigger(processing, "成交額排序")

@app.get("/api/intraday/limit-down")
async def get_intraday_limit_down(limit: int = Query(20, description="返回股票數量")):
    """
    盤中觸發器：跌停篩選

    篩選當日跌停的股票
    適用場景：找出當日表現最弱勢的股票
    """
    processing = [
        {"ProcessType":"EqualValueFilter","ParameterJson":"{\"TargetPropertyNamePath\": [\"Commodity\", \"IsChipsKPopularStocksSortSubject\"], \"Value\": true}"},
        {"ParameterJson":"{\"TargetPropertyNamePath\": [\"StrikePrice\"], \"ComparePropertyNamePath\": [\"Commodity\", \"LimitDown\"]}","ProcessType":"EqualColumnsFilter"},
        {"ProcessType":"AscOrder","ParameterJson":"{\"TargetPropertyNamePath\":[\"ChangeRange\"]}"},
        {"ProcessType":"ThenDescOrder","ParameterJson":"{\"TargetPropertyNamePath\":[\"TotalVolume\"]}"},
        {"ParameterJson":f"{{\"Count\":{limit}}}","ProcessType":"TakeCount"}
    ]
    return await execute_cmoney_intraday_trigger(processing, "跌停篩選")

@app.get("/api/intraday/limit-up")
async def get_intraday_limit_up(limit: int = Query(20, description="返回股票數量")):
    """
    盤中觸發器：漲停篩選

    篩選當日漲停的股票
    適用場景：找出當日表現最強勢的股票
    """
    processing = [
        {"ParameterJson":"{\"TargetPropertyNamePath\": [\"Commodity\", \"IsChipsKPopularStocksSortSubject\"], \"Value\": true}","ProcessType":"EqualValueFilter"},
        {"ProcessType":"EqualColumnsFilter","ParameterJson":"{\"TargetPropertyNamePath\": [\"StrikePrice\"], \"ComparePropertyNamePath\": [\"Commodity\", \"LimitUp\"]}"},
        {"ProcessType":"DescOrder","ParameterJson":"{\"TargetPropertyNamePath\": [\"ChangeRange\"]}"},
        {"ParameterJson":"{\"TargetPropertyNamePath\": [\"TotalVolume\"]}","ProcessType":"ThenDescOrder"},
        {"ProcessType":"TakeCount","ParameterJson":f"{{\"Count\":{limit}}}"}
    ]
    return await execute_cmoney_intraday_trigger(processing, "漲停篩選")

@app.get("/api/intraday/limit-down-by-amount")
async def get_intraday_limit_down_by_amount(limit: int = Query(20, description="返回股票數量")):
    """
    盤中觸發器：跌停篩選+成交額

    按成交額排序，篩選出跌幅大且成交活躍的股票（接近跌停）
    適用場景：找出當日弱勢下跌且賣壓大的股票
    """
    processing = [
        {"ParameterJson":"{ \"TargetPropertyNamePath\" : [ \"TotalTransactionAmount\"]}","ProcessType":"DescOrder"},
        {"ParameterJson":"{\"TargetPropertyNamePath\":[\"Commodity\", \"IsChipsKPopularStocksSortSubject\" ], \"Value\": true}","ProcessType":"EqualValueFilter"},
        {"ParameterJson":"{\"TargetPropertyNamePath\": [\"StrikePrice\"], \"ComparePropertyNamePath\": [\"Commodity\", \"LimitDown\"]}","ProcessType":"MoreThanColumnsFilter"},
        {"ProcessType":"LessThanValueFilter","ParameterJson":"{\"TargetPropertyNamePath\": [\"ChangeRange\"], \"Value\": 0 }"},
        {"ParameterJson":"{\"TargetPropertyNamePath\": [\"ChangeRange\"]}","ProcessType":"AscOrder"},
        {"ProcessType":"ThenDescOrder","ParameterJson":"{\"TargetPropertyNamePath\": [\"TotalVolume\"]}"},
        {"ProcessType":"ThenAscOrder","ParameterJson":"{\"TargetPropertyNamePath\": [\"CommKey\"]}"},
        {"ParameterJson":f"{{\"Count\":{limit}}}","ProcessType":"TakeCount"}
    ]
    return await execute_cmoney_intraday_trigger(processing, "跌停篩選+成交額")

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
            'created_at': get_current_time(),
            'updated_at': get_current_time(),
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
        if db_pool:
            with conn.cursor() as cursor:
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
                conn.commit()
                logger.info(f"✅ 貼文已插入數據庫: {post_id}")
        else:
            logger.warning("⚠️ 數據庫連接不存在，無法保存貼文")

        result = {
            "success": True,
            "message": "貼文創建成功",
            "post_id": post_id,
            "data": body,
            "timestamp": get_current_time().isoformat()
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
                "timestamp": get_current_time().isoformat()
            }
        )

@app.post("/api/manual-posting")
async def manual_posting(request: Request):
    """手動貼文 - 生成內容並寫入數據庫"""
    logger.info("收到 manual_posting 請求")

    conn = None
    try:
        body = await request.json()
        logger.info(f"手動貼文參數: stock_code={body.get('stock_code')}, kol_serial={body.get('kol_serial')}, session_id={body.get('session_id')}")

        # 提取參數
        stock_code = body.get('stock_code', '')
        stock_name = body.get('stock_name', stock_code)
        kol_serial = int(body.get('kol_serial', 200))
        kol_persona = body.get('kol_persona', 'technical')
        session_id = body.get('session_id')
        trigger_type = body.get('trigger_type', 'custom_stocks')
        generation_mode = body.get('generation_mode', 'manual')  # 🔥 NEW: Extract generation_mode (manual/scheduled/self_learning)
        posting_type = body.get('posting_type', 'analysis')
        max_words = body.get('max_words', 200)

        # 🔥 HOTFIX: Cap max_words for personalized type to prevent 502 timeouts
        if posting_type == 'personalized' and max_words > 200:
            logger.warning(f"⚠️  Personalized type max_words capped: {max_words} → 200 (prevent timeout)")
            max_words = 200

        # 🔥 新增：模型 ID 選擇邏輯
        model_id_override = body.get('model_id_override')  # 批量覆蓋模型
        use_kol_default_model = body.get('use_kol_default_model', True)  # 預設使用 KOL 模型

        # 確定使用的模型
        chosen_model_id = None

        # 優先級 1: 批量覆蓋模型（如果設定且不使用 KOL 預設）
        if not use_kol_default_model and model_id_override:
            chosen_model_id = model_id_override
            logger.info(f"🤖 使用批量覆蓋模型: {chosen_model_id}")
        else:
            # 優先級 2: 從數據庫獲取 KOL 的預設模型
            try:
                conn = await asyncpg.connect(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    database=DB_CONFIG['database'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password']
                )
                kol_model_id = await conn.fetchval(
                    "SELECT model_id FROM kol_profiles WHERE serial = $1",
                    str(kol_serial)
                )
                await conn.close()

                if kol_model_id:
                    chosen_model_id = kol_model_id
                    logger.info(f"🤖 使用 KOL 預設模型: {chosen_model_id} (KOL serial: {kol_serial})")
                else:
                    # 優先級 3: 備用預設模型
                    chosen_model_id = "gpt-4o-mini"
                    logger.info(f"🤖 KOL 未設定模型，使用預設: {chosen_model_id}")
            except Exception as db_error:
                logger.warning(f"⚠️  無法獲取 KOL 模型設定: {db_error}，使用預設模型")
                chosen_model_id = "gpt-4o-mini"

        # 使用 GPT 生成內容
        if gpt_generator:
            logger.info(f"使用 GPT 生成器生成內容: stock_code={stock_code}, kol_persona={kol_persona}, model={chosen_model_id}")
            try:
                gpt_result = gpt_generator.generate_stock_analysis(
                    stock_id=stock_code,
                    stock_name=stock_name,
                    kol_persona=kol_persona,
                    serper_analysis={},  # 可選：可接入 Serper API 獲取新聞
                    data_sources=[],
                    content_length="medium",
                    max_words=max_words,
                    model=chosen_model_id  # 🔥 傳遞選定的模型
                )
                title = gpt_result.get('title', f"{stock_name}({stock_code}) 分析")
                content = gpt_result.get('content', '')
                logger.info(f"✅ GPT 內容生成成功: title={title[:30]}...")
            except Exception as gpt_error:
                logger.error(f"❌ GPT 生成失敗，使用模板: {gpt_error}")
                title = f"{stock_name}({stock_code}) 技術分析與操作策略"
                content = f"""【{stock_name}({stock_code}) 深度分析】

一、技術面分析
從技術指標來看，{stock_name}目前呈現出值得關注的訊號。RSI指標顯示股價動能變化，MACD指標則反映短中期趨勢。成交量方面，近期量能有所放大，顯示市場關注度提升。

二、基本面觀察
{stock_name}作為產業中的重要成員，營運狀況值得持續追蹤。投資人應關注公司財報數據、營收表現，以及產業整體景氣變化。

三、操作建議
短線操作者可觀察關鍵價位突破情況，配合量能變化做進出判斷。中長線投資者則需評估基本面是否支撐目前股價水準。

四、風險提醒
- 注意整體市場系統性風險
- 留意產業競爭態勢變化
- 設定合理停損停利點
- 嚴格控制持股比重

以上分析僅供參考，投資需謹慎評估自身風險承受能力。"""
        else:
            logger.warning("⚠️  GPT 生成器不可用，使用模板生成")
            title = f"{stock_name}({stock_code}) 技術分析與操作策略"
            content = f"""【{stock_name}({stock_code}) 深度分析】

一、技術面分析
從技術指標來看，{stock_name}目前呈現出值得關注的訊號。RSI指標顯示股價動能變化，MACD指標則反映短中期趨勢。成交量方面，近期量能有所放大，顯示市場關注度提升。

二、基本面觀察
{stock_name}作為產業中的重要成員，營運狀況值得持續追蹤。投資人應關注公司財報數據、營收表現，以及產業整體景氣變化。

三、操作建議
短線操作者可觀察關鍵價位突破情況，配合量能變化做進出判斷。中長線投資者則需評估基本面是否支撐目前股價水準。

四、風險提醒
- 注意整體市場系統性風險
- 留意產業競爭態勢變化
- 設定合理停損停利點
- 嚴格控制持股比重

以上分析僅供參考，投資需謹慎評估自身風險承受能力。"""

        # 隨機版本生成 - ALL posting_types 都生成 5 個版本（避免模板化）
        alternative_versions = []
        if enhanced_personalization_processor:
            logger.info(f"🎯 開始生成 5 個隨機版本: KOL={kol_serial}, posting_type={posting_type}")
            try:
                # 🔥 FIX: Pass stock info to personalization processor so it can include stock names in fallback
                serper_analysis_with_stock = {
                    'stock_name': stock_name,
                    'stock_code': stock_code
                }
                logger.info(f"📊 傳遞股票信息到個人化模組: {stock_name}({stock_code})")

                personalized_title, personalized_content, random_metadata = enhanced_personalization_processor.personalize_content(
                    standard_title=title,
                    standard_content=content,
                    kol_serial=kol_serial,
                    batch_config={},
                    serper_analysis=serper_analysis_with_stock,
                    trigger_type=trigger_type,
                    real_time_price_data={},
                    posting_type=posting_type,
                    max_words=max_words,
                    kol_persona_override=kol_persona  # 🔥 FIX: Pass persona override to respect user's content_style choice
                )

                # 更新為選中的版本內容
                title = personalized_title
                content = personalized_content

                # 提取其他 4 個版本
                if random_metadata:
                    alternative_versions = random_metadata.get('alternative_versions', [])
                    logger.info(f"✅ 版本生成完成: 選中版本 + {len(alternative_versions)} 個替代版本 = 共 {len(alternative_versions) + 1} 個版本")
            except Exception as e:
                logger.error(f"⚠️  版本生成失敗: {e}，使用原始內容")
        else:
            logger.warning(f"⚠️  個人化模組不可用: posting_type={posting_type}")

        # 生成 UUID 作為 post_id
        import uuid
        post_id = str(uuid.uuid4())

        # 準備數據庫寫入數據
        now = get_current_time()

        # 生成商品標籤
        commodity_tags_data = [
            {"type": "Market", "key": "TWA00", "bullOrBear": 0},
            {"type": "Stock", "key": stock_code, "bullOrBear": 0}
        ]

        # 生成參數記錄
        full_triggers_config_from_request = body.get('full_triggers_config', {})
        logger.info(f"🔍 DEBUG: Received full_triggers_config from request: {json.dumps(full_triggers_config_from_request, ensure_ascii=False)[:200]}...")

        generation_params = {
            "method": "manual",
            "kol_persona": kol_persona,
            "content_style": body.get('content_style', 'chart_analysis'),
            "target_audience": body.get('target_audience', 'active_traders'),
            "trigger_type": trigger_type,
            "posting_type": posting_type,
            "created_at": now.isoformat(),
            # 🔥 FIX: Store full triggers config for schedule recreation
            "full_triggers_config": full_triggers_config_from_request
        }

        logger.info(f"🔍 DEBUG: generation_params to store: {json.dumps(generation_params, ensure_ascii=False)[:200]}...")

        # 確認數據庫連接可用
        if not db_pool:
            logger.error("數據庫連接池不可用")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "數據庫連接不可用",
                    "timestamp": now.isoformat()
                }
            )

        # 寫入數據庫
        conn = get_db_connection()
        conn.rollback()  # 清除任何失敗的事務

        with conn.cursor() as cursor:
            insert_query = """
                INSERT INTO post_records (
                    post_id, created_at, updated_at, session_id,
                    kol_serial, kol_nickname, kol_persona,
                    stock_code, stock_name,
                    title, content, content_md,
                    status, commodity_tags, generation_params, alternative_versions, trigger_type, generation_mode
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
            """

            # 準備 alternative_versions JSON
            alternative_versions_json = json.dumps(alternative_versions, ensure_ascii=False) if alternative_versions else None

            cursor.execute(insert_query, (
                post_id, now, now, session_id,
                kol_serial, f"KOL-{kol_serial}", kol_persona,
                stock_code, stock_name,
                title, content, content,
                'draft',  # 預設為草稿狀態
                json.dumps(commodity_tags_data, ensure_ascii=False),
                json.dumps(generation_params, ensure_ascii=False),
                alternative_versions_json,  # 添加替代版本
                trigger_type,  # 添加 trigger_type
                generation_mode  # 🔥 NEW: 添加 generation_mode
            ))

            conn.commit()
            logger.info(f"✅ 成功寫入數據庫: post_id={post_id}, session_id={session_id}")

        # 返回成功響應
        result = {
            "success": True,
            "message": "手動貼文生成成功",
            "post_id": post_id,
            "content": {
                "title": title,
                "content": content,
                "content_md": content
            },
            "stock_info": {
                "stock_code": stock_code,
                "stock_name": stock_name
            },
            "kol_info": {
                "kol_serial": kol_serial,
                "kol_nickname": f"KOL-{kol_serial}",
                "kol_persona": kol_persona
            },
            "commodity_tags": commodity_tags_data,
            "alternative_versions": alternative_versions,  # 🔥 FIX: Include alternative versions in response
            "timestamp": now.isoformat()
        }

        logger.info("✅ 手動貼文生成成功")
        return result

    except Exception as e:
        logger.error(f"❌ 手動貼文失敗: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

        if conn:
            try:
                conn.rollback()
            except:
                pass

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"手動貼文失敗: {str(e)}",
                "error_type": type(e).__name__,
                "timestamp": get_current_time().isoformat()
            }
        )
    finally:
        if conn:
            return_db_connection(conn)

# ==================== Performance Testing Endpoint ====================

@app.post("/api/debug/performance-test")
async def performance_test(request: Request):
    """性能測試 - 計時每個生成步驟的耗時"""
    import time

    timings = {}
    total_start = time.time()

    try:
        # Step 1: Parse Request
        step_start = time.time()
        body = await request.json()
        timings['1_parse_request'] = round((time.time() - step_start) * 1000, 2)  # ms

        # Extract parameters
        stock_code = body.get('stock_code', '2330')
        stock_name = body.get('stock_name', '台積電')
        kol_serial = int(body.get('kol_serial', 208))
        kol_persona = body.get('kol_persona', 'technical')
        session_id = body.get('session_id', int(time.time() * 1000))
        trigger_type = body.get('trigger_type', 'performance_test')
        posting_type = body.get('posting_type', 'interaction')
        max_words = body.get('max_words', 150)
        model_id_override = body.get('model_id_override')
        use_kol_default_model = body.get('use_kol_default_model', True)

        # Step 2: Model Selection (with DB query)
        step_start = time.time()
        chosen_model_id = None

        if not use_kol_default_model and model_id_override:
            chosen_model_id = model_id_override
        else:
            try:
                conn = await asyncpg.connect(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    database=DB_CONFIG['database'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password']
                )
                kol_model_id = await conn.fetchval(
                    "SELECT model_id FROM kol_profiles WHERE serial = $1",
                    str(kol_serial)
                )
                await conn.close()

                chosen_model_id = kol_model_id if kol_model_id else "gpt-4o-mini"
            except Exception as db_error:
                chosen_model_id = "gpt-4o-mini"

        timings['2_model_selection_db'] = round((time.time() - step_start) * 1000, 2)

        # Step 3: GPT Content Generation
        step_start = time.time()
        title = ""
        content = ""

        if gpt_generator:
            try:
                gpt_result = gpt_generator.generate_stock_analysis(
                    stock_id=stock_code,
                    stock_name=stock_name,
                    kol_persona=kol_persona,
                    serper_analysis={},
                    data_sources=[],
                    content_length="medium",
                    max_words=max_words,
                    model=chosen_model_id
                )
                title = gpt_result.get('title', f"{stock_name}({stock_code}) 分析")
                content = gpt_result.get('content', '')
            except Exception as gpt_error:
                title = f"{stock_name}({stock_code}) 測試標題"
                content = f"測試內容 - GPT 失敗: {gpt_error}"

        timings['3_gpt_generation'] = round((time.time() - step_start) * 1000, 2)

        # Step 4: Alternative Versions Generation
        step_start = time.time()
        alternative_versions = []

        if enhanced_personalization_processor:
            try:
                serper_analysis_with_stock = {
                    'stock_name': stock_name,
                    'stock_code': stock_code
                }

                personalized_title, personalized_content, random_metadata = enhanced_personalization_processor.personalize_content(
                    standard_title=title,
                    standard_content=content,
                    kol_serial=kol_serial,
                    batch_config={},
                    serper_analysis=serper_analysis_with_stock,
                    trigger_type=trigger_type,
                    real_time_price_data={},
                    posting_type=posting_type,
                    max_words=max_words,
                    kol_persona_override=kol_persona  # 🔥 FIX: Pass persona override to respect user's content_style choice
                )

                title = personalized_title
                content = personalized_content

                if random_metadata:
                    alternative_versions = random_metadata.get('alternative_versions', [])
            except Exception as e:
                pass

        timings['4_alternative_versions'] = round((time.time() - step_start) * 1000, 2)

        # Step 5: Database Write
        step_start = time.time()

        import uuid
        post_id = str(uuid.uuid4())
        now = get_current_time()

        commodity_tags_data = [
            {"type": "Market", "key": "TWA00", "bullOrBear": 0},
            {"type": "Stock", "key": stock_code, "bullOrBear": 0}
        ]

        generation_params = {
            "method": "performance_test",
            "kol_persona": kol_persona,
            "trigger_type": trigger_type,
            "posting_type": posting_type,
            "created_at": now.isoformat()
        }

        conn = get_db_connection()
        conn.rollback()

        with conn.cursor() as cursor:
            insert_query = """
                INSERT INTO post_records (
                    post_id, created_at, updated_at, session_id,
                    kol_serial, kol_nickname, kol_persona,
                    stock_code, stock_name,
                    title, content, content_md,
                    status, commodity_tags, generation_params, alternative_versions, trigger_type
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """

            alternative_versions_json = json.dumps(alternative_versions, ensure_ascii=False) if alternative_versions else None

            cursor.execute(insert_query, (
                post_id, now, now, session_id,
                kol_serial, f"KOL-{kol_serial}", kol_persona,
                stock_code, stock_name,
                title, content, content,
                'draft',
                json.dumps(commodity_tags_data, ensure_ascii=False),
                json.dumps(generation_params, ensure_ascii=False),
                alternative_versions_json,
                trigger_type
            ))

            conn.commit()

        return_db_connection(conn)

        timings['5_database_write'] = round((time.time() - step_start) * 1000, 2)

        # Calculate total
        timings['total_time'] = round((time.time() - total_start) * 1000, 2)

        # Calculate percentages
        total_ms = timings['total_time']
        percentages = {}
        for key in timings:
            if key != 'total_time':
                percentages[key] = round((timings[key] / total_ms) * 100, 1) if total_ms > 0 else 0

        return {
            "success": True,
            "post_id": post_id,
            "model_used": chosen_model_id,
            "timings_ms": timings,
            "percentages": percentages,
            "breakdown": {
                "1_parse_request": {
                    "time_ms": timings['1_parse_request'],
                    "percentage": percentages.get('1_parse_request', 0),
                    "description": "解析請求參數"
                },
                "2_model_selection_db": {
                    "time_ms": timings['2_model_selection_db'],
                    "percentage": percentages.get('2_model_selection_db', 0),
                    "description": "模型選擇（含數據庫查詢）"
                },
                "3_gpt_generation": {
                    "time_ms": timings['3_gpt_generation'],
                    "percentage": percentages.get('3_gpt_generation', 0),
                    "description": "GPT 內容生成（OpenAI API 調用）"
                },
                "4_alternative_versions": {
                    "time_ms": timings['4_alternative_versions'],
                    "percentage": percentages.get('4_alternative_versions', 0),
                    "description": "生成 4 個替代版本"
                },
                "5_database_write": {
                    "time_ms": timings['5_database_write'],
                    "percentage": percentages.get('5_database_write', 0),
                    "description": "寫入數據庫"
                }
            },
            "summary": {
                "total_time_ms": timings['total_time'],
                "total_time_seconds": round(timings['total_time'] / 1000, 2),
                "slowest_step": max([(k, v) for k, v in timings.items() if k != 'total_time'], key=lambda x: x[1])[0],
                "slowest_time_ms": max([v for k, v in timings.items() if k != 'total_time'])
            },
            "timestamp": get_current_time().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 性能測試失敗: {e}")
        import traceback
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "timings_ms": timings,
                "timestamp": get_current_time().isoformat()
            }
        )

# ==================== Dashboard API 功能 ====================

@app.get("/api/dashboard/system-monitoring")
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
        "timestamp": get_current_time().isoformat()
    }

    logger.info("返回系統監控數據")
    return result

@app.get("/api/dashboard/content-management")
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
        "timestamp": get_current_time().isoformat()
    }

    logger.info("返回內容管理數據")
    return result

@app.get("/api/dashboard/interaction-analysis")
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
        "timestamp": get_current_time().isoformat()
    }

    logger.info("返回互動分析數據")
    return result

# ==================== Posts API 功能 ====================

@app.get("/api/posts")
async def get_posts(
    skip: int = Query(0, description="跳過的記錄數"),
    limit: int = Query(100, description="返回的記錄數，默認100條"),
    status: str = Query(None, description="狀態篩選"),
    session_id: int = Query(None, description="Session ID篩選")
):
    """獲取貼文列表（從 PostgreSQL 數據庫）"""
    logger.info(f"收到 get_posts 請求: skip={skip}, limit={limit}, status={status}, session_id={session_id}")

    conn = None
    try:
        # 檢查數據庫連接池狀態
        if not db_pool:
            logger.error("❌ 數據庫連接池不存在，無法查詢貼文數據")
            return {
                "success": False,
                "posts": [],
                "count": 0,
                "skip": skip,
                "limit": limit,
                "error": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        # Get connection from pool
        conn = get_db_connection()

        # Reset connection if in failed state
        conn.rollback()  # Clear any failed transactions

        # 查詢 post_records 表
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 首先檢查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'post_records'
                ) as exists;
            """)
            result = cursor.fetchone()
            table_exists = result['exists'] if result else False
            logger.info(f"📊 post_records 表存在狀態: {table_exists}")

            if not table_exists:
                logger.error("❌ post_records 表不存在")
                return {
                    "success": False,
                    "posts": [],
                    "count": 0,
                    "skip": skip,
                    "limit": limit,
                    "error": "post_records 表不存在",
                    "timestamp": get_current_time().isoformat()
                }

            # 獲取總數（在查詢前先檢查）
            count_query = "SELECT COUNT(*) as count FROM post_records"
            count_params = []
            where_clauses = []

            if status:
                where_clauses.append("status = %s")
                count_params.append(status)

            if session_id is not None:
                where_clauses.append("session_id = %s")
                count_params.append(session_id)

            if where_clauses:
                count_query += " WHERE " + " AND ".join(where_clauses)

            cursor.execute(count_query, count_params)
            total_count = cursor.fetchone()['count']
            logger.info(f"📊 數據庫中總貼文數 (filtered): {total_count}")

            # 構建查詢
            query = "SELECT * FROM post_records"
            params = []

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)
                params.extend(count_params)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            logger.info(f"🔍 執行 SQL 查詢: {query} with params: {params}")
            cursor.execute(query, params)
            posts = cursor.fetchall()

            conn.commit()  # Commit after all reads
            logger.info(f"✅ 查詢到 {len(posts)} 條貼文數據，總數: {total_count}")

            # 🔥 FIX: Convert naive UTC datetimes to Taipei timezone
            posts_with_timezone = [convert_post_datetimes_to_taipei(dict(post)) for post in posts]

            # 🔍 DEBUG: Log full_triggers_config content for first post
            if posts_with_timezone:
                first_post = posts_with_timezone[0]
                if 'generation_config' in first_post and first_post['generation_config']:
                    has_ftc = 'full_triggers_config' in first_post['generation_config']
                    logger.info(f"🔍 DEBUG: First post generation_config has full_triggers_config: {has_ftc}")
                    if has_ftc:
                        ftc_content = first_post['generation_config']['full_triggers_config']
                        logger.info(f"🔍 DEBUG: full_triggers_config content: {json.dumps(ftc_content, ensure_ascii=False)[:300]}...")

            return {
                "success": True,
                "posts": posts_with_timezone,
                "count": total_count,
                "skip": skip,
                "limit": limit,
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        if conn:
            conn.rollback()  # Rollback on error
        logger.error(f"❌ 查詢貼文數據失敗: {e}")
        logger.error(f"❌ 錯誤詳情: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"❌ 完整錯誤堆疊: {traceback.format_exc()}")
        return {
            "success": False,
            "posts": [],
            "count": 0,
            "error": str(e),
            "error_type": type(e).__name__,
            "error_details": f"{type(e).__name__}: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/api/posts/refresh-all")
async def refresh_all_interactions():
    """
    刷新所有貼文的互動數據
    從CMoney API獲取最新的likes, comments, shares等數據並更新到數據庫
    """
    logger.info("收到 refresh-all 請求")

    if not db_pool:
        return {"success": False, "error": "數據庫連接不可用", "timestamp": get_current_time().isoformat()}

    conn = None
    try:
        # Get connection from pool
        conn = get_db_connection()
        conn.rollback()  # Clear any failed transactions

        # Get KOL credentials from environment
        email = os.getenv("FORUM_200_EMAIL")
        password = os.getenv("FORUM_200_PASSWORD")

        if not email or not password:
            return {"success": False, "error": "KOL credentials not configured", "timestamp": get_current_time().isoformat()}

        # Fetch all published posts with article_id
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT post_id, article_id, kol_serial
                FROM post_records
                WHERE status = 'published' AND article_id IS NOT NULL
                ORDER BY created_at DESC
            """)
            posts = cursor.fetchall()
            conn.commit()

        logger.info(f"Found {len(posts)} published posts to refresh")

        # Login to CMoney to get access token
        async with httpx.AsyncClient() as client:
            login_response = await client.post(
                "https://www.cmoney.tw/member/login/jsonp.aspx",
                data={"a": email, "b": password, "remember": 0},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0
            )

            if login_response.status_code != 200:
                return {"success": False, "error": "CMoney login failed", "timestamp": get_current_time().isoformat()}

            # Extract access token
            token_data = login_response.json()
            access_token = token_data.get("Data", {}).get("access_token")

            if not access_token:
                return {"success": False, "error": "Failed to get access token", "timestamp": get_current_time().isoformat()}

            # Refresh interaction data for each post
            updated_count = 0
            failed_count = 0

            for post in posts:
                article_id = post['article_id']
                post_id = post['post_id']

                try:
                    # Fetch interaction data from CMoney
                    interaction_response = await client.get(
                        f"https://forumservice.cmoney.tw/api/Article/{article_id}",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "X-Version": "2.0",
                            "accept": "application/json"
                        },
                        timeout=15.0
                    )

                    if interaction_response.status_code == 200:
                        data = interaction_response.json()

                        # Extract interaction metrics
                        likes = data.get("ArticleReplyDto", {}).get("SatisfiedCount", 0)
                        comments = data.get("CommentCount", 0)
                        shares = data.get("ArticleReplyDto", {}).get("ShareCount", 0)
                        bookmarks = data.get("ArticleReplyDto", {}).get("CollectedCount", 0)

                        # Extract emoji counts
                        emojis = data.get("ArticleReplyDto", {}).get("PersonEmotionArticleDetailDto", {})
                        emoji_data = {
                            "like": emojis.get("Like", 0),
                            "dislike": emojis.get("Dislike", 0),
                            "laugh": emojis.get("Laugh", 0),
                            "money": emojis.get("Money", 0),
                            "shock": emojis.get("Shock", 0),
                            "cry": emojis.get("Cry", 0),
                            "think": emojis.get("Think", 0),
                            "angry": emojis.get("Angry", 0)
                        }

                        # Update database
                        with conn.cursor() as update_cursor:
                            update_cursor.execute("""
                                UPDATE post_records
                                SET likes = %s, comments = %s, shares = %s, bookmarks = %s,
                                    emoji_data = %s, last_interaction_update = CURRENT_TIMESTAMP
                                WHERE post_id = %s
                            """, (likes, comments, shares, bookmarks, json.dumps(emoji_data), post_id))

                        updated_count += 1

                except Exception as e:
                    logger.error(f"Failed to update post {post_id}: {e}")
                    failed_count += 1

            conn.commit()

        logger.info(f"Refresh complete: {updated_count} updated, {failed_count} failed")

        return {
            "success": True,
            "updated_count": updated_count,
            "failed_count": failed_count,
            "total_posts": len(posts),
            "timestamp": get_current_time().isoformat()
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Refresh all failed: {e}")
        return {"success": False, "error": str(e), "timestamp": get_current_time().isoformat()}
    finally:
        if conn:
            return_db_connection(conn)

# ==================== Post Management API (Approve/Publish/Edit) ====================

@app.post("/api/posts/{post_id}/approve")
async def approve_post(post_id: str, request: Request):
    """審核通過貼文"""
    logger.info(f"收到 approve_post 請求 - Post ID: {post_id}")

    conn = None
    try:
        body = await request.json()
        reviewer_notes = body.get('reviewer_notes', '')
        approved_by = body.get('approved_by', 'system')
        edited_title = body.get('edited_title')
        edited_content = body.get('edited_content')

        logger.info(f"審核參數: approved_by={approved_by}, has_edits={bool(edited_title or edited_content)}")

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Build update query
            update_fields = [
                "status = 'approved'",
                "reviewer_notes = %s",
                "approved_by = %s",
                "approved_at = %s"
            ]
            params = [reviewer_notes, approved_by, get_current_time()]

            # Add edited title/content if provided
            if edited_title:
                update_fields.append("title = %s")
                params.append(edited_title)
            if edited_content:
                update_fields.append("content = %s")
                params.append(edited_content)

            params.append(post_id)

            query = f"""
                UPDATE post_records
                SET {', '.join(update_fields)}
                WHERE post_id = %s
            """

            cursor.execute(query, params)
            conn.commit()

            if cursor.rowcount == 0:
                raise ValueError(f"Post {post_id} not found")

            logger.info(f"✅ 貼文審核成功 - Post ID: {post_id}")

        return {"success": True, "message": "貼文審核通過"}

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 審核貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: str):
    """發布貼文到 CMoney"""
    logger.info(f"收到 publish_post 請求 - Post ID: {post_id}")

    conn = None
    try:
        # Get post from database
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM post_records WHERE post_id = %s", (post_id,))
            post = cursor.fetchone()

            if not post:
                raise ValueError(f"Post {post_id} not found")

            # Get CMoney credentials
            from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

            cmoney_client = CMoneyClient()
            forum_credentials = get_forum_200_credentials()
            credentials = LoginCredentials(
                email=forum_credentials["email"],
                password=forum_credentials["password"]
            )

            # Login
            logger.info("🔐 登入 CMoney API...")
            login_result = await cmoney_client.login(credentials)

            if not login_result or not login_result.token:
                raise ValueError("CMoney login failed")

            # Publish post
            logger.info(f"📤 發布貼文到 CMoney: {post['title'][:50]}...")

            from src.clients.cmoney.cmoney_client import ArticleData

            # Prepare article data with commodity tags and community topic
            article_data = ArticleData(
                title=post['title'],
                text=post['content']
            )

            # Add community topic if exists
            if post.get('topic_id'):
                article_data.communityTopic = {"id": post['topic_id']}

            # Add commodity tags (stock tags) if exists
            if post.get('stock_code') and post['stock_code'] != '0000':
                article_data.commodity_tags = [
                    {
                        "type": "Stock",
                        "key": post['stock_code'],
                        "bullOrBear": 0  # 0 = neutral, can be set based on trigger type
                    }
                ]

            publish_result = await cmoney_client.publish_article(
                access_token=login_result.token,
                article=article_data
            )

            if not publish_result or not publish_result.success:
                error_msg = publish_result.error_message if publish_result else "Unknown error"
                raise ValueError(f"Failed to publish to CMoney: {error_msg}")

            # Update database
            cursor.execute("""
                UPDATE post_records
                SET status = 'published',
                    published_at = %s,
                    cmoney_post_id = %s,
                    cmoney_post_url = %s
                WHERE post_id = %s
            """, (
                get_current_time(),
                publish_result.post_id,
                publish_result.post_url,
                post_id
            ))
            conn.commit()

            logger.info(f"✅ 貼文發布成功 - Article ID: {publish_result.post_id}")

        return {
            "success": True,
            "post_id": publish_result.post_id,
            "post_url": publish_result.post_url
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 發布貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            return_db_connection(conn)

@app.put("/api/posts/{post_id}/content")
async def update_post_content(post_id: str, request: Request):
    """更新貼文內容（不改變狀態）"""
    logger.info(f"收到 update_post_content 請求 - Post ID: {post_id}")

    conn = None
    try:
        body = await request.json()
        title = body.get('title')
        content = body.get('content')
        content_md = body.get('content_md')

        if not title and not content:
            raise ValueError("Must provide at least title or content")

        conn = get_db_connection()
        with conn.cursor() as cursor:
            update_fields = []
            params = []

            if title:
                update_fields.append("title = %s")
                params.append(title)
            if content:
                update_fields.append("content = %s")
                params.append(content)
            if content_md:
                update_fields.append("content_md = %s")
                params.append(content_md)

            # Always update updated_at
            update_fields.append("updated_at = %s")
            params.append(get_current_time())

            params.append(post_id)

            query = f"""
                UPDATE post_records
                SET {', '.join(update_fields)}
                WHERE post_id = %s
            """

            cursor.execute(query, params)
            conn.commit()

            if cursor.rowcount == 0:
                raise ValueError(f"Post {post_id} not found")

            logger.info(f"✅ 貼文內容更新成功 - Post ID: {post_id}")

        return {"success": True, "message": "貼文內容已更新"}

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 更新貼文內容失敗: {e}")
        return {"success": False, "error": str(e)}
    finally:
        if conn:
            return_db_connection(conn)

@app.get("/api/posts/{post_id}/versions")
async def get_post_versions(post_id: str):
    """獲取貼文的其他生成版本"""
    logger.info(f"收到 get_post_versions 請求 - Post ID: {post_id}")

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # First get the post to find its session_id and stock_code
            cursor.execute("""
                SELECT session_id, stock_codes, kol_serial
                FROM post_records
                WHERE post_id = %s
            """, (post_id,))

            post = cursor.fetchone()
            if not post:
                logger.warning(f"⚠️ 貼文不存在 - Post ID: {post_id}")
                return {"success": False, "versions": [], "error": "Post not found"}

            session_id = post['session_id']
            stock_codes = post['stock_codes']
            kol_serial = post['kol_serial']

            logger.info(f"🔍 查找版本 - Session: {session_id}, Stock: {stock_codes}, KOL: {kol_serial}")

            # Get alternative versions from the same session, stock, and KOL
            cursor.execute("""
                SELECT
                    post_id,
                    title,
                    content,
                    version_number,
                    angle,
                    quality_score,
                    ai_detection_score,
                    risk_level,
                    created_at
                FROM post_records
                WHERE session_id = %s
                  AND stock_codes = %s
                  AND kol_serial = %s
                  AND post_id != %s
                  AND status != 'deleted'
                ORDER BY version_number ASC, created_at DESC
                LIMIT 10
            """, (session_id, stock_codes, kol_serial, post_id))

            versions = cursor.fetchall()

            logger.info(f"✅ 找到 {len(versions)} 個版本")

            # Convert to list of dicts
            versions_list = []
            for v in versions:
                versions_list.append({
                    'post_id': v['post_id'],
                    'title': v['title'],
                    'content': v['content'],
                    'version_number': v['version_number'] or 0,
                    'angle': v['angle'] or '標準分析',
                    'quality_score': v['quality_score'],
                    'ai_detection_score': v['ai_detection_score'],
                    'risk_level': v['risk_level'],
                    'created_at': v['created_at'].isoformat() if v['created_at'] else None
                })

            return {
                "success": True,
                "versions": versions_list,
                "total": len(versions_list)
            }

    except Exception as e:
        logger.error(f"❌ 獲取貼文版本失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "versions": [], "error": str(e)}
    finally:
        if conn:
            return_db_connection(conn)

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: str):
    """刪除貼文（軟刪除）"""
    logger.info(f"🗑️ 開始刪除貼文 - Post ID: {post_id}")

    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 檢查貼文是否存在
            cursor.execute("""
                SELECT post_id, status, cmoney_post_id, kol_serial
                FROM post_records
                WHERE post_id = %s
            """, (post_id,))

            existing_post = cursor.fetchone()
            if not existing_post:
                logger.error(f"❌ 貼文不存在 - Post ID: {post_id}")
                raise HTTPException(status_code=404, detail=f"貼文不存在: {post_id}")

            # 軟刪除：更新狀態為 'deleted'
            cursor.execute("""
                UPDATE post_records
                SET status = 'deleted',
                    updated_at = %s
                WHERE post_id = %s
            """, (get_current_time(), post_id))

            conn.commit()

            logger.info(f"✅ 貼文軟刪除成功 - Post ID: {post_id}")
            return {"success": True, "message": "貼文已刪除"}

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 刪除貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=f"刪除貼文失敗: {str(e)}")
    finally:
        if conn:
            return_db_connection(conn)

# ==================== Trending API 功能 ====================

@app.get("/api/trending")
async def get_trending_topics(limit: int = Query(10, description="返回結果數量")):
    """獲取熱門話題（from real CMoney API）"""
    logger.info(f"收到 trending 請求: limit={limit}")

    try:
        # 🔥 FIX: Replace mock data with real CMoney API call
        from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials

        # Initialize CMoney client
        cmoney_client = CMoneyClient()
        forum_credentials = get_forum_200_credentials()
        credentials = LoginCredentials(
            email=forum_credentials["email"],
            password=forum_credentials["password"]
        )

        # Login to get access token
        logger.info("🔐 Logging in to CMoney API...")
        login_result = await cmoney_client.login(credentials)

        if not login_result or not login_result.token:
            raise Exception("CMoney 登入失敗")

        access_token = login_result.token
        logger.info(f"✅ CMoney 登入成功，token 有效期至: {login_result.expires_at}")

        # Get trending topics from CMoney API
        logger.info("📊 獲取 CMoney 熱門話題...")
        cmoney_topics = await cmoney_client.get_trending_topics(access_token)

        # Transform CMoney Topic objects to TrendingTopic interface
        topics = []
        for topic in cmoney_topics[:limit]:
            # Extract stock_ids from raw_data if available
            stock_ids = []
            if hasattr(topic, 'raw_data') and topic.raw_data:
                related_stocks = topic.raw_data.get('relatedStockSymbols', [])
                if isinstance(related_stocks, list):
                    stock_ids = [str(stock) for stock in related_stocks]

            # Calculate engagement score (mock for now, can be enhanced later)
            engagement_score = 100.0 - (len(topics) * 5.0)  # Decreasing scores

            topics.append({
                "id": str(topic.id) if hasattr(topic, 'id') else f"topic_{len(topics)+1}",
                "title": topic.title if hasattr(topic, 'title') else topic.name,
                "content": f"熱門討論話題：{topic.title if hasattr(topic, 'title') else topic.name}",
                "stock_ids": stock_ids,
                "category": "市場熱議",
                "engagement_score": engagement_score
            })

        result = {
            "topics": topics,
            "timestamp": get_current_time().isoformat()
        }

        logger.info(f"✅ 返回 {len(result['topics'])} 個 CMoney 熱門話題")
        return result

    except Exception as e:
        logger.error(f"❌ 獲取 CMoney 熱門話題失敗: {e}")
        logger.error(f"錯誤詳情: {type(e).__name__}: {str(e)}")

        # Fallback: Return empty list if CMoney API fails
        result = {
            "topics": [],
            "timestamp": get_current_time().isoformat(),
            "error": f"CMoney API 錯誤: {str(e)}"
        }

        logger.warning(f"⚠️  返回空列表（CMoney API 失敗）")
        return result

@app.get("/api/extract-keywords")
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
        "timestamp": get_current_time().isoformat()
    }

    logger.info(f"提取到 {len(keywords)} 個關鍵字")
    return result

@app.get("/api/search-stocks-by-keywords")
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
        "timestamp": get_current_time().isoformat()
    }

    logger.info(f"找到 {len(stocks)} 支相關股票")
    return result

@app.get("/api/analyze-topic")
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
        "timestamp": get_current_time().isoformat()
    }

    logger.info(f"完成話題分析: {topic}")
    return result

@app.get("/api/generate-content")
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
            "generated_at": get_current_time().isoformat()
        },
        "timestamp": get_current_time().isoformat()
    }

    logger.info(f"生成內容完成: {topic}")
    return result

# ==================== 數據庫管理功能 ====================

@app.post("/admin/import-1788-posts")
async def import_1788_posts():
    """導入 1788 筆 post_records 數據（管理員功能）"""
    conn = None
    try:
        if not db_pool:
            return {"error": "數據庫連接不存在"}

        # 讀取 JSON 數據文件
        json_file_path = '/app/post_records_1788.json'
        if not os.path.exists(json_file_path):
            return {"error": "post_records_1788.json 文件不存在"}

        with open(json_file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

        logger.info(f"📊 從 JSON 文件加載 {len(records)} 筆記錄")

        conn = get_db_connection()
        conn.rollback()  # Clear failed transactions

        with conn.cursor() as cursor:
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
            conn.commit()
            
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
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"❌ 導入 1788 筆記錄失敗: {e}")
        if conn:
            conn.rollback()
        return {"error": str(e)}
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/test/insert-sample-data")
async def insert_sample_data():
    """插入樣本數據到 post_records 表（測試功能）"""
    conn = None
    try:
        if not db_pool:
            return {"error": "數據庫連接不存在"}

        conn = get_db_connection()
        conn.rollback()  # Clear failed transactions

        with conn.cursor() as cursor:
            # 創建樣本記錄
            sample_records = [
                {
                    'post_id': 'test-001',
                    'created_at': get_current_time(),
                    'updated_at': get_current_time(),
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
                    'created_at': get_current_time(),
                    'updated_at': get_current_time(),
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
                    'approved_at': get_current_time(),
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
            conn.commit()
            
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
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"❌ 插入樣本數據失敗: {e}")
        if conn:
            conn.rollback()
        return {"error": str(e)}
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/admin/create-post-records-table")
async def create_table_manually():
    """手動創建 post_records 表（管理員功能）"""
    try:
        if not db_pool:
            return {"error": "數據庫連接不存在"}
        
        create_post_records_table()
        return {
            "success": True,
            "message": "post_records 表創建成功",
            "timestamp": get_current_time().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 手動創建表失敗: {e}")
        return {"error": str(e)}

@app.post("/admin/drop-and-recreate-post-records-table")
async def drop_and_recreate_table():
    """刪除並重新創建 post_records 表（管理員功能）"""
    conn = None
    try:
        if not db_pool:
            return {"error": "數據庫連接不存在"}

        conn = get_db_connection()
        conn.rollback()  # Clear failed transactions

        with conn.cursor() as cursor:
            # 刪除現有表
            cursor.execute("DROP TABLE IF EXISTS post_records CASCADE")
            conn.commit()
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
            conn.commit()
            logger.info("✅ 重新創建 post_records 表成功")

        return {
            "success": True,
            "message": "post_records 表已刪除並重新創建",
            "timestamp": get_current_time().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 刪除並重新創建表失敗: {e}")
        if conn:
            conn.rollback()
        return {"error": str(e)}
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/admin/reset-database")
async def reset_database():
    """重置數據庫（管理員功能）"""
    conn = None
    try:
        if not db_pool:
            return {"error": "數據庫連接不存在"}

        conn = get_db_connection()
        conn.rollback()  # Clear failed transactions

        with conn.cursor() as cursor:
            # 刪除現有表
            cursor.execute("DROP TABLE IF EXISTS post_records CASCADE")
            conn.commit()
            logger.info("🗑️ 刪除現有 post_records 表")

        return {
            "success": True,
            "message": "數據庫已重置，表已刪除",
            "timestamp": get_current_time().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ 重置數據庫失敗: {e}")
        if conn:
            conn.rollback()
        return {"error": str(e)}
    finally:
        if conn:
            return_db_connection(conn)

@app.get("/admin/debug-database")
async def debug_database():
    """調試數據庫連接和表狀態（管理員功能）"""
    try:
        debug_info = {
            "timestamp": get_current_time().isoformat(),
            "database_connection": None,
            "table_exists": False,
            "table_count": 0,
            "sample_data": None,
            "error": None
        }
        
        if not db_pool:
            debug_info["error"] = "數據庫連接不存在"
            return debug_info
        
        # 測試數據庫連接
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            debug_info["database_connection"] = "✅ 連接正常"
        except Exception as e:
            debug_info["database_connection"] = f"❌ 連接失敗: {str(e)}"
            debug_info["error"] = str(e)
            return debug_info
        
        # 檢查表是否存在
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'post_records'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                debug_info["table_exists"] = table_exists
                
                if table_exists:
                    # 獲取記錄數
                    cursor.execute("SELECT COUNT(*) FROM post_records")
                    count = cursor.fetchone()[0]
                    debug_info["table_count"] = count
                    
                    # 獲取樣本數據
                    cursor.execute("SELECT post_id, title, status, created_at FROM post_records LIMIT 3")
                    sample_data = cursor.fetchall()
                    debug_info["sample_data"] = [dict(row) for row in sample_data]
                else:
                    debug_info["error"] = "post_records 表不存在"
                    
        except Exception as e:
            debug_info["error"] = f"查詢表信息失敗: {str(e)}"
        
        return debug_info
        
    except Exception as e:
        return {
            "timestamp": get_current_time().isoformat(),
            "error": f"調試失敗: {str(e)}"
        }

@app.post("/admin/fix-database")
async def fix_database():
    """修復數據庫（管理員功能）"""
    try:
        if not db_pool:
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
            "timestamp": get_current_time().isoformat()
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
        
        with conn.cursor() as cursor:
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
            conn.commit()
            
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
                "timestamp": get_current_time().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ 導入 post_records 失敗: {e}")
        return {"error": str(e)}

# ==================== KOL API 功能 ====================

@app.get("/api/kol/list")
async def get_kol_list():
    """獲取 KOL 列表（含真實統計數據）"""
    logger.info("收到 get_kol_list 請求")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接不可用，返回空數據")
            return {
                "success": False,
                "data": [],
                "count": 0,
                "error": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 使用 LEFT JOIN 計算每個 KOL 的真實統計數據
            query = """
                SELECT
                    k.*,
                    COALESCE(COUNT(p.post_id), 0) as total_posts,
                    COALESCE(COUNT(CASE WHEN p.status = 'published' THEN 1 END), 0) as published_posts,
                    COALESCE(AVG(CASE
                        WHEN p.status = 'published' AND (p.likes + p.comments + p.shares) > 0
                        THEN (p.likes + p.comments + p.shares) * 1.0
                        ELSE NULL
                    END), 0) as avg_interaction_rate
                FROM kol_profiles k
                LEFT JOIN post_records p ON k.serial::integer = p.kol_serial
                GROUP BY k.id, k.serial, k.nickname, k.member_id, k.persona, k.status, k.owner,
                         k.email, k.password, k.whitelist, k.notes, k.post_times, k.target_audience,
                         k.interaction_threshold, k.content_types, k.common_terms, k.colloquial_terms,
                         k.tone_style, k.typing_habit, k.backstory, k.expertise, k.data_source,
                         k.prompt_persona, k.prompt_style, k.prompt_guardrails, k.prompt_skeleton,
                         k.prompt_cta, k.prompt_hashtags, k.signature, k.emoji_pack, k.model_id,
                         k.template_variant, k.model_temp, k.max_tokens, k.title_openers,
                         k.title_signature_patterns, k.title_tail_word, k.title_banned_words,
                         k.title_style_examples, k.title_retry_max, k.tone_formal, k.tone_emotion,
                         k.tone_confidence, k.tone_urgency, k.tone_interaction, k.question_ratio,
                         k.content_length, k.interaction_starters, k.require_finlab_api, k.allow_hashtags,
                         k.created_time, k.last_updated, k.best_performing_post, k.humor_probability,
                         k.humor_enabled, k.content_style_probabilities, k.analysis_depth_probabilities,
                         k.content_length_probabilities
                ORDER BY k.serial
            """
            cursor.execute(query)
            kols = cursor.fetchall()

            logger.info(f"查詢到 {len(kols)} 個 KOL 配置（含統計數據）")

            return {
                "success": True,
                "data": [dict(kol) for kol in kols],
                "count": len(kols),
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"查詢 KOL 列表失敗: {e}")
        return {
            "success": False,
            "data": [],
            "count": 0,
            "error": str(e),
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.get("/api/kol/{serial}")
async def get_kol_detail(serial: str):
    """獲取單個 KOL 的詳細資料（含統計數據）"""
    logger.info(f"收到 get_kol_detail 請求 - Serial: {serial}")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接不可用")
            return {
                "success": False,
                "error": "數據庫連接不可用"
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 查詢單個 KOL 的資料，包含統計數據
            query = """
                SELECT
                    k.*,
                    COALESCE(COUNT(p.post_id), 0) as total_posts,
                    COALESCE(COUNT(CASE WHEN p.status = 'published' THEN 1 END), 0) as published_posts,
                    COALESCE(AVG(CASE
                        WHEN p.status = 'published' AND (p.likes + p.comments + p.shares) > 0
                        THEN (p.likes + p.comments + p.shares) * 1.0
                        ELSE NULL
                    END), 0) as avg_interaction_rate
                FROM kol_profiles k
                LEFT JOIN post_records p ON k.serial::integer = p.kol_serial
                WHERE k.serial = %s
                GROUP BY k.id, k.serial, k.nickname, k.member_id, k.persona, k.status, k.owner,
                         k.email, k.password, k.whitelist, k.notes, k.post_times, k.target_audience,
                         k.interaction_threshold, k.content_types, k.common_terms, k.colloquial_terms,
                         k.tone_style, k.typing_habit, k.backstory, k.expertise, k.data_source,
                         k.prompt_persona, k.prompt_style, k.prompt_guardrails, k.prompt_skeleton,
                         k.prompt_cta, k.prompt_hashtags, k.signature, k.emoji_pack, k.model_id,
                         k.template_variant, k.model_temp, k.max_tokens, k.title_openers,
                         k.title_signature_patterns, k.title_tail_word, k.title_banned_words,
                         k.title_style_examples, k.title_retry_max, k.tone_formal, k.tone_emotion,
                         k.tone_confidence, k.tone_urgency, k.tone_interaction, k.question_ratio,
                         k.content_length, k.interaction_starters, k.require_finlab_api, k.allow_hashtags,
                         k.created_time, k.last_updated, k.best_performing_post, k.humor_probability,
                         k.humor_enabled, k.content_style_probabilities, k.analysis_depth_probabilities,
                         k.content_length_probabilities
            """
            cursor.execute(query, (serial,))
            kol = cursor.fetchone()

            if not kol:
                logger.warning(f"找不到 serial 為 {serial} 的 KOL")
                return {
                    "success": False,
                    "error": f"找不到 serial 為 {serial} 的 KOL"
                }

            logger.info(f"查詢到 KOL: {kol['nickname']}")
            return dict(kol)

    except Exception as e:
        logger.error(f"查詢 KOL 詳情失敗: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.get("/api/kol/weekly-posts")
async def get_weekly_posts():
    """獲取本週發文總數"""
    logger.info("收到 get_weekly_posts 請求")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接不可用，返回空數據")
            return {
                "success": False,
                "weekly_posts": 0,
                "error": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 計算本週發文數（從週一開始）
            query = """
                SELECT COUNT(*) as weekly_posts
                FROM post_records
                WHERE created_at >= date_trunc('week', CURRENT_DATE)
                  AND status = 'published'
            """
            cursor.execute(query)
            result = cursor.fetchone()
            weekly_posts = result[0] if result else 0

            logger.info(f"本週發文數: {weekly_posts}")

            return {
                "success": True,
                "weekly_posts": weekly_posts,
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"查詢本週發文數失敗: {e}")
        return {
            "success": False,
            "weekly_posts": 0,
            "error": str(e),
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.get("/api/dashboard/kols/{serial}/posts")
async def get_kol_posts(serial: str, page: int = 1, page_size: int = 10):
    """獲取 KOL 的發文歷史"""
    logger.info(f"收到 get_kol_posts 請求 - Serial: {serial}, Page: {page}, PageSize: {page_size}")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接不可用")
            return {
                "success": False,
                "error": "數據庫連接不可用"
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Calculate offset
            offset = (page - 1) * page_size

            # Count total posts for this KOL
            count_query = """
                SELECT COUNT(*) as count
                FROM post_records
                WHERE kol_serial = %s
            """
            cursor.execute(count_query, (int(serial),))
            total = cursor.fetchone()['count']

            # Get paginated posts
            query = """
                SELECT
                    post_id,
                    title,
                    content,
                    status,
                    stock_code,
                    created_at,
                    published_at,
                    likes,
                    comments,
                    shares,
                    cmoney_post_url
                FROM post_records
                WHERE kol_serial = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (int(serial), page_size, offset))
            posts = cursor.fetchall()

            logger.info(f"查詢到 {len(posts)} 篇貼文，總數: {total}")

            return {
                "success": True,
                "data": {
                    "posts": [dict(post) for post in posts],
                    "pagination": {
                        "current_page": page,
                        "page_size": page_size,
                        "total_items": total,
                        "total_pages": (total + page_size - 1) // page_size
                    }
                }
            }

    except Exception as e:
        logger.error(f"查詢 KOL 發文歷史失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.get("/api/dashboard/kols/{serial}/interactions")
async def get_kol_interactions(serial: str):
    """獲取 KOL 的互動數據和趨勢"""
    logger.info(f"收到 get_kol_interactions 請求 - Serial: {serial}")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接不可用")
            return {
                "success": False,
                "error": "數據庫連接不可用"
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get interaction trend data (daily aggregation for last 30 days)
            query = """
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as post_count,
                    COALESCE(SUM(likes), 0) as total_likes,
                    COALESCE(SUM(comments), 0) as total_comments,
                    COALESCE(SUM(shares), 0) as total_shares,
                    COALESCE(AVG(likes), 0) as avg_likes,
                    COALESCE(AVG(comments), 0) as avg_comments,
                    COALESCE(AVG(shares), 0) as avg_shares
                FROM post_records
                WHERE kol_serial = %s
                  AND status = 'published'
                  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at) DESC
            """
            cursor.execute(query, (int(serial),))
            trend_data = cursor.fetchall()

            logger.info(f"查詢到 {len(trend_data)} 天的互動數據")

            return {
                "success": True,
                "data": {
                    "interaction_trend": [dict(row) for row in trend_data]
                }
            }

    except Exception as e:
        logger.error(f"查詢 KOL 互動數據失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.post("/api/kol/test-login")
async def test_kol_login(request: Request):
    """
    測試 CMoney 登入並獲取 Bearer Token

    用於在創建 KOL 前驗證帳號密碼是否正確

    Request body:
    - email: CMoney 登入郵箱
    - password: CMoney 登入密碼

    Response:
    - success: bool - 登入是否成功
    - token: str - Bearer token（僅在成功時返回）
    - error: str - 錯誤訊息（僅在失敗時返回）
    """
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {
                "success": False,
                "error": "缺少必填欄位: email, password",
                "timestamp": get_current_time().isoformat()
            }

        # 將 src 路徑加入 Python path
        src_path = '/app/src'
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
        cmoney_client = CMoneyClient()

        # 嘗試登入
        credentials = LoginCredentials(email=email, password=password)
        try:
            access_token = await cmoney_client.login(credentials)
            logger.info(f"✅ 測試登入成功: {email}")

            return {
                "success": True,
                "token": access_token.token,
                "message": "登入成功，Bearer Token 已獲取",
                "timestamp": get_current_time().isoformat()
            }
        except Exception as login_error:
            logger.error(f"❌ 測試登入失敗: {login_error}")
            return {
                "success": False,
                "error": f"登入失敗: {str(login_error)}",
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"❌ test_kol_login 異常: {e}")
        return {
            "success": False,
            "error": f"測試登入時發生異常: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }


@app.post("/api/kol/test-nickname")
async def test_kol_nickname(request: Request):
    """
    測試 CMoney 暱稱更新

    用於在創建 KOL 前驗證暱稱是否可用

    Request body:
    - email: CMoney 登入郵箱
    - password: CMoney 登入密碼
    - nickname: 期望的暱稱

    Response:
    - success: bool - 暱稱更新是否成功
    - new_nickname: str - 實際更新後的暱稱（僅在成功時返回）
    - error: str - 錯誤訊息（僅在失敗時返回）
    """
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        nickname = data.get("nickname")

        if not email or not password or not nickname:
            return {
                "success": False,
                "error": "缺少必填欄位: email, password, nickname",
                "timestamp": get_current_time().isoformat()
            }

        # 將 src 路徑加入 Python path
        src_path = '/app/src'
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
        cmoney_client = CMoneyClient()

        # 先登入獲取 token
        credentials = LoginCredentials(email=email, password=password)
        try:
            access_token = await cmoney_client.login(credentials)
            logger.info(f"✅ 測試登入成功: {email}")
        except Exception as login_error:
            logger.error(f"❌ 測試登入失敗: {login_error}")
            return {
                "success": False,
                "error": f"登入失敗: {str(login_error)}",
                "timestamp": get_current_time().isoformat()
            }

        # 嘗試更新暱稱
        try:
            nickname_result = await cmoney_client.update_nickname(access_token.token, nickname)

            if not nickname_result.success:
                logger.warning(f"⚠️ 測試暱稱更新失敗: {nickname_result.error_message}")
                return {
                    "success": False,
                    "error": f"暱稱更新失敗: {nickname_result.error_message}",
                    "detail": "暱稱可能已被使用，請嘗試其他暱稱",
                    "timestamp": get_current_time().isoformat()
                }

            logger.info(f"✅ 測試暱稱更新成功: {nickname}")
            return {
                "success": True,
                "new_nickname": nickname_result.new_nickname or nickname,
                "message": "暱稱更新成功",
                "timestamp": get_current_time().isoformat()
            }

        except Exception as nickname_error:
            logger.error(f"❌ 測試暱稱更新異常: {nickname_error}")
            return {
                "success": False,
                "error": f"暱稱更新時發生異常: {str(nickname_error)}",
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"❌ test_kol_nickname 異常: {e}")
        return {
            "success": False,
            "error": f"測試暱稱時發生異常: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }


@app.post("/api/kol/create")
async def create_kol(request: Request):
    """
    創建新的 KOL 角色

    Phase 1: 基本資訊（必填）
    - email: CMoney 登入郵箱
    - password: CMoney 登入密碼
    - nickname: 期望的 KOL 暱稱

    Phase 2: AI 生成個性化資料（選填）
    - ai_description: 1000字以內的 KOL 描述，用於 AI 生成個性化欄位
    """
    logger.info("收到 create_kol 請求")

    conn = None
    try:
        # 解析請求數據
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        nickname = data.get("nickname")
        member_id_from_user = data.get("member_id", "")  # 用戶手動輸入的 member_id（選填）
        ai_description = data.get("ai_description", "")  # AI 描述（選填）
        model_id = data.get("model_id", "gpt-4o-mini")  # AI 模型 ID

        # Prompt 欄位（Phase 1: 手動填寫）
        prompt_persona = data.get("prompt_persona", "")
        prompt_style = data.get("prompt_style", "")
        prompt_guardrails = data.get("prompt_guardrails", "")
        prompt_skeleton = data.get("prompt_skeleton", "")

        logger.info(f"📝 收到創建 KOL 請求: email={email}, nickname={nickname}, member_id={member_id_from_user or '(未提供)'}")
        logger.info(f"📝 Prompt 欄位: persona={bool(prompt_persona)}, style={bool(prompt_style)}, guardrails={bool(prompt_guardrails)}, skeleton={bool(prompt_skeleton)}")

        # 驗證必填欄位
        if not email or not password or not nickname:
            logger.error("❌ 缺少必填欄位")
            return {
                "success": False,
                "error": "缺少必填欄位: email, password, nickname",
                "timestamp": get_current_time().isoformat()
            }

        # 檢查數據庫連接
        if not db_pool:
            return {
                "success": False,
                "error": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        # Phase 1: 使用 CMoney API 登入並更新暱稱
        logger.info(f"📝 Phase 1: 嘗試使用 {email} 登入 CMoney 並更新暱稱為 {nickname}")

        # 將 src 路徑加入 Python path
        src_path = '/app/src'
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
        cmoney_client = CMoneyClient()

        # 登入 CMoney
        credentials = LoginCredentials(email=email, password=password)
        try:
            access_token = await cmoney_client.login(credentials)
            logger.info(f"✅ CMoney 登入成功: {email}")
        except Exception as login_error:
            logger.error(f"❌ CMoney 登入失敗: {login_error}")
            return {
                "success": False,
                "error": f"CMoney 登入失敗: {str(login_error)}",
                "phase": "login",
                "timestamp": get_current_time().isoformat()
            }

        # 嘗試更新暱稱
        try:
            nickname_result = await cmoney_client.update_nickname(access_token.token, nickname)

            if not nickname_result.success:
                logger.warning(f"⚠️ 暱稱更新失敗: {nickname_result.error_message}")
                return {
                    "success": False,
                    "error": f"暱稱更新失敗: {nickname_result.error_message}",
                    "phase": "nickname_update",
                    "detail": "可能是暱稱已被使用，請嘗試其他暱稱",
                    "timestamp": get_current_time().isoformat()
                }

            logger.info(f"✅ 暱稱更新成功: {nickname}")
            actual_nickname = nickname_result.new_nickname or nickname

        except Exception as nickname_error:
            logger.error(f"❌ 暱稱更新異常: {nickname_error}")
            return {
                "success": False,
                "error": f"暱稱更新異常: {str(nickname_error)}",
                "phase": "nickname_update",
                "timestamp": get_current_time().isoformat()
            }

        # 獲取會員資訊（獲取 member_id）
        logger.info("📝 處理 CMoney 會員 ID...")
        member_id = member_id_from_user  # 優先使用用戶提供的 member_id

        if not member_id:
            # 如果用戶沒有提供，嘗試從 CMoney API 獲取
            try:
                # 使用 CMoney API 獲取當前用戶的會員資訊
                # TODO: 實現 get_current_member_info 方法或從 token 解析 member_id
                member_id = ""  # 暫時設為空，後續可以通過其他 API 獲取
                logger.info(f"✅ 從 API 獲取會員 ID: {member_id or '(無法獲取)'}")
            except Exception as member_error:
                logger.warning(f"⚠️ 從 API 獲取會員資訊失敗: {member_error}")
                # 不阻斷流程，繼續創建
        else:
            logger.info(f"✅ 使用用戶提供的會員 ID: {member_id}")

        # Phase 2: AI 生成個性化資料（如果提供了 ai_description）
        ai_generated_profile = {}
        if ai_description and gpt_generator:
            logger.info(f"🤖 Phase 2: 使用 AI 生成個性化資料...")
            try:
                # 準備 AI prompt
                ai_prompt = f"""
                根據以下描述，為這個 KOL 生成完整的個性化設定。請以 JSON 格式返回，包含以下欄位：

                KOL 描述：
                {ai_description}

                請生成以下欄位的值：
                - persona: 人設類型（fundamental/technical/news/casual 之一）
                - target_audience: 目標受眾
                - expertise: 專業領域
                - backstory: 背景故事（50-100字）
                - tone_style: 語氣風格描述
                - typing_habit: 打字習慣描述
                - common_terms: 常用術語（逗號分隔）
                - colloquial_terms: 口語用詞（逗號分隔）
                - signature: 個人簽名
                - emoji_pack: 常用表情符號（逗號分隔）
                - tone_formal: 正式程度（1-10）
                - tone_emotion: 情感程度（1-10）
                - tone_confidence: 自信程度（1-10）
                - tone_urgency: 緊急程度（1-10）
                - tone_interaction: 互動程度（1-10）
                - question_ratio: 問題比例（0.0-1.0）
                - content_length: 內容長度偏好（short/medium/long）

                請確保返回的是有效的 JSON 格式。
                """

                # 調用 GPT 生成
                import openai
                openai.api_key = os.getenv("OPENAI_API_KEY")

                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "你是一個專業的 KOL 人設設計師，擅長根據描述生成完整的 KOL 個性化設定。"},
                        {"role": "user", "content": ai_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )

                # 解析 AI 回應
                ai_response = response.choices[0].message.content
                import json
                ai_generated_profile = json.loads(ai_response)
                logger.info(f"✅ AI 個性化資料生成成功")

            except Exception as ai_error:
                logger.warning(f"⚠️ AI 生成失敗: {ai_error}，使用預設值")
                # AI 生成失敗不阻斷流程，使用預設值

        # 準備寫入數據庫的資料
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 🔥 FIX: Extract serial from email (format: forum_XXX@cmoney.com.tw)
            import re
            email_pattern = r'forum_(\d+)@cmoney\.com\.tw'
            match = re.match(email_pattern, email)

            if not match:
                logger.error(f"❌ 郵箱格式錯誤: {email}，應為 forum_XXX@cmoney.com.tw")
                return {
                    "success": False,
                    "error": f"郵箱格式錯誤，應為 forum_XXX@cmoney.com.tw 格式（例如：forum_200@cmoney.com.tw）",
                    "phase": "validation",
                    "timestamp": get_current_time().isoformat()
                }

            next_serial = int(match.group(1))  # Extract serial from email
            logger.info(f"✅ 從郵箱提取 KOL serial: {next_serial} (email: {email})")

            # Check if serial already exists
            cursor.execute("SELECT serial FROM kol_profiles WHERE serial = %s", (str(next_serial),))
            existing = cursor.fetchone()
            if existing:
                logger.error(f"❌ KOL serial {next_serial} 已存在")
                return {
                    "success": False,
                    "error": f"KOL serial {next_serial} 已存在，請使用不同的郵箱",
                    "phase": "validation",
                    "timestamp": get_current_time().isoformat()
                }

            # 合併 AI 生成的值和預設值
            persona = ai_generated_profile.get("persona", "casual")
            target_audience = ai_generated_profile.get("target_audience", "一般投資者")
            expertise = ai_generated_profile.get("expertise", "")
            backstory = ai_generated_profile.get("backstory", "")
            tone_style = ai_generated_profile.get("tone_style", "友善、親切")
            typing_habit = ai_generated_profile.get("typing_habit", "正常")
            common_terms = ai_generated_profile.get("common_terms", "")
            colloquial_terms = ai_generated_profile.get("colloquial_terms", "")
            signature = ai_generated_profile.get("signature", "")
            emoji_pack = ai_generated_profile.get("emoji_pack", "😊,👍,💪")
            tone_formal = ai_generated_profile.get("tone_formal", 5)
            tone_emotion = ai_generated_profile.get("tone_emotion", 5)
            tone_confidence = ai_generated_profile.get("tone_confidence", 7)
            tone_urgency = ai_generated_profile.get("tone_urgency", 5)
            tone_interaction = ai_generated_profile.get("tone_interaction", 7)
            question_ratio = ai_generated_profile.get("question_ratio", 0.3)
            content_length = ai_generated_profile.get("content_length", "medium")

            # 插入新的 KOL 到數據庫
            insert_sql = """
                INSERT INTO kol_profiles (
                    serial, nickname, member_id, persona, status, owner, email, password,
                    whitelist, notes, post_times, target_audience, interaction_threshold,
                    common_terms, colloquial_terms, tone_style, typing_habit, backstory,
                    expertise, signature, emoji_pack, tone_formal, tone_emotion,
                    tone_confidence, tone_urgency, tone_interaction, question_ratio,
                    content_length, model_id,
                    prompt_persona, prompt_style, prompt_guardrails, prompt_skeleton,
                    created_time, last_updated
                ) VALUES (
                    %s, %s, %s, %s, 'active', 'system', %s, %s,
                    true, '通過 API 創建', '09:00,12:00,15:00', %s, 0,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s, %s,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
                RETURNING serial, nickname, member_id, persona, email
            """

            cursor.execute(insert_sql, (
                next_serial, actual_nickname, member_id, persona, email, password,
                target_audience, common_terms, colloquial_terms, tone_style, typing_habit, backstory,
                expertise, signature, emoji_pack, tone_formal, tone_emotion,
                tone_confidence, tone_urgency, tone_interaction, question_ratio,
                content_length, model_id,
                prompt_persona, prompt_style, prompt_guardrails, prompt_skeleton
            ))

            new_kol = cursor.fetchone()
            conn.commit()

            logger.info(f"✅ KOL 創建成功: Serial={new_kol['serial']}, Nickname={new_kol['nickname']}")

            return {
                "success": True,
                "message": "KOL 創建成功",
                "data": {
                    "serial": new_kol['serial'],
                    "nickname": new_kol['nickname'],
                    "member_id": new_kol['member_id'],
                    "persona": new_kol['persona'],
                    "email": new_kol['email'],
                    "ai_generated": bool(ai_description and gpt_generator),
                    "ai_profile": ai_generated_profile if ai_generated_profile else None
                },
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"❌ 創建 KOL 失敗: {e}")
        import traceback
        logger.error(f"❌ 完整錯誤堆疊: {traceback.format_exc()}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "error": f"創建 KOL 失敗: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.delete("/api/kol/{serial}")
async def delete_kol(serial: str):
    """
    刪除 KOL 角色

    Parameters:
    - serial: KOL 序號

    Response:
    - success: bool - 是否刪除成功
    - message: str - 成功訊息
    - error: str - 錯誤訊息（僅在失敗時返回）
    """
    logger.info(f"收到刪除 KOL 請求: serial={serial}")

    conn = None
    try:
        # 檢查數據庫連接
        if not db_pool:
            logger.warning("數據庫連接不可用")
            return {
                "success": False,
                "error": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 檢查 KOL 是否存在
            cursor.execute("SELECT serial, nickname FROM kol_profiles WHERE serial = %s", (serial,))
            existing_kol = cursor.fetchone()

            if not existing_kol:
                logger.warning(f"⚠️ KOL serial {serial} 不存在")
                return {
                    "success": False,
                    "error": f"KOL serial {serial} 不存在",
                    "timestamp": get_current_time().isoformat()
                }

            # 執行刪除
            cursor.execute("DELETE FROM kol_profiles WHERE serial = %s", (serial,))
            conn.commit()

            logger.info(f"✅ KOL 刪除成功: Serial={serial}, Nickname={existing_kol['nickname']}")

            return {
                "success": True,
                "message": f"KOL 刪除成功 (Serial: {serial}, Nickname: {existing_kol['nickname']})",
                "deleted_kol": {
                    "serial": existing_kol['serial'],
                    "nickname": existing_kol['nickname']
                },
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"❌ 刪除 KOL 失敗: {e}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "error": f"刪除 KOL 失敗: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)

@app.put("/api/kol/{serial}/personalization")
async def update_kol_personalization(serial: str, request: Request):
    """
    更新 KOL 個人化設定（內容風格、分析深度、內容長度的機率分布）

    Parameters:
    - serial: KOL 序號
    - request body: {
        content_style_probabilities: dict,
        analysis_depth_probabilities: dict,
        content_length_probabilities: dict
      }
    """
    logger.info(f"收到更新 KOL 個人化設定請求: serial={serial}")

    conn = None
    try:
        data = await request.json()
        logger.info(f"接收到個人化設定: {data}")

        # 檢查數據庫連接
        if not db_pool:
            logger.warning("數據庫連接不可用")
            return {
                "success": False,
                "error": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 檢查 KOL 是否存在
            cursor.execute("SELECT serial, nickname FROM kol_profiles WHERE serial = %s", (serial,))
            existing_kol = cursor.fetchone()

            if not existing_kol:
                logger.warning(f"⚠️ KOL serial {serial} 不存在")
                return {
                    "success": False,
                    "error": f"KOL serial {serial} 不存在",
                    "timestamp": get_current_time().isoformat()
                }

            # 提取個人化設定
            content_style_probabilities = data.get('content_style_probabilities', {})
            analysis_depth_probabilities = data.get('analysis_depth_probabilities', {})
            content_length_probabilities = data.get('content_length_probabilities', {})

            # 更新 KOL 個人化設定
            import json
            update_sql = """
                UPDATE kol_profiles
                SET content_style_probabilities = %s,
                    analysis_depth_probabilities = %s,
                    content_length_probabilities = %s,
                    last_updated = NOW()
                WHERE serial = %s
            """
            cursor.execute(update_sql, (
                json.dumps(content_style_probabilities),
                json.dumps(analysis_depth_probabilities),
                json.dumps(content_length_probabilities),
                serial
            ))
            conn.commit()

            logger.info(f"✅ KOL 個人化設定更新成功: Serial={serial}, Nickname={existing_kol['nickname']}")

            return {
                "success": True,
                "message": f"KOL 個人化設定更新成功 (Serial: {serial}, Nickname: {existing_kol['nickname']})",
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"❌ 更新 KOL 個人化設定失敗: {e}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "error": f"更新失敗: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)


# ==================== Schedule API 功能 ====================

@app.get("/api/schedule/tasks")
async def get_schedule_tasks(
    status: str = Query(None, description="狀態篩選"),
    limit: int = Query(100, description="返回的記錄數")
):
    """獲取排程任務列表"""
    logger.info(f"收到 get_schedule_tasks 請求: status={status}, limit={limit}")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接不可用，返回空數據")
            return {
                "success": False,
                "tasks": [],
                "count": 0,
                "error": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        conn.rollback()  # Clear any failed transactions

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM schedule_tasks"
            params = []

            if status:
                query += " WHERE status = %s"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            logger.info(f"執行 SQL 查詢: {query} with params: {params}")
            cursor.execute(query, params)
            tasks = cursor.fetchall()

            logger.info(f"查詢到 {len(tasks)} 個排程任務")

            conn.commit()

            # 🔥 FIX: Handle JSON fields (JSONB or TEXT types)
            import json
            parsed_tasks = []
            for task in tasks:
                task_dict = dict(task)

                # Parse JSON fields - handle both JSONB (already dict) and TEXT (needs parsing)
                json_fields = ['trigger_config', 'schedule_config', 'batch_info', 'generation_config']
                for field in json_fields:
                    field_value = task_dict.get(field)
                    if field_value:
                        # If already a dict (JSONB type from PostgreSQL), keep as is
                        if isinstance(field_value, dict):
                            continue
                        # If string (TEXT type), parse it
                        elif isinstance(field_value, str):
                            try:
                                task_dict[field] = json.loads(field_value)
                            except (json.JSONDecodeError, TypeError) as e:
                                logger.warning(f"Failed to parse {field} for task {task_dict.get('schedule_id')}: {e}")
                                task_dict[field] = None

                # 🔥 FIX: Add display-friendly fields to help frontend
                # Extract stock_sorting for easier display
                if task_dict.get('generation_config'):
                    gen_config = task_dict['generation_config']
                    # Ensure gen_config is a dict
                    if isinstance(gen_config, dict):
                        stock_sorting = gen_config.get('stock_sorting', {})
                        # Ensure stock_sorting is a dict before accessing .get()
                        if isinstance(stock_sorting, dict):
                            task_dict['stock_sorting_display'] = {
                                'method': stock_sorting.get('method', 'none'),
                                'direction': stock_sorting.get('direction', 'desc'),
                                'label': _get_sorting_label(stock_sorting)
                            }
                        else:
                            # Fallback for non-dict stock_sorting
                            task_dict['stock_sorting_display'] = {
                                'method': 'none',
                                'direction': 'desc',
                                'label': '隨機排序'
                            }

                # Ensure daily_execution_time is present (for frontend compatibility)
                if not task_dict.get('daily_execution_time') and task_dict.get('schedule_config'):
                    # Try to extract from schedule_config.posting_time_slots
                    schedule_config = task_dict['schedule_config']
                    if isinstance(schedule_config, dict):
                        posting_time_slots = schedule_config.get('posting_time_slots', [])
                        if posting_time_slots and len(posting_time_slots) > 0:
                            task_dict['daily_execution_time'] = posting_time_slots[0]

                parsed_tasks.append(task_dict)

            return {
                "success": True,
                "tasks": parsed_tasks,
                "count": len(tasks),
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"查詢排程任務失敗: {e}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "tasks": [],
            "count": 0,
            "error": str(e),
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)

@app.get("/api/schedule/daily-stats")
async def get_daily_stats():
    """獲取每日排程統計"""
    logger.info("收到 get_daily_stats 請求")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接不可用")
            return {
                "success": False,
                "data": {},
                "error": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        conn.rollback()  # Clear any failed transactions

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get today's date range
            today_start = get_current_time().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = get_current_time().replace(hour=23, minute=59, second=59, microsecond=999999)

            # Count total posts generated today from schedule_tasks
            cursor.execute("""
                SELECT COALESCE(SUM(total_posts_generated), 0) as today_posts
                FROM schedule_tasks
                WHERE last_run >= %s AND last_run <= %s
            """, (today_start, today_end))
            today_posts = cursor.fetchone()['today_posts']

            # Count scheduled posts (active schedules with next_run in future)
            cursor.execute("""
                SELECT COUNT(*) as scheduled_posts
                FROM schedule_tasks
                WHERE status = 'active' AND next_run > NOW()
            """)
            scheduled_posts = cursor.fetchone()['scheduled_posts']

            # Count completed posts today (schedules that completed today)
            cursor.execute("""
                SELECT COALESCE(SUM(success_count), 0) as completed_posts
                FROM schedule_tasks
                WHERE last_run >= %s AND last_run <= %s
            """, (today_start, today_end))
            completed_posts = cursor.fetchone()['completed_posts']

            # Count failed posts today
            cursor.execute("""
                SELECT COALESCE(SUM(failure_count), 0) as failed_posts
                FROM schedule_tasks
                WHERE last_run >= %s AND last_run <= %s
            """, (today_start, today_end))
            failed_posts = cursor.fetchone()['failed_posts']

            # Count active schedules
            cursor.execute("""
                SELECT COUNT(*) as active_schedules
                FROM schedule_tasks
                WHERE status = 'active'
            """)
            active_schedules = cursor.fetchone()['active_schedules']

            # Count total schedules
            cursor.execute("SELECT COUNT(*) as total_schedules FROM schedule_tasks")
            total_schedules = cursor.fetchone()['total_schedules']

            conn.commit()

            result = {
                "success": True,
                "data": {
                    "today_posts": int(today_posts),
                    "scheduled_posts": int(scheduled_posts),
                    "completed_posts": int(completed_posts),
                    "failed_posts": int(failed_posts),
                    "active_schedules": int(active_schedules),
                    "total_schedules": int(total_schedules)
                },
                "timestamp": get_current_time().isoformat()
            }

            logger.info(f"返回每日排程統計數據: {result['data']}")
            return result

    except Exception as e:
        logger.error(f"查詢每日統計失敗: {e}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "data": {},
            "error": str(e),
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)

@app.get("/api/schedule/scheduler/status")
async def get_scheduler_status():
    """獲取排程器狀態"""
    logger.info("收到 get_scheduler_status 請求")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接池不可用")
            return {
                "success": False,
                "data": {},
                "error": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        # Get connection from pool
        conn = get_db_connection()

        # Reset connection if in failed state
        conn.rollback()

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Count active tasks (status='active')
            cursor.execute("""
                SELECT COUNT(*) as active_tasks
                FROM schedule_tasks
                WHERE status = 'active'
            """)
            active_tasks = cursor.fetchone()['active_tasks']

            # Count pending tasks (status='pending' or next_run is in the future)
            cursor.execute("""
                SELECT COUNT(*) as pending_tasks
                FROM schedule_tasks
                WHERE status = 'pending' OR (status = 'active' AND next_run > NOW())
            """)
            pending_tasks = cursor.fetchone()['pending_tasks']

            # Get next run time (earliest next_run from active schedules)
            cursor.execute("""
                SELECT MIN(next_run) as next_run
                FROM schedule_tasks
                WHERE status = 'active' AND next_run IS NOT NULL
            """)
            next_run_row = cursor.fetchone()
            next_run = next_run_row['next_run'].isoformat() if next_run_row['next_run'] else None

            # Get last run time (most recent last_run)
            cursor.execute("""
                SELECT MAX(last_run) as last_run
                FROM schedule_tasks
                WHERE last_run IS NOT NULL
            """)
            last_run_row = cursor.fetchone()
            last_run = last_run_row['last_run'].isoformat() if last_run_row['last_run'] else None

            # Calculate uptime from earliest started_at
            cursor.execute("""
                SELECT MIN(started_at) as earliest_start
                FROM schedule_tasks
                WHERE started_at IS NOT NULL
            """)
            earliest_start_row = cursor.fetchone()
            uptime = "N/A"
            if earliest_start_row['earliest_start']:
                # Ensure both datetimes are timezone-aware to avoid subtraction error
                earliest_start = earliest_start_row['earliest_start']
                if earliest_start.tzinfo is None:
                    # Database returns naive datetime, assume it's UTC and convert to Taipei
                    tz = pytz.timezone('Asia/Taipei')
                    earliest_start = pytz.utc.localize(earliest_start).astimezone(tz)

                uptime_delta = get_current_time() - earliest_start
                days = uptime_delta.days
                hours = uptime_delta.seconds // 3600
                uptime = f"{days} days, {hours} hours"

            # Determine overall status based on active tasks
            status = "running" if active_tasks > 0 else "idle"

            result = {
                "success": True,
                "data": {
                    "status": status,
                    "active_tasks": int(active_tasks),
                    "pending_tasks": int(pending_tasks),
                    "next_run": next_run,
                    "last_run": last_run,
                    "uptime": uptime
                },
                "timestamp": get_current_time().isoformat()
            }

            conn.commit()  # Commit transaction
            logger.info(f"返回排程器狀態數據: {result['data']}")
            return result

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"查詢排程器狀態失敗: {e}")
        return {
            "success": False,
            "data": {},
            "error": str(e),
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/api/schedule/scheduler/start")
async def start_scheduler():
    """啟動全局排程器 - 將所有 paused 狀態的任務設置為 active"""
    logger.info("收到 start_scheduler 請求 - 啟動全局排程器")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接不可用")
            return {
                "success": False,
                "message": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        conn.rollback()  # Clear any failed transactions

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Update all paused tasks to active
            cursor.execute("""
                UPDATE schedule_tasks
                SET status = 'active', updated_at = NOW()
                WHERE status = 'paused'
                RETURNING schedule_id, schedule_name, schedule_type
            """)
            activated_tasks = cursor.fetchall()

            conn.commit()

            logger.info(f"全局排程器已啟動，激活了 {len(activated_tasks)} 個任務")

            return {
                "success": True,
                "message": f"全局排程器已啟動，激活了 {len(activated_tasks)} 個任務",
                "activated_count": len(activated_tasks),
                "activated_tasks": [dict(task) for task in activated_tasks],
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"啟動全局排程器失敗: {e}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "message": f"啟動失敗: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/api/schedule/scheduler/stop")
async def stop_scheduler():
    """停止全局排程器 - 將所有 active 狀態的任務設置為 paused"""
    logger.info("收到 stop_scheduler 請求 - 停止全局排程器")

    conn = None
    try:
        if not db_pool:
            logger.warning("數據庫連接不可用")
            return {
                "success": False,
                "message": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        conn.rollback()  # Clear any failed transactions

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Update all active tasks to paused
            cursor.execute("""
                UPDATE schedule_tasks
                SET status = 'paused', updated_at = NOW()
                WHERE status = 'active'
                RETURNING schedule_id, schedule_name, schedule_type
            """)
            paused_tasks = cursor.fetchall()

            conn.commit()

            logger.info(f"全局排程器已停止，暫停了 {len(paused_tasks)} 個任務")

            return {
                "success": True,
                "message": f"全局排程器已停止，暫停了 {len(paused_tasks)} 個任務",
                "paused_count": len(paused_tasks),
                "paused_tasks": [dict(task) for task in paused_tasks],
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"停止全局排程器失敗: {e}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "message": f"停止失敗: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/api/schedule/create")
async def create_schedule(request: Request):
    """創建新的排程任務"""
    logger.info("收到 create_schedule 請求")

    conn = None
    try:
        data = await request.json()
        logger.info(f"接收到排程配置: {data}")

        if not db_pool:
            logger.warning("數據庫連接不可用")
            return {
                "success": False,
                "message": "數據庫連接不可用",
                "timestamp": get_current_time().isoformat()
            }

        conn = get_db_connection()
        conn.rollback()  # Clear any failed transactions

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # 生成唯一的 task_id (UUID)
            import uuid
            task_id = str(uuid.uuid4())

            # 從請求中提取字段
            schedule_name = data.get('schedule_name', 'Unnamed Schedule')
            schedule_description = data.get('schedule_description', '')
            schedule_type = data.get('schedule_type', 'weekday_daily')
            interval_seconds = data.get('interval_seconds', 300)
            enabled = data.get('enabled', True)
            timezone = data.get('timezone', 'Asia/Taipei')
            weekdays_only = data.get('weekdays_only', True)
            auto_posting = data.get('auto_posting', False)
            max_posts_per_hour = data.get('max_posts_per_hour', 2)

            # 生成配置 (generation_config)
            generation_config = data.get('generation_config', {})

            # 🔥 FIX: Extract correct parameters from full_triggers_config
            schedule_config_data = data.get('schedule_config', {})
            full_triggers_config = schedule_config_data.get('full_triggers_config', {})

            # Map stockCountLimit → max_stocks
            if 'stockCountLimit' in full_triggers_config:
                generation_config['max_stocks'] = full_triggers_config['stockCountLimit']
                logger.info(f"🔧 Mapped stockCountLimit={full_triggers_config['stockCountLimit']} → max_stocks")

            # Map stockFilterCriteria → stock_sorting
            if 'stockFilterCriteria' in full_triggers_config and full_triggers_config['stockFilterCriteria']:
                criteria_list = full_triggers_config['stockFilterCriteria']
                if isinstance(criteria_list, list) and len(criteria_list) > 0:
                    # Map the first criteria to stock_sorting
                    criteria_map = {
                        'five_day_gain': 'five_day_change_desc',
                        'five_day_loss': 'five_day_loss_desc',
                        'daily_gain': 'daily_change_desc',
                        'daily_loss': 'daily_change_asc',
                        'volume_high': 'volume_desc',
                        'volume_low': 'volume_asc'
                    }
                    first_criteria = criteria_list[0]
                    stock_sorting = criteria_map.get(first_criteria, first_criteria)
                    generation_config['stock_sorting'] = stock_sorting
                    logger.info(f"🔧 Mapped stockFilterCriteria={first_criteria} → stock_sorting={stock_sorting}")

            # Extract daily_execution_time first (needed for next_run calculation later)
            daily_execution_time = data.get('daily_execution_time')

            # 🔥 DEBUG: Log what frontend sent
            logger.info(f"🔍 Frontend sent trigger_config type: {type(data.get('trigger_config'))}")
            logger.info(f"🔍 Frontend sent trigger_config: {data.get('trigger_config')}")
            logger.info(f"🔍 Frontend sent schedule_config type: {type(data.get('schedule_config'))}")
            logger.info(f"🔍 Frontend sent schedule_config: {str(data.get('schedule_config'))[:500]}")

            # 🔥 FIX: Use trigger_config from frontend if provided AND not empty
            trigger_config = data.get('trigger_config')
            # Check if trigger_config is None or empty dict (both should use fallback)
            if not trigger_config or (isinstance(trigger_config, dict) and len(trigger_config) == 0):
                # Fallback: Build from generation_config for backward compatibility
                trigger_type = generation_config.get('trigger_type', 'limit_up_after_hours')
                stock_sorting = generation_config.get('stock_sorting', {})
                kol_assignment = generation_config.get('kol_assignment', 'random')
                max_stocks = generation_config.get('max_stocks', 5)

                trigger_config = {
                    "trigger_type": trigger_type,
                    "stock_codes": [],  # 將由排程器執行時根據觸發器動態獲取
                    "kol_assignment": kol_assignment,
                    "max_stocks": max_stocks,
                    "stock_sorting": stock_sorting
                }
            else:
                # 🔥 FIX: Ensure trigger_config uses the correct max_stocks from stockCountLimit
                if 'stockCountLimit' in full_triggers_config:
                    trigger_config['max_stocks'] = full_triggers_config['stockCountLimit']
                    logger.info(f"🔧 Updated trigger_config.max_stocks={full_triggers_config['stockCountLimit']}")

            # 🔥 FIX: Use schedule_config from frontend if provided, otherwise build from data
            schedule_config = data.get('schedule_config')
            if not schedule_config:
                # Fallback: Build from daily_execution_time for backward compatibility
                posting_time_slots = [daily_execution_time] if daily_execution_time else []

                schedule_config = {
                    "enabled": enabled,
                    "posting_time_slots": posting_time_slots,
                    "timezone": timezone,
                    "weekdays_only": weekdays_only
                }

            # Log what we're storing
            logger.info(f"📝 Storing trigger_config: {str(trigger_config)[:200]}...")
            logger.info(f"📝 Storing schedule_config: {str(schedule_config)[:200]}...")

            # 批次信息 (batch_info)
            batch_info = data.get('batch_info', {})
            session_id = data.get('session_id')
            if session_id:
                batch_info['session_id'] = str(session_id)

            # 計算下次執行時間 (next_run)
            from datetime import datetime, timedelta
            import pytz

            now = datetime.now(pytz.timezone(timezone))
            next_run = None

            if daily_execution_time and enabled:
                # 解析時間 (HH:mm 格式)
                time_parts = daily_execution_time.split(':')
                if len(time_parts) == 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])

                    # 創建今天的執行時間
                    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                    # 如果今天的時間已過，設置為明天
                    if next_run <= now:
                        next_run = next_run + timedelta(days=1)

                    # 如果是工作日模式，跳過週末
                    if weekdays_only:
                        while next_run.weekday() >= 5:  # 5=Saturday, 6=Sunday
                            next_run = next_run + timedelta(days=1)

            # 插入排程任務到資料庫
            insert_sql = """
                INSERT INTO schedule_tasks (
                    schedule_id, schedule_name, schedule_description, status, schedule_type,
                    interval_seconds, auto_posting, max_posts_per_hour,
                    timezone, weekdays_only, daily_execution_time, batch_info, generation_config,
                    trigger_config, schedule_config,
                    next_run, created_at, updated_at,
                    run_count, success_count, failure_count
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s,
                    %s, NOW(), NOW(),
                    0, 0, 0
                )
                RETURNING schedule_id, schedule_name, status, next_run, created_at
            """

            status = 'active' if enabled else 'paused'

            import json
            cursor.execute(insert_sql, (
                task_id,  # This maps to schedule_id column
                schedule_name,
                schedule_description,
                status,
                schedule_type,
                interval_seconds,
                auto_posting,
                max_posts_per_hour,
                timezone,
                weekdays_only,
                daily_execution_time,  # 🔥 FIX: Add daily_execution_time
                json.dumps(batch_info),
                json.dumps(generation_config),
                json.dumps(trigger_config),  # 🔥 FIX: Add trigger_config
                json.dumps(schedule_config),  # 🔥 FIX: Add schedule_config
                next_run
            ))

            result = cursor.fetchone()
            conn.commit()

            logger.info(f"排程創建成功: schedule_id={task_id}, name={schedule_name}")

            return {
                "success": True,
                "message": "排程創建成功",
                "task_id": result['schedule_id'],  # Return as task_id for backwards compatibility
                "task_name": result['schedule_name'],
                "status": result['status'],
                "next_run": result['next_run'].isoformat() if result['next_run'] else None,
                "created_at": result['created_at'].isoformat(),
                "timestamp": get_current_time().isoformat()
            }

    except Exception as e:
        logger.error(f"創建排程失敗: {e}")
        logger.error(f"錯誤詳情: {traceback.format_exc()}")
        if conn:
            conn.rollback()
        return {
            "success": False,
            "message": f"創建失敗: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)

@app.post("/api/schedule/{task_id}/auto-posting")
async def toggle_auto_posting(task_id: str, request: Request):
    """切換排程的自動發文功能"""
    logger.info(f"收到 toggle_auto_posting 請求 - Task ID: {task_id}")

    conn = None
    try:
        body = await request.json()
        enabled = body.get('enabled', False)

        logger.info(f"設定自動發文: {enabled}")

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE schedule_tasks
                SET auto_posting = %s, updated_at = NOW()
                WHERE schedule_id = %s
            """, (enabled, task_id))

            conn.commit()

            if cursor.rowcount == 0:
                raise ValueError(f"Schedule {task_id} not found")

            logger.info(f"✅ 自動發文設定更新成功 - Task ID: {task_id}, enabled={enabled}")

        return {
            "success": True,
            "task_id": task_id,
            "message": f"自動發文已{'開啟' if enabled else '關閉'}",
            "enabled": enabled
        }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 更新自動發文設定失敗: {e}")
        return {
            "success": False,
            "message": f"更新失敗: {str(e)}",
            "timestamp": get_current_time().isoformat()
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.post("/api/schedule/execute/{task_id}")
async def execute_schedule_now(task_id: str, request: Request):
    """
    立即執行排程 (手動觸發)
    Execute a schedule immediately without waiting for scheduled time
    """
    logger.info(f"收到立即執行排程請求 - Task ID: {task_id}")

    conn = None
    try:
        if not db_pool:
            return {
                "success": False,
                "error": "數據庫連接不可用"
            }

        # Get schedule details from database
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT *
                FROM schedule_tasks
                WHERE schedule_id = %s
            """, (task_id,))

            schedule = cursor.fetchone()

            if not schedule:
                return {
                    "success": False,
                    "error": f"找不到排程: {task_id}"
                }

        logger.info(f"📋 排程資訊: {schedule['schedule_name']}")

        # Extract configuration
        trigger_config = schedule.get('trigger_config', {})
        schedule_config = schedule.get('schedule_config', {})
        generation_config = schedule.get('generation_config', {})

        # Parse JSON fields if they're strings
        if isinstance(trigger_config, str):
            trigger_config = json.loads(trigger_config)
        if isinstance(schedule_config, str):
            schedule_config = json.loads(schedule_config)
        if isinstance(generation_config, str):
            generation_config = json.loads(generation_config)

        logger.info(f"🔍 trigger_config: {json.dumps(trigger_config, ensure_ascii=False)[:200]}")
        logger.info(f"🔍 schedule_config: {json.dumps(schedule_config, ensure_ascii=False)[:200]}")

        # 🔥 FIX: Prioritize values from full_triggers_config if available
        full_triggers_config = schedule_config.get('full_triggers_config', {})

        # Extract KOL assignment and max stocks
        kol_assignment = trigger_config.get('kol_assignment', 'random')

        # Use stockCountLimit from full_triggers_config if available, otherwise fallback to trigger_config
        if 'stockCountLimit' in full_triggers_config:
            max_stocks = full_triggers_config['stockCountLimit']
            logger.info(f"🔧 Using max_stocks={max_stocks} from full_triggers_config.stockCountLimit")
        else:
            max_stocks = trigger_config.get('max_stocks', 5)
            logger.info(f"🔧 Using max_stocks={max_stocks} from trigger_config (fallback)")

        # Extract stock_sorting criteria from full_triggers_config if available
        stock_filter_criteria = full_triggers_config.get('stockFilterCriteria', [])
        if stock_filter_criteria:
            logger.info(f"🔧 Using stockFilterCriteria={stock_filter_criteria} from full_triggers_config")

        # 🔥 FIX: Support both old format (stock_codes) and new format (triggerKey)
        stock_codes = trigger_config.get('stock_codes', [])
        trigger_key = trigger_config.get('triggerKey') or trigger_config.get('trigger_type')

        # If no pre-configured stock codes, execute trigger to get stocks
        if not stock_codes and trigger_key:
            logger.info(f"🎯 執行觸發器: {trigger_key}")

            # Get threshold and filters from trigger_config
            threshold = trigger_config.get('threshold', 20)
            filters = trigger_config.get('filters', {})

            # 🔥 FIX: Map stock_filter_criteria to sortBy parameter
            sortBy = None
            if stock_filter_criteria and len(stock_filter_criteria) > 0:
                criteria_to_sortBy = {
                    'five_day_gain': 'five_day_gain',
                    'five_day_loss': 'five_day_loss',
                    'daily_gain': 'change_percent_desc',
                    'daily_loss': 'change_percent_asc',
                    'volume_high': 'volume_desc',
                    'volume_low': 'volume_asc'
                }
                sortBy = criteria_to_sortBy.get(stock_filter_criteria[0])
                logger.info(f"🔧 Mapped stockFilterCriteria[0]={stock_filter_criteria[0]} → sortBy={sortBy}")

            # Execute trigger based on type
            if trigger_key == 'limit_up_after_hours':
                trigger_result = await get_after_hours_limit_up_stocks(
                    limit=max_stocks * 2,  # Fetch more than needed for filtering
                    changeThreshold=9.5,
                    industries="",
                    sortBy=sortBy
                )
                if 'stocks' in trigger_result:
                    stock_codes = [stock['stock_code'] for stock in trigger_result['stocks']]
                    logger.info(f"✅ 觸發器返回 {len(stock_codes)} 檔股票 (sortBy={sortBy})")
            elif trigger_key == 'limit_down_after_hours':
                trigger_result = await get_after_hours_limit_down_stocks(
                    limit=max_stocks * 2,  # Fetch more than needed for filtering
                    changeThreshold=9.5,
                    industries="",
                    sortBy=sortBy
                )
                if 'stocks' in trigger_result:
                    stock_codes = [stock['stock_code'] for stock in trigger_result['stocks']]
                    logger.info(f"✅ 觸發器返回 {len(stock_codes)} 檔股票 (sortBy={sortBy})")
            elif trigger_key == 'intraday_gainers_by_amount':
                logger.info("📡 執行盤中漲幅排序+成交額觸發器...")
                try:
                    trigger_result = await get_intraday_gainers_by_amount(limit=max_stocks)
                    if 'stocks' in trigger_result:
                        # Extract stock_code from dict objects
                        stocks = trigger_result['stocks']
                        stock_codes = [s['stock_code'] if isinstance(s, dict) else s for s in stocks]
                        logger.info(f"✅ 盤中觸發器返回 {len(stock_codes)} 檔股票")
                except Exception as e:
                    logger.error(f"❌ 盤中觸發器失敗: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            elif trigger_key == 'intraday_volume_leaders':
                logger.info("📡 執行盤中成交量排序觸發器...")
                try:
                    trigger_result = await get_intraday_volume_leaders(limit=max_stocks)
                    if 'stocks' in trigger_result:
                        stocks = trigger_result['stocks']
                        stock_codes = [s['stock_code'] if isinstance(s, dict) else s for s in stocks]
                        logger.info(f"✅ 盤中成交量觸發器返回 {len(stock_codes)} 檔股票")
                except Exception as e:
                    logger.error(f"❌ 盤中成交量觸發器失敗: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            elif trigger_key == 'intraday_amount_leaders':
                logger.info("📡 執行盤中成交額排序觸發器...")
                try:
                    trigger_result = await get_intraday_amount_leaders(limit=max_stocks)
                    if 'stocks' in trigger_result:
                        stocks = trigger_result['stocks']
                        stock_codes = [s['stock_code'] if isinstance(s, dict) else s for s in stocks]
                        logger.info(f"✅ 盤中成交額觸發器返回 {len(stock_codes)} 檔股票")
                except Exception as e:
                    logger.error(f"❌ 盤中成交額觸發器失敗: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            elif trigger_key == 'intraday_limit_down':
                logger.info("📡 執行盤中跌停篩選觸發器...")
                try:
                    trigger_result = await get_intraday_limit_down(limit=max_stocks)
                    if 'stocks' in trigger_result:
                        stocks = trigger_result['stocks']
                        stock_codes = [s['stock_code'] if isinstance(s, dict) else s for s in stocks]
                        logger.info(f"✅ 盤中跌停觸發器返回 {len(stock_codes)} 檔股票")
                except Exception as e:
                    logger.error(f"❌ 盤中跌停觸發器失敗: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            elif trigger_key == 'intraday_limit_up':
                logger.info("📡 執行盤中漲停篩選觸發器...")
                try:
                    trigger_result = await get_intraday_limit_up(limit=max_stocks)
                    if 'stocks' in trigger_result:
                        stocks = trigger_result['stocks']
                        stock_codes = [s['stock_code'] if isinstance(s, dict) else s for s in stocks]
                        logger.info(f"✅ 盤中漲停觸發器返回 {len(stock_codes)} 檔股票")
                except Exception as e:
                    logger.error(f"❌ 盤中漲停觸發器失敗: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            elif trigger_key == 'intraday_limit_down_by_amount':
                logger.info("📡 執行盤中跌停篩選+成交額觸發器...")
                try:
                    trigger_result = await get_intraday_limit_down_by_amount(limit=max_stocks)
                    if 'stocks' in trigger_result:
                        stocks = trigger_result['stocks']
                        stock_codes = [s['stock_code'] if isinstance(s, dict) else s for s in stocks]
                        logger.info(f"✅ 盤中跌停+成交額觸發器返回 {len(stock_codes)} 檔股票")
                except Exception as e:
                    logger.error(f"❌ 盤中跌停+成交額觸發器失敗: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            elif trigger_key == 'trending_topics':
                logger.info("📡 執行熱門話題觸發器...")
                try:
                    trigger_result = await get_trending_topics(limit=max_stocks)
                    if 'topics' in trigger_result:
                        topics = trigger_result['topics']
                        stock_codes = []
                        for topic in topics[:max_stocks]:
                            if 'stock_code' in topic:
                                stock_codes.append(topic['stock_code'])
                        logger.info(f"✅ 熱門話題觸發器從 {len(topics)} 個話題提取 {len(stock_codes)} 檔股票")
                except Exception as e:
                    logger.error(f"❌ 熱門話題觸發器失敗: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            else:
                logger.warning(f"⚠️ 未支持的觸發器類型: {trigger_key}")

        if not stock_codes:
            return {
                "success": False,
                "error": "無法獲取股票列表：排程未配置股票且觸發器未返回結果"
            }

        # Apply max_stocks limit
        stock_codes = stock_codes[:max_stocks]
        logger.info(f"📊 最終選定 {len(stock_codes)} 檔股票: {stock_codes}")

        # Generate unique session ID for this execution
        import time
        session_id = int(time.time() * 1000)  # Milliseconds timestamp

        logger.info(f"🚀 開始執行排程: session_id={session_id}, stocks={stock_codes}, kol_assignment={kol_assignment}")

        # TODO: Implement stock selection logic based on trigger_type
        # For now, use custom_stocks mode with provided stock codes

        #  Generate posts for each stock
        generated_posts = []
        failed_posts = []

        # Get KOL list (simplified - using fixed KOLs for now)
        kol_serials = [200, 201, 202]  # TODO: Get from database based on assignment strategy

        for stock_code in stock_codes:
            # Select KOL based on assignment strategy
            if kol_assignment == 'random':
                import random
                kol_serial = random.choice(kol_serials)
            else:
                kol_serial = kol_serials[0]  # Default to first KOL

            try:
                # 🔥 FIX: Get actual stock name from stock_mapping (extract company_name from dict)
                stock_info = stock_mapping.get(stock_code, {})
                stock_name = stock_info.get('company_name', stock_code) if isinstance(stock_info, dict) else stock_code
                logger.info(f"📊 Stock: {stock_code} → {stock_name}")

                # 🔥 FIX: Map content_style to kol_persona
                content_style = generation_config.get('content_style', 'chart_analysis')
                kol_persona_mapping = {
                    'chart_analysis': 'technical',
                    'technical_analysis': 'technical',
                    'fundamental_analysis': 'fundamental',
                    'macro_analysis': 'fundamental',
                    'news_analysis': 'news_driven',
                    'mixed_analysis': 'mixed'
                }
                kol_persona = generation_config.get('kol_persona') or kol_persona_mapping.get(content_style, 'technical')

                logger.info(f"🔍 Content style: {content_style} → KOL persona: {kol_persona}")

                # Call manual_posting logic internally
                # Build request body
                post_body = {
                    "stock_code": stock_code,
                    "stock_name": stock_name,  # 🔥 FIX: Use actual stock name
                    "kol_serial": kol_serial,
                    "kol_persona": kol_persona,  # 🔥 FIX: Use mapped kol_persona
                    "session_id": session_id,
                    "trigger_type": trigger_key or 'custom_stocks',  # 🔥 FIX: Use actual trigger_key that was executed
                    "generation_mode": "scheduled",  # 🔥 NEW: Mark as scheduled generation
                    "posting_type": generation_config.get('posting_type', 'analysis'),
                    "max_words": generation_config.get('max_words', 200),
                    "full_triggers_config": {
                        "trigger_type": trigger_key,  # 🔥 FIX: Use actual trigger_key
                        "stock_codes": stock_codes,
                        "kol_assignment": kol_assignment,
                        "max_stocks": max_stocks
                    }
                }

                # Create a Request object from the body
                from starlette.requests import Request
                from starlette.datastructures import Headers

                # Use the existing manual_posting function
                # We'll call it directly by reconstructing the request
                scope = {
                    'type': 'http',
                    'method': 'POST',
                    'headers': [(b'content-type', b'application/json')],
                }

                # Create mock request
                import io
                body_bytes = json.dumps(post_body).encode('utf-8')

                async def receive():
                    return {'type': 'http.request', 'body': body_bytes}

                async def send(message):
                    pass

                mock_request = Request(scope, receive, send)
                mock_request._body = body_bytes

                # Call manual_posting
                result = await manual_posting(mock_request)

                # 🔥 FIX: Handle JSONResponse objects (FastAPI wraps dict returns)
                from fastapi.responses import JSONResponse
                if isinstance(result, JSONResponse):
                    # Extract the content from JSONResponse
                    result = json.loads(result.body.decode('utf-8'))
                    logger.info(f"🔧 Extracted dict from JSONResponse: success={result.get('success')}")

                if isinstance(result, dict) and result.get('success'):
                    generated_posts.append({
                        "post_id": result.get('post_id'),
                        "stock_code": stock_code,
                        "kol_serial": kol_serial,
                        "title": result.get('content', {}).get('title', ''),
                        "content": result.get('content', {}).get('content', '')
                    })
                    logger.info(f"✅ 生成成功: {stock_code} - KOL {kol_serial}")
                else:
                    failed_posts.append({
                        "stock_code": stock_code,
                        "error": result.get('message', 'Unknown error')
                    })
                    logger.error(f"❌ 生成失敗: {stock_code}")

            except Exception as e:
                logger.error(f"❌ 生成貼文失敗: {stock_code}, error: {e}")
                failed_posts.append({
                    "stock_code": stock_code,
                    "error": str(e)
                })

        logger.info(f"📊 排程執行完成: 成功={len(generated_posts)}, 失敗={len(failed_posts)}")

        return {
            "success": True,
            "message": f"排程執行完成",
            "task_id": task_id,
            "session_id": session_id,
            "schedule_name": schedule['schedule_name'],
            "generated_count": len(generated_posts),
            "failed_count": len(failed_posts),
            "posts": generated_posts,
            "errors": failed_posts,
            "timestamp": get_current_time().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ 立即執行排程失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "task_id": task_id
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.put("/api/schedule/tasks/{task_id}")
async def update_schedule(task_id: str, request: Request):
    """
    編輯排程設定
    Update schedule configuration
    """
    logger.info(f"收到編輯排程請求 - Task ID: {task_id}")

    conn = None
    try:
        data = await request.json()
        logger.info(f"接收到的數據: {data}")

        if not db_pool:
            return {
                "success": False,
                "error": "數據庫連接不可用"
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if schedule exists
            cursor.execute("""
                SELECT schedule_id
                FROM schedule_tasks
                WHERE schedule_id = %s
            """, (task_id,))

            existing = cursor.fetchone()
            if not existing:
                return {
                    "success": False,
                    "error": f"找不到排程: {task_id}"
                }

            # Build UPDATE query dynamically based on provided fields
            update_fields = []
            update_values = []

            # Handle basic fields
            if 'schedule_name' in data:
                update_fields.append("schedule_name = %s")
                update_values.append(data['schedule_name'])

            if 'schedule_description' in data:
                update_fields.append("schedule_description = %s")
                update_values.append(data['schedule_description'])

            if 'auto_posting' in data:
                update_fields.append("auto_posting = %s")
                update_values.append(data['auto_posting'])

            if 'weekdays_only' in data:
                update_fields.append("weekdays_only = %s")
                update_values.append(data['weekdays_only'])

            # Handle JSON fields
            if 'generation_config' in data:
                update_fields.append("generation_config = %s")
                update_values.append(json.dumps(data['generation_config']))

            if 'trigger_config' in data:
                update_fields.append("trigger_config = %s")
                update_values.append(json.dumps(data['trigger_config']))

            if 'schedule_config' in data:
                update_fields.append("schedule_config = %s")
                update_values.append(json.dumps(data['schedule_config']))

            # Always update timestamp
            update_fields.append("updated_at = NOW()")

            if not update_fields:
                return {
                    "success": False,
                    "error": "沒有提供要更新的欄位"
                }

            # Execute UPDATE
            query = f"""
                UPDATE schedule_tasks
                SET {', '.join(update_fields)}
                WHERE schedule_id = %s
                RETURNING *
            """
            update_values.append(task_id)

            cursor.execute(query, update_values)
            updated_schedule = cursor.fetchone()

            conn.commit()

            logger.info(f"✅ 排程更新成功: {task_id}")

            return {
                "success": True,
                "message": "排程更新成功",
                "task_id": task_id,
                "schedule": dict(updated_schedule) if updated_schedule else None
            }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 編輯排程失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "task_id": task_id
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.post("/api/schedule/cancel/{task_id}")
async def cancel_schedule(task_id: str):
    """
    取消/停止排程
    Cancel or stop a schedule
    """
    logger.info(f"收到取消排程請求 - Task ID: {task_id}")

    conn = None
    try:
        if not db_pool:
            return {
                "success": False,
                "error": "數據庫連接不可用"
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if schedule exists
            cursor.execute("""
                SELECT schedule_id, status
                FROM schedule_tasks
                WHERE schedule_id = %s
            """, (task_id,))

            existing = cursor.fetchone()
            if not existing:
                return {
                    "success": False,
                    "error": f"找不到排程: {task_id}"
                }

            # Update status to cancelled
            cursor.execute("""
                UPDATE schedule_tasks
                SET status = 'cancelled',
                    updated_at = NOW()
                WHERE schedule_id = %s
                RETURNING *
            """, (task_id,))

            updated_schedule = cursor.fetchone()
            conn.commit()

            logger.info(f"✅ 排程已取消: {task_id}")

            return {
                "success": True,
                "message": "排程已取消",
                "task_id": task_id,
                "previous_status": existing['status'],
                "new_status": "cancelled"
            }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 取消排程失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "task_id": task_id
        }
    finally:
        if conn:
            return_db_connection(conn)


@app.post("/api/schedule/start/{task_id}")
async def start_schedule(task_id: str):
    """
    啟動/恢復排程
    Start or resume a schedule
    """
    logger.info(f"收到啟動排程請求 - Task ID: {task_id}")

    conn = None
    try:
        if not db_pool:
            return {
                "success": False,
                "error": "數據庫連接不可用"
            }

        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check if schedule exists
            cursor.execute("""
                SELECT schedule_id, status
                FROM schedule_tasks
                WHERE schedule_id = %s
            """, (task_id,))

            existing = cursor.fetchone()
            if not existing:
                return {
                    "success": False,
                    "error": f"找不到排程: {task_id}"
                }

            # Update status to active
            cursor.execute("""
                UPDATE schedule_tasks
                SET status = 'active',
                    updated_at = NOW()
                WHERE schedule_id = %s
                RETURNING *
            """, (task_id,))

            updated_schedule = cursor.fetchone()
            conn.commit()

            logger.info(f"✅ 排程已啟動: {task_id}")

            return {
                "success": True,
                "message": "排程已啟動",
                "task_id": task_id,
                "previous_status": existing['status'],
                "new_status": "active"
            }

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 啟動排程失敗: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "task_id": task_id
        }
    finally:
        if conn:
            return_db_connection(conn)


if __name__ == "__main__":
    import uvicorn
    
    # Railway 使用 PORT 環境變數，本地開發使用 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 啟動 Unified API 服務器: {host}:{port}")
    uvicorn.run(app, host=host, port=port)
