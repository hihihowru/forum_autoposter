"""
話題股票查詢服務
負責查詢話題相關的股票資訊，並整合到話題分配流程中
"""
import logging
import asyncio
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
from clients.google.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)

@dataclass
class StockInfo:
    """股票資訊"""
    stock_id: str
    stock_name: str
    stock_type: str = "Stock"
    confidence: float = 1.0

@dataclass
class TopicStockData:
    """話題股票數據"""
    topic_id: str
    topic_title: str
    has_stocks: bool
    stocks: List[StockInfo]
    raw_data: Optional[Dict[str, Any]] = None

class TopicStockService:
    """話題股票查詢服務"""
    
    def __init__(self, 
                 cmoney_client: Optional[CMoneyClient] = None,
                 sheets_client: Optional[GoogleSheetsClient] = None):
        """
        初始化話題股票服務
        
        Args:
            cmoney_client: CMoney 客戶端
            sheets_client: Google Sheets 客戶端
        """
        self.cmoney_client = cmoney_client or CMoneyClient()
        self.sheets_client = sheets_client or GoogleSheetsClient(
            credentials_file="./credentials/google-service-account.json",
            spreadsheet_id="148CUhBxqE-BZDPTKaAmOJG6m52CxB4KrxD9p5LikN2s"
        )
        self._access_token = None
        self._token_expires_at = None
        
        logger.info("話題股票服務初始化完成")
    
    async def _ensure_valid_token(self) -> str:
        """確保有有效的 access token"""
        if (self._access_token and self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            return self._access_token
        
        # 從 Google Sheets 讀取 KOL 憑證
        try:
            kol_data = self.sheets_client.read_sheet('同學會帳號管理', 'A:Z')
            
            if len(kol_data) < 2:
                raise Exception("沒有找到 KOL 數據")
            
            # 找到第一個有效的 KOL 憑證
            headers = kol_data[0]
            email_idx = None
            password_idx = None
            
            for i, header in enumerate(headers):
                if 'Email' in header or '帳號' in header:
                    email_idx = i
                elif '密碼' in header:
                    password_idx = i
            
            if email_idx is None or password_idx is None:
                raise Exception("找不到 Email 或密碼欄位")
            
            # 使用第一個 KOL 的憑證
            first_kol = kol_data[1]
            email = first_kol[email_idx] if len(first_kol) > email_idx else None
            password = first_kol[password_idx] if len(first_kol) > password_idx else None
            
            if not email or not password:
                raise Exception("KOL 憑證不完整")
            
            # 登入獲取 token
            credentials = LoginCredentials(email=email, password=password)
            access_token = await self.cmoney_client.login(credentials)
            
            self._access_token = access_token.token
            self._token_expires_at = access_token.expires_at
            
            logger.info(f"成功獲取新的 access token: {self._access_token[:30]}...")
            return self._access_token
            
        except Exception as e:
            logger.error(f"獲取 access token 失敗: {e}")
            raise
    
    async def get_topic_stocks(self, topic_id: str) -> TopicStockData:
        """
        獲取話題相關的股票資訊
        
        Args:
            topic_id: 話題 ID
            
        Returns:
            話題股票數據
        """
        try:
            # 確保有有效的 token
            access_token = await self._ensure_valid_token()
            
            # 查詢話題股票資訊
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Version": "2.0",
                "Accept-Encoding": "gzip",
                "cmoneyapi-trace-context": "topic_stock_service"
            }
            
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://forumservice.cmoney.tw/api/Topic/{topic_id}/Trending",
                    headers=headers,
                    timeout=15.0
                )
                
                if response.status_code != 200:
                    logger.warning(f"話題 {topic_id} 查詢失敗: HTTP {response.status_code}")
                    return TopicStockData(
                        topic_id=topic_id,
                        topic_title="",
                        has_stocks=False,
                        stocks=[]
                    )
                
                data = response.json()
                logger.info(f"成功獲取話題 {topic_id} 的股票資訊")
                
                # 解析股票資訊
                stocks = []
                topic_title = data.get('name', '')
                
                # 檢查是否有相關股票
                related_stocks = data.get('relatedStockSymbols', [])
                if related_stocks:
                    for stock_data in related_stocks:
                        if isinstance(stock_data, dict) and stock_data.get('type') == 'Stock':
                            stock_id = stock_data.get('key', '')
                            if stock_id:
                                # 獲取股票名稱（這裡可以擴展為查詢股票名稱的服務）
                                stock_name = self._get_stock_name(stock_id)
                                stocks.append(StockInfo(
                                    stock_id=stock_id,
                                    stock_name=stock_name,
                                    stock_type=stock_data.get('type', 'Stock'),
                                    confidence=1.0
                                ))
                
                has_stocks = len(stocks) > 0
                
                logger.info(f"話題 {topic_id} 找到 {len(stocks)} 個相關股票: {[s.stock_id for s in stocks]}")
                
                return TopicStockData(
                    topic_id=topic_id,
                    topic_title=topic_title,
                    has_stocks=has_stocks,
                    stocks=stocks,
                    raw_data=data
                )
                
        except Exception as e:
            logger.error(f"獲取話題 {topic_id} 股票資訊失敗: {e}")
            return TopicStockData(
                topic_id=topic_id,
                topic_title="",
                has_stocks=False,
                stocks=[]
            )
    
    def _get_stock_name(self, stock_id: str) -> str:
        """
        根據股票代號獲取股票名稱
        
        Args:
            stock_id: 股票代號
            
        Returns:
            股票名稱
        """
        from ...utils.stock_mapping import get_stock_name
        return get_stock_name(stock_id)
    
    def assign_stocks_to_kols(self, stocks: List[StockInfo], kol_serials: List[str]) -> Dict[str, Optional[StockInfo]]:
        """
        將股票隨機分配給 KOL
        
        Args:
            stocks: 股票列表
            kol_serials: KOL 序號列表
            
        Returns:
            KOL 序號 -> 分配的股票 (如果沒有股票則為 None)
        """
        if not stocks:
            # 沒有股票，所有 KOL 都不分配股票
            return {kol_serial: None for kol_serial in kol_serials}
        
        # 隨機分配股票給 KOL
        assignments = {}
        available_stocks = stocks.copy()
        
        for kol_serial in kol_serials:
            if available_stocks:
                # 隨機選擇一個股票
                assigned_stock = random.choice(available_stocks)
                assignments[kol_serial] = assigned_stock
                # 移除已分配的股票（避免重複分配）
                available_stocks.remove(assigned_stock)
            else:
                # 沒有更多股票可分配
                assignments[kol_serial] = None
        
        logger.info(f"股票分配結果: {[(k, v.stock_id if v else None) for k, v in assignments.items()]}")
        return assignments
    
    async def process_topics_with_stocks(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        處理話題列表，為每個話題查詢股票資訊
        
        Args:
            topics: 話題列表
            
        Returns:
            包含股票資訊的話題列表
        """
        processed_topics = []
        
        for topic in topics:
            topic_id = topic.get('id', '')
            if not topic_id:
                logger.warning("話題缺少 ID，跳過")
                continue
            
            # 查詢股票資訊
            stock_data = await self.get_topic_stocks(topic_id)
            
            # 將股票資訊添加到話題數據中
            enhanced_topic = topic.copy()
            enhanced_topic['stock_data'] = {
                'has_stocks': stock_data.has_stocks,
                'stocks': [
                    {
                        'stock_id': stock.stock_id,
                        'stock_name': stock.stock_name,
                        'stock_type': stock.stock_type,
                        'confidence': stock.confidence
                    }
                    for stock in stock_data.stocks
                ],
                'topic_title': stock_data.topic_title
            }
            
            processed_topics.append(enhanced_topic)
            
            # 添加小延遲避免 API 限制
            await asyncio.sleep(0.5)
        
        logger.info(f"處理完成，共 {len(processed_topics)} 個話題")
        return processed_topics

# 創建服務實例的工廠函數
def create_topic_stock_service() -> TopicStockService:
    """創建話題股票服務實例"""
    return TopicStockService()

# 測試函數
async def test_topic_stock_service():
    """測試話題股票服務"""
    try:
        service = create_topic_stock_service()
        
        # 測試話題 ID
        test_topic_id = "136405de-3cfb-4112-8124-af4f0d42bdd8"
        
        print("🔍 測試話題股票服務")
        print("=" * 50)
        
        # 測試單個話題
        stock_data = await service.get_topic_stocks(test_topic_id)
        
        print(f"話題 ID: {stock_data.topic_id}")
        print(f"話題標題: {stock_data.topic_title}")
        print(f"是否有股票: {stock_data.has_stocks}")
        print(f"股票數量: {len(stock_data.stocks)}")
        
        if stock_data.stocks:
            print("股票列表:")
            for stock in stock_data.stocks:
                print(f"  - {stock.stock_id}: {stock.stock_name}")
        
        # 測試股票分配
        if stock_data.stocks:
            test_kols = ["200", "201", "202"]
            assignments = service.assign_stocks_to_kols(stock_data.stocks, test_kols)
            
            print("\n股票分配結果:")
            for kol_serial, stock in assignments.items():
                if stock:
                    print(f"  KOL {kol_serial}: {stock.stock_id} ({stock.stock_name})")
                else:
                    print(f"  KOL {kol_serial}: 無股票分配")
        
        print("\n✅ 測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_topic_stock_service())



