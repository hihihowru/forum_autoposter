"""
並行處理模組 - 解決 API 塞車和超時問題
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
from datetime import datetime
import time
import os
import sys

# 添加專案根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

class ParallelProcessor:
    """並行處理器 - 用於並行處理多個 API 調用和任務"""
    
    def __init__(self, max_concurrent: int = 5, timeout: int = 60, max_retries: int = 3):
        """
        初始化並行處理器
        
        Args:
            max_concurrent: 最大並發數量
            timeout: 單個請求超時時間（秒）
            max_retries: 最大重試次數
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def process_batch_async(
        self, 
        items: List[Any], 
        processor_func: Callable,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        異步並行處理批次任務
        
        Args:
            items: 要處理的項目列表
            processor_func: 處理函數 (async function)
            progress_callback: 進度回調函數
            
        Returns:
            處理結果列表
        """
        logger.info(f"🚀 開始並行處理 {len(items)} 個項目，最大並發數: {self.max_concurrent}")
        
        # 創建任務列表
        tasks = []
        for i, item in enumerate(items):
            task = self._create_limited_task(processor_func, item, i)
            tasks.append(task)
        
        # 並行執行所有任務
        results = []
        completed = 0
        
        # 使用 asyncio.as_completed 來處理完成的任務
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                results.append(result)
                completed += 1
                
                # 調用進度回調
                if progress_callback:
                    await progress_callback(completed, len(items), result)
                    
                logger.info(f"✅ 完成 {completed}/{len(items)} 個任務")
                
            except Exception as e:
                logger.error(f"❌ 任務執行失敗: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                completed += 1
        
        logger.info(f"🎉 並行處理完成: {completed}/{len(items)} 個任務")
        return results
    
    async def _create_limited_task(self, processor_func: Callable, item: Any, index: int):
        """創建有限制的任務（使用信號量控制並發）"""
        async with self.semaphore:
            return await self._execute_with_retry(processor_func, item, index)
    
    async def _execute_with_retry(self, processor_func: Callable, item: Any, index: int):
        """執行帶重試的任務"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 執行任務 {index + 1} (嘗試 {attempt + 1}/{self.max_retries})")
                result = await processor_func(item)
                return {
                    "success": True,
                    "index": index,
                    "result": result,
                    "attempt": attempt + 1,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.warning(f"⚠️ 任務 {index + 1} 嘗試 {attempt + 1} 失敗: {e}")
                if attempt == self.max_retries - 1:
                    # 最後一次嘗試失敗
                    return {
                        "success": False,
                        "index": index,
                        "error": str(e),
                        "attempt": attempt + 1,
                        "timestamp": datetime.now().isoformat()
                    }
                # 指數退避
                await asyncio.sleep(2 ** attempt)
    
    async def process_api_calls_parallel(
        self,
        api_calls: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        並行處理多個 API 調用
        
        Args:
            api_calls: API 調用列表，每個包含 url, method, headers, data 等
            progress_callback: 進度回調函數
            
        Returns:
            API 響應結果列表
        """
        async def process_single_api_call(api_call: Dict[str, Any]) -> Dict[str, Any]:
            """處理單個 API 調用"""
            url = api_call.get('url')
            method = api_call.get('method', 'GET')
            headers = api_call.get('headers', {})
            data = api_call.get('data')
            params = api_call.get('params')
            
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method.upper() == 'GET':
                        response = await client.get(url, headers=headers, params=params)
                    elif method.upper() == 'POST':
                        response = await client.post(url, headers=headers, json=data, params=params)
                    else:
                        raise ValueError(f"不支持的 HTTP 方法: {method}")
                    
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                        "url": url,
                        "method": method
                    }
                    
            except httpx.TimeoutException:
                raise Exception(f"API 調用超時: {url}")
            except httpx.ConnectError:
                raise Exception(f"API 連接失敗: {url}")
            except Exception as e:
                raise Exception(f"API 調用失敗: {url}, 錯誤: {str(e)}")
        
        return await self.process_batch_async(api_calls, process_single_api_call, progress_callback)

class InteractionDataProcessor(ParallelProcessor):
    """互動數據並行處理器"""
    
    def __init__(self, max_concurrent: int = 3, timeout: int = 30):
        super().__init__(max_concurrent, timeout)
        
    async def fetch_interactions_parallel(
        self, 
        posts: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        並行獲取多個貼文的互動數據
        
        Args:
            posts: 貼文列表
            progress_callback: 進度回調函數
            
        Returns:
            互動數據結果列表
        """
        # 定義不追蹤互動數據的 KOL 黑名單
        KOLS_TO_SKIP = [166, 210, 212]
        
        # 過濾掉黑名單中的 KOL
        valid_posts = [post for post in posts if post.get("kol_serial") not in KOLS_TO_SKIP]
        
        logger.info(f"🔄 開始並行獲取 {len(valid_posts)} 篇貼文的互動數據")
        
        async def fetch_single_post_interaction(post: Dict[str, Any]) -> Dict[str, Any]:
            """獲取單個貼文的互動數據"""
            try:
                try:
                    from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
                except ImportError:
                    logger.error("❌ 無法導入 CMoney 客戶端")
                    return {"post_id": post["article_id"], "kol_serial": kol_serial, "error": "CMoney 客戶端導入失敗"}
                
                kol_serial = post.get("kol_serial")
                article_id = post.get("article_id")
                
                # 獲取 KOL 憑證
                credentials = await self._get_kol_credentials(kol_serial)
                if not credentials:
                    raise Exception(f"無法獲取 KOL-{kol_serial} 的憑證")
                
                # 調用 CMoney API
                client = CMoneyClient()
                login_result = await client.login(credentials)
                
                if not login_result or login_result.is_expired:
                    raise Exception(f"KOL-{kol_serial} 登入失敗")
                
                # 獲取互動數據
                interaction_data = await client.get_article_interactions(login_result.token, article_id)
                
                if interaction_data:
                    return {
                        "post_id": post.get("post_id"),
                        "article_id": article_id,
                        "kol_serial": kol_serial,
                        "interaction_data": {
                            'views': interaction_data.views or 0,
                            'likes': interaction_data.likes or 0,
                            'comments': interaction_data.comments or 0,
                            'shares': interaction_data.shares or 0,
                            'engagement_rate': interaction_data.engagement_rate or 0
                        }
                    }
                else:
                    raise Exception(f"無法獲取互動數據: {article_id}")
                    
            except Exception as e:
                logger.error(f"❌ 獲取互動數據失敗 - Post: {post.get('post_id')}, 錯誤: {e}")
                raise
        
        return await self.process_batch_async(valid_posts, fetch_single_post_interaction, progress_callback)
    
    async def _get_kol_credentials(self, kol_serial: int) -> Optional[Any]:
        """獲取 KOL 憑證"""
        try:
            # 首先嘗試從數據庫獲取
            from kol_database_service import kol_db_service
            kol_data = kol_db_service.get_kol_by_serial(str(kol_serial))
            
            if kol_data:
                try:
                    from src.clients.cmoney.cmoney_client import LoginCredentials
                except ImportError:
                    logger.error("❌ 無法導入 LoginCredentials")
                    return None
                return LoginCredentials(email=kol_data.email, password=kol_data.password)
            
            # 回退到硬編碼憑證
            return await self._get_fallback_credentials(kol_serial)
            
        except Exception as e:
            logger.error(f"❌ 獲取 KOL-{kol_serial} 憑證失敗: {e}")
            return await self._get_fallback_credentials(kol_serial)
    
    async def _get_fallback_credentials(self, kol_serial: int) -> Optional[Any]:
        """從環境變數獲取 KOL 憑證"""
        try:
            import os
            try:
                from src.clients.cmoney.cmoney_client import LoginCredentials
            except ImportError:
                logger.error("❌ 無法導入 LoginCredentials")
                return None
            
            # 從環境變數獲取 KOL 憑證
            kol_email = os.getenv(f'KOL_{kol_serial}_EMAIL')
            kol_password = os.getenv(f'KOL_{kol_serial}_PASSWORD')
            
            if kol_email and kol_password:
                logger.info(f"✅ 從環境變數獲取 KOL-{kol_serial} 憑證")
                return LoginCredentials(email=kol_email, password=kol_password)
            else:
                logger.warning(f"⚠️ 環境變數中找不到 KOL-{kol_serial} 的憑證")
                return None
            
        except Exception as e:
            logger.error(f"❌ 從環境變數獲取 KOL-{kol_serial} 憑證失敗: {e}")
            return None

class PostGenerationProcessor(ParallelProcessor):
    """貼文生成並行處理器"""
    
    def __init__(self, max_concurrent: int = 2, timeout: int = 120):
        super().__init__(max_concurrent, timeout)
        
    async def generate_posts_parallel(
        self,
        post_requests: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        並行生成多個貼文
        
        Args:
            post_requests: 貼文生成請求列表
            progress_callback: 進度回調函數
            
        Returns:
            貼文生成結果列表
        """
        logger.info(f"🚀 開始並行生成 {len(post_requests)} 篇貼文")
        
        async def generate_single_post(request: Dict[str, Any]) -> Dict[str, Any]:
            """生成單個貼文"""
            try:
                # 這裡調用現有的貼文生成邏輯
                from main import manual_post_content
                from post_record_service import PostingRequest
                
                # 轉換為 PostingRequest 對象
                posting_request = PostingRequest(**request)
                
                # 調用貼文生成
                result = await manual_post_content(posting_request)
                
                return {
                    "success": result.success,
                    "post_id": result.post_id,
                    "content": result.content,
                    "error": result.error,
                    "timestamp": result.timestamp.isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ 貼文生成失敗: {e}")
                raise
        
        return await self.process_batch_async(post_requests, generate_single_post, progress_callback)

class IntradayTriggerProcessor(ParallelProcessor):
    """盤中觸發器並行處理器"""
    
    def __init__(self, max_concurrent: int = 3, timeout: int = 30):
        super().__init__(max_concurrent, timeout)
        
    async def execute_triggers_parallel(
        self,
        trigger_configs: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        並行執行多個盤中觸發器
        
        Args:
            trigger_configs: 觸發器配置列表
            progress_callback: 進度回調函數
            
        Returns:
            觸發器執行結果列表
        """
        logger.info(f"🚀 開始並行執行 {len(trigger_configs)} 個盤中觸發器")
        
        async def execute_single_trigger(config: Dict[str, Any]) -> Dict[str, Any]:
            """執行單個觸發器"""
            try:
                from routes.intraday_trigger_route import execute_intraday_trigger
                
                # 調用現有的觸發器執行邏輯
                result = await execute_intraday_trigger(config)
                
                return {
                    "success": True,
                    "result": result,
                    "config": config
                }
                
            except Exception as e:
                logger.error(f"❌ 觸發器執行失敗: {e}")
                raise
        
        return await self.process_batch_async(trigger_configs, execute_single_trigger, progress_callback)

# 全局實例
interaction_processor = InteractionDataProcessor(max_concurrent=3, timeout=30)
post_generation_processor = PostGenerationProcessor(max_concurrent=2, timeout=120)
trigger_processor = IntradayTriggerProcessor(max_concurrent=3, timeout=30)
