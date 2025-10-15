#!/usr/bin/env python3
"""
個人化內容生成主流程
整合文長長度權重、文章類型、品質規範等所有個人化元素
"""

import os
import sys
import asyncio
import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.content.content_generator import ContentGenerator
from src.services.content.personalized_prompt_generator import PersonalizedPromptGenerator
from src.services.content.enhanced_prompt_generator import EnhancedPromptGenerator
from src.services.content.content_quality_checker import ContentQualityChecker
from src.services.analysis.enhanced_technical_analyzer import EnhancedTechnicalAnalyzer
from src.services.kol.kol_settings_loader import KOLSettingsLoader
from src.clients.google.sheets_client import GoogleSheetsClient
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PostType(Enum):
    """文章類型"""
    SHARE_OPINION = "share_opinion"  # 分享觀點
    FIND_COMMUNITY = "find_community"  # 找同溫層
    ASK_QUESTION = "ask_question"  # 提問問題引起互動
    TEACHING = "teaching"  # 教學
    NEWS_ALERT = "news_alert"  # 新聞快訊
    ANALYSIS = "analysis"  # 分析
    HUMOR = "humor"  # 幽默

class ContentLength(Enum):
    """內容長度"""
    SHORT = "short"  # 50-100字
    MEDIUM = "medium"  # 200-300字
    LONG = "long"  # 400-500字

@dataclass
class PersonalizedContentRequest:
    """個人化內容生成請求"""
    kol_nickname: str
    topic_title: str
    topic_keywords: str
    trigger_type: str
    stock_data: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None
    force_post_type: Optional[PostType] = None
    force_content_length: Optional[ContentLength] = None

@dataclass
class PersonalizedContentResult:
    """個人化內容生成結果"""
    title: str
    content: str
    post_type: PostType
    content_length: ContentLength
    word_count: int
    quality_score: float
    personalization_score: float
    kol_settings: Dict[str, Any]
    generation_metadata: Dict[str, Any]
    technical_analysis: Optional[Dict[str, Any]] = None

class PersonalizedContentGenerator:
    """個人化內容生成器 - 整合所有個人化元素"""
    
    def __init__(self):
        """初始化個人化內容生成器"""
        
        # 初始化各個組件
        self.content_generator = ContentGenerator()
        self.prompt_generator = PersonalizedPromptGenerator()
        self.enhanced_prompt_generator = EnhancedPromptGenerator()
        self.quality_checker = ContentQualityChecker()
        self.technical_analyzer = EnhancedTechnicalAnalyzer()
        self.kol_settings_loader = KOLSettingsLoader()
        
        # 初始化Google Sheets客戶端
        self.sheets_client = GoogleSheetsClient(
            credentials_file=os.getenv('GOOGLE_CREDENTIALS_FILE'),
            spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID')
        )
        
        # 文章類型權重配置
        self.post_type_weights = {
            PostType.SHARE_OPINION: 0.25,
            PostType.FIND_COMMUNITY: 0.20,
            PostType.ASK_QUESTION: 0.20,
            PostType.TEACHING: 0.15,
            PostType.NEWS_ALERT: 0.10,
            PostType.ANALYSIS: 0.05,
            PostType.HUMOR: 0.05
        }
        
        # 內容長度權重配置
        self.content_length_weights = {
            ContentLength.SHORT: 0.3,  # 30%短文
            ContentLength.MEDIUM: 0.5,  # 50%中等長度
            ContentLength.LONG: 0.2   # 20%長文
        }
        
        logger.info("個人化內容生成器初始化完成")
    
    async def generate_personalized_content(self, request: PersonalizedContentRequest) -> PersonalizedContentResult:
        """生成個人化內容"""
        
        try:
            logger.info(f"🎯 開始為 {request.kol_nickname} 生成個人化內容")
            
            # 1. 載入KOL個人化設定
            kol_settings = await self._load_kol_personalized_settings(request.kol_nickname)
            logger.info(f"📋 KOL設定載入完成: {len(kol_settings)} 項設定")
            
            # 2. 決定文章類型和長度
            post_type = request.force_post_type or self._determine_post_type(kol_settings)
            content_length = request.force_content_length or self._determine_content_length(kol_settings)
            
            logger.info(f"📝 文章類型: {post_type.value}")
            logger.info(f"📏 內容長度: {content_length.value}")
            
            # 3. 獲取技術分析數據 (如果需要)
            technical_analysis = None
            if kol_settings.get('finlab_api_needed', False) and request.stock_data:
                technical_analysis = await self._get_technical_analysis(request.stock_data)
            
            # 4. 生成個人化Prompt
            personalized_prompt = await self._generate_personalized_prompt(
                request, kol_settings, post_type, content_length, technical_analysis
            )
            
            # 5. 生成內容
            content_result = await self._generate_content_with_quality_control(
                personalized_prompt, kol_settings, post_type, content_length
            )
            
            # 6. 計算品質分數
            quality_score = await self._calculate_quality_score(content_result, kol_settings)
            personalization_score = await self._calculate_personalization_score(content_result, kol_settings)
            
            # 7. 準備生成元數據
            generation_metadata = {
                'post_type': post_type.value,
                'content_length': content_length.value,
                'word_count': len(content_result),
                'quality_score': quality_score,
                'personalization_score': personalization_score,
                'generation_time': datetime.now().isoformat(),
                'kol_settings_version': kol_settings.get('version', '1.0'),
                'technical_analysis_used': technical_analysis is not None,
                'trigger_type': request.trigger_type
            }
            
            logger.info(f"✅ 個人化內容生成完成")
            logger.info(f"   品質分數: {quality_score:.2f}")
            logger.info(f"   個人化分數: {personalization_score:.2f}")
            logger.info(f"   字數: {len(content_result)}")
            
            return PersonalizedContentResult(
                title=personalized_prompt.get('title', ''),
                content=content_result,
                post_type=post_type,
                content_length=content_length,
                word_count=len(content_result),
                quality_score=quality_score,
                personalization_score=personalization_score,
                kol_settings=kol_settings,
                generation_metadata=generation_metadata,
                technical_analysis=technical_analysis
            )
            
        except Exception as e:
            logger.error(f"❌ 個人化內容生成失敗: {e}")
            raise
    
    async def _load_kol_personalized_settings(self, kol_nickname: str) -> Dict[str, Any]:
        """載入KOL個人化設定"""
        
        try:
            # 從Google Sheets載入KOL設定
            kol_row = self.kol_settings_loader.get_kol_row_by_nickname(kol_nickname)
            
            if not kol_row:
                logger.warning(f"⚠️ 找不到 {kol_nickname} 的設定，使用預設設定")
                return self._get_default_kol_settings(kol_nickname)
            
            # 轉換為配置字典
            kol_config = self.kol_settings_loader.build_kol_config_dict(kol_row)
            
            # 添加個人化權重設定
            kol_config.update({
                'post_type_weights': self._parse_post_type_weights(kol_row),
                'content_length_weights': self._parse_content_length_weights(kol_row),
                'quality_requirements': self._parse_quality_requirements(kol_row),
                'personalization_requirements': self._parse_personalization_requirements(kol_row)
            })
            
            return kol_config
            
        except Exception as e:
            logger.error(f"❌ 載入KOL設定失敗: {e}")
            return self._get_default_kol_settings(kol_nickname)
    
    def _determine_post_type(self, kol_settings: Dict[str, Any]) -> PostType:
        """決定文章類型"""
        
        # 優先使用KOL個人化權重
        custom_weights = kol_settings.get('post_type_weights', {})
        if custom_weights:
            weights = custom_weights
        else:
            weights = self.post_type_weights
        
        # 根據權重隨機選擇
        post_types = list(weights.keys())
        weights_list = list(weights.values())
        
        selected_type = random.choices(post_types, weights=weights_list, k=1)[0]
        return selected_type
    
    def _determine_content_length(self, kol_settings: Dict[str, Any]) -> ContentLength:
        """決定內容長度"""
        
        # 優先使用KOL個人化權重
        custom_weights = kol_settings.get('content_length_weights', {})
        if custom_weights:
            weights = custom_weights
        else:
            weights = self.content_length_weights
        
        # 根據權重隨機選擇
        lengths = list(weights.keys())
        weights_list = list(weights.values())
        
        selected_length = random.choices(lengths, weights=weights_list, k=1)[0]
        return selected_length
    
    async def _get_technical_analysis(self, stock_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """獲取技術分析數據"""
        
        try:
            stock_id = stock_data.get('stock_id')
            stock_name = stock_data.get('stock_name', '')
            
            if not stock_id:
                return None
            
            analysis = await self.technical_analyzer.get_enhanced_stock_analysis(stock_id, stock_name)
            
            if analysis:
                return {
                    'overall_score': analysis.overall_score,
                    'confidence_score': analysis.confidence_score,
                    'effective_indicators': analysis.effective_indicators,
                    'summary': analysis.summary,
                    'indicators': {name: {
                        'score': ind.overall_score,
                        'confidence': ind.confidence,
                        'signal': ind.signal,
                        'key_insights': ind.key_insights
                    } for name, ind in analysis.indicators.items()}
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 獲取技術分析失敗: {e}")
            return None
    
    async def _generate_personalized_prompt(self, request: PersonalizedContentRequest, 
                                          kol_settings: Dict[str, Any],
                                          post_type: PostType,
                                          content_length: ContentLength,
                                          technical_analysis: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成個人化Prompt"""
        
        # 使用增強版Prompt生成器
        enhanced_prompt = self.enhanced_prompt_generator.generate_enhanced_prompt(
            kol_serial=kol_settings.get('serial', ''),
            kol_nickname=request.kol_nickname,
            persona=kol_settings.get('persona', ''),
            topic_title=request.topic_title,
            stock_data=request.stock_data or {},
            market_context=request.market_data,
            stock_names=[request.stock_data.get('stock_name', '')] if request.stock_data else []
        )
        
        # 添加文章類型和長度指導
        post_type_guidance = self._get_post_type_guidance(post_type)
        content_length_guidance = self._get_content_length_guidance(content_length)
        
        # 添加技術分析指導
        technical_guidance = ""
        if technical_analysis:
            technical_guidance = f"""
技術分析數據：
- 綜合評分: {technical_analysis['overall_score']}/10
- 信心度: {technical_analysis['confidence_score']}%
- 有效指標: {', '.join(technical_analysis['effective_indicators'])}
- 分析摘要: {technical_analysis['summary']}
"""
        
        # 組合最終Prompt
        final_prompt = {
            'system_prompt': enhanced_prompt['system_prompt'],
            'user_prompt': f"""{enhanced_prompt['user_prompt']}

文章類型指導：
{post_type_guidance}

內容長度指導：
{content_length_guidance}

{technical_guidance}

個人化要求：
1. 嚴格按照 {request.kol_nickname} 的個人風格和語氣
2. 使用專屬詞彙和表達方式
3. 遵循固定的打字習慣和格式
4. 確保內容符合品質規範要求
5. 避免AI生成痕跡，要像真人發文
""",
            'generation_params': enhanced_prompt['generation_params'],
            'title': self._generate_personalized_title(request, kol_settings, post_type)
        }
        
        return final_prompt
    
    async def _generate_content_with_quality_control(self, prompt: Dict[str, Any], 
                                                   kol_settings: Dict[str, Any],
                                                   post_type: PostType,
                                                   content_length: ContentLength) -> str:
        """生成內容並進行品質控制"""
        
        max_retries = 3
        quality_threshold = kol_settings.get('quality_requirements', {}).get('min_score', 0.7)
        
        for attempt in range(max_retries):
            try:
                # 生成內容
                content = await self._call_openai_api(prompt)
                
                if not content:
                    continue
                
                # 品質檢查
                quality_score = await self._calculate_quality_score(content, kol_settings)
                
                if quality_score >= quality_threshold:
                    logger.info(f"✅ 內容品質檢查通過: {quality_score:.2f}")
                    return content
                else:
                    logger.warning(f"⚠️ 內容品質不足: {quality_score:.2f} < {quality_threshold}")
                    
                    # 調整Prompt參數
                    prompt = self._adjust_prompt_for_quality(prompt, quality_score, kol_settings)
                    
            except Exception as e:
                logger.error(f"❌ 內容生成失敗 (嘗試 {attempt + 1}): {e}")
                continue
        
        # 如果所有嘗試都失敗，返回最後一次生成的內容
        logger.warning("⚠️ 達到最大重試次數，使用最後生成的內容")
        return content or "內容生成失敗，請稍後再試。"
    
    async def _call_openai_api(self, prompt: Dict[str, Any]) -> str:
        """調用OpenAI API"""
        
        try:
            # 使用現有的OpenAI客戶端
            response = await self.content_generator.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompt['system_prompt']},
                    {"role": "user", "content": prompt['user_prompt']}
                ],
                temperature=prompt['generation_params'].get('temperature', 0.7),
                max_tokens=prompt['generation_params'].get('max_tokens', 1000)
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ OpenAI API調用失敗: {e}")
            return None
    
    async def _calculate_quality_score(self, content: str, kol_settings: Dict[str, Any]) -> float:
        """計算品質分數"""
        
        try:
            # 使用品質檢查器
            quality_result = await self.quality_checker.check_content_quality(content, kol_settings)
            
            # 計算綜合品質分數
            scores = []
            
            # 內容長度分數
            word_count = len(content)
            if 50 <= word_count <= 100:
                scores.append(0.9)  # 短文
            elif 200 <= word_count <= 300:
                scores.append(0.9)  # 中等長度
            elif 400 <= word_count <= 500:
                scores.append(0.9)  # 長文
            else:
                scores.append(0.5)  # 長度不符
            
            # 個人化分數
            personalization_score = self._calculate_personalization_score(content, kol_settings)
            scores.append(personalization_score)
            
            # 互動性分數
            interaction_score = self._calculate_interaction_score(content)
            scores.append(interaction_score)
            
            # 專業性分數
            professionalism_score = self._calculate_professionalism_score(content, kol_settings)
            scores.append(professionalism_score)
            
            # 計算平均分數
            return sum(scores) / len(scores)
            
        except Exception as e:
            logger.error(f"❌ 計算品質分數失敗: {e}")
            return 0.5
    
    def _calculate_personalization_score(self, content: str, kol_settings: Dict[str, Any]) -> float:
        """計算個人化分數"""
        
        score = 0.0
        
        # 檢查個人化表達
        personal_expressions = ["我認為", "我的看法", "我覺得", "我認為", "個人認為"]
        for expr in personal_expressions:
            if expr in content:
                score += 0.2
        
        # 檢查KOL專屬詞彙
        common_words = kol_settings.get('common_words', '').split(',')
        casual_words = kol_settings.get('casual_words', '').split(',')
        
        for word in common_words + casual_words:
            if word.strip() and word.strip() in content:
                score += 0.1
        
        # 檢查語氣風格
        tone_style = kol_settings.get('tone_style', '')
        if tone_style in content:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_interaction_score(self, content: str) -> float:
        """計算互動性分數"""
        
        interaction_indicators = ["？", "大家", "你們", "怎麼看", "覺得", "認為", "留言", "討論"]
        score = 0.0
        
        for indicator in interaction_indicators:
            score += content.count(indicator) * 0.1
        
        return min(score, 1.0)
    
    def _calculate_professionalism_score(self, content: str, kol_settings: Dict[str, Any]) -> float:
        """計算專業性分數"""
        
        score = 0.5  # 基礎分數
        
        # 檢查專業領域詞彙
        expertise = kol_settings.get('expertise', '')
        if expertise and expertise in content:
            score += 0.3
        
        # 檢查專業表達
        professional_expressions = ["分析", "評估", "建議", "觀察", "趨勢", "數據"]
        for expr in professional_expressions:
            if expr in content:
                score += 0.1
        
        return min(score, 1.0)
    
    def _get_post_type_guidance(self, post_type: PostType) -> str:
        """獲取文章類型指導"""
        
        guidance_map = {
            PostType.SHARE_OPINION: """
- 重點：分享個人觀點和看法
- 語氣：自信、有見地
- 結構：觀點 → 論據 → 結論
- 互動：適度引起討論
""",
            PostType.FIND_COMMUNITY: """
- 重點：尋找同溫層，引起共鳴
- 語氣：親切、共鳴
- 結構：情境描述 → 共同感受 → 邀請互動
- 互動：強烈互動引導
""",
            PostType.ASK_QUESTION: """
- 重點：提問問題引起互動
- 語氣：好奇、開放
- 結構：問題提出 → 背景說明 → 邀請回答
- 互動：直接提問
""",
            PostType.TEACHING: """
- 重點：教學分享知識
- 語氣：專業、耐心
- 結構：概念介紹 → 實例說明 → 應用建議
- 互動：鼓勵學習討論
""",
            PostType.NEWS_ALERT: """
- 重點：新聞快訊分享
- 語氣：即時、關注
- 結構：新聞摘要 → 個人解讀 → 影響分析
- 互動：詢問看法
""",
            PostType.ANALYSIS: """
- 重點：深度分析
- 語氣：理性、客觀
- 結構：數據呈現 → 分析過程 → 結論
- 互動：專業討論
""",
            PostType.HUMOR: """
- 重點：幽默風趣
- 語氣：輕鬆、有趣
- 結構：情境設定 → 幽默轉折 → 輕鬆結尾
- 互動：引起會心一笑
"""
        }
        
        return guidance_map.get(post_type, "")
    
    def _get_content_length_guidance(self, content_length: ContentLength) -> str:
        """獲取內容長度指導"""
        
        guidance_map = {
            ContentLength.SHORT: """
- 目標字數：50-100字
- 重點：簡潔有力，直擊要害
- 風格：快速決策，重點突出
- 適用：快訊、簡短觀點
""",
            ContentLength.MEDIUM: """
- 目標字數：200-300字
- 重點：平衡分析，完整論述
- 風格：結構完整，邏輯清晰
- 適用：一般分析、觀點分享
""",
            ContentLength.LONG: """
- 目標字數：400-500字
- 重點：深度分析，詳細展開
- 風格：論述豐富，專業深入
- 適用：深度分析、教學內容
"""
        }
        
        return guidance_map.get(content_length, "")
    
    def _generate_personalized_title(self, request: PersonalizedContentRequest, 
                                   kol_settings: Dict[str, Any],
                                   post_type: PostType) -> str:
        """生成個人化標題"""
        
        # 使用KOL的標題風格
        signature_openers = kol_settings.get('signature_openers', [])
        signature_patterns = kol_settings.get('signature_patterns', [])
        tail_word = kol_settings.get('tail_word', '')
        
        # 根據文章類型選擇標題風格
        if post_type == PostType.ASK_QUESTION:
            title_templates = [
                f"{random.choice(signature_openers) if signature_openers else '大家'}怎麼看{request.topic_title}？",
                f"{request.topic_title}，{random.choice(signature_patterns) if signature_patterns else '你們覺得呢'}？",
                f"關於{request.topic_title}，想問問{random.choice(signature_openers) if signature_openers else '大家'}的意見"
            ]
        elif post_type == PostType.SHARE_OPINION:
            title_templates = [
                f"{random.choice(signature_openers) if signature_openers else '我'}對{request.topic_title}的看法",
                f"{request.topic_title} - {random.choice(signature_patterns) if signature_patterns else '個人觀點'}",
                f"聊聊{request.topic_title}{tail_word}"
            ]
        else:
            title_templates = [
                f"{request.topic_title}{tail_word}",
                f"{random.choice(signature_openers) if signature_openers else '關於'}{request.topic_title}",
                f"{request.topic_title} - {random.choice(signature_patterns) if signature_patterns else '分析'}"
            ]
        
        return random.choice(title_templates)
    
    def _adjust_prompt_for_quality(self, prompt: Dict[str, Any], quality_score: float, 
                                  kol_settings: Dict[str, Any]) -> Dict[str, Any]:
        """根據品質分數調整Prompt"""
        
        # 調整溫度參數
        current_temp = prompt['generation_params'].get('temperature', 0.7)
        
        if quality_score < 0.5:
            # 品質太低，降低溫度增加穩定性
            new_temp = max(0.3, current_temp - 0.2)
        elif quality_score < 0.7:
            # 品質中等，微調溫度
            new_temp = max(0.4, current_temp - 0.1)
        else:
            # 品質還可以，保持或微調
            new_temp = min(0.9, current_temp + 0.1)
        
        prompt['generation_params']['temperature'] = new_temp
        
        # 添加品質改進指導
        quality_guidance = f"""
品質改進要求：
- 當前品質分數: {quality_score:.2f}
- 目標品質分數: 0.8以上
- 請加強個人化表達和專業性
- 確保內容符合KOL風格
"""
        
        prompt['user_prompt'] += quality_guidance
        
        return prompt
    
    def _parse_post_type_weights(self, kol_row: Dict[str, str]) -> Dict[PostType, float]:
        """解析文章類型權重"""
        
        weights_str = kol_row.get('PostTypeWeights', '')
        if not weights_str:
            return {}
        
        weights = {}
        for item in weights_str.split(','):
            if ':' in item:
                post_type_str, weight_str = item.split(':')
                try:
                    post_type = PostType(post_type_str.strip())
                    weight = float(weight_str.strip())
                    weights[post_type] = weight
                except (ValueError, KeyError):
                    continue
        
        return weights
    
    def _parse_content_length_weights(self, kol_row: Dict[str, str]) -> Dict[ContentLength, float]:
        """解析內容長度權重"""
        
        weights_str = kol_row.get('ContentLengthWeights', '')
        if not weights_str:
            return {}
        
        weights = {}
        for item in weights_str.split(','):
            if ':' in item:
                length_str, weight_str = item.split(':')
                try:
                    content_length = ContentLength(length_str.strip())
                    weight = float(weight_str.strip())
                    weights[content_length] = weight
                except (ValueError, KeyError):
                    continue
        
        return weights
    
    def _parse_quality_requirements(self, kol_row: Dict[str, str]) -> Dict[str, Any]:
        """解析品質要求"""
        
        return {
            'min_score': float(kol_row.get('MinQualityScore', '0.7')),
            'min_personalization': float(kol_row.get('MinPersonalizationScore', '0.6')),
            'min_interaction': float(kol_row.get('MinInteractionScore', '0.5')),
            'min_professionalism': float(kol_row.get('MinProfessionalismScore', '0.6'))
        }
    
    def _parse_personalization_requirements(self, kol_row: Dict[str, str]) -> Dict[str, Any]:
        """解析個人化要求"""
        
        return {
            'use_signature_words': kol_row.get('UseSignatureWords', 'TRUE').upper() == 'TRUE',
            'use_casual_expressions': kol_row.get('UseCasualExpressions', 'TRUE').upper() == 'TRUE',
            'follow_typing_habits': kol_row.get('FollowTypingHabits', 'TRUE').upper() == 'TRUE',
            'use_ending_style': kol_row.get('UseEndingStyle', 'TRUE').upper() == 'TRUE'
        }
    
    def _get_default_kol_settings(self, kol_nickname: str) -> Dict[str, Any]:
        """獲取預設KOL設定"""
        
        return {
            'nickname': kol_nickname,
            'persona': '一般',
            'content_length': 'medium',
            'question_ratio': 0.5,
            'interaction_starters': ['大家怎麼看', '你們覺得呢'],
            'ending_style': '歡迎討論',
            'post_type_weights': self.post_type_weights,
            'content_length_weights': self.content_length_weights,
            'quality_requirements': {
                'min_score': 0.7,
                'min_personalization': 0.6,
                'min_interaction': 0.5,
                'min_professionalism': 0.6
            },
            'personalization_requirements': {
                'use_signature_words': True,
                'use_casual_expressions': True,
                'follow_typing_habits': True,
                'use_ending_style': True
            }
        }

# 測試函數
async def test_personalized_content_generator():
    """測試個人化內容生成器"""
    
    print("🧪 測試個人化內容生成器")
    
    try:
        generator = PersonalizedContentGenerator()
        
        # 測試請求
        request = PersonalizedContentRequest(
            kol_nickname="川川哥",
            topic_title="台積電漲停分析",
            topic_keywords="台積電,2330,漲停,技術分析",
            trigger_type="limit_up",
            stock_data={
                'stock_id': '2330',
                'stock_name': '台積電',
                'price': 580.0,
                'change_percent': 9.8
            }
        )
        
        # 生成內容
        result = await generator.generate_personalized_content(request)
        
        if result:
            print(f"✅ 內容生成成功!")
            print(f"   標題: {result.title}")
            print(f"   文章類型: {result.post_type.value}")
            print(f"   內容長度: {result.content_length.value}")
            print(f"   字數: {result.word_count}")
            print(f"   品質分數: {result.quality_score:.2f}")
            print(f"   個人化分數: {result.personalization_score:.2f}")
            print(f"   內容預覽: {result.content[:100]}...")
        else:
            print("❌ 內容生成失敗")
    
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_personalized_content_generator())


