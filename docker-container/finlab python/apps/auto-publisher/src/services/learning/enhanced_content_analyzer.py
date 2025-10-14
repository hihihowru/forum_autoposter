"""
增強版內容分析器
基於實際範例分析的高互動內容特徵
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import numpy as np
from collections import Counter
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class EnhancedContentFeatures:
    """增強版內容特徵"""
    content_id: str
    content: str
    
    # 高互動特徵 (基於範例分析)
    personal_score: float          # 個人化表達分數
    emotion_score: float           # 情感表達分數
    interaction_score: float       # 互動引導分數
    creative_score: float          # 創意表達分數
    humor_score: float             # 幽默元素分數
    direct_answer_score: float     # 直接回答分數
    structure_score: float         # 結構化分數
    
    # 計算指標
    total_engagement_score: float
    engagement_level: str          # 'high', 'medium', 'low'
    
    # 詳細分析
    personal_pronouns: List[str]
    emotion_words: List[str]
    questions: List[str]
    creative_elements: List[str]
    humor_elements: List[str]
    
    analyzed_at: datetime

@dataclass
class ContentOptimization:
    """內容優化建議"""
    content_id: str
    current_score: float
    target_score: float
    improvement_potential: float
    specific_recommendations: List[str]
    priority_actions: List[str]
    expected_improvement: float

class EnhancedContentAnalyzer:
    """增強版內容分析器"""
    
    def __init__(self):
        # 基於範例分析的高互動特徵詞典
        self.personal_pronouns = [
            "我", "我的", "我們", "我們的", "你", "你的", "你們", "你們的",
            "他", "他的", "她", "她的", "他們", "她們", "自己", "本人", "個人"
        ]
        
        self.emotion_words = [
            "不知道", "拜託", "期待", "希望", "擔心", "開心", "難過", "興奮",
            "驚訝", "憤怒", "害怕", "焦慮", "緊張", "放鬆", "滿意", "失望",
            "驚喜", "感動", "感謝", "喜歡", "討厭", "愛", "恨"
        ]
        
        self.interaction_words = [
            "你覺得", "你認為", "你怎麼看", "你覺得呢", "你認為呢",
            "留言", "分享", "按讚", "追蹤", "訂閱", "關注", "加入",
            "參與", "討論", "交流", "互動", "回覆", "評論", "告訴我"
        ]
        
        self.creative_elements = [
            "🔥", "❤️", "😊", "😄", "😅", "😂", "🤣", "😎", "😍", "🥰", "😘",
            "💪", "👍", "👏", "🎉", "🚀", "💯", "⭐", "✨", "💎", "🎯"
        ]
        
        self.humor_elements = [
            "神仙打架", "火焰冰塊", "膠著狀態", "暈頭轉向", "趴趴走",
            "真的假的", "太扯了", "太誇張", "太猛了", "笑死", "笑爛",
            "笑爆", "笑翻", "GG", "gg", "爽", "爽爆", "爽翻", "嗨", "嗨翻"
        ]
        
        self.direct_answer_indicators = [
            "如標題", "很多人再問", "是什麼意思", "大體來說", "原因是在於",
            "至於說", "我也不知道", "坦白說", "簡單來說", "總結來說"
        ]
        
        # 高互動模式基準 (基於範例分析)
        self.high_engagement_threshold = 0.7
        self.medium_engagement_threshold = 0.4
        
        # 各特徵的權重 (基於範例分析結果)
        self.feature_weights = {
            'personal': 0.20,      # 個人化表達
            'emotion': 0.15,       # 情感表達
            'interaction': 0.20,   # 互動引導
            'creative': 0.20,      # 創意表達
            'humor': 0.15,         # 幽默元素
            'direct_answer': 0.05, # 直接回答
            'structure': 0.05      # 結構化
        }
    
    async def analyze_content(self, content: str, content_id: str = None) -> EnhancedContentFeatures:
        """
        分析內容的高互動特徵
        
        Args:
            content: 要分析的內容
            content_id: 內容ID
            
        Returns:
            增強版內容特徵
        """
        try:
            # 分析各項特徵
            personal_score, personal_pronouns = self._analyze_personal_expression(content)
            emotion_score, emotion_words = self._analyze_emotion_expression(content)
            interaction_score, questions = self._analyze_interaction_guidance(content)
            creative_score, creative_elements = self._analyze_creative_expression(content)
            humor_score, humor_elements = self._analyze_humor_elements(content)
            direct_answer_score = self._analyze_direct_answer(content)
            structure_score = self._analyze_structure(content)
            
            # 計算總分
            total_score = (
                personal_score * self.feature_weights['personal'] +
                emotion_score * self.feature_weights['emotion'] +
                interaction_score * self.feature_weights['interaction'] +
                creative_score * self.feature_weights['creative'] +
                humor_score * self.feature_weights['humor'] +
                direct_answer_score * self.feature_weights['direct_answer'] +
                structure_score * self.feature_weights['structure']
            )
            
            # 確定互動等級
            if total_score >= self.high_engagement_threshold:
                engagement_level = "high"
            elif total_score >= self.medium_engagement_threshold:
                engagement_level = "medium"
            else:
                engagement_level = "low"
            
            return EnhancedContentFeatures(
                content_id=content_id or f"content_{datetime.now().timestamp()}",
                content=content,
                personal_score=personal_score,
                emotion_score=emotion_score,
                interaction_score=interaction_score,
                creative_score=creative_score,
                humor_score=humor_score,
                direct_answer_score=direct_answer_score,
                structure_score=structure_score,
                total_engagement_score=total_score,
                engagement_level=engagement_level,
                personal_pronouns=personal_pronouns,
                emotion_words=emotion_words,
                questions=questions,
                creative_elements=creative_elements,
                humor_elements=humor_elements,
                analyzed_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"增強版內容分析失敗: {e}")
            raise
    
    def _analyze_personal_expression(self, content: str) -> Tuple[float, List[str]]:
        """分析個人化表達"""
        found_pronouns = []
        for pronoun in self.personal_pronouns:
            if pronoun in content:
                found_pronouns.append(pronoun)
        
        # 基於範例分析：高互動內容通常有2-4個個人代詞
        score = min(len(found_pronouns) * 0.25, 1.0)
        return score, found_pronouns
    
    def _analyze_emotion_expression(self, content: str) -> Tuple[float, List[str]]:
        """分析情感表達"""
        found_emotions = []
        for emotion in self.emotion_words:
            if emotion in content:
                found_emotions.append(emotion)
        
        # 基於範例分析：高互動內容通常有1-3個情感詞彙
        score = min(len(found_emotions) * 0.3, 1.0)
        return score, found_emotions
    
    def _analyze_interaction_guidance(self, content: str) -> Tuple[float, List[str]]:
        """分析互動引導"""
        # 問題數量
        questions = re.findall(r'[？?]', content)
        
        # 互動詞彙
        found_interactions = []
        for word in self.interaction_words:
            if word in content:
                found_interactions.append(word)
        
        # 基於範例分析：高互動內容通常有1-2個問題或互動詞彙
        question_score = min(len(questions) * 0.3, 0.6)
        interaction_score = min(len(found_interactions) * 0.2, 0.4)
        
        total_score = min(question_score + interaction_score, 1.0)
        return total_score, questions
    
    def _analyze_creative_expression(self, content: str) -> Tuple[float, List[str]]:
        """分析創意表達"""
        found_creatives = []
        for element in self.creative_elements:
            if element in content:
                found_creatives.append(element)
        
        # 基於範例分析：高互動內容通常有1-3個表情符號（限制最多3個）
        emoji_count = min(len(found_creatives), 3)  # 限制最多3個emoji
        score = min(emoji_count * 0.33, 1.0)
        return score, found_creatives
    
    def _analyze_humor_elements(self, content: str) -> Tuple[float, List[str]]:
        """分析幽默元素"""
        found_humors = []
        for element in self.humor_elements:
            if element in content:
                found_humors.append(element)
        
        # 基於範例分析：高互動內容通常有1-2個幽默元素
        score = min(len(found_humors) * 0.4, 1.0)
        return score, found_humors
    
    def _analyze_direct_answer(self, content: str) -> float:
        """分析直接回答"""
        found_indicators = 0
        for indicator in self.direct_answer_indicators:
            if indicator in content:
                found_indicators += 1
        
        # 基於範例分析：直接回答問題的內容互動較高
        score = min(found_indicators * 0.3, 1.0)
        return score
    
    def _analyze_structure(self, content: str) -> float:
        """分析結構化"""
        score = 0.0
        
        # 分點說明
        if re.search(r'\d+、', content):
            score += 0.4
        
        # 段落結構
        paragraphs = len([p for p in content.split('\n') if p.strip()])
        if 2 <= paragraphs <= 6:
            score += 0.3
        
        # 總結性表達
        summary_words = ["以上", "總結", "結論", "總之", "簡單來說"]
        if any(word in content for word in summary_words):
            score += 0.3
        
        return min(score, 1.0)
    
    async def generate_optimization_suggestions(self, features: EnhancedContentFeatures) -> ContentOptimization:
        """生成內容優化建議"""
        recommendations = []
        priority_actions = []
        
        # 個人化表達建議
        if features.personal_score < 0.3:
            recommendations.append("增加個人化表達，如「我認為」、「我的看法」、「我覺得」")
            priority_actions.append("在內容開頭加入個人觀點")
        
        # 情感表達建議
        if features.emotion_score < 0.2:
            recommendations.append("加入情感表達，如「期待」、「希望」、「擔心」")
            priority_actions.append("分享個人感受和經驗")
        
        # 互動引導建議
        if features.interaction_score < 0.3:
            recommendations.append("添加互動元素，如「你覺得呢？」、「留言告訴我」")
            priority_actions.append("在內容結尾提出問題")
        
        # 創意表達建議
        if features.creative_score < 0.2:
            recommendations.append("使用表情符號增加視覺吸引力，如🔥❤️😊")
            priority_actions.append("在重點處添加相關表情符號")
        
        # 幽默元素建議
        if features.humor_score < 0.2:
            recommendations.append("加入幽默元素，如創意比喻或輕鬆表達")
            priority_actions.append("使用生動的比喻和描述")
        
        # 直接回答建議
        if features.direct_answer_score < 0.2:
            recommendations.append("直接回答讀者問題，避免過於正式")
            priority_actions.append("用「簡單來說」或「總結來說」開頭")
        
        # 計算改善潛力
        current_score = features.total_engagement_score
        target_score = 0.8  # 目標高分
        improvement_potential = target_score - current_score
        expected_improvement = min(improvement_potential * 0.8, 0.3)  # 預期改善幅度
        
        return ContentOptimization(
            content_id=features.content_id,
            current_score=current_score,
            target_score=target_score,
            improvement_potential=improvement_potential,
            specific_recommendations=recommendations,
            priority_actions=priority_actions,
            expected_improvement=expected_improvement
        )
    
    async def compare_with_high_engagement_examples(self, content: str) -> Dict[str, Any]:
        """與高互動範例比較"""
        try:
            features = await self.analyze_content(content)
            
            # 高互動範例特徵 (基於實際分析)
            high_engagement_examples = [
                {
                    "type": "personal_share",
                    "scores": {"personal": 0.4, "emotion": 0.6, "interaction": 0.6, "creative": 1.0, "humor": 0.4},
                    "description": "個人分享型 - 高度個人化，情感豐富，互動性強"
                },
                {
                    "type": "market_analysis", 
                    "scores": {"personal": 0.6, "emotion": 0.3, "interaction": 0.0, "creative": 0.0, "humor": 1.0},
                    "description": "市場分析型 - 直接回答問題，有幽默感"
                },
                {
                    "type": "news_analysis",
                    "scores": {"personal": 0.4, "emotion": 0.3, "interaction": 1.0, "creative": 0.4, "humor": 1.0},
                    "description": "新聞分析型 - 結合新聞分析與創意表達"
                }
            ]
            
            # 找出最相似的範例
            similarities = []
            for example in high_engagement_examples:
                similarity = self._calculate_similarity(features, example['scores'])
                similarities.append({
                    "type": example['type'],
                    "description": example['description'],
                    "similarity": similarity,
                    "scores": example['scores']
                })
            
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            return {
                "current_features": asdict(features),
                "most_similar_example": similarities[0] if similarities else None,
                "all_similarities": similarities,
                "optimization": await self.generate_optimization_suggestions(features)
            }
            
        except Exception as e:
            logger.error(f"與高互動範例比較失敗: {e}")
            return {}
    
    def _calculate_similarity(self, features: EnhancedContentFeatures, example_scores: Dict[str, float]) -> float:
        """計算與範例的相似度"""
        current_scores = {
            "personal": features.personal_score,
            "emotion": features.emotion_score,
            "interaction": features.interaction_score,
            "creative": features.creative_score,
            "humor": features.humor_score
        }
        
        # 計算餘弦相似度
        dot_product = sum(current_scores[key] * example_scores[key] for key in current_scores)
        norm_current = sum(score ** 2 for score in current_scores.values()) ** 0.5
        norm_example = sum(score ** 2 for score in example_scores.values()) ** 0.5
        
        if norm_current == 0 or norm_example == 0:
            return 0.0
        
        return dot_product / (norm_current * norm_example)
    
    def get_high_engagement_tips(self) -> List[str]:
        """獲取高互動技巧 (基於範例分析)"""
        return [
            "個人化表達：多使用「我認為」、「我的看法」、「我覺得」",
            "情感分享：加入「期待」、「希望」、「擔心」等情感詞彙",
            "互動引導：提出問題如「你覺得呢？」或邀請「留言告訴我」",
            "創意表達：使用表情符號🔥❤️😊增加視覺吸引力",
            "幽默元素：使用創意比喻如「神仙打架」、「火焰冰塊膠著狀態」",
            "直接回答：用「簡單來說」、「總結來說」直接回答問題",
            "結構化：使用分點說明但避免過於正式",
            "個人經驗：分享「今天」、「昨天」、「剛剛」的個人經歷"
        ]
