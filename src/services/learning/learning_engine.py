"""
智能自我學習引擎
負責分析互動成效、AI偵測結果，並動態調整KOL策略
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class LearningMetrics:
    """學習指標"""
    kol_id: str
    content_type: str
    topic_category: str
    engagement_score: float
    ai_detection_score: float
    sentiment_score: float
    interaction_count: int
    comment_quality_score: float
    learning_timestamp: datetime

@dataclass
class LearningInsight:
    """學習洞察"""
    insight_type: str  # 'content_optimization', 'persona_adjustment', 'timing_optimization'
    kol_id: str
    description: str
    confidence: float
    recommended_action: str
    expected_improvement: float
    created_at: datetime

@dataclass
class KOLStrategy:
    """KOL策略配置"""
    kol_id: str
    content_type_weights: Dict[str, float]
    persona_adjustments: Dict[str, Any]
    timing_preferences: Dict[str, Any]
    interaction_style: Dict[str, Any]
    last_updated: datetime

class LearningEngine:
    """智能學習引擎"""
    
    def __init__(self):
        self.model_path = "models/learning_models/"
        self.engagement_model = None
        self.ai_detection_model = None
        self.scaler = StandardScaler()
        self.learning_history = []
        self.kol_strategies = {}
        
        # 初始化模型目錄
        os.makedirs(self.model_path, exist_ok=True)
        
        # 載入現有模型
        self._load_models()
    
    def _load_models(self):
        """載入已訓練的模型"""
        try:
            if os.path.exists(f"{self.model_path}/engagement_model.pkl"):
                self.engagement_model = joblib.load(f"{self.model_path}/engagement_model.pkl")
                logger.info("成功載入互動預測模型")
            
            if os.path.exists(f"{self.model_path}/ai_detection_model.pkl"):
                self.ai_detection_model = joblib.load(f"{self.model_path}/ai_detection_model.pkl")
                logger.info("成功載入AI偵測模型")
                
        except Exception as e:
            logger.warning(f"載入模型失敗: {e}")
    
    def _save_models(self):
        """保存訓練好的模型"""
        try:
            if self.engagement_model:
                joblib.dump(self.engagement_model, f"{self.model_path}/engagement_model.pkl")
            
            if self.ai_detection_model:
                joblib.dump(self.ai_detection_model, f"{self.model_path}/ai_detection_model.pkl")
                
            logger.info("模型保存成功")
        except Exception as e:
            logger.error(f"保存模型失敗: {e}")
    
    async def analyze_interaction_effectiveness(self, interaction_data: List[Dict]) -> List[LearningMetrics]:
        """
        分析互動成效
        
        Args:
            interaction_data: 互動數據列表
            
        Returns:
            學習指標列表
        """
        learning_metrics = []
        
        for data in interaction_data:
            try:
                # 計算互動分數
                engagement_score = self._calculate_engagement_score(data)
                
                # 計算AI偵測分數
                ai_detection_score = await self._analyze_ai_detection(data)
                
                # 計算情感分數
                sentiment_score = self._analyze_sentiment(data)
                
                # 計算留言品質分數
                comment_quality_score = await self._analyze_comment_quality(data)
                
                metric = LearningMetrics(
                    kol_id=data.get('kol_id', ''),
                    content_type=data.get('content_type', ''),
                    topic_category=data.get('topic_category', ''),
                    engagement_score=engagement_score,
                    ai_detection_score=ai_detection_score,
                    sentiment_score=sentiment_score,
                    interaction_count=data.get('total_interactions', 0),
                    comment_quality_score=comment_quality_score,
                    learning_timestamp=datetime.now()
                )
                
                learning_metrics.append(metric)
                
            except Exception as e:
                logger.error(f"分析互動成效失敗: {e}")
                continue
        
        return learning_metrics
    
    def _calculate_engagement_score(self, data: Dict) -> float:
        """計算互動分數"""
        try:
            likes = data.get('likes_count', 0)
            comments = data.get('comments_count', 0)
            shares = data.get('shares_count', 0)
            saves = data.get('saves_count', 0)
            views = max(data.get('views_count', 1), 1)  # 避免除零
            
            # 加權計算互動分數
            engagement_score = (
                likes * 0.3 +
                comments * 0.4 +
                shares * 0.2 +
                saves * 0.1
            ) / views
            
            return min(engagement_score, 1.0)  # 限制在0-1之間
            
        except Exception as e:
            logger.error(f"計算互動分數失敗: {e}")
            return 0.0
    
    async def _analyze_ai_detection(self, data: Dict) -> float:
        """分析AI偵測結果"""
        try:
            comments = data.get('comments', [])
            if not comments:
                return 0.0
            
            ai_detection_signals = []
            
            for comment in comments:
                # 分析留言中的AI偵測信號
                ai_signals = self._detect_ai_signals(comment)
                ai_detection_signals.extend(ai_signals)
            
            # 計算AI偵測分數 (0-1，越高表示越可能被發現是AI)
            if not ai_detection_signals:
                return 0.0
            
            ai_score = sum(ai_detection_signals) / len(ai_detection_signals)
            return min(ai_score, 1.0)
            
        except Exception as e:
            logger.error(f"分析AI偵測失敗: {e}")
            return 0.0
    
    def _detect_ai_signals(self, comment: Dict) -> List[float]:
        """偵測單一留言中的AI信號"""
        signals = []
        content = comment.get('content', '').lower()
        
        # AI偵測關鍵詞
        ai_keywords = [
            'ai', '人工智慧', '機器人', 'bot', '自動生成',
            'chatgpt', 'gpt', 'claude', 'bard', 'copilot',
            '看起來像ai', '感覺是ai', 'ai生成', '機器寫的'
        ]
        
        # 檢查是否包含AI相關關鍵詞
        for keyword in ai_keywords:
            if keyword in content:
                signals.append(0.8)  # 高信號
        
        # 檢查語言模式
        if self._detect_ai_language_patterns(content):
            signals.append(0.6)  # 中等信號
        
        # 檢查情感表達
        if self._detect_ai_emotion_patterns(content):
            signals.append(0.4)  # 低信號
        
        return signals
    
    def _detect_ai_language_patterns(self, content: str) -> bool:
        """偵測AI語言模式"""
        # 過於正式或結構化的語言
        formal_patterns = [
            '根據', '基於', '綜合分析', '總結來說',
            '首先', '其次', '最後', '總而言之'
        ]
        
        pattern_count = sum(1 for pattern in formal_patterns if pattern in content)
        return pattern_count >= 2
    
    def _detect_ai_emotion_patterns(self, content: str) -> bool:
        """偵測AI情感表達模式"""
        # 缺乏個人化情感表達
        personal_indicators = ['我覺得', '我認為', '我的看法', '個人覺得']
        personal_count = sum(1 for indicator in personal_indicators if indicator in content)
        
        # 過多客觀描述
        objective_indicators = ['數據顯示', '統計表明', '研究指出', '分析結果']
        objective_count = sum(1 for indicator in objective_indicators if indicator in content)
        
        return personal_count == 0 and objective_count >= 2
    
    def _analyze_sentiment(self, data: Dict) -> float:
        """分析情感分數"""
        try:
            comments = data.get('comments', [])
            if not comments:
                return 0.5  # 中性分數
            
            sentiment_scores = []
            for comment in comments:
                content = comment.get('content', '')
                sentiment = self._calculate_sentiment_score(content)
                sentiment_scores.append(sentiment)
            
            return np.mean(sentiment_scores) if sentiment_scores else 0.5
            
        except Exception as e:
            logger.error(f"分析情感失敗: {e}")
            return 0.5
    
    def _calculate_sentiment_score(self, content: str) -> float:
        """計算單一內容的情感分數"""
        # 簡化的情感分析
        positive_words = ['好', '棒', '讚', '厲害', '支持', '認同', '同意']
        negative_words = ['爛', '差', '反對', '不同意', '質疑', '懷疑']
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        if positive_count + negative_count == 0:
            return 0.5
        
        return (positive_count - negative_count) / (positive_count + negative_count) * 0.5 + 0.5
    
    async def _analyze_comment_quality(self, data: Dict) -> float:
        """分析留言品質"""
        try:
            comments = data.get('comments', [])
            if not comments:
                return 0.0
            
            quality_scores = []
            for comment in comments:
                content = comment.get('content', '')
                quality = self._calculate_comment_quality(content)
                quality_scores.append(quality)
            
            return np.mean(quality_scores) if quality_scores else 0.0
            
        except Exception as e:
            logger.error(f"分析留言品質失敗: {e}")
            return 0.0
    
    def _calculate_comment_quality(self, content: str) -> float:
        """計算單一留言的品質分數"""
        if len(content) < 5:
            return 0.1  # 太短的留言品質低
        
        quality_score = 0.0
        
        # 長度分數 (適中長度較好)
        length_score = min(len(content) / 100, 1.0) * 0.3
        quality_score += length_score
        
        # 內容豐富度
        if any(char in content for char in ['？', '?', '！', '!']):
            quality_score += 0.2
        
        # 是否包含具體資訊
        if any(word in content for word in ['股價', '技術', '基本面', '分析', '數據']):
            quality_score += 0.3
        
        # 是否為有意義的討論
        if len(content.split()) >= 3:
            quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    async def generate_learning_insights(self, metrics: List[LearningMetrics]) -> List[LearningInsight]:
        """生成學習洞察"""
        insights = []
        
        # 按KOL分組分析
        kol_groups = {}
        for metric in metrics:
            if metric.kol_id not in kol_groups:
                kol_groups[metric.kol_id] = []
            kol_groups[metric.kol_id].append(metric)
        
        for kol_id, kol_metrics in kol_groups.items():
            # 內容優化洞察
            content_insight = self._analyze_content_optimization(kol_id, kol_metrics)
            if content_insight:
                insights.append(content_insight)
            
            # 人格調整洞察
            persona_insight = self._analyze_persona_adjustment(kol_id, kol_metrics)
            if persona_insight:
                insights.append(persona_insight)
            
            # 時機優化洞察
            timing_insight = self._analyze_timing_optimization(kol_id, kol_metrics)
            if timing_insight:
                insights.append(timing_insight)
        
        return insights
    
    def _analyze_content_optimization(self, kol_id: str, metrics: List[LearningMetrics]) -> Optional[LearningInsight]:
        """分析內容優化機會"""
        if len(metrics) < 3:
            return None
        
        # 分析不同內容類型的表現
        content_performance = {}
        for metric in metrics:
            content_type = metric.content_type
            if content_type not in content_performance:
                content_performance[content_type] = []
            content_performance[content_type].append(metric.engagement_score)
        
        # 找出表現最好和最差的內容類型
        best_type = None
        worst_type = None
        best_score = 0
        worst_score = 1
        
        for content_type, scores in content_performance.items():
            avg_score = np.mean(scores)
            if avg_score > best_score:
                best_score = avg_score
                best_type = content_type
            if avg_score < worst_score:
                worst_score = avg_score
                worst_type = content_type
        
        if best_type and worst_type and best_score - worst_score > 0.2:
            return LearningInsight(
                insight_type='content_optimization',
                kol_id=kol_id,
                description=f"內容類型 '{best_type}' 表現優於 '{worst_type}' ({best_score:.2f} vs {worst_score:.2f})",
                confidence=0.8,
                recommended_action=f"增加 {best_type} 類型內容，減少 {worst_type} 類型內容",
                expected_improvement=best_score - worst_score,
                created_at=datetime.now()
            )
        
        return None
    
    def _analyze_persona_adjustment(self, kol_id: str, metrics: List[LearningMetrics]) -> Optional[LearningInsight]:
        """分析人格調整機會"""
        if len(metrics) < 5:
            return None
        
        # 分析AI偵測分數
        ai_scores = [m.ai_detection_score for m in metrics]
        avg_ai_score = np.mean(ai_scores)
        
        if avg_ai_score > 0.3:  # 如果AI偵測分數過高
            return LearningInsight(
                insight_type='persona_adjustment',
                kol_id=kol_id,
                description=f"AI偵測分數過高 ({avg_ai_score:.2f})，可能被識別為AI生成內容",
                confidence=0.7,
                recommended_action="調整人格表達方式，增加更多個人化元素和情感表達",
                expected_improvement=0.2,
                created_at=datetime.now()
            )
        
        return None
    
    def _analyze_timing_optimization(self, kol_id: str, metrics: List[LearningMetrics]) -> Optional[LearningInsight]:
        """分析時機優化機會"""
        # 這裡可以根據發文時間和互動表現進行分析
        # 暫時返回None，後續可以擴展
        return None
    
    async def update_kol_strategies(self, insights: List[LearningInsight]) -> Dict[str, KOLStrategy]:
        """根據洞察更新KOL策略"""
        updated_strategies = {}
        
        for insight in insights:
            kol_id = insight.kol_id
            
            if kol_id not in self.kol_strategies:
                # 初始化策略
                self.kol_strategies[kol_id] = KOLStrategy(
                    kol_id=kol_id,
                    content_type_weights={},
                    persona_adjustments={},
                    timing_preferences={},
                    interaction_style={},
                    last_updated=datetime.now()
                )
            
            strategy = self.kol_strategies[kol_id]
            
            # 根據洞察類型更新策略
            if insight.insight_type == 'content_optimization':
                self._update_content_weights(strategy, insight)
            elif insight.insight_type == 'persona_adjustment':
                self._update_persona_adjustments(strategy, insight)
            elif insight.insight_type == 'timing_optimization':
                self._update_timing_preferences(strategy, insight)
            
            strategy.last_updated = datetime.now()
            updated_strategies[kol_id] = strategy
        
        return updated_strategies
    
    def _update_content_weights(self, strategy: KOLStrategy, insight: LearningInsight):
        """更新內容類型權重"""
        # 解析推薦動作
        if "增加" in insight.recommended_action and "減少" in insight.recommended_action:
            # 提取內容類型
            parts = insight.recommended_action.split("增加")[1].split("類型內容")
            if len(parts) >= 1:
                increase_type = parts[0].strip()
                if increase_type not in strategy.content_type_weights:
                    strategy.content_type_weights[increase_type] = 0.5
                strategy.content_type_weights[increase_type] += 0.1
    
    def _update_persona_adjustments(self, strategy: KOLStrategy, insight: LearningInsight):
        """更新人格調整"""
        if "個人化元素" in insight.recommended_action:
            strategy.persona_adjustments['personalization'] = strategy.persona_adjustments.get('personalization', 0) + 0.1
        
        if "情感表達" in insight.recommended_action:
            strategy.persona_adjustments['emotion'] = strategy.persona_adjustments.get('emotion', 0) + 0.1
    
    def _update_timing_preferences(self, strategy: KOLStrategy, insight: LearningInsight):
        """更新時機偏好"""
        # 暫時不實作，後續可以擴展
        pass
    
    async def train_models(self, training_data: List[Dict]):
        """訓練預測模型"""
        try:
            # 準備訓練數據
            X, y_engagement, y_ai_detection = self._prepare_training_data(training_data)
            
            if len(X) < 10:
                logger.warning("訓練數據不足，跳過模型訓練")
                return
            
            # 標準化特徵
            X_scaled = self.scaler.fit_transform(X)
            
            # 訓練互動預測模型
            self.engagement_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.engagement_model.fit(X_scaled, y_engagement)
            
            # 訓練AI偵測模型
            self.ai_detection_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.ai_detection_model.fit(X_scaled, y_ai_detection)
            
            # 保存模型
            self._save_models()
            
            logger.info("模型訓練完成")
            
        except Exception as e:
            logger.error(f"模型訓練失敗: {e}")
    
    def _prepare_training_data(self, training_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """準備訓練數據"""
        features = []
        engagement_targets = []
        ai_detection_targets = []
        
        for data in training_data:
            # 提取特徵
            feature_vector = [
                data.get('content_length', 0),
                data.get('has_images', 0),
                data.get('has_hashtags', 0),
                data.get('posting_hour', 12),
                data.get('topic_heat', 0.5),
                data.get('kol_experience', 0.5)
            ]
            
            features.append(feature_vector)
            engagement_targets.append(data.get('engagement_score', 0))
            ai_detection_targets.append(data.get('ai_detection_score', 0))
        
        return np.array(features), np.array(engagement_targets), np.array(ai_detection_targets)
    
    async def predict_engagement(self, content_features: Dict) -> float:
        """預測內容互動潛力"""
        if not self.engagement_model:
            return 0.5  # 默認分數
        
        try:
            feature_vector = np.array([
                content_features.get('content_length', 0),
                content_features.get('has_images', 0),
                content_features.get('has_hashtags', 0),
                content_features.get('posting_hour', 12),
                content_features.get('topic_heat', 0.5),
                content_features.get('kol_experience', 0.5)
            ]).reshape(1, -1)
            
            feature_scaled = self.scaler.transform(feature_vector)
            prediction = self.engagement_model.predict(feature_scaled)[0]
            
            return max(0, min(1, prediction))  # 限制在0-1之間
            
        except Exception as e:
            logger.error(f"預測互動潛力失敗: {e}")
            return 0.5
    
    async def predict_ai_detection(self, content_features: Dict) -> float:
        """預測AI偵測風險"""
        if not self.ai_detection_model:
            return 0.3  # 默認風險
        
        try:
            feature_vector = np.array([
                content_features.get('content_length', 0),
                content_features.get('has_images', 0),
                content_features.get('has_hashtags', 0),
                content_features.get('posting_hour', 12),
                content_features.get('topic_heat', 0.5),
                content_features.get('kol_experience', 0.5)
            ]).reshape(1, -1)
            
            feature_scaled = self.scaler.transform(feature_vector)
            prediction = self.ai_detection_model.predict(feature_scaled)[0]
            
            return max(0, min(1, prediction))  # 限制在0-1之間
            
        except Exception as e:
            logger.error(f"預測AI偵測風險失敗: {e}")
            return 0.3
    
    def get_kol_strategy(self, kol_id: str) -> Optional[KOLStrategy]:
        """獲取KOL策略"""
        return self.kol_strategies.get(kol_id)
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """獲取學習摘要"""
        return {
            'total_insights': len(self.learning_history),
            'active_kols': len(self.kol_strategies),
            'model_status': {
                'engagement_model': self.engagement_model is not None,
                'ai_detection_model': self.ai_detection_model is not None
            },
            'last_updated': datetime.now().isoformat()
        }

