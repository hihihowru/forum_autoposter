#!/usr/bin/env python3
"""
發文生成系統整合服務
整合觸發器適配器與發文生成系統
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from src.services.posting.trigger_adapter import TriggerAdapter, PostingSystemConfig, PostingSystemTriggerType
from src.services.posting.posting_service import PostingService
from src.services.posting.kol_integration_service import KOLIntegrationService, KOLProfile
from src.clients.google.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)

@dataclass
class PostingSystemSession:
    """發文生成系統會話"""
    session_id: str
    trigger_type: PostingSystemTriggerType
    config: PostingSystemConfig
    status: str  # "created" | "generating" | "completed" | "failed"
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class PostingSystemIntegration:
    """發文生成系統整合服務"""
    
    def __init__(self, sheets_client: GoogleSheetsClient):
        self.sheets_client = sheets_client
        self.trigger_adapter = TriggerAdapter(sheets_client)
        self.posting_service = PostingService()
        self.kol_service = KOLIntegrationService()
        self.active_sessions: Dict[str, PostingSystemSession] = {}
        self.logger = logging.getLogger(__name__)
    
    async def create_session(self, config: PostingSystemConfig) -> str:
        """創建發文生成會話"""
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            session = PostingSystemSession(
                session_id=session_id,
                trigger_type=config.trigger_type,
                config=config,
                status="created",
                created_at=datetime.now()
            )
            
            self.active_sessions[session_id] = session
            self.logger.info(f"創建發文生成會話: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"創建會話失敗: {e}")
            raise
    
    async def execute_session(self, session_id: str) -> Dict[str, Any]:
        """執行發文生成會話"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"會話不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            session.status = "generating"
            
            self.logger.info(f"開始執行會話: {session_id}")
            
            # 1. 執行觸發器適配器
            trigger_result = await self.trigger_adapter.execute_posting_system_trigger(session.config)
            
            # 2. 創建發文生成系統會話
            posting_session_id = await self.posting_service.create_session({
                "trigger_type": session.trigger_type.value,
                "stock_codes": session.config.stock_codes,
                "max_posts": session.config.max_posts,
                "data_sources": session.config.data_sources,
                "kol_assignment_mode": session.config.kol_assignment_mode,
                "content_mode": session.config.content_mode
            })
            
            # 3. 生成發文內容
            generation_result = await self.posting_service.generate_posts(posting_session_id)
            
            # 4. 整合結果
            session.result = {
                "trigger_result": trigger_result,
                "posting_session_id": posting_session_id,
                "generation_result": generation_result,
                "total_generated_posts": trigger_result.get("generated_posts", 0),
                "execution_time": trigger_result.get("execution_time", 0)
            }
            
            session.status = "completed"
            session.completed_at = datetime.now()
            
            self.logger.info(f"會話執行完成: {session_id}")
            
            return session.result
            
        except Exception as e:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = "failed"
                self.active_sessions[session_id].error = str(e)
            
            self.logger.error(f"執行會話失敗: {session_id} - {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[PostingSystemSession]:
        """獲取會話資訊"""
        return self.active_sessions.get(session_id)
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有會話"""
        sessions = []
        for session in self.active_sessions.values():
            sessions.append({
                "session_id": session.session_id,
                "trigger_type": session.trigger_type.value,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "total_generated_posts": session.result.get("total_generated_posts", 0) if session.result else 0,
                "execution_time": session.result.get("execution_time", 0) if session.result else 0,
                "error": session.error
            })
        
        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)
    
    async def get_session_posts(self, session_id: str) -> List[Dict[str, Any]]:
        """獲取會話的發文列表"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"會話不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            if not session.result or "posting_session_id" not in session.result:
                return []
            
            posting_session_id = session.result["posting_session_id"]
            posts = await self.posting_service.get_posts(posting_session_id)
            
            return posts
            
        except Exception as e:
            self.logger.error(f"獲取會話發文失敗: {session_id} - {e}")
            return []
    
    async def approve_post(self, session_id: str, post_id: str) -> Dict[str, Any]:
        """審核通過發文"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"會話不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            if not session.result or "posting_session_id" not in session.result:
                raise ValueError("會話未完成或無發文數據")
            
            posting_session_id = session.result["posting_session_id"]
            result = await self.posting_service.approve_post(posting_session_id, post_id)
            
            self.logger.info(f"發文審核通過: {post_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"審核發文失敗: {session_id}/{post_id} - {e}")
            raise
    
    async def reject_post(self, session_id: str, post_id: str, reason: str = "") -> Dict[str, Any]:
        """審核拒絕發文"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"會話不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            if not session.result or "posting_session_id" not in session.result:
                raise ValueError("會話未完成或無發文數據")
            
            posting_session_id = session.result["posting_session_id"]
            result = await self.posting_service.reject_post(posting_session_id, post_id, reason)
            
            self.logger.info(f"發文審核拒絕: {post_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"拒絕發文失敗: {session_id}/{post_id} - {e}")
            raise
    
    async def publish_post(self, session_id: str, post_id: str) -> Dict[str, Any]:
        """發布發文"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"會話不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            if not session.result or "posting_session_id" not in session.result:
                raise ValueError("會話未完成或無發文數據")
            
            posting_session_id = session.result["posting_session_id"]
            result = await self.posting_service.publish_post(posting_session_id, post_id)
            
            self.logger.info(f"發文發布成功: {post_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"發布發文失敗: {session_id}/{post_id} - {e}")
            raise
    
    # ==================== KOL管理方法 ====================
    
    async def get_available_kols(self) -> List[Dict[str, Any]]:
        """獲取可用的KOL列表"""
        try:
            active_kols = await self.kol_service.get_active_kols()
            kol_list = []
            
            for kol in active_kols:
                kol_dict = self.kol_service.export_kol_to_dict(kol)
                kol_list.append(kol_dict)
            
            self.logger.info(f"獲取到 {len(kol_list)} 個可用KOL")
            return kol_list
            
        except Exception as e:
            self.logger.error(f"獲取KOL列表失敗: {e}")
            return []
    
    async def get_kol_by_serial(self, serial: int) -> Optional[Dict[str, Any]]:
        """根據序號獲取KOL資料"""
        try:
            kol = await self.kol_service.get_kol_by_serial(serial)
            if kol:
                return self.kol_service.export_kol_to_dict(kol)
            return None
            
        except Exception as e:
            self.logger.error(f"獲取KOL資料失敗: {serial} - {e}")
            return None
    
    async def get_kols_by_persona(self, persona: str) -> List[Dict[str, Any]]:
        """根據人設獲取KOL列表"""
        try:
            persona_kols = await self.kol_service.get_kols_by_persona(persona)
            kol_list = []
            
            for kol in persona_kols:
                kol_dict = self.kol_service.export_kol_to_dict(kol)
                kol_list.append(kol_dict)
            
            self.logger.info(f"找到 {len(kol_list)} 個 {persona} 人設KOL")
            return kol_list
            
        except Exception as e:
            self.logger.error(f"根據人設獲取KOL失敗: {persona} - {e}")
            return []
    
    async def assign_kols_to_session(self, session_id: str, kol_serials: List[int]) -> Dict[str, Any]:
        """為會話指派KOL"""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"會話不存在: {session_id}")
            
            session = self.active_sessions[session_id]
            assigned_kols = []
            
            for serial in kol_serials:
                kol = await self.kol_service.get_kol_by_serial(serial)
                if kol:
                    kol_dict = self.kol_service.export_kol_to_dict(kol)
                    assigned_kols.append(kol_dict)
                    self.logger.info(f"指派KOL: {kol.nickname} ({serial}) 到會話 {session_id}")
                else:
                    self.logger.warning(f"找不到KOL: {serial}")
            
            # 更新會話配置
            session.config.kol_assignment_mode = "fixed"
            session.config.selected_kols = assigned_kols
            
            return {
                "success": True,
                "assigned_count": len(assigned_kols),
                "assigned_kols": assigned_kols
            }
            
        except Exception as e:
            self.logger.error(f"指派KOL失敗: {session_id} - {e}")
            return {
                "success": False,
                "error": str(e),
                "assigned_count": 0,
                "assigned_kols": []
            }

# 工廠函數
def create_posting_system_integration(sheets_client: GoogleSheetsClient) -> PostingSystemIntegration:
    """創建發文生成系統整合服務實例"""
    return PostingSystemIntegration(sheets_client)

# 使用範例
async def example_usage():
    """使用範例"""
    from src.clients.google.sheets_client import GoogleSheetsClient
    
    # 初始化
    sheets_client = GoogleSheetsClient()
    integration = create_posting_system_integration(sheets_client)
    
    # 配置盤後漲停觸發器
    config = PostingSystemConfig(
        trigger_type=PostingSystemTriggerType.AFTER_HOURS_LIMIT_UP,
        max_posts=10,
        enable_publishing=False,
        enable_learning=True
    )
    
    # 創建會話
    session_id = await integration.create_session(config)
    
    # 執行會話
    result = await integration.execute_session(session_id)
    
    # 獲取發文列表
    posts = await integration.get_session_posts(session_id)
    
    print(f"會話結果: {result}")
    print(f"發文列表: {posts}")

if __name__ == "__main__":
    asyncio.run(example_usage())
