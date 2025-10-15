#!/usr/bin/env python3
"""
工作流程遷移腳本
逐步將現有觸發器遷移到發文生成系統
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.posting.posting_system_integration import PostingSystemIntegration, PostingSystemConfig, PostingSystemTriggerType
from src.clients.google.sheets_client import GoogleSheetsClient

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkflowMigration:
    """工作流程遷移器"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient()
        self.integration = PostingSystemIntegration(self.sheets_client)
        self.logger = logging.getLogger(__name__)
    
    async def migrate_after_hours_limit_up(self, max_posts: int = 10) -> str:
        """遷移盤後漲停觸發器"""
        try:
            self.logger.info("開始遷移盤後漲停觸發器")
            
            # 配置觸發器
            config = PostingSystemConfig(
                trigger_type=PostingSystemTriggerType.AFTER_HOURS_LIMIT_UP,
                max_posts=max_posts,
                enable_publishing=False,
                enable_learning=True,
                data_sources={
                    "stock_price_api": True,
                    "monthly_revenue_api": True,
                    "financial_report_api": True,
                    "news_sources": True
                },
                kol_assignment_mode="dynamic",
                content_mode="one_to_one"
            )
            
            # 創建會話
            session_id = await self.integration.create_session(config)
            self.logger.info(f"創建會話: {session_id}")
            
            # 執行會話
            result = await self.integration.execute_session(session_id)
            self.logger.info(f"會話執行完成: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"遷移盤後漲停觸發器失敗: {e}")
            raise
    
    async def migrate_intraday_limit_up(self, stock_codes: list, max_posts: int = 10) -> str:
        """遷移盤中漲停觸發器"""
        try:
            self.logger.info(f"開始遷移盤中漲停觸發器: {stock_codes}")
            
            # 配置觸發器
            config = PostingSystemConfig(
                trigger_type=PostingSystemTriggerType.INTRADAY_LIMIT_UP,
                stock_codes=stock_codes,
                max_posts=max_posts,
                enable_publishing=False,
                enable_learning=True,
                data_sources={
                    "stock_price_api": True,
                    "monthly_revenue_api": True,
                    "financial_report_api": True,
                    "news_sources": True
                },
                kol_assignment_mode="dynamic",
                content_mode="one_to_one"
            )
            
            # 創建會話
            session_id = await self.integration.create_session(config)
            self.logger.info(f"創建會話: {session_id}")
            
            # 執行會話
            result = await self.integration.execute_session(session_id)
            self.logger.info(f"會話執行完成: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"遷移盤中漲停觸發器失敗: {e}")
            raise
    
    async def migrate_trending_topic(self, max_posts: int = 10) -> str:
        """遷移熱門話題觸發器"""
        try:
            self.logger.info("開始遷移熱門話題觸發器")
            
            # 配置觸發器
            config = PostingSystemConfig(
                trigger_type=PostingSystemTriggerType.TRENDING_TOPIC,
                max_posts=max_posts,
                enable_publishing=False,
                enable_learning=True,
                data_sources={
                    "stock_price_api": True,
                    "monthly_revenue_api": True,
                    "financial_report_api": True,
                    "news_sources": True
                },
                kol_assignment_mode="dynamic",
                content_mode="one_to_one"
            )
            
            # 創建會話
            session_id = await self.integration.create_session(config)
            self.logger.info(f"創建會話: {session_id}")
            
            # 執行會話
            result = await self.integration.execute_session(session_id)
            self.logger.info(f"會話執行完成: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"遷移熱門話題觸發器失敗: {e}")
            raise
    
    async def migrate_custom_stocks(self, stock_codes: list, max_posts: int = 10) -> str:
        """遷移自定義股票觸發器"""
        try:
            self.logger.info(f"開始遷移自定義股票觸發器: {stock_codes}")
            
            # 配置觸發器
            config = PostingSystemConfig(
                trigger_type=PostingSystemTriggerType.CUSTOM_STOCKS,
                stock_codes=stock_codes,
                max_posts=max_posts,
                enable_publishing=False,
                enable_learning=True,
                data_sources={
                    "stock_price_api": True,
                    "monthly_revenue_api": True,
                    "financial_report_api": True,
                    "news_sources": True
                },
                kol_assignment_mode="dynamic",
                content_mode="one_to_one"
            )
            
            # 創建會話
            session_id = await self.integration.create_session(config)
            self.logger.info(f"創建會話: {session_id}")
            
            # 執行會話
            result = await self.integration.execute_session(session_id)
            self.logger.info(f"會話執行完成: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"遷移自定義股票觸發器失敗: {e}")
            raise
    
    async def migrate_stock_code_list(self, stock_codes: list, max_posts: int = 10) -> str:
        """遷移股票代號列表觸發器"""
        try:
            self.logger.info(f"開始遷移股票代號列表觸發器: {stock_codes}")
            
            # 配置觸發器
            config = PostingSystemConfig(
                trigger_type=PostingSystemTriggerType.STOCK_CODE_LIST,
                stock_codes=stock_codes,
                max_posts=max_posts,
                enable_publishing=False,
                enable_learning=True,
                data_sources={
                    "stock_price_api": True,
                    "monthly_revenue_api": True,
                    "financial_report_api": True,
                    "news_sources": True
                },
                kol_assignment_mode="dynamic",
                content_mode="one_to_one"
            )
            
            # 創建會話
            session_id = await self.integration.create_session(config)
            self.logger.info(f"創建會話: {session_id}")
            
            # 執行會話
            result = await self.integration.execute_session(session_id)
            self.logger.info(f"會話執行完成: {session_id}")
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"遷移股票代號列表觸發器失敗: {e}")
            raise
    
    async def list_migration_sessions(self) -> list:
        """列出遷移會話"""
        try:
            sessions = await self.integration.list_sessions()
            self.logger.info(f"找到 {len(sessions)} 個遷移會話")
            return sessions
        except Exception as e:
            self.logger.error(f"列出遷移會話失敗: {e}")
            return []
    
    async def get_migration_session_posts(self, session_id: str) -> list:
        """獲取遷移會話的發文列表"""
        try:
            posts = await self.integration.get_session_posts(session_id)
            self.logger.info(f"會話 {session_id} 有 {len(posts)} 篇發文")
            return posts
        except Exception as e:
            self.logger.error(f"獲取遷移會話發文失敗: {e}")
            return []
    
    async def approve_migration_post(self, session_id: str, post_id: str) -> dict:
        """審核通過遷移發文"""
        try:
            result = await self.integration.approve_post(session_id, post_id)
            self.logger.info(f"發文審核通過: {post_id}")
            return result
        except Exception as e:
            self.logger.error(f"審核遷移發文失敗: {e}")
            raise
    
    async def reject_migration_post(self, session_id: str, post_id: str, reason: str = "") -> dict:
        """審核拒絕遷移發文"""
        try:
            result = await self.integration.reject_post(session_id, post_id, reason)
            self.logger.info(f"發文審核拒絕: {post_id}")
            return result
        except Exception as e:
            self.logger.error(f"拒絕遷移發文失敗: {e}")
            raise
    
    async def publish_migration_post(self, session_id: str, post_id: str) -> dict:
        """發布遷移發文"""
        try:
            result = await self.integration.publish_post(session_id, post_id)
            self.logger.info(f"發文發布成功: {post_id}")
            return result
        except Exception as e:
            self.logger.error(f"發布遷移發文失敗: {e}")
            raise

# 使用範例
async def example_migration():
    """遷移範例"""
    migration = WorkflowMigration()
    
    try:
        # 1. 遷移盤後漲停觸發器
        print("🚀 開始遷移盤後漲停觸發器...")
        session_id = await migration.migrate_after_hours_limit_up(max_posts=5)
        print(f"✅ 盤後漲停觸發器遷移完成: {session_id}")
        
        # 2. 獲取發文列表
        posts = await migration.get_migration_session_posts(session_id)
        print(f"📊 生成 {len(posts)} 篇發文")
        
        # 3. 審核發文
        for post in posts[:2]:  # 審核前2篇
            post_id = post.get("id")
            if post_id:
                await migration.approve_migration_post(session_id, post_id)
                print(f"✅ 發文審核通過: {post_id}")
        
        # 4. 列出所有遷移會話
        sessions = await migration.list_migration_sessions()
        print(f"📋 總共 {len(sessions)} 個遷移會話")
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")

if __name__ == "__main__":
    asyncio.run(example_migration())
