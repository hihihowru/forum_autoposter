"""
並行批量貼文生成器 - 解決 API 塞車問題
"""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
from fastapi.responses import StreamingResponse

from parallel_processor import post_generation_processor
from post_record_service import PostingRequest

logger = logging.getLogger(__name__)

class ParallelBatchGenerator:
    """並行批量貼文生成器"""
    
    def __init__(self, max_concurrent: int = 2, timeout: int = 120):
        """
        初始化並行批量生成器
        
        Args:
            max_concurrent: 最大並發數量（貼文生成比較耗時，建議設為 2-3）
            timeout: 單個貼文生成超時時間（秒）
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        
    async def generate_posts_parallel_stream(
        self,
        request: Any,  # BatchPostRequest
        progress_callback: Optional[callable] = None
    ) -> AsyncGenerator[str, None]:
        """
        並行生成貼文並使用 Server-Sent Events 流式返回結果
        
        Args:
            request: 批量貼文生成請求
            progress_callback: 進度回調函數
            
        Yields:
            Server-Sent Events 格式的字符串
        """
        total_posts = len(request.posts)
        successful_posts = 0
        failed_posts = 0
        
        logger.info(f"🚀 開始並行批量生成 {total_posts} 篇貼文，最大並發數: {self.max_concurrent}")
        
        # 生成 batch 級別的共享 commodity tags
        batch_commodity_tags = []
        should_use_shared_tags = False
        
        # 檢查是否啟用共享標籤
        if request.tags_config and request.tags_config.get('stock_tags', {}).get('batch_shared_tags', False):
            should_use_shared_tags = True
            logger.info("🏷️ 根據前端標籤配置啟用全貼同群股標")
        elif request.batch_config.get('shared_commodity_tags', True):
            should_use_shared_tags = True
            logger.info("🏷️ 根據批量配置啟用共享標籤")
        
        if should_use_shared_tags:
            logger.info("🏷️ 生成 batch 級別的共享 commodity tags...")
            # 這裡可以實現共享標籤生成邏輯
            logger.info(f"✅ 生成 {len(batch_commodity_tags)} 個共享 commodity tags")
        else:
            logger.info("🏷️ 未啟用共享標籤，每個貼文將使用獨立標籤")
        
        # 發送開始事件
        yield f"data: {json.dumps({'type': 'batch_start', 'total': total_posts, 'session_id': request.session_id, 'shared_tags_count': len(batch_commodity_tags), 'parallel_mode': True})}\n\n"
        
        try:
            # 準備貼文生成請求列表
            post_requests = []
            for index, post_data in enumerate(request.posts):
                # 為每個貼文智能分配數據源
                logger.info(f"🧠 為第 {index + 1} 篇貼文智能分配數據源...")
                
                # 創建KOL和股票配置
                from smart_data_source_assigner import KOLProfile, StockProfile, smart_assigner
                
                kol_profile = KOLProfile(
                    serial=int(post_data.get('kol_serial', 150)),
                    nickname=f"KOL-{post_data.get('kol_serial', 150)}",
                    persona=request.batch_config.get('kol_persona', 'technical'),
                    expertise_areas=[],
                    content_style=request.batch_config.get('content_style', 'chart_analysis'),
                    target_audience=request.batch_config.get('target_audience', 'active_traders')
                )
                
                stock_profile = StockProfile(
                    stock_code=post_data.get('stock_code'),
                    stock_name=post_data.get('stock_name'),
                    industry='unknown',
                    market_cap='medium',
                    volatility='medium',
                    news_frequency='medium'
                )
                
                # 智能分配數據源
                data_source_assignment = smart_assigner.assign_data_sources(
                    kol_profile=kol_profile,
                    stock_profile=stock_profile,
                    batch_context={'trigger_type': 'manual_batch'}
                )
                
                hybrid_data_sources = data_source_assignment.get('recommended_sources', ['finlab', 'serper'])
                logger.info(f"✅ 第 {index + 1} 篇貼文分配數據源: {hybrid_data_sources}")
                
                # 準備新聞配置
                news_config = request.news_config or {}
                
                # 如果有熱門話題，更新新聞搜索關鍵字
                if hasattr(request, 'trending_topics') and request.trending_topics:
                    topic_keywords = []
                    for topic in request.trending_topics[:3]:  # 取前3個話題
                        topic_id = topic.get('id', '')
                        topic_title = topic.get('title', '')
                        if topic_title:
                            topic_keywords.append({
                                "id": f"topic_{topic_id}",
                                "keyword": topic_title,
                                "type": "trigger_keyword",
                                "description": f"熱門話題關鍵字: {topic_title}"
                            })
                    
                    news_config['search_keywords'] = topic_keywords
                    logger.info(f"✅ 更新後的搜索關鍵字: {topic_keywords}")
                
                # 創建貼文生成請求
                post_request = {
                    'stock_code': post_data.get('stock_code'),
                    'stock_name': post_data.get('stock_name'),
                    'kol_serial': post_data.get('kol_serial'),
                    'kol_persona': request.batch_config.get('kol_persona', 'technical'),
                    'content_style': request.batch_config.get('content_style', 'chart_analysis'),
                    'target_audience': request.batch_config.get('target_audience', 'active_traders'),
                    'batch_mode': True,
                    'session_id': request.session_id,
                    'data_sources': hybrid_data_sources,
                    'explainability_config': request.explainability_config,
                    'news_config': news_config,
                    'tags_config': request.tags_config,
                    'shared_commodity_tags': batch_commodity_tags
                }
                post_requests.append(post_request)
            
            # 定義進度回調函數
            async def progress_callback_internal(completed: int, total: int, result: Dict[str, Any]):
                """內部進度回調函數"""
                nonlocal successful_posts, failed_posts
                
                percentage = round(completed / total * 100, 1)
                
                if result.get("success"):
                    successful_posts += 1
                    logger.info(f"✅ 進度: {completed}/{total} ({percentage}%) - 貼文生成成功")
                    
                    # 發送貼文生成完成事件
                    post_response = {
                        'type': 'post_generated',
                        'success': True,
                        'post_id': result.get("post_id"),
                        'content': result.get("content"),
                        'error': None,
                        'timestamp': result.get("timestamp"),
                        'progress': {
                            'current': completed,
                            'total': total,
                            'percentage': percentage,
                            'successful': successful_posts,
                            'failed': failed_posts
                        }
                    }
                    yield f"data: {json.dumps(post_response)}\n\n"
                    
                else:
                    failed_posts += 1
                    logger.warning(f"❌ 進度: {completed}/{total} ({percentage}%) - 貼文生成失敗: {result.get('error', 'Unknown error')}")
                    
                    # 發送錯誤事件
                    error_response = {
                        'type': 'post_error',
                        'success': False,
                        'error': result.get('error', 'Unknown error'),
                        'progress': {
                            'current': completed,
                            'total': total,
                            'percentage': percentage,
                            'successful': successful_posts,
                            'failed': failed_posts
                        }
                    }
                    yield f"data: {json.dumps(error_response)}\n\n"
                
                # 調用外部進度回調
                if progress_callback:
                    await progress_callback(completed, total, result)
            
            # 並行生成所有貼文
            logger.info(f"🚀 開始並行生成 {len(post_requests)} 篇貼文...")
            
            # 使用自定義的並行處理器
            results = await self._generate_posts_with_progress(
                post_requests,
                progress_callback_internal
            )
            
            # 發送完成事件
            completion_response = {
                'type': 'batch_complete',
                'success': True,
                'total_posts': total_posts,
                'successful_posts': successful_posts,
                'failed_posts': failed_posts,
                'completion_rate': round(successful_posts / total_posts * 100, 1) if total_posts > 0 else 0,
                'timestamp': datetime.now().isoformat(),
                'parallel_mode': True
            }
            yield f"data: {json.dumps(completion_response)}\n\n"
            
            logger.info(f"🎉 並行批量生成完成: 成功 {successful_posts} 篇，失敗 {failed_posts} 篇")
            
        except Exception as e:
            logger.error(f"❌ 並行批量生成失敗: {e}")
            import traceback
            logger.error(f"📋 錯誤堆疊: {traceback.format_exc()}")
            
            # 發送錯誤事件
            error_response = {
                'type': 'batch_error',
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_response)}\n\n"
    
    async def _generate_posts_with_progress(
        self,
        post_requests: List[Dict[str, Any]],
        progress_callback: callable
    ) -> List[Dict[str, Any]]:
        """
        帶進度回調的並行貼文生成
        
        Args:
            post_requests: 貼文生成請求列表
            progress_callback: 進度回調函數
            
        Returns:
            生成結果列表
        """
        # 創建信號量來控制並發數
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def generate_single_post_with_semaphore(request: Dict[str, Any], index: int) -> Dict[str, Any]:
            """帶信號量控制的單個貼文生成"""
            async with semaphore:
                return await self._generate_single_post(request, index)
        
        # 創建任務列表
        tasks = []
        for i, request in enumerate(post_requests):
            task = asyncio.create_task(generate_single_post_with_semaphore(request, i))
            tasks.append(task)
        
        # 並行執行並處理結果
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
                    async for event in progress_callback(completed, len(post_requests), result):
                        yield event
                        
            except Exception as e:
                logger.error(f"❌ 任務執行失敗: {e}")
                error_result = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                results.append(error_result)
                completed += 1
                
                # 調用進度回調
                if progress_callback:
                    async for event in progress_callback(completed, len(post_requests), error_result):
                        yield event
        
        return results
    
    async def _generate_single_post(self, request: Dict[str, Any], index: int) -> Dict[str, Any]:
        """生成單個貼文"""
        try:
            logger.info(f"🔄 生成第 {index + 1} 篇貼文...")
            
            # 轉換為 PostingRequest 對象
            posting_request = PostingRequest(**request)
            
            # 調用現有的貼文生成邏輯
            from main import manual_post_content
            result = await manual_post_content(posting_request)
            
            return {
                "success": result.success,
                "post_id": result.post_id,
                "content": result.content,
                "error": result.error,
                "timestamp": result.timestamp.isoformat(),
                "index": index
            }
            
        except Exception as e:
            logger.error(f"❌ 第 {index + 1} 篇貼文生成失敗: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "index": index
            }

# 全局實例
parallel_batch_generator = ParallelBatchGenerator(max_concurrent=2, timeout=120)


