"""
增強版自我學習API
包含高成效特徵分析、LLM內容分類、自動發文設定生成
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import asyncio
from dataclasses import dataclass, asdict
import statistics
import re
import openai
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enhanced-self-learning", tags=["enhanced-self-learning"])

# ==================== 數據模型 ====================

class HighPerformanceFeature(BaseModel):
    feature_id: str
    feature_name: str
    feature_type: str  # 'content', 'timing', 'structure', 'interaction', 'kol'
    description: str
    frequency_in_top_posts: float  # 在前10%貼文中的出現頻率
    frequency_in_all_posts: float   # 在所有貼文中的出現頻率
    improvement_potential: float    # 改善潛力分數
    setting_key: str               # 對應的設定鍵名
    is_modifiable: bool            # 是否可修改
    modification_method: str       # 修改方法
    examples: List[str]           # 範例

class ContentCategory(BaseModel):
    category_id: str
    category_name: str
    description: str
    top_posts: List[Dict[str, Any]]
    avg_performance_score: float
    key_characteristics: List[str]
    success_rate: float

class PostingSetting(BaseModel):
    setting_id: str
    setting_name: str
    description: str
    trigger_type: str              # 'limit_up', 'limit_down', 'volume_surge', 'news_event'
    content_length: str           # 'short', 'medium', 'long'
    has_news_link: bool
    has_question_interaction: bool
    has_emoji: bool
    has_hashtag: bool
    humor_level: str              # 'none', 'light', 'moderate', 'strong'
    kol_style: str                # 'professional', 'casual', 'humorous', 'analytical'
    posting_time_preference: List[str]
    stock_tags_count: int
    content_structure: str        # 'narrative', 'bullet_points', 'mixed'
    interaction_elements: List[str]
    expected_performance: float
    confidence_level: float
    based_on_features: List[str]

class EnhancedAnalysisReport(BaseModel):
    analysis_timestamp: str
    total_posts_analyzed: int
    top_performance_features: List[HighPerformanceFeature]
    content_categories: List[ContentCategory]
    generated_settings: List[PostingSetting]
    modification_capabilities: Dict[str, Any]
    recommendations: List[str]

# ==================== LLM 內容分類服務 ====================

class LLMContentClassifier:
    def __init__(self):
        # 設置 OpenAI API (如果可用)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.use_openai = bool(self.openai_api_key)
        
        # 預定義的分類標準
        self.classification_criteria = {
            'content_type': ['分析型', '新聞型', '互動型', '幽默型', '專業型'],
            'tone': ['正式', '輕鬆', '幽默', '專業', '親切'],
            'structure': ['敘述型', '條列型', '問答型', '混合型'],
            'interaction_level': ['高互動', '中互動', '低互動'],
            'complexity': ['簡單', '中等', '複雜']
        }
    
    async def classify_content(self, content: str) -> Dict[str, str]:
        """使用LLM或規則分類內容"""
        if self.use_openai:
            return await self._classify_with_openai(content)
        else:
            return await self._classify_with_rules(content)
    
    async def _classify_with_openai(self, content: str) -> Dict[str, str]:
        """使用OpenAI API分類"""
        try:
            prompt = f"""
            請分析以下貼文內容，並按照以下標準進行分類：

            內容類型: 分析型、新聞型、互動型、幽默型、專業型
            語調: 正式、輕鬆、幽默、專業、親切
            結構: 敘述型、條列型、問答型、混合型
            互動程度: 高互動、中互動、低互動
            複雜度: 簡單、中等、複雜

            貼文內容: {content}

            請以JSON格式返回分類結果。
            """
            
            # 這裡應該調用OpenAI API
            # 暫時返回模擬結果
            return {
                'content_type': '分析型',
                'tone': '專業',
                'structure': '混合型',
                'interaction_level': '中互動',
                'complexity': '中等'
            }
        except Exception as e:
            logger.error(f"OpenAI分類失敗: {e}")
            return await self._classify_with_rules(content)
    
    async def _classify_with_rules(self, content: str) -> Dict[str, str]:
        """使用規則分類內容"""
        classifications = {}
        
        # 內容類型分類
        if any(keyword in content for keyword in ['分析', '技術', '指標', '趨勢']):
            classifications['content_type'] = '分析型'
        elif any(keyword in content for keyword in ['新聞', '報導', '消息']):
            classifications['content_type'] = '新聞型'
        elif any(keyword in content for keyword in ['？', '?', '大家', '你們']):
            classifications['content_type'] = '互動型'
        elif any(keyword in content for keyword in ['哈哈', '笑死', '搞笑', '😂']):
            classifications['content_type'] = '幽默型'
        else:
            classifications['content_type'] = '專業型'
        
        # 語調分類
        if any(keyword in content for keyword in ['哈哈', '笑死', '搞笑', '😂', '😄']):
            classifications['tone'] = '幽默'
        elif any(keyword in content for keyword in ['大家', '你們', '我們', '一起']):
            classifications['tone'] = '親切'
        elif any(keyword in content for keyword in ['分析', '數據', '指標', '技術']):
            classifications['tone'] = '專業'
        elif any(keyword in content for keyword in ['不錯', '還好', '還可以']):
            classifications['tone'] = '輕鬆'
        else:
            classifications['tone'] = '正式'
        
        # 結構分類
        if content.count('•') > 2 or content.count('-') > 2:
            classifications['structure'] = '條列型'
        elif content.count('？') > 1 or content.count('?') > 1:
            classifications['structure'] = '問答型'
        elif len(content.split('\n')) > 3:
            classifications['structure'] = '混合型'
        else:
            classifications['structure'] = '敘述型'
        
        # 互動程度分類
        interaction_elements = content.count('？') + content.count('?') + content.count('！') + content.count('!')
        if interaction_elements > 3:
            classifications['interaction_level'] = '高互動'
        elif interaction_elements > 1:
            classifications['interaction_level'] = '中互動'
        else:
            classifications['interaction_level'] = '低互動'
        
        # 複雜度分類
        if len(content) > 500:
            classifications['complexity'] = '複雜'
        elif len(content) > 200:
            classifications['complexity'] = '中等'
        else:
            classifications['complexity'] = '簡單'
        
        return classifications

# ==================== 高成效特徵分析服務 ====================

class HighPerformanceFeatureAnalyzer:
    def __init__(self):
        self.feature_definitions = {
            # 內容特徵
            'content_length_short': {'name': '短內容', 'type': 'content', 'setting_key': 'content_length'},
            'content_length_medium': {'name': '中等內容', 'type': 'content', 'setting_key': 'content_length'},
            'content_length_long': {'name': '長內容', 'type': 'content', 'setting_key': 'content_length'},
            'has_stock_analysis': {'name': '股票分析', 'type': 'content', 'setting_key': 'include_analysis'},
            'has_technical_indicators': {'name': '技術指標', 'type': 'content', 'setting_key': 'include_technical'},
            'has_market_outlook': {'name': '市場展望', 'type': 'content', 'setting_key': 'include_outlook'},
            'has_risk_warning': {'name': '風險提醒', 'type': 'content', 'setting_key': 'include_risk'},
            
            # 結構特徵
            'has_bullet_points': {'name': '條列式結構', 'type': 'structure', 'setting_key': 'content_structure'},
            'has_numbered_list': {'name': '編號列表', 'type': 'structure', 'setting_key': 'content_structure'},
            'has_paragraphs': {'name': '段落結構', 'type': 'structure', 'setting_key': 'content_structure'},
            'has_headings': {'name': '標題結構', 'type': 'structure', 'setting_key': 'content_structure'},
            
            # 互動特徵
            'has_question': {'name': '問句互動', 'type': 'interaction', 'setting_key': 'include_questions'},
            'has_poll': {'name': '投票互動', 'type': 'interaction', 'setting_key': 'include_poll'},
            'has_call_to_action': {'name': '行動呼籲', 'type': 'interaction', 'setting_key': 'include_cta'},
            'has_emoji': {'name': '表情符號', 'type': 'interaction', 'setting_key': 'include_emoji'},
            'has_hashtag': {'name': '標籤使用', 'type': 'interaction', 'setting_key': 'include_hashtag'},
            
            # 時間特徵
            'morning_posting': {'name': '上午發文', 'type': 'timing', 'setting_key': 'preferred_time'},
            'afternoon_posting': {'name': '下午發文', 'type': 'timing', 'setting_key': 'preferred_time'},
            'evening_posting': {'name': '晚上發文', 'type': 'timing', 'setting_key': 'preferred_time'},
            'weekend_posting': {'name': '週末發文', 'type': 'timing', 'setting_key': 'preferred_time'},
            
            # KOL特徵
            'professional_tone': {'name': '專業語調', 'type': 'kol', 'setting_key': 'kol_style'},
            'casual_tone': {'name': '輕鬆語調', 'type': 'kol', 'setting_key': 'kol_style'},
            'humorous_tone': {'name': '幽默語調', 'type': 'kol', 'setting_key': 'kol_style'},
            'analytical_tone': {'name': '分析語調', 'type': 'kol', 'setting_key': 'kol_style'},
        }
    
    async def analyze_features(self, posts: List[Dict]) -> List[HighPerformanceFeature]:
        """分析高成效特徵"""
        if not posts:
            return []
        
        # 計算每篇貼文的成效分數
        scored_posts = []
        for post in posts:
            score = self._calculate_performance_score(post)
            scored_posts.append((post, score))
        
        # 按分數排序
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        
        # 取前20%
        total_posts = len(scored_posts)
        top20_count = max(1, int(total_posts * 0.2))
        top20_posts = [post for post, score in scored_posts[:top20_count]]
        all_posts = [post for post, score in scored_posts]
        
        # 分析每個特徵
        features = []
        for feature_id, feature_info in self.feature_definitions.items():
            feature = await self._analyze_single_feature(
                feature_id, feature_info, top20_posts, all_posts
            )
            if feature:
                features.append(feature)
        
        # 按改善潛力排序
        features.sort(key=lambda x: x.improvement_potential, reverse=True)
        
        return features[:20]  # 返回前20個特徵
    
    def _calculate_performance_score(self, post: Dict) -> float:
        """計算貼文成效分數"""
        total_interactions = (post.get('likes', 0) or 0) + (post.get('comments', 0) or 0) + (post.get('shares', 0) or 0) + (post.get('views', 0) or 0) + (post.get('donations', 0) or 0)
        engagement_rate = post.get('engagement_rate', 0)
        
        # 綜合分數計算
        interaction_score = min(total_interactions / 100, 1.0) * 40
        engagement_score = min(engagement_rate / 10, 1.0) * 30
        content_score = self._assess_content_quality(post) * 20
        timing_score = self._assess_timing_score(post) * 10
        
        return interaction_score + engagement_score + content_score + timing_score
    
    def _assess_content_quality(self, post: Dict) -> float:
        """評估內容品質"""
        title = post.get('title', '')
        content = post.get('content', '')
        full_text = f"{title} {content}"
        
        quality_score = 0.5
        
        # 內容長度適中
        if 100 <= len(content) <= 800:
            quality_score += 0.1
        
        # 包含股票標記
        if post.get('commodity_tags'):
            quality_score += 0.1
        
        # 包含互動元素
        if any(keyword in full_text for keyword in ['？', '?', '！', '!']):
            quality_score += 0.1
        
        # 包含Emoji
        if any(emoji in full_text for emoji in ['😂', '😄', '😆', '👍', '👏']):
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _assess_timing_score(self, post: Dict) -> float:
        """評估發文時機分數"""
        create_time = post.get('create_time', '')
        if not create_time:
            return 0.5
        
        try:
            post_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
            hour = post_time.hour
            
            if 9 <= hour <= 11 or 19 <= hour <= 21:
                return 1.0
            elif 14 <= hour <= 16:
                return 0.8
            else:
                return 0.4
        except:
            return 0.5
    
    async def _analyze_single_feature(self, feature_id: str, feature_info: Dict, top20_posts: List[Dict], all_posts: List[Dict]) -> Optional[HighPerformanceFeature]:
        """分析單個特徵"""
        feature_name = feature_info['name']
        feature_type = feature_info['type']
        setting_key = feature_info['setting_key']
        
        # 計算特徵在前20%貼文中的頻率
        top20_count = self._count_feature_occurrence(feature_id, top20_posts)
        top20_frequency = top20_count / len(top20_posts) if top20_posts else 0
        
        # 計算特徵在所有貼文中的頻率
        all_count = self._count_feature_occurrence(feature_id, all_posts)
        all_frequency = all_count / len(all_posts) if all_posts else 0
        
        # 計算改善潛力
        improvement_potential = top20_frequency - all_frequency
        
        # 只返回有改善潛力的特徵
        if improvement_potential <= 0:
            return None
        
        # 判斷是否可修改
        is_modifiable, modification_method = self._assess_modifiability(feature_id, setting_key)
        
        # 生成範例
        examples = self._generate_examples(feature_id, top20_posts)
        
        return HighPerformanceFeature(
            feature_id=feature_id,
            feature_name=feature_name,
            feature_type=feature_type,
            description=f"{feature_name}在高成效貼文中出現頻率較高",
            frequency_in_top_posts=top20_frequency,
            frequency_in_all_posts=all_frequency,
            improvement_potential=improvement_potential,
            setting_key=setting_key,
            is_modifiable=is_modifiable,
            modification_method=modification_method,
            examples=examples
        )
    
    def _count_feature_occurrence(self, feature_id: str, posts: List[Dict]) -> int:
        """計算特徵出現次數"""
        count = 0
        
        for post in posts:
            title = post.get('title', '')
            content = post.get('content', '')
            full_text = f"{title} {content}"
            create_time = post.get('create_time', '')
            
            if feature_id == 'content_length_short' and len(content) < 200:
                count += 1
            elif feature_id == 'content_length_medium' and 200 <= len(content) <= 500:
                count += 1
            elif feature_id == 'content_length_long' and len(content) > 500:
                count += 1
            elif feature_id == 'has_stock_analysis' and any(keyword in full_text for keyword in ['分析', '技術', '指標']):
                count += 1
            elif feature_id == 'has_technical_indicators' and any(keyword in full_text for keyword in ['MA', 'RSI', 'MACD', 'KD']):
                count += 1
            elif feature_id == 'has_question' and ('？' in full_text or '?' in full_text):
                count += 1
            elif feature_id == 'has_emoji' and any(emoji in full_text for emoji in ['😂', '😄', '😆', '👍', '👏']):
                count += 1
            elif feature_id == 'has_hashtag' and '#' in full_text:
                count += 1
            elif feature_id == 'has_bullet_points' and ('•' in content or '-' in content):
                count += 1
            elif feature_id == 'morning_posting' and create_time:
                try:
                    post_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                    if 6 <= post_time.hour < 12:
                        count += 1
                except:
                    pass
            elif feature_id == 'afternoon_posting' and create_time:
                try:
                    post_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                    if 12 <= post_time.hour < 18:
                        count += 1
                except:
                    pass
            elif feature_id == 'evening_posting' and create_time:
                try:
                    post_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                    if 18 <= post_time.hour < 24:
                        count += 1
                except:
                    pass
            # 可以繼續添加更多特徵檢測邏輯
        
        return count
    
    def _assess_modifiability(self, feature_id: str, setting_key: str) -> tuple[bool, str]:
        """評估特徵的可修改性"""
        modifiable_features = {
            'content_length_short': (True, '調整內容生成長度設定'),
            'content_length_medium': (True, '調整內容生成長度設定'),
            'content_length_long': (True, '調整內容生成長度設定'),
            'has_question': (True, '在內容生成中加入問句'),
            'has_emoji': (True, '在內容生成中加入表情符號'),
            'has_hashtag': (True, '在內容生成中加入標籤'),
            'has_bullet_points': (True, '調整內容結構為條列式'),
            'morning_posting': (True, '調整發文時間偏好'),
            'afternoon_posting': (True, '調整發文時間偏好'),
            'evening_posting': (True, '調整發文時間偏好'),
        }
        
        return modifiable_features.get(feature_id, (False, '暫無修改方法'))
    
    def _generate_examples(self, feature_id: str, top10_posts: List[Dict]) -> List[str]:
        """生成特徵範例"""
        examples = []
        
        for post in top10_posts[:3]:  # 取前3個範例
            title = post.get('title', '')
            content = post.get('content', '')
            
            if feature_id == 'has_question' and ('？' in content or '?' in content):
                examples.append(f"標題: {title[:50]}...")
            elif feature_id == 'has_emoji' and any(emoji in content for emoji in ['😂', '😄', '😆']):
                examples.append(f"標題: {title[:50]}...")
            elif feature_id == 'content_length_medium' and 200 <= len(content) <= 500:
                examples.append(f"標題: {title[:50]}...")
        
        return examples

# ==================== 自動發文設定生成服務 ====================

class PostingSettingGenerator:
    def __init__(self):
        self.setting_templates = {
            'high_interaction': {
                'trigger_type': 'limit_up',
                'content_length': 'medium',
                'has_question_interaction': True,
                'has_emoji': True,
                'humor_level': 'light',
                'kol_style': 'casual'
            },
            'professional_analysis': {
                'trigger_type': 'volume_surge',
                'content_length': 'long',
                'has_news_link': True,
                'has_question_interaction': False,
                'humor_level': 'none',
                'kol_style': 'professional'
            },
            'humorous_engagement': {
                'trigger_type': 'limit_down',
                'content_length': 'short',
                'has_emoji': True,
                'has_hashtag': True,
                'humor_level': 'strong',
                'kol_style': 'humorous'
            }
        }
    
    async def generate_settings(self, features: List[HighPerformanceFeature], categories: List[ContentCategory]) -> List[PostingSetting]:
        """生成多種發文設定"""
        settings = []
        
        # 基於高成效特徵生成設定
        feature_based_settings = await self._generate_feature_based_settings(features)
        settings.extend(feature_based_settings)
        
        # 基於內容分類生成設定
        category_based_settings = await self._generate_category_based_settings(categories)
        settings.extend(category_based_settings)
        
        # 生成組合設定
        combination_settings = await self._generate_combination_settings(features, categories)
        settings.extend(combination_settings)
        
        return settings
    
    async def _generate_feature_based_settings(self, features: List[HighPerformanceFeature]) -> List[PostingSetting]:
        """基於特徵生成設定"""
        settings = []
        
        # 選擇前5個最有潛力的特徵
        top_features = features[:5]
        
        for i, feature in enumerate(top_features):
            setting = PostingSetting(
                setting_id=f'feature_based_{i+1}',
                setting_name=f'基於{feature.feature_name}的設定',
                description=f'基於{feature.feature_name}特徵優化的發文設定',
                trigger_type='limit_up',
                content_length='medium',
                has_news_link=False,
                has_question_interaction=feature.feature_id == 'has_question',
                has_emoji=feature.feature_id == 'has_emoji',
                has_hashtag=feature.feature_id == 'has_hashtag',
                humor_level='light',
                kol_style='casual',
                posting_time_preference=['14:00-16:00', '19:00-21:00'],
                stock_tags_count=2,
                content_structure='mixed',
                interaction_elements=['question', 'emoji'] if feature.feature_id == 'has_question' else ['emoji'],
                expected_performance=70 + (feature.improvement_potential * 10),
                confidence_level=0.8,
                based_on_features=[feature.feature_name]
            )
            settings.append(setting)
        
        return settings
    
    async def _generate_category_based_settings(self, categories: List[ContentCategory]) -> List[PostingSetting]:
        """基於內容分類生成設定"""
        settings = []
        
        for i, category in enumerate(categories[:3]):  # 取前3個分類
            setting = PostingSetting(
                setting_id=f'category_based_{i+1}',
                setting_name=f'基於{category.category_name}的設定',
                description=f'基於{category.category_name}分類優化的發文設定',
                trigger_type='volume_surge',
                content_length='long' if category.avg_performance_score > 80 else 'medium',
                has_news_link=True,
                has_question_interaction='互動型' in category.key_characteristics,
                has_emoji='幽默型' in category.key_characteristics,
                has_hashtag=True,
                humor_level='strong' if '幽默型' in category.key_characteristics else 'light',
                kol_style='professional' if '專業型' in category.key_characteristics else 'casual',
                posting_time_preference=['09:00-11:00', '15:00-17:00'],
                stock_tags_count=3,
                content_structure='mixed',
                interaction_elements=['question', 'emoji', 'hashtag'],
                expected_performance=category.avg_performance_score,
                confidence_level=0.75,
                based_on_features=category.key_characteristics
            )
            settings.append(setting)
        
        return settings
    
    async def _generate_combination_settings(self, features: List[HighPerformanceFeature], categories: List[ContentCategory]) -> List[PostingSetting]:
        """生成組合設定"""
        settings = []
        
        # 生成不同觸發器類型的設定
        trigger_types = ['limit_up', 'limit_down', 'volume_surge', 'news_event']
        
        for i, trigger_type in enumerate(trigger_types):
            setting = PostingSetting(
                setting_id=f'combination_{i+1}',
                setting_name=f'{trigger_type}觸發器設定',
                description=f'針對{trigger_type}觸發器優化的綜合設定',
                trigger_type=trigger_type,
                content_length='medium',
                has_news_link=trigger_type == 'news_event',
                has_question_interaction=True,
                has_emoji=True,
                has_hashtag=True,
                humor_level='moderate',
                kol_style='casual',
                posting_time_preference=['14:00-16:00', '19:00-21:00'],
                stock_tags_count=2,
                content_structure='mixed',
                interaction_elements=['question', 'emoji', 'hashtag'],
                expected_performance=75,
                confidence_level=0.7,
                based_on_features=['綜合優化']
            )
            settings.append(setting)
        
        return settings

# ==================== 全局服務實例 ====================

llm_classifier = LLMContentClassifier()
feature_analyzer = HighPerformanceFeatureAnalyzer()
setting_generator = PostingSettingGenerator()

# ==================== API 端點 ====================

@router.get("/enhanced-analysis")
async def get_enhanced_analysis(
    kol_serial: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_external: bool = True
):
    """獲取增強版自我學習分析"""
    try:
        # 這裡應該從實際數據源獲取貼文數據
        # 暫時使用模擬數據
        mock_posts = [
            {
                'post_id': '1',
                'article_id': 'A001',
                'kol_nickname': '龜狗一日散戶',
                'title': '2330台積電技術分析',
                'content': '今天來分析一下台積電的技術指標，RSI已經超買，MACD也出現背離信號，大家覺得會回調嗎？',
                'create_time': '2024-12-19T10:00:00Z',
                'likes': 50,
                'comments': 20,
                'shares': 10,
                'bookmarks': 5,
                'engagement_rate': 8.5,
                'source': 'system',
                'commodity_tags': [{'key': '2330', 'type': 'stock', 'bullOrBear': '0'}]
            },
            {
                'post_id': '2',
                'article_id': 'A002',
                'kol_nickname': '板橋大who',
                'title': '2317鴻海漲停分析',
                'content': '鴻海今天漲停了！主要原因是AI伺服器訂單增加，未來展望看好。大家有買嗎？',
                'create_time': '2024-12-19T14:00:00Z',
                'likes': 80,
                'comments': 30,
                'shares': 15,
                'bookmarks': 8,
                'engagement_rate': 12.3,
                'source': 'system',
                'commodity_tags': [{'key': '2317', 'type': 'stock', 'bullOrBear': '0'}]
            }
        ]
        
        # 分析高成效特徵
        top_features = await feature_analyzer.analyze_features(mock_posts)
        
        # LLM內容分類
        categories = []
        for post in mock_posts:
            classification = await llm_classifier.classify_content(post['content'])
            # 這裡應該將分類結果組織成ContentCategory對象
            # 暫時跳過詳細實現
        
        # 生成發文設定
        generated_settings = await setting_generator.generate_settings(top_features, categories)
        
        # 生成修改能力報告
        modification_capabilities = {
            'modifiable_features': len([f for f in top_features if f.is_modifiable]),
            'total_features': len(top_features),
            'modification_methods': list(set([f.modification_method for f in top_features if f.is_modifiable])),
            'unmodifiable_features': [f.feature_name for f in top_features if not f.is_modifiable]
        }
        
        # 生成建議
        recommendations = [
            '建議優先調整可修改的高成效特徵',
            '結合多個特徵生成綜合發文設定',
            '定期更新特徵分析以保持效果',
            '測試不同設定組合的實際效果'
        ]
        
        report = EnhancedAnalysisReport(
            analysis_timestamp=datetime.now().isoformat(),
            total_posts_analyzed=len(mock_posts),
            top_performance_features=top_features,
            content_categories=categories,
            generated_settings=generated_settings,
            modification_capabilities=modification_capabilities,
            recommendations=recommendations
        )
        
        return {
            "success": True,
            "data": report.dict()
        }
        
    except Exception as e:
        logger.error(f"獲取增強版分析失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取增強版分析失敗: {str(e)}")

@router.post("/generate-settings")
async def generate_posting_settings(
    features: List[str],
    categories: List[str],
    trigger_types: List[str]
):
    """生成發文設定"""
    try:
        # 這裡應該基於傳入的參數生成設定
        # 暫時返回模擬設定
        settings = [
            {
                'setting_id': 'generated_1',
                'setting_name': '高互動設定',
                'description': '基於高互動特徵生成的設定',
                'trigger_type': 'limit_up',
                'content_length': 'medium',
                'has_news_link': True,
                'has_question_interaction': True,
                'has_emoji': True,
                'expected_performance': 85,
                'confidence_level': 0.8
            }
        ]
        
        return {
            "success": True,
            "data": settings
        }
        
    except Exception as e:
        logger.error(f"生成發文設定失敗: {e}")
        raise HTTPException(status_code=500, detail=f"生成發文設定失敗: {str(e)}")

@router.get("/modification-capabilities")
async def get_modification_capabilities():
    """獲取修改能力報告"""
    try:
        capabilities = {
            'modifiable_settings': [
                'content_length',
                'include_questions',
                'include_emoji',
                'include_hashtag',
                'content_structure',
                'preferred_time',
                'kol_style'
            ],
            'unmodifiable_settings': [
                'market_conditions',
                'stock_fundamentals',
                'external_events'
            ],
            'modification_methods': [
                '調整內容生成參數',
                '修改發文時間偏好',
                '更新KOL風格設定',
                '調整互動元素配置'
            ]
        }
        
        return {
            "success": True,
            "data": capabilities
        }
        
    except Exception as e:
        logger.error(f"獲取修改能力失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取修改能力失敗: {str(e)}")

