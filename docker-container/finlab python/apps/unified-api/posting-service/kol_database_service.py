"""
KOL 數據庫模型和服務
建立後端 KOL 數據庫表，確保資料不會丟失
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import ARRAY

# 添加專案根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

# 數據庫配置
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres-db:5432/posting_management")

# 創建數據庫引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    
    # 發文設定
    post_times = Column(String(100))
    target_audience = Column(String(50))
    interaction_threshold = Column(Float, default=0.6)
    content_types = Column(ARRAY(String))
    
    # 人設設定
    common_terms = Column(Text)
    colloquial_terms = Column(Text)
    tone_style = Column(Text)
    typing_habit = Column(Text)
    backstory = Column(Text)
    expertise = Column(Text)
    data_source = Column(String(100))
    
    # Prompt 設定
    prompt_persona = Column(Text)
    prompt_style = Column(Text)
    prompt_guardrails = Column(Text)
    prompt_skeleton = Column(Text)
    prompt_cta = Column(Text)
    prompt_hashtags = Column(Text)
    
    # 模型設定
    signature = Column(String(100))
    emoji_pack = Column(String(100))
    model_id = Column(String(50), default="gpt-4o-mini")
    template_variant = Column(String(50), default="default")
    model_temp = Column(Float, default=0.5)
    max_tokens = Column(Integer, default=700)
    
    # 標題設定
    title_openers = Column(ARRAY(String))
    title_signature_patterns = Column(ARRAY(String))
    title_tail_word = Column(String(20))
    title_banned_words = Column(ARRAY(String))
    title_style_examples = Column(ARRAY(String))
    title_retry_max = Column(Integer, default=3)
    
    # 語氣設定
    tone_formal = Column(Integer, default=5)
    tone_emotion = Column(Integer, default=5)
    tone_confidence = Column(Integer, default=7)
    tone_urgency = Column(Integer, default=4)
    tone_interaction = Column(Integer, default=6)
    
    # 內容設定
    question_ratio = Column(Float, default=0.5)
    content_length = Column(String(20), default="medium")
    interaction_starters = Column(ARRAY(String))
    require_finlab_api = Column(Boolean, default=True)
    allow_hashtags = Column(Boolean, default=True)
    
    # 時間戳記
    created_time = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 統計數據
    total_posts = Column(Integer, default=0)
    published_posts = Column(Integer, default=0)
    avg_interaction_rate = Column(Float, default=0.0)
    best_performing_post = Column(String(100))

class KOLDatabaseService:
    """KOL 數據庫服務"""
    
    def __init__(self):
        """初始化數據庫服務"""
        self.engine = engine
        self.SessionLocal = SessionLocal
        self._create_tables()
        logger.info("🗄️ KOL 數據庫服務初始化完成")
    
    def _create_tables(self):
        """創建數據表"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ KOL 數據表創建成功")
        except Exception as e:
            logger.error(f"❌ 創建 KOL 數據表失敗: {e}")
            raise
    
    def get_db(self) -> Session:
        """獲取數據庫會話"""
        db = self.SessionLocal()
        try:
            return db
        finally:
            pass
    
    def create_kol(self, kol_data: Dict[str, Any]) -> Optional[KOLProfile]:
        """創建 KOL"""
        try:
            db = self.get_db()
            kol = KOLProfile(**kol_data)
            db.add(kol)
            db.commit()
            db.refresh(kol)
            logger.info(f"✅ 創建 KOL {kol.serial} 成功")
            return kol
        except Exception as e:
            logger.error(f"❌ 創建 KOL 失敗: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def get_kol_by_serial(self, serial: str) -> Optional[KOLProfile]:
        """根據序號獲取 KOL"""
        try:
            db = self.get_db()
            # 確保 serial 是字符串類型，避免類型不匹配錯誤
            serial_str = str(serial)
            kol = db.query(KOLProfile).filter(KOLProfile.serial == serial_str).first()
            return kol
        except Exception as e:
            logger.error(f"❌ 獲取 KOL {serial} 失敗: {e}")
            return None
        finally:
            db.close()
    
    def get_kol_by_member_id(self, member_id: str) -> Optional[KOLProfile]:
        """根據 Member ID 獲取 KOL"""
        try:
            db = self.get_db()
            kol = db.query(KOLProfile).filter(KOLProfile.member_id == member_id).first()
            return kol
        except Exception as e:
            logger.error(f"❌ 獲取 KOL {member_id} 失敗: {e}")
            return None
        finally:
            db.close()
    
    def get_all_kols(self) -> List[KOLProfile]:
        """獲取所有 KOL"""
        try:
            db = self.get_db()
            kols = db.query(KOLProfile).all()
            return kols
        except Exception as e:
            logger.error(f"❌ 獲取所有 KOL 失敗: {e}")
            return []
        finally:
            db.close()
    
    def update_kol(self, serial: str, update_data: Dict[str, Any]) -> Optional[KOLProfile]:
        """更新 KOL"""
        try:
            db = self.get_db()
            kol = db.query(KOLProfile).filter(KOLProfile.serial == serial).first()
            if kol:
                for key, value in update_data.items():
                    if hasattr(kol, key):
                        setattr(kol, key, value)
                kol.last_updated = datetime.utcnow()
                db.commit()
                db.refresh(kol)
                logger.info(f"✅ 更新 KOL {serial} 成功")
                return kol
            return None
        except Exception as e:
            logger.error(f"❌ 更新 KOL {serial} 失敗: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def delete_kol(self, serial: str) -> bool:
        """刪除 KOL"""
        try:
            db = self.get_db()
            kol = db.query(KOLProfile).filter(KOLProfile.serial == serial).first()
            if kol:
                db.delete(kol)
                db.commit()
                logger.info(f"✅ 刪除 KOL {serial} 成功")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 刪除 KOL {serial} 失敗: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_kol_list_for_selection(self) -> List[Dict[str, Any]]:
        """獲取用於選擇的 KOL 列表"""
        try:
            kols = self.get_all_kols()
            return [
                {
                    "serial": kol.serial,
                    "nickname": kol.nickname,
                    "member_id": kol.member_id,
                    "persona": kol.persona,
                    "status": kol.status,
                    "email": kol.email,
                    "owner": kol.owner
                }
                for kol in kols
            ]
        except Exception as e:
            logger.error(f"❌ 獲取 KOL 選擇列表失敗: {e}")
            return []
    
    def get_kol_credentials(self, serial: str) -> Optional[Dict[str, str]]:
        """獲取 KOL 登入憑證"""
        try:
            kol = self.get_kol_by_serial(serial)
            if kol:
                return {
                    "email": kol.email,
                    "password": kol.password,
                    "member_id": kol.member_id
                }
            return None
        except Exception as e:
            logger.error(f"❌ 獲取 KOL {serial} 憑證失敗: {e}")
            return None
    
    def sync_kols_from_data_manager(self) -> bool:
        """從 KOL 數據管理器同步數據到數據庫"""
        try:
            from kol_data_manager import kol_data_manager
            
            all_kol_data = kol_data_manager.get_all_kol_data()
            synced_count = 0
            
            for serial, data in all_kol_data.items():
                # 檢查是否已存在
                existing_kol = self.get_kol_by_serial(serial)
                
                if existing_kol:
                    # 更新現有 KOL
                    update_data = {
                        "nickname": data.get("暱稱", f"KOL_{serial}"),
                        "member_id": data.get("MemberId", serial),
                        "persona": data.get("人設", "綜合派"),
                        "email": data.get("Email(帳號)", ""),
                        "password": data.get("密碼", ""),
                        "status": data.get("狀態", "active"),
                        "owner": data.get("認領人", "威廉用"),
                        "notes": data.get("備註", ""),
                        "post_times": data.get("發文時間", ""),
                        "target_audience": data.get("目標受眾", ""),
                        "interaction_threshold": data.get("互動閾值", 0.6),
                        "common_terms": data.get("常用詞彙", ""),
                        "colloquial_terms": data.get("口語化用詞", ""),
                        "tone_style": data.get("語氣風格", ""),
                        "typing_habit": data.get("常用打字習慣", ""),
                        "backstory": data.get("前導故事", ""),
                        "expertise": data.get("專長領域", ""),
                        "data_source": data.get("數據源", ""),
                        "prompt_persona": data.get("PromptPersona", ""),
                        "prompt_style": data.get("PromptStyle", ""),
                        "prompt_guardrails": data.get("PromptGuardrails", ""),
                        "prompt_skeleton": data.get("PromptSkeleton", ""),
                        "prompt_cta": data.get("PromptCTA", ""),
                        "prompt_hashtags": data.get("PromptHashtags", ""),
                        "signature": data.get("Signature", ""),
                        "emoji_pack": data.get("EmojiPack", ""),
                        "model_id": data.get("ModelId", "gpt-4o-mini"),
                        "model_temp": data.get("ModelTemp", 0.5),
                        "max_tokens": data.get("MaxTokens", 700)
                    }
                    self.update_kol(serial, update_data)
                else:
                    # 創建新 KOL
                    create_data = {
                        "serial": serial,
                        "nickname": data.get("暱稱", f"KOL_{serial}"),
                        "member_id": data.get("MemberId", serial),
                        "persona": data.get("人設", "綜合派"),
                        "email": data.get("Email(帳號)", ""),
                        "password": data.get("密碼", ""),
                        "status": data.get("狀態", "active"),
                        "owner": data.get("認領人", "威廉用"),
                        "notes": data.get("備註", ""),
                        "post_times": data.get("發文時間", ""),
                        "target_audience": data.get("目標受眾", ""),
                        "interaction_threshold": data.get("互動閾值", 0.6),
                        "common_terms": data.get("常用詞彙", ""),
                        "colloquial_terms": data.get("口語化用詞", ""),
                        "tone_style": data.get("語氣風格", ""),
                        "typing_habit": data.get("常用打字習慣", ""),
                        "backstory": data.get("前導故事", ""),
                        "expertise": data.get("專長領域", ""),
                        "data_source": data.get("數據源", ""),
                        "prompt_persona": data.get("PromptPersona", ""),
                        "prompt_style": data.get("PromptStyle", ""),
                        "prompt_guardrails": data.get("PromptGuardrails", ""),
                        "prompt_skeleton": data.get("PromptSkeleton", ""),
                        "prompt_cta": data.get("PromptCTA", ""),
                        "prompt_hashtags": data.get("PromptHashtags", ""),
                        "signature": data.get("Signature", ""),
                        "emoji_pack": data.get("EmojiPack", ""),
                        "model_id": data.get("ModelId", "gpt-4o-mini"),
                        "model_temp": data.get("ModelTemp", 0.5),
                        "max_tokens": data.get("MaxTokens", 700)
                    }
                    self.create_kol(create_data)
                
                synced_count += 1
            
            logger.info(f"✅ 成功同步 {synced_count} 個 KOL 到數據庫")
            return True
            
        except Exception as e:
            logger.error(f"❌ 同步 KOL 數據失敗: {e}")
            return False

# 創建全局 KOL 數據庫服務實例
kol_db_service = KOLDatabaseService()


