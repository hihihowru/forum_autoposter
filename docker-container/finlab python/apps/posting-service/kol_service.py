"""
KOL 管理服務
管理 KOL 憑證和配置
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import sys

# 添加專案根目錄到 Python 路徑
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

class KOLService:
    """KOL 管理服務"""
    
    def __init__(self):
        """初始化 KOL 服務"""
        self.kol_credentials = {}
        self.kol_tokens = {}
        self._load_kol_credentials()
        logger.info("🔐 KOL 服務初始化完成")
    
    def _load_kol_credentials(self):
        """載入 KOL 憑證 - 使用數據庫服務"""
        try:
            # 使用數據庫服務
            from kol_database_service import kol_db_service
            
            # 獲取所有 KOL 憑證
            all_kols = kol_db_service.get_all_kols()
            
            for kol in all_kols:
                self.kol_credentials[kol.serial] = {
                    "email": kol.email,
                    "password": kol.password,
                    "member_id": kol.member_id
                }
                logger.info(f"載入KOL憑證: {kol.serial} - {kol.email}")
            
            logger.info(f"📋 從數據庫載入了 {len(self.kol_credentials)} 個 KOL 憑證")
            
        except Exception as e:
            logger.error(f"從數據庫載入憑證失敗: {e}")
            logger.info("使用預設KOL憑證配置")
            self._load_default_credentials()
    
    def _load_default_credentials(self):
        """載入預設KOL憑證（備用方案）"""
        self.kol_credentials = {
            # KOL 160-185 的 CMoney 真實憑證
            "160": {"email": "forum_160@cmoney.com.tw", "password": "Q6c8qA5w"},
            "161": {"email": "forum_161@cmoney.com.tw", "password": "i3R7hK4j"},
            "162": {"email": "forum_162@cmoney.com.tw", "password": "G8u9dX1k"},
            "163": {"email": "forum_163@cmoney.com.tw", "password": "z5Y4sW6m"},
            "164": {"email": "forum_164@cmoney.com.tw", "password": "S9f7vK2e"},
            "165": {"email": "forum_165@cmoney.com.tw", "password": "R3n6tL9c"},
            "166": {"email": "forum_166@cmoney.com.tw", "password": "b4P9jH8x"},
            "167": {"email": "forum_167@cmoney.com.tw", "password": "D2p7cT6b"},
            "168": {"email": "forum_168@cmoney.com.tw", "password": "k5V1sW2j"},
            "169": {"email": "forum_169@cmoney.com.tw", "password": "o9Q6vJ2f"},
            "170": {"email": "forum_170@cmoney.com.tw", "password": "w1F7hT0l"},
            "171": {"email": "forum_171@cmoney.com.tw", "password": "j6R9cP2f"},
            "172": {"email": "forum_172@cmoney.com.tw", "password": "E7q5dS3j"},
            "173": {"email": "forum_173@cmoney.com.tw", "password": "x4J6hT1n"},
            "174": {"email": "forum_174@cmoney.com.tw", "password": "s3N0qW8j"},
            "175": {"email": "forum_175@cmoney.com.tw", "password": "B0h8tE2k"},
            "176": {"email": "forum_176@cmoney.com.tw", "password": "n8C3kV0r"},
            "177": {"email": "forum_177@cmoney.com.tw", "password": "f5J1cV9s"},
            "178": {"email": "forum_178@cmoney.com.tw", "password": "y7U1jD4c"},
            "179": {"email": "forum_179@cmoney.com.tw", "password": "I2m0wN8x"},
            "180": {"email": "forum_180@cmoney.com.tw", "password": "e5X3qK4n"},
            "181": {"email": "forum_181@cmoney.com.tw", "password": "u1N8wA6t"},
            "182": {"email": "forum_182@cmoney.com.tw", "password": "G2p8xJ7k"},
            "183": {"email": "forum_183@cmoney.com.tw", "password": "v3A5dN9r"},
            "184": {"email": "forum_184@cmoney.com.tw", "password": "Q6u2pZ7n"},
            "185": {"email": "forum_185@cmoney.com.tw", "password": "M9h2kU8r"},
            
            # 原有的 186-198 KOL
            "186": {"email": "forum_186@cmoney.com.tw", "password": "t7L9uY0f"},
            "187": {"email": "forum_187@cmoney.com.tw", "password": "a4E9jV8t"},
            "188": {"email": "forum_188@cmoney.com.tw", "password": "z6G5wN2m"},
            "189": {"email": "forum_189@cmoney.com.tw", "password": "c8L5nO3q"},
            "190": {"email": "forum_190@cmoney.com.tw", "password": "W4x6hU0r"},
            "191": {"email": "forum_191@cmoney.com.tw", "password": "H7u4rE2j"},
            "192": {"email": "forum_192@cmoney.com.tw", "password": "S3c6oJ9h"},
            "193": {"email": "forum_193@cmoney.com.tw", "password": "X2t1vU7l"},
            "194": {"email": "forum_194@cmoney.com.tw", "password": "j3H5dM7p"},
            "195": {"email": "forum_195@cmoney.com.tw", "password": "P9n1fT3x"},
            "196": {"email": "forum_196@cmoney.com.tw", "password": "b4C1pL3r"},
            "197": {"email": "forum_197@cmoney.com.tw", "password": "O8a3pF4c"},
            "198": {"email": "forum_198@cmoney.com.tw", "password": "i0L5fC3s"},
            
            # 新增的 200-209 KOL (真實憑證)
            "200": {"email": "forum_200@cmoney.com.tw", "password": "N9t1kY3x"},
            "201": {"email": "forum_201@cmoney.com.tw", "password": "m7C1lR4t"},
            "202": {"email": "forum_202@cmoney.com.tw", "password": "x2U9nW5p"},
            "203": {"email": "forum_203@cmoney.com.tw", "password": "y7O3cL9k"},
            "204": {"email": "forum_204@cmoney.com.tw", "password": "f4E9sC8w"},
            "205": {"email": "forum_205@cmoney.com.tw", "password": "Z5u6dL9o"},
            "206": {"email": "forum_206@cmoney.com.tw", "password": "T1t7kS9j"},
            "207": {"email": "forum_207@cmoney.com.tw", "password": "w2B3cF6l"},
            "208": {"email": "forum_208@cmoney.com.tw", "password": "q4N8eC7h"},
            "209": {"email": "forum_209@cmoney.com.tw", "password": "V5n6hK0f"},
            
        }
        
        # KOL 名字映射表
        self.kol_names = {
            "160": "短線獵人", "161": "技術達人", "162": "總經專家", "163": "消息靈通", "164": "散戶代表",
            "165": "地方股神", "166": "八卦王", "167": "爆料專家", "168": "技術高手", "169": "價值投資者",
            "170": "新聞獵人", "171": "數據分析師", "172": "短線高手", "173": "綜合分析師", "174": "技術分析師",
            "175": "總經達人", "176": "消息靈通", "177": "散戶代表", "178": "地方股神", "179": "八卦王",
            "180": "爆料專家", "181": "技術高手", "182": "價值投資者", "183": "新聞獵人", "184": "數據分析師",
            "185": "短線高手",
            "186": "技術分析師", "187": "總經達人", "188": "消息靈通", "189": "散戶代表", "190": "地方股神",
            "191": "八卦王", "192": "爆料專家", "193": "技術高手", "194": "價值投資者", "195": "新聞獵人",
            "196": "數據分析師", "197": "短線高手", "198": "綜合分析師",
            "200": "川川哥", "201": "韭割哥", "202": "梅川褲子", "203": "龜狗一日散戶", "204": "板橋大who",
            "205": "八卦護城河", "206": "小道爆料王", "207": "信號宅神", "208": "長線韭韭", "209": "報爆哥_209", "210": "數據獵人"
        }
        
        # KOL 人設映射表
        self.kol_personas = {
            "160": "短線派", "161": "技術派", "162": "總經派", "163": "消息派", "164": "散戶派",
            "165": "地方派", "166": "八卦派", "167": "爆料派", "168": "技術派", "169": "價值派",
            "170": "新聞派", "171": "數據派", "172": "短線派", "173": "綜合派", "174": "技術派",
            "175": "總經派", "176": "消息派", "177": "散戶派", "178": "地方派", "179": "八卦派",
            "180": "爆料派", "181": "技術派", "182": "價值派", "183": "新聞派", "184": "數據派",
            "185": "短線派",
            "186": "技術派", "187": "總經派", "188": "消息派", "189": "散戶派", "190": "地方派",
            "191": "八卦派", "192": "爆料派", "193": "技術派", "194": "價值派", "195": "新聞派",
            "196": "數據派", "197": "短線派", "198": "綜合派",
            "200": "技術派", "201": "總經派", "202": "消息派", "203": "散戶派", "204": "地方派",
            "205": "八卦派", "206": "爆料派", "207": "技術派", "208": "價值派", "209": "新聞派", "210": "數據派"
        }
        
        # KOL 個人化設定映射表
        self.kol_personalized_settings = {
            "160": {"post_times": "9:00-17:00", "target_audience": "day_traders", "interaction_threshold": 0.3, "content_types": ["short_term"], "common_terms": "短線", "colloquial_terms": "當沖", "tone_style": "aggressive"},
            "161": {"post_times": "9:00-17:00", "target_audience": "technical_traders", "interaction_threshold": 0.5, "content_types": ["technical"], "common_terms": "技術", "colloquial_terms": "技術面", "tone_style": "technical"},
            "162": {"post_times": "9:00-17:00", "target_audience": "macro_traders", "interaction_threshold": 0.6, "content_types": ["macro"], "common_terms": "總經", "colloquial_terms": "大環境", "tone_style": "analytical"},
            "163": {"post_times": "9:00-17:00", "target_audience": "news_traders", "interaction_threshold": 0.4, "content_types": ["news"], "common_terms": "消息", "colloquial_terms": "內線", "tone_style": "urgent"},
            "164": {"post_times": "9:00-17:00", "target_audience": "retail_traders", "interaction_threshold": 0.3, "content_types": ["tips"], "common_terms": "散戶", "colloquial_terms": "小資", "tone_style": "friendly"},
            "165": {"post_times": "9:00-17:00", "target_audience": "local_traders", "interaction_threshold": 0.4, "content_types": ["local"], "common_terms": "地方", "colloquial_terms": "在地", "tone_style": "local"},
            "166": {"post_times": "9:00-17:00", "target_audience": "gossip_lovers", "interaction_threshold": 0.7, "content_types": ["gossip"], "common_terms": "八卦", "colloquial_terms": "小道", "tone_style": "playful"},
            "167": {"post_times": "9:00-17:00", "target_audience": "insider_traders", "interaction_threshold": 0.8, "content_types": ["insider"], "common_terms": "爆料", "colloquial_terms": "內幕", "tone_style": "mysterious"},
            "168": {"post_times": "9:00-17:00", "target_audience": "technical_traders", "interaction_threshold": 0.5, "content_types": ["technical"], "common_terms": "技術", "colloquial_terms": "技術面", "tone_style": "technical"},
            "169": {"post_times": "9:00-17:00", "target_audience": "value_investors", "interaction_threshold": 0.6, "content_types": ["fundamental"], "common_terms": "價值", "colloquial_terms": "基本面", "tone_style": "conservative"},
            "170": {"post_times": "9:00-17:00", "target_audience": "news_traders", "interaction_threshold": 0.4, "content_types": ["news"], "common_terms": "新聞", "colloquial_terms": "消息", "tone_style": "informative"},
            "171": {"post_times": "9:00-17:00", "target_audience": "data_traders", "interaction_threshold": 0.5, "content_types": ["data"], "common_terms": "數據", "colloquial_terms": "數字", "tone_style": "data_driven"},
            "172": {"post_times": "9:00-17:00", "target_audience": "day_traders", "interaction_threshold": 0.3, "content_types": ["short_term"], "common_terms": "短線", "colloquial_terms": "當沖", "tone_style": "aggressive"},
            "173": {"post_times": "9:00-17:00", "target_audience": "general_traders", "interaction_threshold": 0.5, "content_types": ["comprehensive"], "common_terms": "綜合", "colloquial_terms": "全方位", "tone_style": "balanced"},
            "174": {"post_times": "9:00-17:00", "target_audience": "technical_traders", "interaction_threshold": 0.5, "content_types": ["technical"], "common_terms": "技術", "colloquial_terms": "技術面", "tone_style": "technical"},
            "175": {"post_times": "9:00-17:00", "target_audience": "macro_traders", "interaction_threshold": 0.6, "content_types": ["macro"], "common_terms": "總經", "colloquial_terms": "大環境", "tone_style": "analytical"},
            "176": {"post_times": "9:00-17:00", "target_audience": "news_traders", "interaction_threshold": 0.4, "content_types": ["news"], "common_terms": "消息", "colloquial_terms": "內線", "tone_style": "urgent"},
            "177": {"post_times": "9:00-17:00", "target_audience": "retail_traders", "interaction_threshold": 0.3, "content_types": ["tips"], "common_terms": "散戶", "colloquial_terms": "小資", "tone_style": "friendly"},
            "178": {"post_times": "9:00-17:00", "target_audience": "local_traders", "interaction_threshold": 0.4, "content_types": ["local"], "common_terms": "地方", "colloquial_terms": "在地", "tone_style": "local"},
            "179": {"post_times": "9:00-17:00", "target_audience": "gossip_lovers", "interaction_threshold": 0.7, "content_types": ["gossip"], "common_terms": "八卦", "colloquial_terms": "小道", "tone_style": "playful"},
            "180": {"post_times": "9:00-17:00", "target_audience": "insider_traders", "interaction_threshold": 0.8, "content_types": ["insider"], "common_terms": "爆料", "colloquial_terms": "內幕", "tone_style": "mysterious"},
            "181": {"post_times": "9:00-17:00", "target_audience": "technical_traders", "interaction_threshold": 0.5, "content_types": ["technical"], "common_terms": "技術", "colloquial_terms": "技術面", "tone_style": "technical"},
            "182": {"post_times": "9:00-17:00", "target_audience": "value_investors", "interaction_threshold": 0.6, "content_types": ["fundamental"], "common_terms": "價值", "colloquial_terms": "基本面", "tone_style": "conservative"},
            "183": {"post_times": "9:00-17:00", "target_audience": "news_traders", "interaction_threshold": 0.4, "content_types": ["news"], "common_terms": "新聞", "colloquial_terms": "消息", "tone_style": "informative"},
            "184": {"post_times": "9:00-17:00", "target_audience": "data_traders", "interaction_threshold": 0.5, "content_types": ["data"], "common_terms": "數據", "colloquial_terms": "數字", "tone_style": "data_driven"},
            "185": {"post_times": "9:00-17:00", "target_audience": "day_traders", "interaction_threshold": 0.3, "content_types": ["short_term"], "common_terms": "短線", "colloquial_terms": "當沖", "tone_style": "aggressive"},
            "186": {"post_times": "9:00-17:00", "target_audience": "active_traders", "interaction_threshold": 0.5, "content_types": ["analysis"], "common_terms": "技術分析", "colloquial_terms": "技術面", "tone_style": "professional"},
            "187": {"post_times": "9:00-17:00", "target_audience": "value_investors", "interaction_threshold": 0.6, "content_types": ["macro"], "common_terms": "總經", "colloquial_terms": "大環境", "tone_style": "analytical"},
            "188": {"post_times": "9:00-17:00", "target_audience": "news_traders", "interaction_threshold": 0.4, "content_types": ["news"], "common_terms": "消息面", "colloquial_terms": "內線", "tone_style": "urgent"},
            "189": {"post_times": "9:00-17:00", "target_audience": "retail_traders", "interaction_threshold": 0.3, "content_types": ["tips"], "common_terms": "散戶", "colloquial_terms": "小資", "tone_style": "friendly"},
            "190": {"post_times": "9:00-17:00", "target_audience": "local_traders", "interaction_threshold": 0.4, "content_types": ["local"], "common_terms": "地方", "colloquial_terms": "在地", "tone_style": "local"},
            "191": {"post_times": "9:00-17:00", "target_audience": "gossip_lovers", "interaction_threshold": 0.7, "content_types": ["gossip"], "common_terms": "八卦", "colloquial_terms": "小道", "tone_style": "playful"},
            "192": {"post_times": "9:00-17:00", "target_audience": "insider_traders", "interaction_threshold": 0.8, "content_types": ["insider"], "common_terms": "爆料", "colloquial_terms": "內幕", "tone_style": "mysterious"},
            "193": {"post_times": "9:00-17:00", "target_audience": "technical_traders", "interaction_threshold": 0.5, "content_types": ["technical"], "common_terms": "技術", "colloquial_terms": "技術面", "tone_style": "technical"},
            "194": {"post_times": "9:00-17:00", "target_audience": "value_investors", "interaction_threshold": 0.6, "content_types": ["fundamental"], "common_terms": "價值", "colloquial_terms": "基本面", "tone_style": "conservative"},
            "195": {"post_times": "9:00-17:00", "target_audience": "news_traders", "interaction_threshold": 0.4, "content_types": ["news"], "common_terms": "新聞", "colloquial_terms": "消息", "tone_style": "informative"},
            "196": {"post_times": "9:00-17:00", "target_audience": "data_traders", "interaction_threshold": 0.5, "content_types": ["data"], "common_terms": "數據", "colloquial_terms": "數字", "tone_style": "data_driven"},
            "197": {"post_times": "9:00-17:00", "target_audience": "day_traders", "interaction_threshold": 0.3, "content_types": ["short_term"], "common_terms": "短線", "colloquial_terms": "當沖", "tone_style": "aggressive"},
            "198": {"post_times": "9:00-17:00", "target_audience": "general_traders", "interaction_threshold": 0.5, "content_types": ["comprehensive"], "common_terms": "綜合", "colloquial_terms": "全方位", "tone_style": "balanced"},
            "200": {"post_times": "9:00-17:00", "target_audience": "technical_traders", "interaction_threshold": 0.5, "content_types": ["technical"], "common_terms": "技術", "colloquial_terms": "技術面", "tone_style": "professional"},
            "201": {"post_times": "9:00-17:00", "target_audience": "macro_traders", "interaction_threshold": 0.6, "content_types": ["macro"], "common_terms": "總經", "colloquial_terms": "大環境", "tone_style": "analytical"},
            "202": {"post_times": "9:00-17:00", "target_audience": "news_traders", "interaction_threshold": 0.4, "content_types": ["news"], "common_terms": "消息", "colloquial_terms": "內線", "tone_style": "urgent"},
            "203": {"post_times": "9:00-17:00", "target_audience": "retail_traders", "interaction_threshold": 0.3, "content_types": ["tips"], "common_terms": "散戶", "colloquial_terms": "小資", "tone_style": "friendly"},
            "204": {"post_times": "9:00-17:00", "target_audience": "local_traders", "interaction_threshold": 0.4, "content_types": ["local"], "common_terms": "地方", "colloquial_terms": "在地", "tone_style": "local"},
            "205": {"post_times": "9:00-17:00", "target_audience": "gossip_lovers", "interaction_threshold": 0.7, "content_types": ["gossip"], "common_terms": "八卦", "colloquial_terms": "小道", "tone_style": "playful"},
            "206": {"post_times": "9:00-17:00", "target_audience": "insider_traders", "interaction_threshold": 0.8, "content_types": ["insider"], "common_terms": "爆料", "colloquial_terms": "內幕", "tone_style": "mysterious"},
            "207": {"post_times": "9:00-17:00", "target_audience": "technical_traders", "interaction_threshold": 0.5, "content_types": ["technical"], "common_terms": "技術", "colloquial_terms": "技術面", "tone_style": "technical"},
            "208": {"post_times": "9:00-17:00", "target_audience": "value_investors", "interaction_threshold": 0.6, "content_types": ["fundamental"], "common_terms": "價值", "colloquial_terms": "基本面", "tone_style": "conservative"},
            "209": {"post_times": "9:00-17:00", "target_audience": "news_traders", "interaction_threshold": 0.4, "content_types": ["news"], "common_terms": "新聞", "colloquial_terms": "消息", "tone_style": "informative"},
            "210": {"post_times": "9:00-17:00", "target_audience": "data_traders", "interaction_threshold": 0.5, "content_types": ["data"], "common_terms": "數據", "colloquial_terms": "數字", "tone_style": "data_driven"}
        }
        
        logger.info("使用預設KOL憑證配置")
    
    def get_kol_credentials(self, kol_serial: str) -> Optional[Dict[str, str]]:
        """獲取 KOL 憑證"""
        return self.kol_credentials.get(kol_serial)
    
    def get_all_kol_serials(self) -> List[str]:
        """獲取所有 KOL 序號"""
        return list(self.kol_credentials.keys())
    
    def get_kol_list_for_selection(self) -> List[Dict[str, Any]]:
        """獲取用於選擇的 KOL 列表"""
        try:
            from kol_database_service import kol_db_service
            return kol_db_service.get_kol_list_for_selection()
        except Exception as e:
            logger.error(f"獲取KOL選擇列表失敗: {e}")
            # 返回基本列表
            return [
                {
                    "serial": serial,
                    "nickname": self.kol_names.get(serial, f"KOL_{serial}"),
                    "persona": self.kol_personas.get(serial, "綜合派"),
                    "status": "active",
                    "email": creds["email"],
                    "member_id": serial
                }
                for serial, creds in self.kol_credentials.items()
            ]
    
    async def login_kol(self, kol_serial: str) -> Optional[str]:
        """登入 KOL 並返回 access token"""
        try:
            # 檢查是否已有有效 token
            if kol_serial in self.kol_tokens:
                token_data = self.kol_tokens[kol_serial]
                if token_data.get('expires_at') and datetime.now() < token_data['expires_at']:
                    logger.info(f"✅ 使用快取的 KOL {kol_serial} token")
                    return token_data['token']
            
            # 獲取憑證
            creds = self.get_kol_credentials(kol_serial)
            if not creds:
                logger.error(f"❌ 找不到 KOL {kol_serial} 的憑證")
                return None
            
            logger.info(f"🔐 開始登入 KOL {kol_serial}...")
            
            # 使用 CMoney Client 登入
            from src.clients.cmoney.cmoney_client import CMoneyClient, LoginCredentials
            cmoney_client = CMoneyClient()
            
            credentials = LoginCredentials(
                email=creds['email'],
                password=creds['password']
            )
            
            token = await cmoney_client.login(credentials)
            
            # 快取 token
            self.kol_tokens[kol_serial] = {
                'token': token.token,
                'expires_at': token.expires_at,
                'created_at': datetime.now()
            }
            
            logger.info(f"✅ KOL {kol_serial} 登入成功")
            return token.token
            
        except Exception as e:
            logger.error(f"❌ KOL {kol_serial} 登入失敗: {e}")
            return None
    
    def get_kol_info(self, kol_serial: str) -> Optional[Dict[str, Any]]:
        """獲取 KOL 基本資訊"""
        try:
            from kol_database_service import kol_db_service
            kol = kol_db_service.get_kol_by_serial(str(kol_serial))
            if kol:
                return {
                    "serial": kol.serial,
                    "nickname": kol.nickname,
                    "persona": kol.persona,
                    "email": kol.email,
                    "member_id": kol.member_id,
                    "status": kol.status,
                    "owner": kol.owner,
                    "last_login": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"獲取KOL {kol_serial} 資訊失敗: {e}")
        
        # 備用方案
        creds = self.get_kol_credentials(kol_serial)
        if creds:
            personalized_settings = self.kol_personalized_settings.get(kol_serial, {})
            return {
                "serial": kol_serial,
                "nickname": self.kol_names.get(kol_serial, f"KOL_{kol_serial}"),
                "persona": self.kol_personas.get(kol_serial, "綜合派"),
                "email": creds["email"],
                "member_id": creds.get("member_id", kol_serial),
                "status": "active",
                "owner": "威廉用",
                "last_login": datetime.now().isoformat(),
                "post_times": personalized_settings.get("post_times", "9:00-17:00"),
                "target_audience": personalized_settings.get("target_audience", "general_traders"),
                "interaction_threshold": personalized_settings.get("interaction_threshold", 0.5),
                "content_types": personalized_settings.get("content_types", ["analysis"]),
                "common_terms": personalized_settings.get("common_terms", ""),
                "colloquial_terms": personalized_settings.get("colloquial_terms", ""),
                "tone_style": personalized_settings.get("tone_style", "professional")
            }
        return None
    
    def get_all_kol_info(self) -> List[Dict[str, Any]]:
        """獲取所有 KOL 資訊"""
        kol_info_list = []
        for serial in self.get_all_kol_serials():
            info = self.get_kol_info(serial)
            if info:
                kol_info_list.append(info)
        return kol_info_list

# 創建全局 KOL 服務實例
kol_service = KOLService()
