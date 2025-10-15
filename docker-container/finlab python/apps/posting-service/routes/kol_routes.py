"""
KOL 管理路由
"""

import os
import sys
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

# 添加專案根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/test", tags=["KOL測試"])

@router.post("/kol-login/{kol_serial}")
async def test_kol_login(kol_serial: str):
    """測試 KOL 登入功能"""
    logger.info(f"🔐 測試 KOL 登入 - Serial: {kol_serial}")
    
    try:
        # 使用發佈服務測試登入
        from publish_service import publish_service
        
        # 測試登入
        access_token = await publish_service.login_kol(kol_serial)
        
        if access_token:
            logger.info(f"✅ KOL {kol_serial} 登入測試成功")
            return {
                "success": True,
                "message": f"KOL {kol_serial} 登入成功",
                "access_token": access_token[:50] + "...",
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ KOL {kol_serial} 登入測試失敗")
            return {
                "success": False,
                "message": f"KOL {kol_serial} 登入失敗",
                "error": "無法獲取 access token",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ KOL {kol_serial} 登入測試異常: {e}")
        raise HTTPException(status_code=500, detail=f"KOL 登入測試失敗: {str(e)}")

@router.get("/kol-info/{kol_serial}")
async def get_kol_info(kol_serial: str):
    """獲取 KOL 基本資訊"""
    try:
        from kol_service import kol_service
        
        info = kol_service.get_kol_info(kol_serial)
        if info:
            return {
                "success": True,
                "data": info,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"找不到 KOL {kol_serial}",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"❌ 獲取 KOL {kol_serial} 資訊失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 KOL 資訊失敗: {str(e)}")

@router.get("/kol-list")
async def get_all_kol_info():
    """獲取所有 KOL 資訊"""
    try:
        from kol_service import kol_service
        
        kol_list = kol_service.get_all_kol_info()
        return {
            "success": True,
            "data": kol_list,
            "count": len(kol_list),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ 獲取 KOL 列表失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取 KOL 列表失敗: {str(e)}")

