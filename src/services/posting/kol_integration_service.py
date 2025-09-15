#!/usr/bin/env python3
"""
KOL資料整合服務
從Google Sheets讀取KOL資料並整合到發文生成系統
"""

import os
import sys
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clients.google.sheets_client import GoogleSheetsClient

logger = logging.getLogger(__name__)

@dataclass
class KOLProfile:
    """KOL個人資料"""
    serial: int
    nickname: str
    persona: str
    member_id: str
    email: str
    password: str
    whitelist: bool
    status: str
    content_types: List[str]
    posting_times: List[str]
    target_audience: str
    interaction_threshold: float
    common_words: List[str]
    colloquial_words: List[str]
    tone_style: str
    typing_habit: str
    background_story: str
    expertise_areas: List[str]
    data_sources: List[str]
    created_at: str
    last_updated: str
    topic_preferences: List[str]
    banned_categories: List[str]
    stock_mention_format: str
    stock_mention_secondary_format: str
    stock_mention_frequency_weight: float
    stock_mention_context_modifier: str
    prompt_persona: str
    prompt_style: str
    prompt_guardrails: str
    prompt_skeleton: str
    prompt_cta: str
    prompt_hashtags: str
    typing_habit_detail: str
    signature: str
    emoji_pack: str
    model_id: str
    template_variant: str
    model_temp: float
    max_tokens: int
    title_openers: List[str]
    title_signature_patterns: List[str]
    title_tail_word: str
    title_banned_words: List[str]
    title_style_examples: List[str]
    title_retry_max: int
    tone_formal: int
    tone_emotion: int
    tone_confidence: int
    tone_urgency: int
    tone_interaction: int
    question_ratio: float
    content_length: str
    interaction_starters: List[str]
    require_finlab_api: bool
    allow_hashtags: bool

class KOLIntegrationService:
    """KOL整合服務"""
    
    def __init__(self):
        self.sheets_client = GoogleSheetsClient()
        self.logger = logging.getLogger(__name__)
    
    async def load_kol_profiles_from_sheets(self) -> List[KOLProfile]:
        """從Google Sheets載入KOL資料"""
        try:
            self.logger.info("開始從Google Sheets載入KOL資料")
            
            # 讀取KOL角色紀錄表
            sheet_data = await self.sheets_client.read_sheet('貼文紀錄表KOL 角色紀錄表')
            
            kol_profiles = []
            for row in sheet_data[1:]:  # 跳過標題行
                if not row or len(row) < 10:  # 跳過空行或資料不足的行
                    continue
                
                try:
                    # 解析KOL資料
                    kol_profile = self._parse_kol_row(row)
                    if kol_profile:
                        kol_profiles.append(kol_profile)
                        self.logger.info(f"載入KOL: {kol_profile.nickname} ({kol_profile.serial})")
                
                except Exception as e:
                    self.logger.error(f"解析KOL資料失敗: {row[:5]} - {e}")
                    continue
            
            self.logger.info(f"成功載入 {len(kol_profiles)} 個KOL資料")
            return kol_profiles
            
        except Exception as e:
            self.logger.error(f"載入KOL資料失敗: {e}")
            return []
    
    def _parse_kol_row(self, row: List[str]) -> Optional[KOLProfile]:
        """解析KOL資料行"""
        try:
            if len(row) < 50:  # 確保有足夠的欄位
                return None
            
            # 基本資料
            serial = int(row[0]) if row[0] and row[0].isdigit() else 0
            nickname = row[1] if row[1] else ""
            persona = row[4] if row[4] else ""
            member_id = row[5] if row[5] else ""
            email = row[6] if row[6] else ""
            password = row[7] if row[7] else ""
            whitelist = row[8] == "TRUE" if row[8] else False
            status = row[9] if row[9] else "inactive"
            
            # 內容設定
            content_types = row[11].split(',') if row[11] else []
            posting_times = row[12].split(',') if row[12] else []
            target_audience = row[13] if row[13] else ""
            interaction_threshold = float(row[14]) if row[14] else 0.5
            
            # 語言風格
            common_words = row[15].split(',') if row[15] else []
            colloquial_words = row[16].split(',') if row[16] else []
            tone_style = row[17] if row[17] else ""
            typing_habit = row[18] if row[18] else ""
            background_story = row[19] if row[19] else ""
            
            # 專業領域
            expertise_areas = row[20].split(',') if row[20] else []
            data_sources = row[21].split(',') if row[21] else []
            
            # 時間戳記
            created_at = row[22] if row[22] else datetime.now().isoformat()
            last_updated = row[23] if row[23] else datetime.now().isoformat()
            
            # 話題偏好
            topic_preferences = row[25].split(',') if row[25] else []
            banned_categories = row[26].split(',') if row[26] else []
            
            # 股票提及設定
            stock_mention_format = row[27] if row[27] else ""
            stock_mention_secondary_format = row[28] if row[28] else ""
            stock_mention_frequency_weight = float(row[29]) if row[29] else 1.0
            stock_mention_context_modifier = row[30] if row[30] else ""
            
            # Prompt設定
            prompt_persona = row[32] if row[32] else ""
            prompt_style = row[33] if row[33] else ""
            prompt_guardrails = row[34] if row[34] else ""
            prompt_skeleton = row[35] if row[35] else ""
            prompt_cta = row[36] if row[36] else ""
            prompt_hashtags = row[37] if row[37] else ""
            
            # 打字習慣和簽名
            typing_habit_detail = row[38] if row[38] else ""
            signature = row[39] if row[39] else ""
            emoji_pack = row[40] if row[40] else ""
            
            # 模型設定
            model_id = row[41] if row[41] else "gpt-4o-mini"
            template_variant = row[42] if row[42] else "default"
            model_temp = float(row[43]) if row[43] else 0.7
            max_tokens = int(row[44]) if row[44] else 500
            
            # 標題設定
            title_openers = row[45].split(',') if row[45] else []
            title_signature_patterns = row[46].split(',') if row[46] else []
            title_tail_word = row[47] if row[47] else ""
            title_banned_words = row[48].split(',') if row[48] else []
            title_style_examples = row[49].split(',') if row[49] else []
            title_retry_max = int(row[50]) if row[50] else 3
            
            # 語調設定
            tone_formal = int(row[51]) if row[51] else 5
            tone_emotion = int(row[52]) if row[52] else 5
            tone_confidence = int(row[53]) if row[53] else 5
            tone_urgency = int(row[54]) if row[54] else 5
            tone_interaction = int(row[55]) if row[55] else 5
            
            # 內容設定
            question_ratio = float(row[56]) if row[56] else 0.3
            content_length = row[57] if row[57] else "medium"
            interaction_starters = row[58].split(',') if row[58] else []
            
            # 功能開關
            require_finlab_api = row[59] == "TRUE" if row[59] else False
            allow_hashtags = row[60] == "TRUE" if row[60] else True
            
            return KOLProfile(
                serial=serial,
                nickname=nickname,
                persona=persona,
                member_id=member_id,
                email=email,
                password=password,
                whitelist=whitelist,
                status=status,
                content_types=content_types,
                posting_times=posting_times,
                target_audience=target_audience,
                interaction_threshold=interaction_threshold,
                common_words=common_words,
                colloquial_words=colloquial_words,
                tone_style=tone_style,
                typing_habit=typing_habit,
                background_story=background_story,
                expertise_areas=expertise_areas,
                data_sources=data_sources,
                created_at=created_at,
                last_updated=last_updated,
                topic_preferences=topic_preferences,
                banned_categories=banned_categories,
                stock_mention_format=stock_mention_format,
                stock_mention_secondary_format=stock_mention_secondary_format,
                stock_mention_frequency_weight=stock_mention_frequency_weight,
                stock_mention_context_modifier=stock_mention_context_modifier,
                prompt_persona=prompt_persona,
                prompt_style=prompt_style,
                prompt_guardrails=prompt_guardrails,
                prompt_skeleton=prompt_skeleton,
                prompt_cta=prompt_cta,
                prompt_hashtags=prompt_hashtags,
                typing_habit_detail=typing_habit_detail,
                signature=signature,
                emoji_pack=emoji_pack,
                model_id=model_id,
                template_variant=template_variant,
                model_temp=model_temp,
                max_tokens=max_tokens,
                title_openers=title_openers,
                title_signature_patterns=title_signature_patterns,
                title_tail_word=title_tail_word,
                title_banned_words=title_banned_words,
                title_style_examples=title_style_examples,
                title_retry_max=title_retry_max,
                tone_formal=tone_formal,
                tone_emotion=tone_emotion,
                tone_confidence=tone_confidence,
                tone_urgency=tone_urgency,
                tone_interaction=tone_interaction,
                question_ratio=question_ratio,
                content_length=content_length,
                interaction_starters=interaction_starters,
                require_finlab_api=require_finlab_api,
                allow_hashtags=allow_hashtags
            )
            
        except Exception as e:
            self.logger.error(f"解析KOL資料行失敗: {e}")
            return None
    
    async def get_active_kols(self) -> List[KOLProfile]:
        """獲取活躍的KOL列表"""
        try:
            all_kols = await self.load_kol_profiles_from_sheets()
            active_kols = [kol for kol in all_kols if kol.status == "active"]
            
            self.logger.info(f"找到 {len(active_kols)} 個活躍KOL")
            return active_kols
            
        except Exception as e:
            self.logger.error(f"獲取活躍KOL失敗: {e}")
            return []
    
    async def get_kol_by_serial(self, serial: int) -> Optional[KOLProfile]:
        """根據序號獲取KOL資料"""
        try:
            all_kols = await self.load_kol_profiles_from_sheets()
            for kol in all_kols:
                if kol.serial == serial:
                    return kol
            
            return None
            
        except Exception as e:
            self.logger.error(f"根據序號獲取KOL失敗: {serial} - {e}")
            return None
    
    async def get_kols_by_persona(self, persona: str) -> List[KOLProfile]:
        """根據人設獲取KOL列表"""
        try:
            all_kols = await self.load_kol_profiles_from_sheets()
            persona_kols = [kol for kol in all_kols if persona.lower() in kol.persona.lower()]
            
            self.logger.info(f"找到 {len(persona_kols)} 個 {persona} 人設KOL")
            return persona_kols
            
        except Exception as e:
            self.logger.error(f"根據人設獲取KOL失敗: {persona} - {e}")
            return []
    
    def export_kol_to_dict(self, kol: KOLProfile) -> Dict[str, Any]:
        """將KOL資料轉換為字典格式"""
        return {
            "serial": kol.serial,
            "nickname": kol.nickname,
            "persona": kol.persona,
            "member_id": kol.member_id,
            "email": kol.email,
            "status": kol.status,
            "content_types": kol.content_types,
            "posting_times": kol.posting_times,
            "target_audience": kol.target_audience,
            "interaction_threshold": kol.interaction_threshold,
            "common_words": kol.common_words,
            "colloquial_words": kol.colloquial_words,
            "tone_style": kol.tone_style,
            "typing_habit": kol.typing_habit,
            "background_story": kol.background_story,
            "expertise_areas": kol.expertise_areas,
            "data_sources": kol.data_sources,
            "topic_preferences": kol.topic_preferences,
            "banned_categories": kol.banned_categories,
            "stock_mention_format": kol.stock_mention_format,
            "prompt_persona": kol.prompt_persona,
            "prompt_style": kol.prompt_style,
            "prompt_guardrails": kol.prompt_guardrails,
            "prompt_skeleton": kol.prompt_skeleton,
            "prompt_cta": kol.prompt_cta,
            "prompt_hashtags": kol.prompt_hashtags,
            "signature": kol.signature,
            "emoji_pack": kol.emoji_pack,
            "model_id": kol.model_id,
            "model_temp": kol.model_temp,
            "max_tokens": kol.max_tokens,
            "question_ratio": kol.question_ratio,
            "content_length": kol.content_length,
            "interaction_starters": kol.interaction_starters,
            "require_finlab_api": kol.require_finlab_api,
            "allow_hashtags": kol.allow_hashtags
        }

# 工廠函數
def create_kol_integration_service() -> KOLIntegrationService:
    """創建KOL整合服務實例"""
    return KOLIntegrationService()

# 使用範例
async def example_usage():
    """使用範例"""
    kol_service = create_kol_integration_service()
    
    # 獲取所有活躍KOL
    active_kols = await kol_service.get_active_kols()
    print(f"活躍KOL數量: {len(active_kols)}")
    
    # 獲取特定人設的KOL
    technical_kols = await kol_service.get_kols_by_persona("技術派")
    print(f"技術派KOL: {[kol.nickname for kol in technical_kols]}")
    
    # 獲取特定序號的KOL
    kol_200 = await kol_service.get_kol_by_serial(200)
    if kol_200:
        print(f"KOL 200: {kol_200.nickname} - {kol_200.persona}")

if __name__ == "__main__":
    asyncio.run(example_usage())
