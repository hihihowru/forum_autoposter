#!/usr/bin/env python3
"""
智能自我學習機制 - 完整版
基於實際 CMoney 互動數據的學習系統
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class InteractionData:
    """互動數據結構"""
    article_id: str
    kol_id: str
    kol_nickname: str
    likes: int
    comments: int
    shares: int
    emoji_total: int
    total_interactions: int
    engagement_rate: float
    post_timestamp: str
    content: str
    topic_id: str
    views: Optional[int] = None
    sentiment_score: Optional[float] = None

@dataclass
class LearningInsight:
    """學習洞察"""
    insight_type: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    description: str
    suggested_actions: List[str]
    confidence: float
    timestamp: datetime
    impact_score: float
    implementation_difficulty: str

@dataclass
class KOLStrategy:
    """KOL 策略"""
    kol_id: str
    content_type_weights: Dict[str, float]
    persona_adjustments: Dict[str, float]
    timing_preferences: Dict[str, Any]
    interaction_style: Dict[str, Any]
    last_updated: datetime

class RealTimeAnalyzer:
    """實時分析器"""
    
    def __init__(self):
        self.interaction_history = []
        self.kol_performance = defaultdict(list)
        
    def analyze_interaction_performance(self, interaction_data: InteractionData) -> Dict[str, Any]:
        """分析互動表現"""
        # 計算綜合互動分數
        engagement_score = self._calculate_engagement_score(interaction_data)
        
        # 分析表情情感
        emoji_sentiment = self._analyze_emoji_sentiment(interaction_data)
        
        # 分析時間模式
        timing_analysis = self._analyze_timing_pattern(interaction_data)
        
        # 分析內容特徵
        content_analysis = self._analyze_content_features(interaction_data)
        
        # 計算病毒傳播潛力
        viral_potential = self._calculate_viral_potential(interaction_data)
        
        # 計算品牌影響力
        brand_impact = self._calculate_brand_impact(interaction_data)
        
        return {
            'engagement_score': engagement_score,
            'emoji_sentiment': emoji_sentiment,
            'timing_analysis': timing_analysis,
            'content_analysis': content_analysis,
            'viral_potential': viral_potential,
            'brand_impact': brand_impact,
            'performance_trend': self._analyze_performance_trend(interaction_data),
            'overall_score': self._calculate_overall_score(engagement_score, viral_potential, brand_impact)
        }
    
    def _calculate_engagement_score(self, data: InteractionData) -> float:
        """計算綜合互動分數"""
        # 加權計算
        likes_weight = 0.3
        comments_weight = 0.4
        shares_weight = 0.2
        emoji_weight = 0.1
        
        weighted_score = (
            data.likes * likes_weight +
            data.comments * comments_weight +
            data.shares * shares_weight +
            data.emoji_total * emoji_weight
        )
        
        # 標準化到 0-100 分
        normalized_score = min(weighted_score * 5, 100)
        
        return normalized_score
    
    def _analyze_emoji_sentiment(self, data: InteractionData) -> Dict[str, Any]:
        """分析表情情感"""
        return {
            'positive_ratio': 0.8,  # 假設 80% 正面表情
            'engagement_level': 'high' if data.emoji_total > 5 else 'medium',
            'sentiment_score': 0.7  # 0-1 的情感分數
        }
    
    def _analyze_timing_pattern(self, data: InteractionData) -> Dict[str, Any]:
        """分析時間模式"""
        try:
            post_time = datetime.fromisoformat(data.post_timestamp.replace('Z', '+00:00'))
            hour = post_time.hour
            
            return {
                'post_hour': hour,
                'is_peak_hour': 9 <= hour <= 11 or 19 <= hour <= 21,
                'timezone_effect': 'positive' if 9 <= hour <= 21 else 'negative',
                'optimal_timing': self._find_optimal_timing(hour),
                'timing_score': self._calculate_timing_score(hour)
            }
        except:
            return {
                'post_hour': 0,
                'is_peak_hour': False,
                'timezone_effect': 'unknown',
                'optimal_timing': 'unknown',
                'timing_score': 0.5
            }
    
    def _analyze_content_features(self, data: InteractionData) -> Dict[str, Any]:
        """分析內容特徵"""
        content = data.content
        if not content:
            content = "貼文內容..."
        
        return {
            'content_length': len(content),
            'readability_score': self._calculate_readability(content),
            'personalization_level': self._analyze_personalization(content),
            'ai_detection_risk': self._assess_ai_detection_risk(content),
            'engagement_potential': self._assess_engagement_potential(content),
            'content_quality_score': self._calculate_content_quality_score(content)
        }
    
    def _calculate_readability(self, content: str) -> float:
        """計算可讀性分數"""
        sentences = content.split('。')
        avg_sentence_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
        
        if avg_sentence_length < 20:
            return 90
        elif avg_sentence_length < 30:
            return 70
        else:
            return 50
    
    def _analyze_personalization(self, content: str) -> float:
        """分析個人化程度"""
        personal_indicators = [
            '我覺得', '我認為', '我的看法', '個人覺得', '我', '我的',
            '哈哈', '呵呵', '靠', '幹', '真的假的', '...', '!!!'
        ]
        
        personal_count = sum(1 for indicator in personal_indicators if indicator in content)
        return min(personal_count / 5, 1.0)
    
    def _assess_ai_detection_risk(self, content: str) -> float:
        """評估 AI 偵測風險"""
        risk_factors = 0
        
        # 檢查過於正式的語言
        formal_indicators = ['因此', '然而', '此外', '總而言之', '綜上所述']
        risk_factors += sum(1 for indicator in formal_indicators if indicator in content)
        
        # 檢查缺乏個人化
        personal_score = self._analyze_personalization(content)
        risk_factors += (1 - personal_score) * 3
        
        # 檢查結構過於規整
        sentences = content.split('。')
        if len(sentences) > 2:
            sentence_lengths = [len(s) for s in sentences if s.strip()]
            if sentence_lengths:
                length_variance = np.var(sentence_lengths)
                if length_variance < 50:
                    risk_factors += 2
        
        return min(risk_factors / 10, 1.0)
    
    def _assess_engagement_potential(self, content: str) -> float:
        """評估互動潛力"""
        engagement_indicators = [
            '你覺得', '大家怎麼看', '歡迎討論', '分享你的看法',
            '?', '？', '！', '!!!', '哈哈', '呵呵'
        ]
        
        engagement_count = sum(1 for indicator in engagement_indicators if indicator in content)
        return min(engagement_count / 3, 1.0)
    
    def _calculate_content_quality_score(self, content: str) -> float:
        """計算內容品質分數"""
        readability = self._calculate_readability(content)
        personalization = self._analyze_personalization(content) * 100
        engagement_potential = self._assess_engagement_potential(content) * 100
        
        return (readability + personalization + engagement_potential) / 3
    
    def _find_optimal_timing(self, hour: int) -> str:
        """找到最佳發文時機"""
        if 9 <= hour <= 11:
            return "morning_peak"
        elif 12 <= hour <= 14:
            return "lunch_time"
        elif 19 <= hour <= 21:
            return "evening_peak"
        else:
            return "off_peak"
    
    def _calculate_timing_score(self, hour: int) -> float:
        """計算時機分數"""
        if 9 <= hour <= 11 or 19 <= hour <= 21:
            return 0.9
        elif 12 <= hour <= 14:
            return 0.7
        else:
            return 0.3
    
    def _calculate_viral_potential(self, data: InteractionData) -> float:
        """計算病毒傳播潛力"""
        share_ratio = data.shares / max(data.total_interactions, 1)
        comment_ratio = data.comments / max(data.total_interactions, 1)
        emoji_ratio = data.emoji_total / max(data.total_interactions, 1)
        
        viral_score = (
            share_ratio * 0.5 +
            comment_ratio * 0.3 +
            emoji_ratio * 0.2
        ) * 100
        
        return min(viral_score, 100)
    
    def _calculate_brand_impact(self, data: InteractionData) -> float:
        """計算品牌影響力"""
        engagement_quality = data.total_interactions / max(data.views or 1000, 1)
        sentiment_impact = data.sentiment_score or 0.5
        
        brand_score = (engagement_quality * 0.6 + sentiment_impact * 0.4) * 100
        return min(brand_score, 100)
    
    def _calculate_overall_score(self, engagement_score: float, viral_potential: float, brand_impact: float) -> float:
        """計算整體分數"""
        return (engagement_score * 0.5 + viral_potential * 0.3 + brand_impact * 0.2)
    
    def _analyze_performance_trend(self, data: InteractionData) -> Dict[str, Any]:
        """分析表現趨勢"""
        self.kol_performance[data.kol_id].append(data)
        
        if len(self.kol_performance[data.kol_id]) < 2:
            return {'trend': 'insufficient_data', 'change_rate': 0}
        
        recent_data = self.kol_performance[data.kol_id][-5:]
        if len(recent_data) >= 2:
            recent_avg = sum(d.total_interactions for d in recent_data) / len(recent_data)
            previous_avg = sum(d.total_interactions for d in self.kol_performance[data.kol_id][:-5]) / max(len(self.kol_performance[data.kol_id]) - 5, 1)
            
            change_rate = (recent_avg - previous_avg) / max(previous_avg, 1)
            
            if change_rate > 0.1:
                trend = 'improving'
            elif change_rate < -0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
            change_rate = 0
        
        return {'trend': trend, 'change_rate': change_rate}

class PatternDetector:
    """模式偵測器"""
    
    def __init__(self):
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
    
    def detect_patterns(self, interaction_data: InteractionData, performance_analysis: Dict) -> Dict[str, Any]:
        """偵測模式"""
        patterns = {
            'success_patterns': self._detect_success_patterns(interaction_data, performance_analysis),
            'failure_patterns': self._detect_failure_patterns(interaction_data, performance_analysis),
            'audience_patterns': self._detect_audience_patterns(interaction_data, performance_analysis)
        }
        
        return patterns
    
    def _detect_success_patterns(self, data: InteractionData, analysis: Dict) -> List[Dict]:
        """偵測成功模式"""
        patterns = []
        
        # 高互動模式
        if analysis['overall_score'] > 70:
            patterns.append({
                'type': 'high_engagement',
                'description': '高互動表現',
                'confidence': 0.8,
                'features': {
                    'engagement_score': analysis['engagement_score'],
                    'emoji_sentiment': analysis['emoji_sentiment']['sentiment_score'],
                    'timing': analysis['timing_analysis']['optimal_timing']
                }
            })
        
        # 病毒傳播模式
        if analysis['viral_potential'] > 60:
            patterns.append({
                'type': 'viral_content',
                'description': '病毒傳播潛力',
                'confidence': 0.8,
                'features': {
                    'viral_potential': analysis['viral_potential'],
                    'share_rate': data.shares / max(data.total_interactions, 1),
                    'comment_rate': data.comments / max(data.total_interactions, 1)
                }
            })
        
        # 最佳時機模式
        if analysis['timing_analysis']['is_peak_hour']:
            patterns.append({
                'type': 'optimal_timing',
                'description': '最佳發文時機',
                'confidence': 0.6,
                'features': {
                    'post_hour': analysis['timing_analysis']['post_hour'],
                    'timezone_effect': analysis['timing_analysis']['timezone_effect']
                }
            })
        
        return patterns
    
    def _detect_failure_patterns(self, data: InteractionData, analysis: Dict) -> List[Dict]:
        """偵測失敗模式"""
        patterns = []
        
        # 低互動模式
        if analysis['overall_score'] < 30:
            patterns.append({
                'type': 'low_engagement',
                'description': '互動率偏低',
                'confidence': 0.8,
                'features': {
                    'engagement_score': analysis['engagement_score'],
                    'content_length': analysis['content_analysis']['content_length']
                }
            })
        
        # AI 偵測風險模式
        if analysis['content_analysis']['ai_detection_risk'] > 0.7:
            patterns.append({
                'type': 'ai_detection_risk',
                'description': 'AI 偵測風險較高',
                'confidence': 0.9,
                'features': {
                    'ai_detection_risk': analysis['content_analysis']['ai_detection_risk'],
                    'personalization_level': analysis['content_analysis']['personalization_level']
                }
            })
        
        # 非最佳時機模式
        if not analysis['timing_analysis']['is_peak_hour']:
            patterns.append({
                'type': 'suboptimal_timing',
                'description': '發文時機不佳',
                'confidence': 0.5,
                'features': {
                    'post_hour': analysis['timing_analysis']['post_hour'],
                    'timezone_effect': analysis['timing_analysis']['timezone_effect']
                }
            })
        
        return patterns
    
    def _detect_audience_patterns(self, data: InteractionData, analysis: Dict) -> List[Dict]:
        """偵測受眾模式"""
        patterns = []
        
        # 受眾活躍度模式
        if data.comments > 0:
            patterns.append({
                'type': 'active_audience',
                'description': '受眾互動活躍',
                'confidence': 0.7,
                'features': {
                    'comment_count': data.comments,
                    'engagement_rate': data.engagement_rate
                }
            })
        
        # 表情回應模式
        if data.emoji_total > 5:
            patterns.append({
                'type': 'emoji_response',
                'description': '受眾表情回應積極',
                'confidence': 0.6,
                'features': {
                    'emoji_total': data.emoji_total,
                    'sentiment_score': analysis['emoji_sentiment']['sentiment_score']
                }
            })
        
        return patterns

class RiskAssessor:
    """風險評估器"""
    
    def __init__(self):
        self.risk_thresholds = {
            'ai_detection': 0.7,
            'low_engagement': 0.3,
            'negative_sentiment': 0.4,
            'suboptimal_timing': 0.5
        }
    
    def assess_risks(self, interaction_data: InteractionData, performance_analysis: Dict, patterns: Dict) -> Dict[str, Any]:
        """評估風險"""
        risks = {
            'ai_detection_risk': self._assess_ai_detection_risk(performance_analysis, patterns),
            'engagement_risk': self._assess_engagement_risk(performance_analysis, patterns),
            'timing_risk': self._assess_timing_risk(performance_analysis, patterns),
            'content_quality_risk': self._assess_content_quality_risk(performance_analysis, patterns),
            'overall_risk': 0.0
        }
        
        # 計算整體風險
        risk_scores = [risks[k] for k in risks.keys() if k != 'overall_risk']
        risks['overall_risk'] = sum(risk_scores) / len(risk_scores)
        
        # 生成風險預警
        risks['risk_alerts'] = self._generate_risk_alerts(risks)
        
        return risks
    
    def _assess_ai_detection_risk(self, analysis: Dict, patterns: Dict) -> float:
        """評估 AI 偵測風險"""
        base_risk = analysis['content_analysis']['ai_detection_risk']
        
        # 根據模式調整風險
        for pattern in patterns['failure_patterns']:
            if pattern['type'] == 'ai_detection_risk':
                base_risk += 0.2
        
        return min(base_risk, 1.0)
    
    def _assess_engagement_risk(self, analysis: Dict, patterns: Dict) -> float:
        """評估互動風險"""
        base_risk = 1.0 - (analysis['overall_score'] / 100)
        
        # 根據模式調整風險
        for pattern in patterns['failure_patterns']:
            if pattern['type'] == 'low_engagement':
                base_risk += 0.3
        
        return min(base_risk, 1.0)
    
    def _assess_timing_risk(self, analysis: Dict, patterns: Dict) -> float:
        """評估時機風險"""
        if analysis['timing_analysis']['is_peak_hour']:
            return 0.2
        else:
            return 0.6
    
    def _assess_content_quality_risk(self, analysis: Dict, patterns: Dict) -> float:
        """評估內容品質風險"""
        risks = []
        
        # 可讀性風險
        if analysis['content_analysis']['readability_score'] < 50:
            risks.append(0.5)
        
        # 個人化風險
        if analysis['content_analysis']['personalization_level'] < 0.3:
            risks.append(0.4)
        
        # 互動潛力風險
        if analysis['content_analysis']['engagement_potential'] < 0.3:
            risks.append(0.3)
        
        return sum(risks) / max(len(risks), 1)
    
    def _generate_risk_alerts(self, risks: Dict) -> List[Dict]:
        """生成風險預警"""
        alerts = []
        
        for risk_type, risk_score in risks.items():
            if risk_type in ['overall_risk', 'risk_alerts']:
                continue
                
            if isinstance(risk_score, (int, float)) and risk_score > 0.7:
                alerts.append({
                    'type': risk_type,
                    'level': 'critical',
                    'description': f'{risk_type} 風險過高',
                    'immediate_action_required': True
                })
            elif isinstance(risk_score, (int, float)) and risk_score > 0.5:
                alerts.append({
                    'type': risk_type,
                    'level': 'warning',
                    'description': f'{risk_type} 風險需要注意',
                    'immediate_action_required': False
                })
        
        return alerts

class LearningInsightGenerator:
    """學習洞察生成器"""
    
    def __init__(self):
        self.insight_templates = {
            'content_optimization': {
                'low_engagement': '互動率偏低，建議增加個人化元素和情感表達',
                'ai_detection_risk': 'AI 偵測風險較高，需要增加人性化表達',
                'low_personalization': '個人化程度不足，建議增加個人觀點和經驗'
            },
            'timing_optimization': {
                'suboptimal_timing': '發文時機不佳，建議在高峰時段發文',
                'off_peak': '非高峰時段發文，可能影響互動效果'
            },
            'content_quality': {
                'low_readability': '可讀性較低，建議簡化語言結構',
                'low_engagement_potential': '互動潛力不足，建議增加互動元素'
            }
        }
    
    def generate_insights(self, interaction_data: InteractionData, performance_analysis: Dict, patterns: Dict, risks: Dict) -> List[LearningInsight]:
        """生成學習洞察"""
        insights = []
        
        # 基於風險生成洞察
        insights.extend(self._generate_risk_based_insights(risks, performance_analysis))
        
        # 基於模式生成洞察
        insights.extend(self._generate_pattern_based_insights(patterns, performance_analysis))
        
        # 基於表現趨勢生成洞察
        insights.extend(self._generate_trend_based_insights(performance_analysis))
        
        return insights
    
    def _generate_risk_based_insights(self, risks: Dict, analysis: Dict) -> List[LearningInsight]:
        """基於風險生成洞察"""
        insights = []
        
        # AI 偵測風險洞察
        if risks['ai_detection_risk'] > 0.7:
            insights.append(LearningInsight(
                insight_type='ai_detection_risk',
                priority='critical',
                description='AI 偵測風險較高，需要立即調整',
                suggested_actions=[
                    '增加口語化表達',
                    '添加不完整句子',
                    '使用更多表情符號',
                    '加入個人化細節',
                    '避免過於正式的語言結構'
                ],
                confidence=0.9,
                timestamp=datetime.now(),
                impact_score=0.8,
                implementation_difficulty='medium'
            ))
        
        # 互動風險洞察
        if risks['engagement_risk'] > 0.6:
            insights.append(LearningInsight(
                insight_type='content_optimization',
                priority='high',
                description='互動率偏低，建議增加個人化元素和情感表達',
                suggested_actions=[
                    '增加個人觀點和經驗分享',
                    '使用更多情感詞彙',
                    '添加互動性問題',
                    '使用表情符號增加親和力',
                    '分享個人故事或經歷'
                ],
                confidence=0.8,
                timestamp=datetime.now(),
                impact_score=0.7,
                implementation_difficulty='medium'
            ))
        
        # 時機風險洞察
        if risks['timing_risk'] > 0.5:
            insights.append(LearningInsight(
                insight_type='timing_optimization',
                priority='medium',
                description='發文時機不佳，建議在高峰時段發文',
                suggested_actions=[
                    '選擇 9-11 點或 19-21 點發文',
                    '避開深夜和凌晨時段',
                    '考慮受眾的活躍時間',
                    '測試不同時段的互動效果'
                ],
                confidence=0.7,
                timestamp=datetime.now(),
                impact_score=0.6,
                implementation_difficulty='easy'
            ))
        
        return insights
    
    def _generate_pattern_based_insights(self, patterns: Dict, analysis: Dict) -> List[LearningInsight]:
        """基於模式生成洞察"""
        insights = []
        
        # 成功模式洞察
        for pattern in patterns['success_patterns']:
            if pattern['type'] == 'high_engagement':
                insights.append(LearningInsight(
                    insight_type='success_pattern',
                    priority='low',
                    description='發現高互動模式，建議保持並優化',
                    suggested_actions=[
                        '保持當前的內容風格',
                        '進一步優化個人化表達',
                        '在相似時段發文',
                        '擴大成功模式的應用'
                    ],
                    confidence=pattern['confidence'],
                    timestamp=datetime.now(),
                    impact_score=0.6,
                    implementation_difficulty='easy'
                ))
        
        # 失敗模式洞察
        for pattern in patterns['failure_patterns']:
            if pattern['type'] == 'low_engagement':
                insights.append(LearningInsight(
                    insight_type='content_optimization',
                    priority='high',
                    description='發現低互動模式，需要調整策略',
                    suggested_actions=[
                        '增加內容的趣味性',
                        '使用更多視覺元素',
                        '調整內容長度',
                        '增加互動性問題'
                    ],
                    confidence=pattern['confidence'],
                    timestamp=datetime.now(),
                    impact_score=0.7,
                    implementation_difficulty='medium'
                ))
        
        return insights
    
    def _generate_trend_based_insights(self, analysis: Dict) -> List[LearningInsight]:
        """基於趨勢生成洞察"""
        insights = []
        
        trend = analysis.get('performance_trend', {})
        if trend.get('trend') == 'declining':
            insights.append(LearningInsight(
                insight_type='performance_trend',
                priority='high',
                description='表現呈下降趨勢，需要策略調整',
                suggested_actions=[
                    '分析下降原因',
                    '調整內容策略',
                    '優化發文時機',
                    '增加與受眾的互動'
                ],
                confidence=0.7,
                timestamp=datetime.now(),
                impact_score=0.7,
                implementation_difficulty='medium'
            ))
        
        return insights

class SelfLearningSystem:
    """智能自我學習系統"""
    
    def __init__(self):
        self.real_time_analyzer = RealTimeAnalyzer()
        self.pattern_detector = PatternDetector()
        self.risk_assessor = RiskAssessor()
        self.insight_generator = LearningInsightGenerator()
        self.kol_strategies = {}
        
        logger.info("智能自我學習系統初始化完成")
    
    async def process_interaction_data(self, interaction_data: InteractionData) -> Dict[str, Any]:
        """處理互動數據並生成學習結果"""
        try:
            logger.info(f"開始處理 {interaction_data.kol_nickname} 的互動數據")
            
            # 1. 實時分析
            performance_analysis = self.real_time_analyzer.analyze_interaction_performance(interaction_data)
            
            # 2. 模式偵測
            patterns = self.pattern_detector.detect_patterns(interaction_data, performance_analysis)
            
            # 3. 風險評估
            risks = self.risk_assessor.assess_risks(interaction_data, performance_analysis, patterns)
            
            # 4. 生成洞察
            insights = self.insight_generator.generate_insights(interaction_data, performance_analysis, patterns, risks)
            
            # 5. 更新策略
            strategy_updates = self._update_kol_strategy(interaction_data.kol_id, insights)
            
            # 6. 生成報告
            learning_report = {
                'kol_id': interaction_data.kol_id,
                'kol_nickname': interaction_data.kol_nickname,
                'article_id': interaction_data.article_id,
                'performance_analysis': performance_analysis,
                'patterns': patterns,
                'risks': risks,
                'insights': [asdict(insight) for insight in insights],
                'strategy_updates': strategy_updates,
                'learning_summary': self._generate_learning_summary(insights, risks),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"完成 {interaction_data.kol_nickname} 的學習分析")
            return learning_report
            
        except Exception as e:
            logger.error(f"處理互動數據失敗: {e}")
            return {'error': str(e)}
    
    def _update_kol_strategy(self, kol_id: str, insights: List[LearningInsight]) -> Dict[str, Any]:
        """更新 KOL 策略"""
        if kol_id not in self.kol_strategies:
            self.kol_strategies[kol_id] = KOLStrategy(
                kol_id=kol_id,
                content_type_weights={'investment': 0.5, 'personal': 0.3, 'news': 0.2},
                persona_adjustments={'personalization': 0.5, 'emotion': 0.5, 'authenticity': 0.5},
                timing_preferences={'optimal_hours': [9, 10, 11, 19, 20, 21]},
                interaction_style={'casual': 0.5, 'professional': 0.5},
                last_updated=datetime.now()
            )
        
        strategy = self.kol_strategies[kol_id]
        updates = {}
        
        # 根據洞察調整策略
        for insight in insights:
            if insight.insight_type == 'content_optimization':
                if insight.priority in ['high', 'critical']:
                    strategy.persona_adjustments['personalization'] += 0.1
                    strategy.persona_adjustments['emotion'] += 0.1
                    updates['personalization_increased'] = True
            
            elif insight.insight_type == 'timing_optimization':
                if insight.priority in ['medium', 'high']:
                    updates['timing_adjusted'] = True
            
            elif insight.insight_type == 'ai_detection_risk':
                if insight.priority == 'critical':
                    strategy.persona_adjustments['authenticity'] += 0.2
                    strategy.interaction_style['casual'] += 0.2
                    updates['authenticity_increased'] = True
        
        strategy.last_updated = datetime.now()
        return updates
    
    def _generate_learning_summary(self, insights: List[LearningInsight], risks: Dict) -> Dict[str, Any]:
        """生成學習摘要"""
        # 過濾掉非數值類型的風險
        numeric_risks = {k: v for k, v in risks.items() 
                        if isinstance(v, (int, float)) and k not in ['overall_risk', 'risk_alerts']}
        
        return {
            'total_insights': len(insights),
            'critical_insights': len([i for i in insights if i.priority == 'critical']),
            'high_priority_insights': len([i for i in insights if i.priority == 'high']),
            'highest_risk': max(numeric_risks.keys(), key=lambda k: numeric_risks[k]) if numeric_risks else 'none',
            'overall_risk_level': risks.get('overall_risk', 0),
            'recommended_actions': len([i for i in insights if i.impact_score > 0.6]),
            'learning_progress': 'improving' if len(insights) > 0 else 'stable'
        }

async def main():
    """主函數 - 測試自我學習系統"""
    print("🧠 智能自我學習機制完整版測試")
    print("=" * 60)
    
    # 初始化學習系統
    learning_system = SelfLearningSystem()
    
    # 模擬互動數據
    test_data = [
        InteractionData(
            article_id='173477844',
            kol_id='9505549',
            kol_nickname='龜狗一日散戶',
            likes=8,
            comments=1,
            shares=1,
            emoji_total=8,
            total_interactions=18,
            engagement_rate=0.018,
            post_timestamp='2025-09-02T17:41:09.295405',
            content='貼文內容...',
            topic_id='2025-09-02 17:41:13',
            views=1000,
            sentiment_score=0.7
        ),
        InteractionData(
            article_id='173477845',
            kol_id='9505550',
            kol_nickname='板橋大who',
            likes=9,
            comments=0,
            shares=0,
            emoji_total=9,
            total_interactions=18,
            engagement_rate=0.018,
            post_timestamp='2025-09-02T17:41:09.704825',
            content='貼文內容...',
            topic_id='2025-09-02 17:41:13',
            views=1000,
            sentiment_score=0.6
        )
    ]
    
    # 處理每個互動數據
    for i, data in enumerate(test_data, 1):
        print(f"\n📊 處理第 {i} 個互動數據:")
        print(f"   KOL: {data.kol_nickname}")
        print(f"   Article ID: {data.article_id}")
        print(f"   互動數: {data.total_interactions}")
        
        # 執行學習分析
        learning_report = await learning_system.process_interaction_data(data)
        
        if 'error' not in learning_report:
            # 顯示分析結果
            print(f"\n📈 分析結果:")
            print(f"   整體分數: {learning_report['performance_analysis']['overall_score']:.1f}/100")
            print(f"   互動分數: {learning_report['performance_analysis']['engagement_score']:.1f}/100")
            print(f"   病毒傳播潛力: {learning_report['performance_analysis']['viral_potential']:.1f}")
            print(f"   品牌影響力: {learning_report['performance_analysis']['brand_impact']:.1f}")
            
            # 顯示風險評估
            risks = learning_report['risks']
            print(f"\n⚠️ 風險評估:")
            print(f"   整體風險: {risks['overall_risk']:.2f}")
            print(f"   AI 偵測風險: {risks['ai_detection_risk']:.2f}")
            print(f"   互動風險: {risks['engagement_risk']:.2f}")
            
            # 顯示風險預警
            if risks['risk_alerts']:
                print(f"   風險預警 ({len(risks['risk_alerts'])} 個):")
                for alert in risks['risk_alerts']:
                    print(f"     - [{alert['level'].upper()}] {alert['description']}")
            
            # 顯示洞察
            insights = learning_report['insights']
            if insights:
                print(f"\n💡 學習洞察 ({len(insights)} 個):")
                for j, insight in enumerate(insights, 1):
                    print(f"   {j}. [{insight['priority'].upper()}] {insight['description']}")
                    print(f"      影響分數: {insight['impact_score']:.1f}, 實施難度: {insight['implementation_difficulty']}")
                    for action in insight['suggested_actions'][:2]:  # 只顯示前2個建議
                        print(f"      - {action}")
            else:
                print(f"\n✅ 沒有發現需要調整的問題")
            
            # 顯示學習摘要
            summary = learning_report['learning_summary']
            print(f"\n📋 學習摘要:")
            print(f"   總洞察數: {summary['total_insights']}")
            print(f"   關鍵洞察: {summary['critical_insights']}")
            print(f"   高優先級洞察: {summary['high_priority_insights']}")
            print(f"   建議行動: {summary['recommended_actions']}")
        else:
            print(f"❌ 分析失敗: {learning_report['error']}")
    
    print(f"\n" + "=" * 60)
    print("✅ 智能自我學習機制完整版測試完成")
    print("💡 系統能夠:")
    print("   - 實時分析互動表現")
    print("   - 偵測成功和失敗模式")
    print("   - 評估各種風險")
    print("   - 生成具體改進建議")
    print("   - 自動調整 KOL 策略")
    print("   - 計算病毒傳播潛力")
    print("   - 評估品牌影響力")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
