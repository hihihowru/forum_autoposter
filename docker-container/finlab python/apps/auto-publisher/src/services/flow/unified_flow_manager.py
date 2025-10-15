"""
統一的流程管理器
整合所有可重用組件，避免重複代碼
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from src.clients.google.sheets_client import GoogleSheetsClient
from src.services.assign.assignment_service import AssignmentService, TopicData
from src.services.content.content_generator import ContentGenerator, ContentRequest
from src.services.stock.stock_data_service import StockDataService
from src.services.stock.topic_stock_service import TopicStockService
from src.services.trending_topic_news_service import TrendingTopicNewsService, TrendingTopicPost, PostGenerationResult
# PostgreSQL 服務將在需要時動態導入
from src.utils.limit_up_data_parser import LimitUpDataParser

logger = logging.getLogger(__name__)

@dataclass
class FlowConfig:
    """流程配置"""
    flow_type: str  # "trending_topic" | "limit_up_stock"
    max_assignments_per_topic: int = 3
    enable_stock_analysis: bool = True
    enable_content_generation: bool = True
    enable_sheets_recording: bool = True
    enable_publishing: bool = False

@dataclass
class FlowResult:
    """流程執行結果"""
    success: bool
    flow_type: str
    processed_topics: int
    generated_posts: int
    errors: List[str]
    execution_time: float

class UnifiedFlowManager:
    """統一的流程管理器"""
    
    def __init__(self, sheets_client: GoogleSheetsClient):
        """初始化流程管理器"""
        self.sheets_client = sheets_client
        self.cmoney_client = CMoneyClient()
        self.assignment_service = AssignmentService(sheets_client)
        self.content_generator = ContentGenerator()
        self.stock_data_service = StockDataService()
        self.topic_stock_service = TopicStockService()
        self.limit_up_parser = LimitUpDataParser()
        
        # 新增：熱門話題新聞搜尋服務
        self.trending_news_service = TrendingTopicNewsService()
        
        # PostgreSQL 服務將在需要時動態初始化
        
        # 統一的認證管理
        self._access_token = None
        self._token_expires_at = None
        
        logger.info("統一流程管理器初始化完成")
    
    def _get_mock_trending_topics(self) -> List[Topic]:
        """獲取模擬熱門話題數據"""
        from src.clients.cmoney.models import Topic
        
        mock_topics = [
            Topic(
                id="mock_topic_001",
                title="台股高檔震盪，開高走平背後的真相？",
                name="台股高檔震盪，開高走平背後的真相？",
                last_article_create_time=datetime.now().isoformat(),
                raw_data={
                    "id": "mock_topic_001",
                    "title": "台股高檔震盪，開高走平背後的真相？",
                    "name": "台股高檔震盪，開高走平背後的真相？",
                    "description": "台股今日開高後走平，市場關注後續走勢",
                    "keywords": "台股,大盤,震盪,技術分析",
                    "relatedStockSymbols": [
                        {"key": "2330", "type": "Stock"},
                        {"key": "2454", "type": "Stock"},
                        {"key": "2317", "type": "Stock"}
                    ]
                }
            ),
            Topic(
                id="mock_topic_002",
                title="AI概念股強勢，台積電領軍上攻",
                name="AI概念股強勢，台積電領軍上攻",
                last_article_create_time=datetime.now().isoformat(),
                raw_data={
                    "id": "mock_topic_002",
                    "title": "AI概念股強勢，台積電領軍上攻",
                    "name": "AI概念股強勢，台積電領軍上攻",
                    "description": "AI概念股表現強勢，台積電領軍科技股上攻",
                    "keywords": "AI,台積電,科技股,半導體",
                    "relatedStockSymbols": [
                        {"key": "2330", "type": "Stock"},
                        {"key": "2454", "type": "Stock"},
                        {"key": "2379", "type": "Stock"}
                    ]
                }
            ),
            Topic(
                id="mock_topic_003",
                title="通膨數據出爐，央行政策走向引關注",
                name="通膨數據出爐，央行政策走向引關注",
                last_article_create_time=datetime.now().isoformat(),
                raw_data={
                    "id": "mock_topic_003",
                    "title": "通膨數據出爐，央行政策走向引關注",
                    "name": "通膨數據出爐，央行政策走向引關注",
                    "description": "最新通膨數據公布，市場關注央行政策動向",
                    "keywords": "通膨,央行,利率,總經",
                    "relatedStockSymbols": [
                        {"key": "2881", "type": "Stock"},
                        {"key": "2882", "type": "Stock"},
                        {"key": "2886", "type": "Stock"}
                    ]
                }
            ),
            Topic(
                id="mock_topic_004",
                title="生技股異軍突起，減重藥題材發酵",
                name="生技股異軍突起，減重藥題材發酵",
                last_article_create_time=datetime.now().isoformat(),
                raw_data={
                    "id": "mock_topic_004",
                    "title": "生技股異軍突起，減重藥題材發酵",
                    "name": "生技股異軍突起，減重藥題材發酵",
                    "description": "生技股異軍突起，減重藥題材持續發酵",
                    "keywords": "生技,減重藥,醫療,新藥",
                    "relatedStockSymbols": [
                        {"key": "6919", "type": "Stock"},
                        {"key": "4743", "type": "Stock"},
                        {"key": "6547", "type": "Stock"}
                    ]
                }
            ),
            Topic(
                id="mock_topic_005",
                title="電動車概念股回溫，充電樁建設加速",
                name="電動車概念股回溫，充電樁建設加速",
                last_article_create_time=datetime.now().isoformat(),
                raw_data={
                    "id": "mock_topic_005",
                    "title": "電動車概念股回溫，充電樁建設加速",
                    "name": "電動車概念股回溫，充電樁建設加速",
                    "description": "電動車概念股回溫，充電樁建設加速進行",
                    "keywords": "電動車,充電樁,新能源,環保",
                    "relatedStockSymbols": [
                        {"key": "3661", "type": "Stock"},
                        {"key": "2308", "type": "Stock"},
                        {"key": "2377", "type": "Stock"}
                    ]
                }
            )
        ]
        
        logger.info(f"生成 {len(mock_topics)} 個模擬熱門話題")
        return mock_topics
    
    async def _ensure_valid_token(self) -> str:
        """確保有有效的 access token"""
        if (self._access_token and self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            return self._access_token
        
        # 使用統一的登入憑證
        credentials = LoginCredentials(
            email='forum_200@cmoney.com.tw',
            password='N9t1kY3x'
        )
        
        access_token = await self.cmoney_client.login(credentials)
        self._access_token = access_token.token
        self._token_expires_at = access_token.expires_at
        
        logger.info("成功獲取新的 access token")
        return self._access_token
    
    async def execute_trending_topic_flow(self, config: FlowConfig) -> FlowResult:
        """執行熱門話題流程 - 整合智能新聞搜尋"""
        start_time = datetime.now()
        
        try:
            logger.info("開始執行熱門話題流程（整合智能新聞搜尋）")
            
            # 1. 嘗試獲取真實熱門話題
            topics = []
            try:
                # 獲取 access token
                token = await self._ensure_valid_token()
                
                # 獲取熱門話題
                topics = await self.cmoney_client.get_trending_topics(token)
                logger.info(f"成功獲取到 {len(topics)} 個真實熱門話題")
                
            except Exception as e:
                logger.warning(f"獲取真實熱門話題失敗: {e}")
                logger.info("使用模擬熱門話題數據作為fallback")
                
                # 使用模擬數據
                topics = self._get_mock_trending_topics()
                logger.info(f"使用 {len(topics)} 個模擬熱門話題")
            
            # 2. 處理話題（包含股票查詢）
            processed_topics = await self.topic_stock_service.process_topics_with_stocks(topics)
            
            # 3. 轉換為貼文格式並執行智能新聞搜尋
            trending_posts = self._convert_topics_to_posts(processed_topics)
            
            # 4. 使用智能新聞搜尋服務處理每個貼文
            post_results = await self.trending_news_service.process_trending_topic_posts(trending_posts)
            
            # 5. 記錄結果到 PostgreSQL
            if config.enable_sheets_recording:
                await self._record_trending_topic_results_to_postgresql(post_results)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 統計結果
            successful_posts = [r for r in post_results if r.success]
            failed_posts = [r for r in post_results if not r.success]
            
            logger.info(f"熱門話題流程完成: {len(successful_posts)} 個成功, {len(failed_posts)} 個失敗")
            
            return FlowResult(
                success=True,
                flow_type="trending_topic",
                processed_topics=len(processed_topics),
                generated_posts=len(successful_posts),
                errors=[r.error_message for r in failed_posts if r.error_message],
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"熱門話題流程執行失敗: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return FlowResult(
                success=False,
                flow_type="trending_topic",
                processed_topics=0,
                generated_posts=0,
                errors=[str(e)],
                execution_time=execution_time
            )
    
    def _convert_topics_to_posts(self, processed_topics: List[Dict[str, Any]]) -> List[TrendingTopicPost]:
        """將處理後的話題轉換為貼文格式"""
        posts = []
        
        for topic_data in processed_topics:
            topic_id = topic_data.get('id', 'unknown')
            topic_title = topic_data.get('title', '')
            topic_content = topic_data.get('content', '')
            stock_ids = topic_data.get('stock_ids', [])
            
            # 為每個股票-話題組合創建一個貼文
            if stock_ids:
                for stock_id in stock_ids:
                    post_id = f"{topic_id}_{stock_id}"
                    post = TrendingTopicPost(
                        post_id=post_id,
                        topic_title=topic_title,
                        topic_content=topic_content,
                        stock_ids=[stock_id],
                        is_topic_only=False,
                        kol_info={}
                    )
                    posts.append(post)
            else:
                # 純話題貼文
                post_id = f"{topic_id}_topic_only"
                post = TrendingTopicPost(
                    post_id=post_id,
                    topic_title=topic_title,
                    topic_content=topic_content,
                    stock_ids=[],
                    is_topic_only=True,
                    kol_info={}
                )
                posts.append(post)
        
        logger.info(f"轉換為 {len(posts)} 個貼文")
        return posts
    
    async def _record_trending_topic_results_to_postgresql(self, post_results: List[PostGenerationResult]):
        """記錄熱門話題結果到 PostgreSQL"""
        try:
            logger.info(f"開始記錄 {len(post_results)} 個貼文結果到 PostgreSQL")
            
            # 動態導入 PostgreSQL 服務
            import sys
            import os
            posting_service_path = os.path.join(os.path.dirname(__file__), '../../../docker-container/finlab python/apps/posting-service')
            if posting_service_path not in sys.path:
                sys.path.insert(0, posting_service_path)
            
            from postgresql_service import PostgreSQLPostRecordService
            post_service = PostgreSQLPostRecordService()
            
            for result in post_results:
                if not result.success:
                    continue
                
                # 準備 PostgreSQL 記錄數據
                post_data = {
                    'post_id': result.post_id,
                    'kol_serial': "",  # 待分配
                    'kol_nickname': "",  # 待分配
                    'kol_persona': "",  # 待分配
                    'stock_code': ", ".join(result.stock_ids) if result.stock_ids else "",
                    'stock_name': "",  # 待查詢
                    'title': result.generated_content.title if result.generated_content else result.topic_title,
                    'content': result.generated_content.content if result.generated_content else "",
                    'content_md': result.generated_content.content if result.generated_content else "",
                    'status': 'ready_to_gen',
                    'content_type': 'trending_topic',
                    'topic_id': result.post_id,
                    'topic_title': result.topic_title,
                    'topic_keywords': ", ".join(result.stock_ids) if result.stock_ids else "",
                    'generated_at': datetime.now(),
                    'news_sources': len(result.news_results),
                    'confidence_score': result.generated_content.confidence_score if result.generated_content else 0.0
                }
                
                # 保存到 PostgreSQL
                post_service.create_post_record(post_data)
                logger.info(f"記錄貼文到 PostgreSQL: {result.post_id}")
                
        except Exception as e:
            logger.error(f"記錄到 PostgreSQL 失敗: {e}")
    
    async def execute_limit_up_stock_flow(self, config: FlowConfig) -> FlowResult:
        """執行漲停股流程"""
        start_time = datetime.now()
        
        try:
            logger.info("開始執行漲停股流程")
            
            # 1. 獲取漲停股列表（這裡需要實現漲停股篩選邏輯）
            limit_up_stocks = await self._get_limit_up_stocks()
            logger.info(f"獲取到 {len(limit_up_stocks)} 檔漲停股")
            
            # 2. 轉換為話題格式
            topics = self._convert_stocks_to_topics(limit_up_stocks)
            
            # 3. 執行統一的處理流程
            result = await self._execute_unified_flow(topics, config)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return FlowResult(
                success=True,
                flow_type="limit_up_stock",
                processed_topics=len(topics),
                generated_posts=result.get('generated_posts', 0),
                errors=result.get('errors', []),
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"漲停股流程執行失敗: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return FlowResult(
                success=False,
                flow_type="limit_up_stock",
                processed_topics=0,
                generated_posts=0,
                errors=[str(e)],
                execution_time=execution_time
            )
    
    async def execute_intraday_limit_up_flow(self, stock_ids: List[str], config: FlowConfig) -> FlowResult:
        """執行盤中漲停股流程"""
        start_time = datetime.now()
        
        try:
            logger.info(f"開始執行盤中漲停股流程，股票代號: {stock_ids}")
            
            # 1. 驗證股票代號
            valid_stock_ids = self._validate_stock_ids(stock_ids)
            logger.info(f"有效股票代號: {valid_stock_ids}")
            
            # 2. 使用 Serper API 抓取相關資料並解析漲停資訊
            limit_up_stocks = await self._get_intraday_limit_up_stocks_with_serper(valid_stock_ids)
            logger.info(f"確認漲停股票: {[stock['stock_id'] for stock in limit_up_stocks]}")
            
            # 3. 轉換為話題格式
            topics = self._convert_intraday_stocks_to_topics(limit_up_stocks)
            
            # 4. 執行統一的處理流程
            result = await self._execute_unified_flow(topics, config)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return FlowResult(
                success=True,
                flow_type="intraday_limit_up",
                processed_topics=len(topics),
                generated_posts=result.get('generated_posts', 0),
                errors=result.get('errors', []),
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"盤中漲停股流程執行失敗: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return FlowResult(
                success=False,
                flow_type="intraday_limit_up",
                processed_topics=0,
                generated_posts=0,
                errors=[str(e)],
                execution_time=execution_time
            )
    
    async def _execute_unified_flow(self, topics: List[Dict[str, Any]], config: FlowConfig) -> Dict[str, Any]:
        """執行統一的處理流程"""
        result = {
            'generated_posts': 0,
            'errors': []
        }
        
        try:
            # 1. 載入 KOL 配置
            self.assignment_service.load_kol_profiles()
            active_kols = [kol for kol in self.assignment_service._kol_profiles if kol.enabled]
            logger.info(f"載入 {len(active_kols)} 個活躍 KOL")
            
            # 2. 處理每個話題
            for topic in topics:
                try:
                    # 2.1 話題分類
                    classification = self.assignment_service.classify_topic(
                        topic.get('id', ''),
                        topic.get('title', ''),
                        topic.get('content', '')
                    )
                    
                    # 2.2 創建 TopicData
                    topic_data = TopicData(
                        topic_id=topic.get('id', ''),
                        title=topic.get('title', ''),
                        input_index=0,
                        persona_tags=classification.persona_tags,
                        industry_tags=classification.industry_tags,
                        event_tags=classification.event_tags,
                        stock_tags=classification.stock_tags,
                        classification=classification
                    )
                    
                    # 2.3 KOL 分派
                    assignments = self.assignment_service.assign_topics(
                        [topic_data], 
                        max_assignments_per_topic=config.max_assignments_per_topic
                    )
                    
                    # 2.4 股票分配
                    stock_assignments = {}
                    if topic.get('stock_data', {}).get('has_stocks', False):
                        stocks = topic['stock_data']['stocks']
                        kol_serials = [assignment.kol_serial for assignment in assignments]
                        stock_assignments = self.topic_stock_service.assign_stocks_to_kols(stocks, kol_serials)
                    
                    # 2.5 內容生成
                    if config.enable_content_generation:
                        generated_count = await self._generate_content_for_assignments(
                            assignments, stock_assignments, topic_data
                        )
                        result['generated_posts'] += generated_count
                    
                    # 2.6 Google Sheets 記錄
                    if config.enable_sheets_recording:
                        await self._record_to_sheets(assignments, topic_data)
                    
                except Exception as e:
                    error_msg = f"處理話題 {topic.get('title', '')} 失敗: {e}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    continue
            
            return result
            
        except Exception as e:
            error_msg = f"統一流程執行失敗: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            return result
    
    async def _generate_content_for_assignments(self, assignments, stock_assignments, topic_data) -> int:
        """為分派生成內容"""
        generated_count = 0
        
        for assignment in assignments:
            try:
                kol = next((k for k in self.assignment_service._kol_profiles 
                           if k.serial == assignment.kol_serial), None)
                if not kol:
                    continue
                
                # 準備市場數據
                market_data = {}
                assigned_stock = stock_assignments.get(assignment.kol_serial)
                if assigned_stock and assigned_stock.stock_id:
                    # 根據 KOL 角色獲取對應的數據
                    role_based_data = assigned_stock.get('role_based_data', {})
                    kol_role = self._map_kol_persona_to_role(kol.persona)
                    role_data = role_based_data.get(kol_role, {})
                    
                    market_data = {
                        'stock_id': assigned_stock.stock_id,
                        'stock_name': assigned_stock.stock_name,
                        'stock_data': assigned_stock,
                        'has_stock': True,
                        'kol_role': kol_role,
                        'role_data': role_data,
                        'serper_analysis': assigned_stock.get('serper_analysis', {}),
                        'data_sources': role_data.get('data_sources', []),
                        'analysis_focus': role_data.get('analysis_focus', []),
                        'content_guidance': role_data.get('content_guidance', '')
                    }
                else:
                    market_data = {'has_stock': False}
                
                # 生成內容
                content_request = ContentRequest(
                    topic_title=topic_data.title,
                    topic_keywords=", ".join(topic_data.persona_tags + topic_data.industry_tags + topic_data.event_tags),
                    kol_persona=kol.persona,
                    kol_nickname=kol.nickname,
                    content_type="investment",
                    target_audience="active_traders",
                    market_data=market_data
                )
                
                generated = self.content_generator.generate_complete_content(content_request)
                if generated.success:
                    generated_count += 1
                    logger.info(f"為 {kol.nickname} ({kol_role}) 生成內容成功")
                
            except Exception as e:
                logger.error(f"為 KOL {assignment.kol_serial} 生成內容失敗: {e}")
                continue
        
        return generated_count
    
    def _map_kol_persona_to_role(self, persona: str) -> str:
        """將 KOL 人設映射到角色"""
        persona_lower = persona.lower()
        
        if any(keyword in persona_lower for keyword in ['技術', '籌碼', '線圖', '指標']):
            return '籌碼派'
        elif any(keyword in persona_lower for keyword in ['基本面', '財報', '營收', '獲利']):
            return '基本面派'
        elif any(keyword in persona_lower for keyword in ['消息', '新聞', '事件', '公告']):
            return '消息派'
        else:
            return '綜合派'  # 預設為綜合派
    
    async def _record_to_sheets(self, assignments, topic_data):
        """記錄到 Google Sheets"""
        try:
            for assignment in assignments:
                kol = next((k for k in self.assignment_service._kol_profiles 
                           if k.serial == assignment.kol_serial), None)
                if not kol:
                    continue
                
                # 準備記錄數據
                record = [
                    assignment.task_id,           # 貼文ID
                    str(assignment.kol_serial),   # KOL Serial
                    kol.nickname,                 # KOL 暱稱
                    kol.member_id,                # KOL ID
                    kol.persona,                  # Persona
                    "investment",                 # Content Type
                    "1",                          # 已派發TopicIndex
                    topic_data.topic_id,          # 已派發TopicID
                    topic_data.title,             # 已派發TopicTitle
                    ", ".join(topic_data.persona_tags + topic_data.industry_tags),  # 已派發TopicKeywords
                    "",                          # 生成內容
                    "ready_to_gen",               # 發文狀態
                    datetime.now().isoformat(),   # 上次排程時間
                    "",                          # 發文時間戳記
                    "",                          # 最近錯誤訊息
                    "",                          # 平台發文ID
                    "",                          # 平台發文URL
                    ""                           # 分配股票資訊
                ]
                
                self.sheets_client.append_sheet('貼文記錄表', [record])
                logger.info(f"記錄到 Google Sheets: {assignment.task_id}")
                
        except Exception as e:
            logger.error(f"記錄到 Google Sheets 失敗: {e}")
    
    async def _get_limit_up_stocks(self) -> List[Dict[str, Any]]:
        """獲取漲停股列表（需要實現）"""
        # TODO: 實現漲停股篩選邏輯
        # 可以使用 FinLab API 或其他數據源
        return []
    
    def _convert_stocks_to_topics(self, stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """將股票轉換為話題格式"""
        topics = []
        for stock in stocks:
            topic = {
                'id': f"limit_up_{stock.get('stock_id', '')}",
                'title': f"{stock.get('stock_name', '')} 漲停分析",
                'content': f"{stock.get('stock_name', '')} 今日漲停，技術面分析",
                'stock_data': {
                    'has_stocks': True,
                    'stocks': [stock]
                }
            }
            topics.append(topic)
        return topics
    
    def _validate_stock_ids(self, stock_ids: List[str]) -> List[str]:
        """驗證股票代號格式"""
        valid_ids = []
        for stock_id in stock_ids:
            # 檢查是否為4位數字
            if isinstance(stock_id, str) and stock_id.isdigit() and len(stock_id) == 4:
                valid_ids.append(stock_id)
            else:
                logger.warning(f"無效的股票代號格式: {stock_id}")
        return valid_ids
    
    async def _get_intraday_limit_up_stocks_with_serper(self, stock_ids: List[str]) -> List[Dict[str, Any]]:
        """使用 Serper API 獲取盤中漲停股列表並分析漲停原因"""
        limit_up_stocks = []
        
        for stock_id in stock_ids:
            try:
                logger.info(f"處理股票: {stock_id}")
                
                # 1. 統一使用 Serper API 分析漲停原因
                serper_analysis = await self._analyze_limit_up_reason(stock_id)
                
                # 2. 解析漲停資訊（從你提供的資料中提取）
                stock_info = self._parse_limit_up_info(stock_id, serper_analysis)
                
                if stock_info:
                    # 3. 根據 KOL 角色特性派發數據源
                    enhanced_stock_info = await self._distribute_data_by_kol_role(stock_info, serper_analysis)
                    limit_up_stocks.append(enhanced_stock_info)
                    logger.info(f"確認漲停: {stock_id} 漲幅 {enhanced_stock_info.get('change_percent', 0):.2f}%")
                else:
                    logger.warning(f"無法解析漲停資訊: {stock_id}")
                    
            except Exception as e:
                logger.error(f"處理股票 {stock_id} 時發生錯誤: {e}")
                continue
        
        return limit_up_stocks
    
    async def _analyze_limit_up_reason(self, stock_id: str) -> Dict[str, Any]:
        """使用 Serper API 分析漲停原因"""
        try:
            logger.info(f"分析漲停原因: {stock_id}")
            
            # 使用 Serper API 搜尋相關資料
            serper_data = await self._fetch_serper_data(stock_id)
            
            # 分析漲停原因
            analysis_result = {
                'stock_id': stock_id,
                'serper_data': serper_data,
                'limit_up_reasons': [],
                'news_sources': [],
                'analysis_sources': [],
                'key_events': [],
                'market_sentiment': 'neutral'
            }
            
            if serper_data and serper_data.get('organic'):
                organic_results = serper_data['organic']
                
                # 提取新聞和分析來源
                for result in organic_results[:10]:  # 取前10個結果
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    link = result.get('link', '')
                    
                    # 分類資料來源
                    if any(keyword in title.lower() for keyword in ['新聞', '報導', '消息', '公告']):
                        analysis_result['news_sources'].append({
                            'title': title,
                            'snippet': snippet,
                            'link': link,
                            'type': 'news'
                        })
                    elif any(keyword in title.lower() for keyword in ['分析', '報告', '研究', '評析']):
                        analysis_result['analysis_sources'].append({
                            'title': title,
                            'snippet': snippet,
                            'link': link,
                            'type': 'analysis'
                        })
                    
                    # 提取關鍵事件
                    if any(keyword in snippet.lower() for keyword in ['漲停', '漲幅', '利多', '好消息', '突破']):
                        analysis_result['key_events'].append({
                            'title': title,
                            'snippet': snippet,
                            'link': link
                        })
                
                # 分析市場情緒
                positive_keywords = ['利多', '好消息', '突破', '成長', '獲利', '營收']
                negative_keywords = ['利空', '壞消息', '下跌', '虧損', '風險']
                
                positive_count = sum(1 for event in analysis_result['key_events'] 
                                   if any(keyword in event['snippet'].lower() for keyword in positive_keywords))
                negative_count = sum(1 for event in analysis_result['key_events'] 
                                   if any(keyword in event['snippet'].lower() for keyword in negative_keywords))
                
                if positive_count > negative_count:
                    analysis_result['market_sentiment'] = 'positive'
                elif negative_count > positive_count:
                    analysis_result['market_sentiment'] = 'negative'
            
            logger.info(f"漲停原因分析完成: {stock_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"分析漲停原因失敗: {stock_id} - {e}")
            return {'stock_id': stock_id, 'error': str(e)}
    
    async def _distribute_data_by_kol_role(self, stock_info: Dict[str, Any], serper_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """根據 KOL 角色特性派發數據源"""
        stock_id = stock_info.get('stock_id', '')
        
        try:
            logger.info(f"根據 KOL 角色派發數據源: {stock_id}")
            
            # 獲取所有 KOL 角色
            kol_roles = self._get_kol_roles()
            
            # 為每個角色準備對應的數據源
            role_based_data = {}
            
            for role in kol_roles:
                role_data = await self._prepare_data_for_role(role, stock_id, serper_analysis)
                role_based_data[role] = role_data
            
            # 整合到股票資訊中
            enhanced_stock_info = stock_info.copy()
            enhanced_stock_info.update({
                'serper_analysis': serper_analysis,
                'role_based_data': role_based_data,
                'available_roles': list(kol_roles),
                'data_distribution_strategy': 'role_based'
            })
            
            logger.info(f"角色數據派發完成: {stock_id}")
            return enhanced_stock_info
            
        except Exception as e:
            logger.error(f"角色數據派發失敗: {stock_id} - {e}")
            return stock_info
    
    def _get_kol_roles(self) -> List[str]:
        """獲取所有 KOL 角色"""
        return [
            '籌碼派',      # 技術面、籌碼面
            '基本面派',    # 財報、營收、基本面
            '消息派',      # 新聞、消息、事件
            '綜合派'       # 全方位分析
        ]
    
    async def _prepare_data_for_role(self, role: str, stock_id: str, serper_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """為特定角色準備數據"""
        role_data = {
            'role': role,
            'data_sources': [],
            'analysis_focus': [],
            'content_guidance': ''
        }
        
        try:
            if role == '籌碼派':
                # 技術面數據
                technical_data = await self._fetch_technical_data(stock_id)
                role_data['data_sources'].append({
                    'type': 'technical',
                    'data': technical_data,
                    'priority': 'high'
                })
                role_data['analysis_focus'] = ['技術指標', '籌碼分析', '價量關係']
                role_data['content_guidance'] = '專注於技術面分析，包含 MACD、KD、RSI 等指標，以及籌碼面分析'
                
            elif role == '基本面派':
                # 財報和營收數據
                revenue_data = await self._fetch_revenue_data(stock_id)
                financial_data = await self._fetch_financial_data(stock_id)
                
                role_data['data_sources'].append({
                    'type': 'revenue',
                    'data': revenue_data,
                    'priority': 'high'
                })
                role_data['data_sources'].append({
                    'type': 'financial',
                    'data': financial_data,
                    'priority': 'high'
                })
                role_data['analysis_focus'] = ['營收成長', '獲利能力', '財務比率']
                role_data['content_guidance'] = '專注於基本面分析，包含營收、獲利、財務比率等指標'
                
            elif role == '消息派':
                # 新聞和分析資料
                role_data['data_sources'].append({
                    'type': 'news',
                    'data': {
                        'success': True,
                        'sources': serper_analysis.get('news_sources', []),
                        'count': len(serper_analysis.get('news_sources', []))
                    },
                    'priority': 'high'
                })
                role_data['data_sources'].append({
                    'type': 'analysis',
                    'data': {
                        'success': True,
                        'sources': serper_analysis.get('analysis_sources', []),
                        'count': len(serper_analysis.get('analysis_sources', []))
                    },
                    'priority': 'high'
                })
                role_data['analysis_focus'] = ['市場消息', '產業動態', '公司公告']
                role_data['content_guidance'] = '專注於消息面分析，包含新聞、公告、產業動態等'
                
            elif role == '綜合派':
                # 全方位數據
                technical_data = await self._fetch_technical_data(stock_id)
                revenue_data = await self._fetch_revenue_data(stock_id)
                financial_data = await self._fetch_financial_data(stock_id)
                market_data = await self._fetch_market_data(stock_id)
                
                role_data['data_sources'].extend([
                    {
                        'type': 'technical',
                        'data': technical_data,
                        'priority': 'medium'
                    },
                    {
                        'type': 'revenue',
                        'data': revenue_data,
                        'priority': 'medium'
                    },
                    {
                        'type': 'financial',
                        'data': financial_data,
                        'priority': 'medium'
                    },
                    {
                        'type': 'market',
                        'data': market_data,
                        'priority': 'medium'
                    },
                    {
                        'type': 'news',
                        'data': {
                            'success': True,
                            'sources': serper_analysis.get('news_sources', []),
                            'count': len(serper_analysis.get('news_sources', []))
                        },
                        'priority': 'medium'
                    }
                ])
                role_data['analysis_focus'] = ['技術面', '基本面', '消息面', '綜合分析']
                role_data['content_guidance'] = '全方位分析，包含技術面、基本面、消息面等各面向'
            
            return role_data
            
        except Exception as e:
            logger.error(f"為角色 {role} 準備數據失敗: {stock_id} - {e}")
            return role_data
    
    async def _enhance_stock_data(self, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """增強股票數據，調用各種數據支線"""
        stock_id = stock_info.get('stock_id', '')
        
        try:
            logger.info(f"開始增強股票數據: {stock_id}")
            
            # 並行調用各種數據支線
            tasks = [
                self._fetch_revenue_data(stock_id),
                self._fetch_technical_data(stock_id),
                self._fetch_financial_data(stock_id),
                self._fetch_market_data(stock_id)
            ]
            
            # 等待所有任務完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合結果
            revenue_data, technical_data, financial_data, market_data = results
            
            # 檢查是否有異常
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"數據支線 {i} 調用失敗: {result}")
            
            # 將數據整合到股票資訊中
            enhanced_stock_info = stock_info.copy()
            enhanced_stock_info.update({
                'revenue_data': revenue_data if not isinstance(revenue_data, Exception) else {},
                'technical_data': technical_data if not isinstance(technical_data, Exception) else {},
                'financial_data': financial_data if not isinstance(financial_data, Exception) else {},
                'market_data': market_data if not isinstance(market_data, Exception) else {},
                'data_sources': {
                    'revenue': 'available' if not isinstance(revenue_data, Exception) else 'unavailable',
                    'technical': 'available' if not isinstance(technical_data, Exception) else 'unavailable',
                    'financial': 'available' if not isinstance(financial_data, Exception) else 'unavailable',
                    'market': 'available' if not isinstance(market_data, Exception) else 'unavailable'
                }
            })
            
            logger.info(f"股票數據增強完成: {stock_id}")
            return enhanced_stock_info
            
        except Exception as e:
            logger.error(f"增強股票數據失敗: {stock_id} - {e}")
            return stock_info
    
    async def _fetch_revenue_data(self, stock_id: str) -> Dict[str, Any]:
        """獲取月營收數據"""
        try:
            logger.info(f"獲取月營收數據: {stock_id}")
            
            # 調用營收 API
            revenue_url = "http://localhost:8008"
            response = await self._make_api_request(f"{revenue_url}/revenue/{stock_id}/summary")
            
            if response and response.get('success', False):
                return {
                    'success': True,
                    'data': response.get('data', {}),
                    'source': 'revenue-api'
                }
            else:
                logger.warning(f"營收 API 調用失敗: {stock_id}")
                return {'success': False, 'error': 'API call failed'}
                
        except Exception as e:
            logger.error(f"獲取營收數據失敗: {stock_id} - {e}")
            return {'success': False, 'error': str(e)}
    
    async def _fetch_technical_data(self, stock_id: str) -> Dict[str, Any]:
        """獲取技術面整理數據"""
        try:
            logger.info(f"獲取技術面數據: {stock_id}")
            
            # 調用技術分析 API
            technical_url = "http://localhost:8002"
            response = await self._make_api_request(f"{technical_url}/analyze/{stock_id}")
            
            if response and response.get('success', False):
                return {
                    'success': True,
                    'data': response.get('data', {}),
                    'source': 'analyze-api'
                }
            else:
                logger.warning(f"技術分析 API 調用失敗: {stock_id}")
                return {'success': False, 'error': 'API call failed'}
                
        except Exception as e:
            logger.error(f"獲取技術面數據失敗: {stock_id} - {e}")
            return {'success': False, 'error': str(e)}
    
    async def _fetch_financial_data(self, stock_id: str) -> Dict[str, Any]:
        """獲取財報數據"""
        try:
            logger.info(f"獲取財報數據: {stock_id}")
            
            # 調用財報 API
            financial_url = "http://localhost:8009"
            response = await self._make_api_request(f"{financial_url}/financial/{stock_id}/summary")
            
            if response and response.get('success', False):
                return {
                    'success': True,
                    'data': response.get('data', {}),
                    'source': 'financial-api'
                }
            else:
                logger.warning(f"財報 API 調用失敗: {stock_id}")
                return {'success': False, 'error': 'API call failed'}
                
        except Exception as e:
            logger.error(f"獲取財報數據失敗: {stock_id} - {e}")
            return {'success': False, 'error': str(e)}
    
    async def _fetch_market_data(self, stock_id: str) -> Dict[str, Any]:
        """獲取市場數據"""
        try:
            logger.info(f"獲取市場數據: {stock_id}")
            
            # 調用基本面分析器
            fundamental_url = "http://localhost:8010"
            response = await self._make_api_request(f"{fundamental_url}/analyze/fundamental?stock_id={stock_id}")
            
            if response and response.get('success', False):
                return {
                    'success': True,
                    'data': response.get('data', {}),
                    'source': 'fundamental-analyzer'
                }
            else:
                logger.warning(f"基本面分析 API 調用失敗: {stock_id}")
                return {'success': False, 'error': 'API call failed'}
                
        except Exception as e:
            logger.error(f"獲取市場數據失敗: {stock_id} - {e}")
            return {'success': False, 'error': str(e)}
    
    async def _make_api_request(self, url: str) -> Optional[Dict[str, Any]]:
        """發送 API 請求"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"API 請求失敗: {url} - {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"API 請求異常: {url} - {e}")
            return None
    
    async def _fetch_serper_data(self, stock_id: str) -> Dict[str, Any]:
        """使用 Serper API 抓取股票相關資料"""
        try:
            import requests
            
            # Serper API 配置
            serper_api_key = os.getenv("SERPER_API_KEY")
            if not serper_api_key:
                logger.warning("未設定 SERPER_API_KEY，跳過 Serper API 查詢")
                return {}
            
            # 搜尋查詢
            search_query = f"{stock_id} 股票 漲停 今日 新聞 分析"
            
            headers = {
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": search_query,
                "num": 10,  # 取得前10筆結果
                "gl": "tw",  # 台灣地區
                "hl": "zh-tw"  # 繁體中文
            }
            
            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Serper API 查詢成功: {stock_id}")
                return data
            else:
                logger.error(f"Serper API 查詢失敗: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Serper API 查詢異常: {e}")
            return {}
    
    def _parse_limit_up_info(self, stock_id: str, serper_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析漲停資訊"""
        try:
            # 從漲停資料解析器中獲取股票資訊
            stock_data = self.limit_up_parser.get_stock_data(stock_id)
            
            if not stock_data:
                logger.warning(f"找不到股票 {stock_id} 的漲停資料")
                return None
            
            stock_info = {
                'stock_id': stock_id,
                'stock_name': stock_data.get('stock_name', f'股票{stock_id}'),
                'current_price': stock_data.get('current_price', 0),
                'change_amount': stock_data.get('change_amount', 0),
                'change_percent': stock_data.get('change_percent', 0),
                'high_price': stock_data.get('high_price', 0),
                'low_price': stock_data.get('low_price', 0),
                'volume': stock_data.get('volume', 0),
                'turnover': stock_data.get('turnover', 0),
                'rank': stock_data.get('rank', 0),
                'limit_up_time': datetime.now().isoformat(),
                'serper_data': serper_data,  # 包含 Serper API 查詢結果
                'news_sources': self._extract_news_sources(serper_data),
                'analysis_sources': self._extract_analysis_sources(serper_data)
            }
            
            return stock_info
            
        except Exception as e:
            logger.error(f"解析漲停資訊失敗: {e}")
            return None
    
    def _extract_news_sources(self, serper_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """從 Serper 資料中提取新聞來源"""
        news_sources = []
        
        try:
            organic_results = serper_data.get('organic', [])
            
            for result in organic_results[:5]:  # 取前5筆
                news_source = {
                    'title': result.get('title', ''),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', ''),
                    'source': result.get('source', '')
                }
                news_sources.append(news_source)
                
        except Exception as e:
            logger.error(f"提取新聞來源失敗: {e}")
        
        return news_sources
    
    def _extract_analysis_sources(self, serper_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """從 Serper 資料中提取分析來源"""
        analysis_sources = []
        
        try:
            organic_results = serper_data.get('organic', [])
            
            # 篩選分析相關的結果
            for result in organic_results:
                title = result.get('title', '').lower()
                snippet = result.get('snippet', '').lower()
                
                # 檢查是否為分析相關內容
                analysis_keywords = ['分析', '技術', '基本面', '財報', '展望', '預測', '評等']
                if any(keyword in title or keyword in snippet for keyword in analysis_keywords):
                    analysis_source = {
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'snippet': result.get('snippet', ''),
                        'source': result.get('source', ''),
                        'type': 'analysis'
                    }
                    analysis_sources.append(analysis_source)
                    
        except Exception as e:
            logger.error(f"提取分析來源失敗: {e}")
        
        return analysis_sources
    
    def _convert_intraday_stocks_to_topics(self, stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """將盤中漲停股轉換為話題格式"""
        topics = []
        for stock in stocks:
            topic = {
                'id': f"intraday_limit_up_{stock.get('stock_id', '')}",
                'title': f"{stock.get('stock_name', '')} 盤中漲停！漲幅 {stock.get('change_percent', 0):.1f}%",
                'content': f"{stock.get('stock_name', '')} 盤中強勢漲停，漲幅達 {stock.get('change_percent', 0):.1f}%，成交量 {stock.get('volume', 0)} 張",
                'stock_data': {
                    'has_stocks': True,
                    'stocks': [stock]
                },
                'intraday_data': {
                    'is_intraday': True,
                    'limit_up_time': stock.get('limit_up_time'),
                    'change_percent': stock.get('change_percent'),
                    'volume': stock.get('volume')
                }
            }
            topics.append(topic)
        return topics

# 創建服務實例的工廠函數
def create_unified_flow_manager(sheets_client: GoogleSheetsClient) -> UnifiedFlowManager:
    """創建統一流程管理器實例"""
    return UnifiedFlowManager(sheets_client)
