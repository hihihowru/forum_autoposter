#!/usr/bin/env python3
"""
配置管理器
統一管理系統配置，包括環境變數、API金鑰、KOL設定等
"""

import os
import json
import yaml
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

@dataclass
class GoogleConfig:
    """Google 相關配置"""
    credentials_file: str = field(default_factory=lambda: os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials/google-service-account.json'))
    spreadsheet_id: str = field(default_factory=lambda: os.getenv('GOOGLE_SHEETS_ID', ''))
    api_key: str = field(default_factory=lambda: os.getenv('GOOGLE_API_KEY', ''))

@dataclass
class CMoneyConfig:
    """CMoney 相關配置"""
    base_url: str = "https://www.cmoney.tw"
    default_email: str = "forum_200@cmoney.com.tw"
    default_password: str = field(default_factory=lambda: os.getenv('CMONEY_PASSWORD', ''))
    timeout: int = 30
    max_retries: int = 3

@dataclass
class OpenAIConfig:
    """OpenAI 相關配置"""
    api_key: str = field(default_factory=lambda: os.getenv('OPENAI_API_KEY', ''))
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 60

@dataclass
class KOLConfig:
    """KOL 相關配置"""
    max_posts_per_day: int = 10
    min_content_length: int = 100
    max_content_length: int = 500
    enable_personalization: bool = True
    enable_learning: bool = True
    default_persona: str = "專業分析師"

@dataclass
class ContentConfig:
    """內容生成相關配置"""
    enable_quality_check: bool = True
    enable_plagiarism_check: bool = True
    min_quality_score: float = 0.7
    max_generation_retries: int = 3
    enable_emoji: bool = True
    enable_hashtags: bool = True

@dataclass
class WorkflowConfig:
    """工作流程相關配置"""
    enable_parallel_processing: bool = True
    max_concurrent_workflows: int = 3
    workflow_timeout: int = 300
    enable_auto_retry: bool = True
    retry_delay: int = 60

@dataclass
class LoggingConfig:
    """日誌相關配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/main_workflow.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class SystemConfig:
    """系統配置"""
    google: GoogleConfig = field(default_factory=GoogleConfig)
    cmoney: CMoneyConfig = field(default_factory=CMoneyConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    kol: KOLConfig = field(default_factory=KOLConfig)
    content: ContentConfig = field(default_factory=ContentConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器"""
        self.config_path = config_path or "config/system_config.yaml"
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> SystemConfig:
        """載入配置"""
        try:
            # 嘗試從文件載入配置
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                return self._create_config_from_dict(config_data)
            else:
                # 使用默認配置
                return SystemConfig()
                
        except Exception as e:
            print(f"載入配置文件失敗: {e}")
            return SystemConfig()
    
    def _create_config_from_dict(self, config_data: Dict[str, Any]) -> SystemConfig:
        """從字典創建配置對象"""
        return SystemConfig(
            google=GoogleConfig(**config_data.get('google', {})),
            cmoney=CMoneyConfig(**config_data.get('cmoney', {})),
            openai=OpenAIConfig(**config_data.get('openai', {})),
            kol=KOLConfig(**config_data.get('kol', {})),
            content=ContentConfig(**config_data.get('content', {})),
            workflow=WorkflowConfig(**config_data.get('workflow', {})),
            logging=LoggingConfig(**config_data.get('logging', {}))
        )
    
    def _validate_config(self):
        """驗證配置"""
        errors = []
        
        # 檢查必要的環境變數
        required_env_vars = [
            ('OPENAI_API_KEY', self.config.openai.api_key),
            ('CMONEY_PASSWORD', self.config.cmoney.default_password),
            ('GOOGLE_SHEETS_ID', self.config.google.spreadsheet_id)
        ]
        
        for var_name, value in required_env_vars:
            if not value:
                errors.append(f"缺少必要的環境變數: {var_name}")
        
        # 檢查文件路徑
        if not Path(self.config.google.credentials_file).exists():
            errors.append(f"Google 憑證文件不存在: {self.config.google.credentials_file}")
        
        if errors:
            raise ValueError(f"配置驗證失敗:\n" + "\n".join(errors))
    
    def get_config(self) -> SystemConfig:
        """獲取配置"""
        return self.config
    
    def get_kol_credentials(self) -> Dict[str, Dict[str, str]]:
        """獲取 KOL 憑證"""
        return {
            "200": {
                "email": "forum_200@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD', ''),
                "nickname": "川川哥",
                "persona": "籌碼派"
            },
            "201": {
                "email": "forum_201@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD_201', ''),
                "nickname": "韭割哥",
                "persona": "情緒派"
            },
            "202": {
                "email": "forum_202@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD_202', ''),
                "nickname": "梅川褲子",
                "persona": "技術派"
            },
            "203": {
                "email": "forum_203@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD_203', ''),
                "nickname": "信號宅神",
                "persona": "信號派"
            },
            "204": {
                "email": "forum_204@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD_204', ''),
                "nickname": "八卦護城河",
                "persona": "八卦派"
            },
            "205": {
                "email": "forum_205@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD_205', ''),
                "nickname": "長線韭韭",
                "persona": "長線派"
            },
            "206": {
                "email": "forum_206@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD_206', ''),
                "nickname": "報爆哥_209",
                "persona": "爆料派"
            },
            "207": {
                "email": "forum_207@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD_207', ''),
                "nickname": "板橋大who",
                "persona": "分析派"
            },
            "208": {
                "email": "forum_208@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD_208', ''),
                "nickname": "韭割哥",
                "persona": "情緒派"
            },
            "209": {
                "email": "forum_209@cmoney.com.tw",
                "password": os.getenv('CMONEY_PASSWORD_209', ''),
                "nickname": "小道爆料王",
                "persona": "爆料派"
            }
        }
    
    def get_kol_personalization_settings(self) -> Dict[str, Dict[str, Any]]:
        """獲取 KOL 個人化設定（基於真實 UGC 數據分析）"""
        return {
            "200": {  # 川川哥 - 互動型 KOL（問句 13.1%）
                "persona": "PPT鄉民派",
                "nickname": "川川哥",
                "writing_style": "親民互動，善用問句",
                "content_length": "short",  # ≤15字
                "emoji_usage": "moderate",  # 3.5%
                "hashtag_style": "interactive",
                "tone": "friendly",
                "key_phrases": ["怎麼了？", "該買嗎？", "怎麼看？"],
                "avoid_topics": ["過於專業", "複雜分析"],
                "preferred_data_sources": ["基本面", "市場情緒"],
                "prompt_template": "互動型分析師",
                "title_style": "question",  # 問句類 13.1%
                "ai_detection_risk_score": 0.15,
                "personalization_level": 0.85,
                "creativity_score": 8.5,
                "coherence_score": 8.8
            },
            "201": {  # 韭割哥 - 感嘆型 KOL（感嘆句 5.1%）
                "persona": "酸民派",
                "nickname": "韭割哥",
                "writing_style": "情緒化表達，善用感嘆句",
                "content_length": "short",  # ≤15字
                "emoji_usage": "frequent",  # 3.5%
                "hashtag_style": "emotional",
                "tone": "sarcastic",
                "key_phrases": ["太猛了！", "好棒！", "舒服！", "神了！"],
                "avoid_topics": ["過於正面", "專業分析"],
                "preferred_data_sources": ["情緒指標", "散戶動向"],
                "prompt_template": "情緒化分析師",
                "title_style": "exclamation",  # 感嘆類 5.1%
                "ai_detection_risk_score": 0.25,
                "personalization_level": 0.95,
                "creativity_score": 9.0,
                "coherence_score": 8.5
            },
            "202": {  # 梅川褲子 - 專業型 KOL（基本面 2.9%）
                "persona": "古人派",
                "nickname": "梅川褲子",
                "writing_style": "古典文雅，善用專業術語",
                "content_length": "short",  # ≤15字
                "emoji_usage": "minimal",  # 3.5%
                "hashtag_style": "classical",
                "tone": "elegant",
                "key_phrases": ["營收成長", "技術突破", "基本面轉好"],
                "avoid_topics": ["八卦", "情緒化"],
                "preferred_data_sources": ["基本面", "技術面"],
                "prompt_template": "古典分析師",
                "title_style": "professional",  # 專業類 2.9%
                "ai_detection_risk_score": 0.20,
                "personalization_level": 0.80,
                "creativity_score": 7.0,
                "coherence_score": 9.2
            },
            "203": {  # 信號宅神 - 指令型 KOL（指令句 3.1%）
                "persona": "信號派",
                "nickname": "信號宅神",
                "writing_style": "明確指令，善用提醒句",
                "content_length": "short",  # ≤15字
                "emoji_usage": "signal_focused",  # 3.5%
                "hashtag_style": "signal",
                "tone": "directive",
                "key_phrases": ["注意！", "快看！", "提醒！"],
                "avoid_topics": ["模糊分析", "長期投資"],
                "preferred_data_sources": ["技術信號", "突破確認"],
                "prompt_template": "信號分析師",
                "title_style": "command",  # 指令類 3.1%
                "ai_detection_risk_score": 0.18,
                "personalization_level": 0.75,
                "creativity_score": 6.5,
                "coherence_score": 9.5
            },
            "204": {  # 八卦護城河 - 話題型 KOL（AI 1.3%）
                "persona": "八卦派",
                "nickname": "八卦護城河",
                "writing_style": "熱門話題，善用八卦",
                "content_length": "short",  # ≤15字
                "emoji_usage": "gossip",  # 3.5%
                "hashtag_style": "gossip",
                "tone": "mysterious",
                "key_phrases": ["內幕", "小道消息", "護城河"],
                "avoid_topics": ["公開資訊", "正式公告"],
                "preferred_data_sources": ["市場傳聞", "內部消息"],
                "prompt_template": "八卦爆料專家",
                "title_style": "topic",  # 話題類
                "ai_detection_risk_score": 0.30,
                "personalization_level": 0.90,
                "creativity_score": 8.5,
                "coherence_score": 8.0
            },
            "205": {  # 長線韭韭 - 平衡型 KOL（綜合型）
                "persona": "長線派",
                "nickname": "長線韭韭",
                "writing_style": "平衡表達，綜合多種風格",
                "content_length": "short",  # ≤15字
                "emoji_usage": "minimal",  # 3.5%
                "hashtag_style": "investment",
                "tone": "balanced",
                "key_phrases": ["長期投資", "價值投資", "基本面"],
                "avoid_topics": ["短線操作", "投機"],
                "preferred_data_sources": ["財報", "基本面"],
                "prompt_template": "價值投資分析師",
                "title_style": "balanced",  # 平衡型
                "ai_detection_risk_score": 0.12,
                "personalization_level": 0.70,
                "creativity_score": 6.0,
                "coherence_score": 9.8
            },
            "206": {  # 報爆哥_209 - 活潑型 KOL（表情符號 3.5%）
                "persona": "爆料派",
                "nickname": "報爆哥",
                "writing_style": "活潑生動，善用表情符號",
                "content_length": "short",  # ≤15字
                "emoji_usage": "frequent",  # 3.5%
                "hashtag_style": "breaking",
                "tone": "lively",
                "key_phrases": ["獨家", "搶先", "爆料"],
                "avoid_topics": ["舊聞", "公開資訊"],
                "preferred_data_sources": ["獨家消息", "內部爆料"],
                "prompt_template": "獨家爆料記者",
                "title_style": "emoji",  # 表情符號類
                "ai_detection_risk_score": 0.35,
                "personalization_level": 0.92,
                "creativity_score": 8.8,
                "coherence_score": 7.5
            },
            "207": {  # 板橋大who - 簡潔型 KOL（≤15字）
                "persona": "分析派",
                "nickname": "板橋大who",
                "writing_style": "簡潔明瞭，重點突出",
                "content_length": "short",  # ≤15字
                "emoji_usage": "moderate",  # 3.5%
                "hashtag_style": "analytical",
                "tone": "concise",
                "key_phrases": ["深度分析", "多角度", "綜合評估"],
                "avoid_topics": ["表面分析", "單一角度"],
                "preferred_data_sources": ["綜合分析", "多維度數據"],
                "prompt_template": "深度分析師",
                "title_style": "concise",  # 簡潔型
                "ai_detection_risk_score": 0.15,
                "personalization_level": 0.75,
                "creativity_score": 7.2,
                "coherence_score": 9.3
            },
            "208": {  # 韭割哥 - 幽默型 KOL（搞笑比喻）
                "persona": "幽默派",
                "nickname": "韭割哥",
                "writing_style": "幽默風趣，善用搞笑比喻",
                "content_length": "short",  # ≤15字
                "emoji_usage": "frequent",  # 3.5%
                "hashtag_style": "humorous",
                "tone": "funny",
                "key_phrases": ["韭菜", "割韭菜", "搞笑比喻"],
                "avoid_topics": ["過於專業", "複雜分析"],
                "preferred_data_sources": ["情緒指標", "散戶動向"],
                "prompt_template": "幽默分析師",
                "title_style": "humorous",  # 幽默型
                "ai_detection_risk_score": 0.25,
                "personalization_level": 0.95,
                "creativity_score": 9.0,
                "coherence_score": 8.5
            },
            "209": {  # 小道爆料王 - 提醒型 KOL（指令句 3.1%）
                "persona": "提醒派",
                "nickname": "小道爆料王",
                "writing_style": "提醒關注，善用指令句",
                "content_length": "short",  # ≤15字
                "emoji_usage": "moderate",  # 3.5%
                "hashtag_style": "alert",
                "tone": "alert",
                "key_phrases": ["注意！", "提醒！", "關注！"],
                "avoid_topics": ["過於樂觀", "盲目看多"],
                "preferred_data_sources": ["技術信號", "市場提醒"],
                "prompt_template": "提醒分析師",
                "title_style": "alert",  # 提醒型
                "ai_detection_risk_score": 0.18,
                "personalization_level": 0.80,
                "creativity_score": 7.5,
                "coherence_score": 9.0
            }
        }
    
    def save_config(self, config: SystemConfig, path: Optional[str] = None):
        """保存配置到文件"""
        save_path = path or self.config_path
        
        # 創建目錄
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 轉換為字典
        config_dict = {
            'google': {
                'credentials_file': config.google.credentials_file,
                'spreadsheet_id': config.google.spreadsheet_id,
                'api_key': config.google.api_key
            },
            'cmoney': {
                'base_url': config.cmoney.base_url,
                'default_email': config.cmoney.default_email,
                'timeout': config.cmoney.timeout,
                'max_retries': config.cmoney.max_retries
            },
            'openai': {
                'model': config.openai.model,
                'max_tokens': config.openai.max_tokens,
                'temperature': config.openai.temperature,
                'timeout': config.openai.timeout
            },
            'kol': {
                'max_posts_per_day': config.kol.max_posts_per_day,
                'min_content_length': config.kol.min_content_length,
                'max_content_length': config.kol.max_content_length,
                'enable_personalization': config.kol.enable_personalization,
                'enable_learning': config.kol.enable_learning,
                'default_persona': config.kol.default_persona
            },
            'content': {
                'enable_quality_check': config.content.enable_quality_check,
                'enable_plagiarism_check': config.content.enable_plagiarism_check,
                'min_quality_score': config.content.min_quality_score,
                'max_generation_retries': config.content.max_generation_retries,
                'enable_emoji': config.content.enable_emoji,
                'enable_hashtags': config.content.enable_hashtags
            },
            'workflow': {
                'enable_parallel_processing': config.workflow.enable_parallel_processing,
                'max_concurrent_workflows': config.workflow.max_concurrent_workflows,
                'workflow_timeout': config.workflow.workflow_timeout,
                'enable_auto_retry': config.workflow.enable_auto_retry,
                'retry_delay': config.workflow.retry_delay
            },
            'logging': {
                'level': config.logging.level,
                'format': config.logging.format,
                'file_path': config.logging.file_path,
                'max_file_size': config.logging.max_file_size,
                'backup_count': config.logging.backup_count
            }
        }
        
        # 保存到文件
        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True)
        
        print(f"配置已保存到: {save_path}")
    
    def reload_config(self):
        """重新載入配置"""
        self.config = self._load_config()
        self._validate_config()
        print("配置已重新載入")
    
    def get_environment_info(self) -> Dict[str, Any]:
        """獲取環境資訊"""
        return {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'config_path': self.config_path,
            'config_exists': Path(self.config_path).exists(),
            'environment_vars': {
                'OPENAI_API_KEY': '已設定' if os.getenv('OPENAI_API_KEY') else '未設定',
                'CMONEY_PASSWORD': '已設定' if os.getenv('CMONEY_PASSWORD') else '未設定',
                'GOOGLE_SHEETS_ID': '已設定' if os.getenv('GOOGLE_SHEETS_ID') else '未設定'
            }
        }
