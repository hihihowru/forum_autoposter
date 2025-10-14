"""
手動發文服務
提供手動發文功能的後端 API 和業務邏輯
"""

import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

logger = logging.getLogger(__name__)

# 資料庫配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/posting_management")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 資料模型
class PostRecord(Base):
    """貼文記錄表"""
    __tablename__ = "post_records"
    
    # 主鍵和時間戳
    post_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    # 基礎資訊欄位
    session_id = Column(Integer, nullable=True)
    kol_serial = Column(Integer, nullable=False)
    kol_nickname = Column(String, nullable=False)
    kol_persona = Column(String, nullable=True)
    
    # 股票資訊欄位
    stock_code = Column(String, nullable=False)
    stock_name = Column(String, nullable=False)
    
    # 內容欄位
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_md = Column(Text, nullable=True)
    
    # 狀態管理欄位
    status = Column(String, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    
    # 平台資訊欄位
    cmoney_post_id = Column(String, nullable=True)
    cmoney_post_url = Column(String, nullable=True)
    publish_error = Column(Text, nullable=True)
    
    # 互動數據欄位
    views = Column(Integer, nullable=True)
    likes = Column(Integer, nullable=True)
    comments = Column(Integer, nullable=True)
    shares = Column(Integer, nullable=True)
    
    # 話題資訊欄位
    topic_id = Column(String, nullable=True)
    topic_title = Column(String, nullable=True)
    
    # 分析數據欄位
    technical_analysis = Column(JSON, nullable=True)
    serper_data = Column(JSON, nullable=True)
    
    # 品質評分欄位
    quality_score = Column(Float, nullable=True)
    ai_detection_score = Column(Float, nullable=True)
    
    # 多選標籤欄位
    commodity_tags = Column(JSON, nullable=True)

class KOLProfile(Base):
    """KOL 資料表"""
    __tablename__ = "kol_profiles"
    
    # 基本資料
    id = Column(Integer, primary_key=True, index=True)
    serial = Column(String(10), unique=True, index=True, nullable=False)
    nickname = Column(String(100), nullable=False)
    member_id = Column(String(20), unique=True, index=True, nullable=False)
    persona = Column(String(50), nullable=False)
    status = Column(String(20), default="active")
    owner = Column(String(50), default="威廉用")
    
    # 登入憑證
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    whitelist = Column(Boolean, default=True)
    notes = Column(Text)

# Pydantic 模型
class ManualPostingRequest(BaseModel):
    """手動發文請求"""
    kol_serial: int
    title: str
    content: str
    stock_codes: List[str]
    communityTopics: List[str]

class ManualPostingResponse(BaseModel):
    """手動發文回應"""
    success: bool
    post_id: str
    message: str

class KOLInfo(BaseModel):
    """KOL 資訊"""
    serial: str
    nickname: str
    persona: str
    status: str

class StockInfo(BaseModel):
    """股票資訊"""
    code: str
    name: str
    industry: str

class TopicInfo(BaseModel):
    """話題資訊"""
    id: str
    title: str
    name: str

# 服務類
class ManualPostingService:
    """手動發文服務"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.stock_mapping = self._load_stock_mapping()
    
    def _load_stock_mapping(self) -> Dict[str, Dict[str, Any]]:
        """載入股票映射資料"""
        try:
            with open('stock_mapping.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 只保留四位數股票代號
            four_digit_stocks = {}
            for code, info in data.items():
                if len(code) == 4 and code.isdigit():
                    four_digit_stocks[code] = info
            
            logger.info(f"載入 {len(four_digit_stocks)} 個四位數股票")
            return four_digit_stocks
            
        except Exception as e:
            logger.error(f"載入股票映射失敗: {e}")
            return {}
    
    def get_kols(self) -> List[KOLInfo]:
        """獲取所有 KOL 列表"""
        try:
            kols = self.db.query(KOLProfile).filter(KOLProfile.status == "active").all()
            return [
                KOLInfo(
                    serial=kol.serial,
                    nickname=kol.nickname,
                    persona=kol.persona,
                    status=kol.status
                )
                for kol in kols
            ]
        except Exception as e:
            logger.error(f"獲取 KOL 列表失敗: {e}")
            return []
    
    def get_stocks(self) -> List[StockInfo]:
        """獲取股票列表"""
        try:
            stocks = []
            for code, info in self.stock_mapping.items():
                stocks.append(StockInfo(
                    code=code,
                    name=info.get('company_name', ''),
                    industry=info.get('industry', '')
                ))
            return stocks
        except Exception as e:
            logger.error(f"獲取股票列表失敗: {e}")
            return []
    
    def search_stocks(self, query: str) -> List[StockInfo]:
        """搜尋股票"""
        if not query:
            return self.get_stocks()
        
        query = query.lower()
        results = []
        
        for code, info in self.stock_mapping.items():
            company_name = info.get('company_name', '').lower()
            industry = info.get('industry', '').lower()
            
            if (query in code or 
                query in company_name or 
                query in industry):
                results.append(StockInfo(
                    code=code,
                    name=info.get('company_name', ''),
                    industry=info.get('industry', '')
                ))
        
        return results[:50]  # 限制結果數量
    
    def get_kol_info(self, kol_serial: int) -> Optional[Dict[str, Any]]:
        """獲取 KOL 資訊"""
        try:
            kol = self.db.query(KOLProfile).filter(KOLProfile.serial == str(kol_serial)).first()
            if kol:
                return {
                    'serial': kol.serial,
                    'nickname': kol.nickname,
                    'persona': kol.persona,
                    'status': kol.status
                }
            return None
        except Exception as e:
            logger.error(f"獲取 KOL 資訊失敗: {e}")
            return None
    
    def get_stock_name(self, stock_code: str) -> str:
        """獲取股票名稱"""
        stock_info = self.stock_mapping.get(stock_code)
        if stock_info:
            return stock_info.get('company_name', stock_code)
        return stock_code
    
    def process_stock_selection(self, stock_codes: List[str]) -> Dict[str, Any]:
        """處理多選股票"""
        if not stock_codes:
            return {
                'primary_code': '',
                'primary_name': '',
                'all_stocks': None
            }
        
        # 第一個股票作為主要股票
        primary_code = stock_codes[0]
        primary_name = self.get_stock_name(primary_code)
        
        # 所有股票資訊
        all_stocks = {
            "primary": {"code": primary_code, "name": primary_name},
            "additional": [
                {"code": code, "name": self.get_stock_name(code)} 
                for code in stock_codes[1:]
            ]
        }
        
        return {
            'primary_code': primary_code,
            'primary_name': primary_name,
            'all_stocks': all_stocks
        }
    
    def process_topic_selection(self, topic_ids: List[str]) -> Dict[str, Any]:
        """處理多選話題"""
        if not topic_ids:
            return {
                'primary_id': '',
                'primary_title': '',
                'all_topics': None
            }
        
        # 第一個話題作為主要話題
        primary_id = topic_ids[0]
        primary_title = f"話題-{primary_id}"  # 暫時使用 ID 作為標題
        
        # 所有話題資訊
        all_topics = {
            "primary": {"id": primary_id, "title": primary_title},
            "additional": [
                {"id": tid, "title": f"話題-{tid}"} 
                for tid in topic_ids[1:]
            ]
        }
        
        return {
            'primary_id': primary_id,
            'primary_title': primary_title,
            'all_topics': all_topics
        }
    
    def submit_manual_post(self, request: ManualPostingRequest) -> ManualPostingResponse:
        """提交手動發文"""
        try:
            # 1. 生成唯一 post_id
            post_id = f"manual-{uuid.uuid4()}-{request.kol_serial}"
            
            # 2. 獲取 KOL 資訊
            kol_info = self.get_kol_info(request.kol_serial)
            if not kol_info:
                return ManualPostingResponse(
                    success=False,
                    post_id="",
                    message=f"找不到 KOL-{request.kol_serial}"
                )
            
            # 3. 處理多選股票
            stock_data = self.process_stock_selection(request.stock_codes)
            
            # 4. 處理多選話題
            topic_data = self.process_topic_selection(request.communityTopics)
            
            # 5. 記錄到 post_records
            post_record = PostRecord(
                post_id=post_id,
                kol_serial=request.kol_serial,
                kol_nickname=kol_info['nickname'],
                kol_persona=kol_info['persona'],
                title=request.title,
                content=request.content,
                stock_code=stock_data['primary_code'],
                stock_name=stock_data['primary_name'],
                topic_id=topic_data['primary_id'],
                topic_title=topic_data['primary_title'],
                commodity_tags=stock_data['all_stocks'],
                status='success',
                created_at=datetime.now()
            )
            
            # 6. 保存到資料庫
            self.db.add(post_record)
            self.db.commit()
            
            logger.info(f"手動發文成功: {post_id}")
            
            return ManualPostingResponse(
                success=True,
                post_id=post_id,
                message="發文記錄已保存"
            )
            
        except Exception as e:
            logger.error(f"手動發文失敗: {e}")
            self.db.rollback()
            return ManualPostingResponse(
                success=False,
                post_id="",
                message=f"發文失敗: {str(e)}"
            )
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取最近的發文記錄"""
        try:
            posts = self.db.query(PostRecord).filter(
                PostRecord.status == 'success'
            ).order_by(PostRecord.created_at.desc()).limit(limit).all()
            
            return [
                {
                    'post_id': post.post_id,
                    'kol_nickname': post.kol_nickname,
                    'title': post.title,
                    'created_at': post.created_at.isoformat() if post.created_at else '',
                    'stock_name': post.stock_name,
                    'topic_title': post.topic_title
                }
                for post in posts
            ]
        except Exception as e:
            logger.error(f"獲取發文記錄失敗: {e}")
            return []

# 全域服務實例
manual_posting_service = ManualPostingService()
