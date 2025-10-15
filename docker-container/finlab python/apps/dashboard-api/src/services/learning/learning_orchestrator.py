"""
學習協調器
整合所有學習模組，提供統一的學習服務接口
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

from .learning_engine import LearningEngine, LearningMetrics, LearningInsight, KOLStrategy
from .ai_detection_service import AIDetectionService, AIDetectionResult
from .engagement_analyzer import EngagementAnalyzer, EngagementMetrics, EngagementInsight
from .content_analyzer import ContentAnalyzer, ContentFeatures, ContentPattern, ContentInsight
from .enhanced_content_analyzer import EnhancedContentAnalyzer, EnhancedContentFeatures, ContentOptimization

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class LearningSession:
    """學習會話"""
    session_id: str
    kol_id: str
    content_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = 'running'  # 'running', 'completed', 'failed'
    results: Dict[str, Any] = None

@dataclass
class LearningReport:
    """學習報告"""
    report_id: str
    kol_id: str
    period_start: datetime
    period_end: datetime
    total_posts: int
    avg_engagement_score: float
    avg_ai_detection_score: float
    insights: List[LearningInsight]
    recommendations: List[str]
    strategy_updates: Dict[str, Any]
    generated_at: datetime

class LearningOrchestrator:
    """學習協調器"""
    
    def __init__(self):
        self.learning_engine = LearningEngine()
        self.ai_detection_service = AIDetectionService()
        self.engagement_analyzer = EngagementAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.enhanced_content_analyzer = EnhancedContentAnalyzer()
        
        self.active_sessions = {}
        self.learning_history = []
        
        logger.info("學習協調器初始化完成")
    
    async def start_learning_session(self, kol_id: str, content_id: str) -> str:
        """開始學習會話"""
        session_id = f"session_{kol_id}_{content_id}_{datetime.now().timestamp()}"
        
        session = LearningSession(
            session_id=session_id,
            kol_id=kol_id,
            content_id=content_id,
            start_time=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"開始學習會話: {session_id}")
        return session_id
    
    async def process_interaction_data(self, session_id: str, interaction_data: Dict) -> Dict[str, Any]:
        """處理互動數據"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"找不到學習會話: {session_id}")
            
            # 1. AI偵測分析
            ai_detection_result = await self._analyze_ai_detection(interaction_data)
            
            # 2. 互動成效分析
            engagement_metrics = await self._analyze_engagement(interaction_data)
            
            # 3. 學習引擎分析
            learning_metrics = await self._analyze_learning_metrics(interaction_data, ai_detection_result, engagement_metrics)
            
            # 4. 增強版內容分析
            enhanced_content_features = await self._analyze_enhanced_content(interaction_data)
            
            # 5. 生成洞察
            insights = await self._generate_insights(learning_metrics, engagement_metrics, enhanced_content_features)
            
            # 6. 更新策略
            strategy_updates = await self._update_strategies(insights)
            
            # 7. 保存結果
            results = {
                'ai_detection': asdict(ai_detection_result),
                'engagement_metrics': asdict(engagement_metrics[0]) if engagement_metrics else {},
                'learning_metrics': asdict(learning_metrics[0]) if learning_metrics else {},
                'enhanced_content_features': asdict(enhanced_content_features) if enhanced_content_features else {},
                'insights': [asdict(insight) for insight in insights],
                'strategy_updates': strategy_updates
            }
            
            session.results = results
            session.status = 'completed'
            session.end_time = datetime.now()
            
            # 移動到歷史記錄
            self.learning_history.append(session)
            del self.active_sessions[session_id]
            
            logger.info(f"學習會話完成: {session_id}")
            return results
            
        except Exception as e:
            logger.error(f"處理互動數據失敗: {e}")
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = 'failed'
            raise
    
    async def _analyze_ai_detection(self, interaction_data: Dict) -> AIDetectionResult:
        """分析AI偵測"""
        content = interaction_data.get('generated_content', '')
        content_id = interaction_data.get('content_id', '')
        
        return await self.ai_detection_service.detect_ai_content(content, content_id)
    
    async def _analyze_engagement(self, interaction_data: Dict) -> List[EngagementMetrics]:
        """分析互動成效"""
        return await self.engagement_analyzer.analyze_engagement_data([interaction_data])
    
    async def _analyze_learning_metrics(self, interaction_data: Dict, 
                                      ai_detection_result: AIDetectionResult,
                                      engagement_metrics: List[EngagementMetrics]) -> List[LearningMetrics]:
        """分析學習指標"""
        # 整合AI偵測和互動分析結果
        enhanced_data = {
            **interaction_data,
            'ai_detection_score': ai_detection_result.detection_score,
            'engagement_score': engagement_metrics[0].engagement_rate if engagement_metrics else 0.0
        }
        
        return await self.learning_engine.analyze_interaction_effectiveness([enhanced_data])
    
    async def _analyze_enhanced_content(self, interaction_data: Dict) -> Optional[EnhancedContentFeatures]:
        """分析增強版內容特徵"""
        content = interaction_data.get('generated_content', '')
        content_id = interaction_data.get('content_id', '')
        
        if not content:
            return None
        
        return await self.enhanced_content_analyzer.analyze_content(content, content_id)
    
    async def _generate_insights(self, learning_metrics: List[LearningMetrics], 
                               engagement_metrics: List[EngagementMetrics],
                               enhanced_content_features: Optional[EnhancedContentFeatures] = None) -> List[LearningInsight]:
        """生成學習洞察"""
        # 從學習引擎生成洞察
        learning_insights = await self.learning_engine.generate_learning_insights(learning_metrics)
        
        # 從互動分析器生成洞察
        engagement_insights = await self.engagement_analyzer.generate_engagement_insights(engagement_metrics)
        
        # 從增強版內容分析生成洞察
        content_insights = []
        if enhanced_content_features:
            content_insights = await self._generate_content_insights(enhanced_content_features)
        
        # 合併洞察
        all_insights = learning_insights + engagement_insights + content_insights
        
        # 按重要性排序
        all_insights.sort(key=lambda x: x.expected_improvement, reverse=True)
        
        return all_insights
    
    async def _generate_content_insights(self, features: EnhancedContentFeatures) -> List[LearningInsight]:
        """生成內容洞察"""
        insights = []
        
        # 基於增強版內容特徵生成洞察
        if features.total_engagement_score < 0.4:
            insight = LearningInsight(
                insight_type='content_optimization',
                kol_id='',  # 會在調用時設置
                description=f"內容互動潛力較低 ({features.total_engagement_score:.2f})，需要優化內容特徵",
                confidence=0.8,
                recommended_action="增加個人化表達、互動元素和創意表達",
                expected_improvement=0.3,
                created_at=datetime.now()
            )
            insights.append(insight)
        
        # 個人化表達洞察
        if features.personal_score < 0.3:
            insight = LearningInsight(
                insight_type='personalization_improvement',
                kol_id='',
                description=f"個人化表達不足 ({features.personal_score:.2f})，缺乏個人觀點",
                confidence=0.7,
                recommended_action="增加「我認為」、「我的看法」等個人化表達",
                expected_improvement=0.2,
                created_at=datetime.now()
            )
            insights.append(insight)
        
        # 互動引導洞察
        if features.interaction_score < 0.3:
            insight = LearningInsight(
                insight_type='interaction_improvement',
                kol_id='',
                description=f"互動引導不足 ({features.interaction_score:.2f})，缺乏讀者參與元素",
                confidence=0.7,
                recommended_action="添加問題引導或行動呼籲，如「你覺得呢？」",
                expected_improvement=0.25,
                created_at=datetime.now()
            )
            insights.append(insight)
        
        return insights
    
    async def _update_strategies(self, insights: List[LearningInsight]) -> Dict[str, Any]:
        """更新策略"""
        return await self.learning_engine.update_kol_strategies(insights)
    
    async def generate_learning_report(self, kol_id: str, days: int = 7) -> LearningReport:
        """生成學習報告"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # 獲取期間內的學習會話
            period_sessions = [
                session for session in self.learning_history
                if session.kol_id == kol_id and start_time <= session.start_time <= end_time
            ]
            
            if not period_sessions:
                return LearningReport(
                    report_id=f"report_{kol_id}_{datetime.now().timestamp()}",
                    kol_id=kol_id,
                    period_start=start_time,
                    period_end=end_time,
                    total_posts=0,
                    avg_engagement_score=0.0,
                    avg_ai_detection_score=0.0,
                    insights=[],
                    recommendations=[],
                    strategy_updates={},
                    generated_at=datetime.now()
                )
            
            # 計算統計數據
            total_posts = len(period_sessions)
            engagement_scores = []
            ai_detection_scores = []
            all_insights = []
            
            for session in period_sessions:
                if session.results:
                    engagement_scores.append(session.results.get('engagement_metrics', {}).get('engagement_rate', 0))
                    ai_detection_scores.append(session.results.get('ai_detection', {}).get('detection_score', 0))
                    all_insights.extend(session.results.get('insights', []))
            
            avg_engagement_score = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0
            avg_ai_detection_score = sum(ai_detection_scores) / len(ai_detection_scores) if ai_detection_scores else 0.0
            
            # 生成建議
            recommendations = self._generate_recommendations(all_insights, avg_engagement_score, avg_ai_detection_score)
            
            # 獲取策略更新
            strategy_updates = self.learning_engine.get_kol_strategy(kol_id)
            strategy_dict = asdict(strategy_updates) if strategy_updates else {}
            
            report = LearningReport(
                report_id=f"report_{kol_id}_{datetime.now().timestamp()}",
                kol_id=kol_id,
                period_start=start_time,
                period_end=end_time,
                total_posts=total_posts,
                avg_engagement_score=avg_engagement_score,
                avg_ai_detection_score=avg_ai_detection_score,
                insights=all_insights,
                recommendations=recommendations,
                strategy_updates=strategy_dict,
                generated_at=datetime.now()
            )
            
            logger.info(f"生成學習報告: {report.report_id}")
            return report
            
        except Exception as e:
            logger.error(f"生成學習報告失敗: {e}")
            raise
    
    def _generate_recommendations(self, insights: List[Dict], avg_engagement: float, avg_ai_detection: float) -> List[str]:
        """生成建議"""
        recommendations = []
        
        # 基於洞察生成建議
        for insight in insights:
            if insight.get('expected_improvement', 0) > 0.1:
                recommendations.append(insight.get('recommended_action', ''))
        
        # 基於整體表現生成建議
        if avg_engagement < 0.03:
            recommendations.append("整體互動率偏低，建議調整內容策略，增加互動元素")
        
        if avg_ai_detection > 0.4:
            recommendations.append("AI偵測風險較高，建議增加更多個人化表達和情感元素")
        
        # 去重並限制數量
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:5]
    
    async def batch_process_historical_data(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """批量處理歷史數據"""
        try:
            logger.info(f"開始批量處理 {len(historical_data)} 筆歷史數據")
            
            # 按KOL分組
            kol_groups = {}
            for data in historical_data:
                kol_id = data.get('kol_id', 'unknown')
                if kol_id not in kol_groups:
                    kol_groups[kol_id] = []
                kol_groups[kol_id].append(data)
            
            results = {}
            
            for kol_id, kol_data in kol_groups.items():
                logger.info(f"處理KOL {kol_id} 的 {len(kol_data)} 筆數據")
                
                # 批量AI偵測
                ai_results = await self.ai_detection_service.batch_analyze_content(kol_data)
                
                # 批量互動分析
                engagement_results = await self.engagement_analyzer.analyze_engagement_data(kol_data)
                
                # 整合數據進行學習
                enhanced_data = []
                for i, data in enumerate(kol_data):
                    enhanced_data.append({
                        **data,
                        'ai_detection_score': ai_results[i].detection_score if i < len(ai_results) else 0.0,
                        'engagement_score': engagement_results[i].engagement_rate if i < len(engagement_results) else 0.0
                    })
                
                # 學習分析
                learning_metrics = await self.learning_engine.analyze_interaction_effectiveness(enhanced_data)
                insights = await self.learning_engine.generate_learning_insights(learning_metrics)
                strategy_updates = await self.learning_engine.update_kol_strategies(insights)
                
                results[kol_id] = {
                    'total_posts': len(kol_data),
                    'ai_detection_summary': self.ai_detection_service.get_detection_summary(ai_results),
                    'engagement_summary': self.engagement_analyzer.get_performance_summary(kol_id),
                    'insights_count': len(insights),
                    'strategy_updated': bool(strategy_updates)
                }
            
            logger.info("批量處理完成")
            return results
            
        except Exception as e:
            logger.error(f"批量處理歷史數據失敗: {e}")
            raise
    
    async def train_models(self, training_data: List[Dict]) -> Dict[str, Any]:
        """訓練模型"""
        try:
            logger.info(f"開始訓練模型，數據量: {len(training_data)}")
            
            # 準備訓練數據
            enhanced_training_data = []
            for data in training_data:
                # 添加計算特徵
                enhanced_data = {
                    **data,
                    'content_length': len(data.get('generated_content', '')),
                    'has_images': 1 if data.get('has_images', False) else 0,
                    'has_hashtags': 1 if '#' in data.get('generated_content', '') else 0,
                    'posting_hour': datetime.fromisoformat(data.get('posting_time', datetime.now().isoformat())).hour,
                    'topic_heat': data.get('topic_heat', 0.5),
                    'kol_experience': data.get('kol_experience', 0.5)
                }
                enhanced_training_data.append(enhanced_data)
            
            # 訓練模型
            await self.learning_engine.train_models(enhanced_training_data)
            
            logger.info("模型訓練完成")
            return {
                'status': 'success',
                'training_samples': len(enhanced_training_data),
                'models_trained': ['engagement_model', 'ai_detection_model']
            }
            
        except Exception as e:
            logger.error(f"模型訓練失敗: {e}")
            raise
    
    def get_learning_dashboard(self) -> Dict[str, Any]:
        """獲取學習儀表板"""
        return {
            'active_sessions': len(self.active_sessions),
            'total_sessions': len(self.learning_history),
            'learning_engine_summary': self.learning_engine.get_learning_summary(),
            'recent_insights': [
                {
                    'kol_id': session.kol_id,
                    'content_id': session.content_id,
                    'insights_count': len(session.results.get('insights', [])) if session.results else 0,
                    'timestamp': session.start_time.isoformat()
                }
                for session in self.learning_history[-10:]  # 最近10個會話
            ],
            'system_health': {
                'ai_detection_service': 'healthy',
                'engagement_analyzer': 'healthy',
                'learning_engine': 'healthy'
            }
        }
    
    def get_kol_learning_status(self, kol_id: str) -> Dict[str, Any]:
        """獲取KOL學習狀態"""
        kol_sessions = [s for s in self.learning_history if s.kol_id == kol_id]
        
        if not kol_sessions:
            return {
                'kol_id': kol_id,
                'total_sessions': 0,
                'last_learning': None,
                'strategy': None,
                'status': 'no_data'
            }
        
        latest_session = max(kol_sessions, key=lambda s: s.start_time)
        strategy = self.learning_engine.get_kol_strategy(kol_id)
        
        return {
            'kol_id': kol_id,
            'total_sessions': len(kol_sessions),
            'last_learning': latest_session.start_time.isoformat(),
            'strategy': asdict(strategy) if strategy else None,
            'status': 'active' if latest_session.status == 'completed' else 'pending'
        }
