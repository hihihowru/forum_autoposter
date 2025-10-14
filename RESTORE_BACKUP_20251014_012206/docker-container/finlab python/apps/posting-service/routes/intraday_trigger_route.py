"""
盤中觸發器 API 路由
"""
from fastapi import APIRouter, HTTPException
import httpx
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/intraday-trigger", tags=["intraday-trigger"])

# CMoney API 配置
CMONEY_API_BASE = "https://asterisk-chipsapi.cmoney.tw"

# 使用 forum_200 KOL 憑證動態取得 token
FORUM_200_CREDENTIALS = {
    "email": "forum_200@cmoney.com.tw",
    "password": "N9t1kY3x",
    "member_id": "9505546"
}

# Token 快取
_token_cache = {
    "token": None,
    "expires_at": None,
    "created_at": None
}

async def get_dynamic_auth_token() -> str:
    """使用 forum_200 KOL 憑證動態取得 CMoney API token"""
    try:
        # 檢查快取的 token 是否仍然有效
        if (_token_cache["token"] and 
            _token_cache["expires_at"] and 
            datetime.now() < _token_cache["expires_at"]):
            logger.info("✅ 使用快取的 CMoney API token")
            return _token_cache["token"]
        
        logger.info("🔐 開始使用 forum_200 憑證登入 CMoney...")
        
        # 使用 CMoney Client 登入
        import sys
        import os
        src_path = '/app/src'
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
        
        cmoney_client = CMoneyClient()
        credentials = LoginCredentials(
            email=FORUM_200_CREDENTIALS["email"],
            password=FORUM_200_CREDENTIALS["password"]
        )
        
        login_result = await cmoney_client.login(credentials)
        
        if not login_result or not login_result.token:
            raise Exception("forum_200 登入失敗")
        
        # 快取 token
        _token_cache["token"] = login_result.token
        _token_cache["expires_at"] = login_result.expires_at
        _token_cache["created_at"] = datetime.now()
        
        logger.info(f"✅ forum_200 登入成功，token 有效期至: {login_result.expires_at}")
        return login_result.token
        
    except Exception as e:
        logger.error(f"❌ 動態取得 CMoney API token 失敗: {e}")
        raise HTTPException(status_code=500, detail=f"認證失敗: {str(e)}")

@router.post("/execute")
async def execute_intraday_trigger(trigger_config: Dict[str, Any]):
    """執行盤中觸發器"""
    try:
        logger.info(f"🚀 [盤中觸發器] 收到請求: {trigger_config}")
        
        # 準備請求參數
        columns = "交易時間,傳輸序號,內外盤旗標,即時成交價,即時成交量,最低價,最高價,標的,漲跌,漲跌幅,累計成交總額,累計成交量,開盤價"
        endpoint = trigger_config.get("endpoint")
        processing = trigger_config.get("processing", [])
        
        logger.info(f"📋 [盤中觸發器] 解析配置 - endpoint: {endpoint}, processing: {processing}")
        
        if not endpoint or not processing:
            logger.error(f"❌ [盤中觸發器] 配置錯誤 - endpoint: {endpoint}, processing: {processing}")
            raise HTTPException(status_code=400, detail="缺少必要的觸發器配置")
        
        # 準備請求數據
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

@router.get("/health")
async def health_check():
    """健康檢查"""
    return {"status": "ok", "service": "intraday-trigger"}
