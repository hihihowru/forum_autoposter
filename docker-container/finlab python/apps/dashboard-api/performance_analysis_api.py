"""
成效分析系統 API
取前10%成效好的貼文進行深度分析
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import asyncio
from dataclasses import dataclass, asdict
import statistics

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/performance-analysis", tags=["performance-analysis"])

# ==================== 數據模型 ====================

class PerformanceMetric(BaseModel):
    metric_name: str
    value: float
    unit: str
    trend: str  # 'up', 'down', 'stable'
    change_percentage: float
    significance: str  # 'high', 'medium', 'low'

class TopPostAnalysis(BaseModel):
    post_id: str
    article_id: str
    kol_nickname: str
    title: str
    content: str
    create_time: str
    total_interactions: int
    engagement_rate: float
    performance_score: float
    ranking: int
    key_features: List[str]
    success_factors: List[str]

class FeatureCorrelation(BaseModel):
    feature_pair: str
    correlation_score: float
    significance: str
    description: str
    recommendation: str

class PerformanceInsight(BaseModel):
    insight_id: str
    insight_type: str  # 'pattern', 'anomaly', 'opportunity', 'risk'
    title: str
    description: str
    confidence: float
    impact_score: float
    evidence: List[str]
    actionable_recommendations: List[str]
    affected_kols: List[str]

class PerformanceReport(BaseModel):
    analysis_period: str
    total_posts_analyzed: int
    top10_percent_count: int
    overall_performance_score: float
    performance_metrics: List[PerformanceMetric]
    top_posts_analysis: List[TopPostAnalysis]
    feature_correlations: List[FeatureCorrelation]
    insights: List[PerformanceInsight]
    summary: str
    timestamp: str

# ==================== 成效分析服務 ====================

class PerformanceAnalysisService:
    def __init__(self):
        self.analysis_cache = {}
        self.performance_thresholds = {
            'high_performance': 80,
            'medium_performance': 60,
            'low_performance': 40
        }
    
    async def analyze_top_performers(self, posts: List[Dict]) -> List[TopPostAnalysis]:
        """分析前10%高成效貼文"""
        if not posts:
            return []
        
        # 計算每篇貼文的成效分數
        scored_posts = []
        for post in posts:
            score = self._calculate_performance_score(post)
            scored_posts.append((post, score))
        
        # 按分數排序
        scored_posts.sort(key=lambda x: x[1], reverse=True)
        
        # 取前10%
        total_posts = len(scored_posts)
        top10_count = max(1, int(total_posts * 0.1))
        top_posts = scored_posts[:top10_count]
        
        # 分析每篇高成效貼文
        top_post_analyses = []
        for i, (post, score) in enumerate(top_posts):
            analysis = TopPostAnalysis(
                post_id=post.get('post_id', ''),
                article_id=post.get('article_id', ''),
                kol_nickname=post.get('kol_nickname', ''),
                title=post.get('title', ''),
                content=post.get('content', ''),
                create_time=post.get('create_time', ''),
                total_interactions=self._calculate_total_interactions(post),
                engagement_rate=post.get('engagement_rate', 0),
                performance_score=score,
                ranking=i + 1,
                key_features=self._extract_key_features(post),
                success_factors=self._identify_success_factors(post)
            )
            top_post_analyses.append(analysis)
        
        return top_post_analyses
    
    def _calculate_performance_score(self, post: Dict) -> float:
        """計算貼文成效分數"""
        # 基礎互動分數 (40%)
        total_interactions = self._calculate_total_interactions(post)
        interaction_score = min(total_interactions / 100, 1.0) * 40
        
        # 互動率分數 (30%)
        engagement_rate = post.get('engagement_rate', 0)
        engagement_score = min(engagement_rate / 10, 1.0) * 30
        
        # 內容品質分數 (20%)
        content_quality = self._assess_content_quality(post)
        quality_score = content_quality * 20
        
        # 時機分數 (10%)
        timing_score = self._assess_timing_score(post) * 10
        
        return interaction_score + engagement_score + quality_score + timing_score
    
    def _calculate_total_interactions(self, post: Dict) -> int:
        """計算總互動數"""
        return (post.get('likes', 0) or 0) + (post.get('comments', 0) or 0) + (post.get('shares', 0) or 0) + (post.get('bookmarks', 0) or 0)
    
    def _assess_content_quality(self, post: Dict) -> float:
        """評估內容品質"""
        title = post.get('title', '')
        content = post.get('content', '')
        full_text = f"{title} {content}"
        
        quality_score = 0.5  # 基礎分數
        
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
        
        # 包含數字
        if any(char.isdigit() for char in full_text):
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
            
            # 最佳發文時段
            if 9 <= hour <= 11 or 19 <= hour <= 21:
                return 1.0
            elif 14 <= hour <= 16:
                return 0.8
            elif 12 <= hour <= 13 or 22 <= hour <= 23:
                return 0.6
            else:
                return 0.4
        except:
            return 0.5
    
    def _extract_key_features(self, post: Dict) -> List[str]:
        """提取關鍵特徵"""
        features = []
        title = post.get('title', '')
        content = post.get('content', '')
        full_text = f"{title} {content}"
        
        # 發文時間特徵
        create_time = post.get('create_time', '')
        if create_time:
            try:
                post_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                hour = post_time.hour
                if 9 <= hour <= 11:
                    features.append('上午發文')
                elif 14 <= hour <= 16:
                    features.append('下午發文')
                elif 19 <= hour <= 21:
                    features.append('晚上發文')
            except:
                pass
        
        # 內容特徵
        if post.get('commodity_tags'):
            features.append('包含股票標記')
        
        if any(keyword in full_text for keyword in ['哈哈', '笑死', '搞笑', '幽默']):
            features.append('幽默內容')
        
        if any(emoji in full_text for emoji in ['😂', '😄', '😆']):
            features.append('使用Emoji')
        
        if any(keyword in full_text for keyword in ['？', '?']):
            features.append('互動引導')
        
        if len(content) >= 200:
            features.append('詳細內容')
        
        return features
    
    def _identify_success_factors(self, post: Dict) -> List[str]:
        """識別成功因素"""
        factors = []
        title = post.get('title', '')
        content = post.get('content', '')
        full_text = f"{title} {content}"
        
        # 高互動率
        engagement_rate = post.get('engagement_rate', 0)
        if engagement_rate > 5:
            factors.append('高互動率')
        
        # 內容長度適中
        if 200 <= len(content) <= 500:
            factors.append('內容長度適中')
        
        # 包含熱門話題
        if post.get('community_topic'):
            factors.append('熱門話題')
        
        # 系統發文
        if post.get('source') == 'system':
            factors.append('系統發文')
        
        # 包含數字
        if any(char.isdigit() for char in full_text):
            factors.append('數據支撐')
        
        return factors
    
    async def analyze_feature_correlations(self, top_posts: List[TopPostAnalysis]) -> List[FeatureCorrelation]:
        """分析特徵相關性"""
        correlations = []
        
        if len(top_posts) < 3:
            return correlations
        
        # 分析發文時間與成效的相關性
        time_correlations = self._analyze_time_correlation(top_posts)
        correlations.extend(time_correlations)
        
        # 分析內容特徵與成效的相關性
        content_correlations = self._analyze_content_correlation(top_posts)
        correlations.extend(content_correlations)
        
        # 分析KOL與成效的相關性
        kol_correlations = self._analyze_kol_correlation(top_posts)
        correlations.extend(kol_correlations)
        
        return correlations
    
    def _analyze_time_correlation(self, top_posts: List[TopPostAnalysis]) -> List[FeatureCorrelation]:
        """分析時間相關性"""
        correlations = []
        
        # 統計不同時段的成效
        time_performance = {'morning': [], 'afternoon': [], 'evening': [], 'night': []}
        
        for post in top_posts:
            try:
                post_time = datetime.fromisoformat(post.create_time.replace('Z', '+00:00'))
                hour = post_time.hour
                
                if 6 <= hour < 12:
                    time_performance['morning'].append(post.performance_score)
                elif 12 <= hour < 18:
                    time_performance['afternoon'].append(post.performance_score)
                elif 18 <= hour < 24:
                    time_performance['evening'].append(post.performance_score)
                else:
                    time_performance['night'].append(post.performance_score)
            except:
                continue
        
        # 計算各時段的平均成效
        for time_slot, scores in time_performance.items():
            if scores:
                avg_score = statistics.mean(scores)
                if avg_score > 70:
                    correlations.append(FeatureCorrelation(
                        feature_pair=f'發文時段-{time_slot}',
                        correlation_score=avg_score,
                        significance='high' if avg_score > 80 else 'medium',
                        description=f'{time_slot}時段發文成效較佳',
                        recommendation=f'建議在{time_slot}時段增加發文頻率'
                    ))
        
        return correlations
    
    def _analyze_content_correlation(self, top_posts: List[TopPostAnalysis]) -> List[FeatureCorrelation]:
        """分析內容相關性"""
        correlations = []
        
        # 統計不同內容特徵的成效
        feature_performance = {
            'has_stock_tags': [],
            'has_humor': [],
            'has_emoji': [],
            'has_interaction': [],
            'detailed_content': []
        }
        
        for post in top_posts:
            if '包含股票標記' in post.key_features:
                feature_performance['has_stock_tags'].append(post.performance_score)
            
            if '幽默內容' in post.key_features:
                feature_performance['has_humor'].append(post.performance_score)
            
            if '使用Emoji' in post.key_features:
                feature_performance['has_emoji'].append(post.performance_score)
            
            if '互動引導' in post.key_features:
                feature_performance['has_interaction'].append(post.performance_score)
            
            if '詳細內容' in post.key_features:
                feature_performance['detailed_content'].append(post.performance_score)
        
        # 計算各特徵的平均成效
        feature_names = {
            'has_stock_tags': '股票標記',
            'has_humor': '幽默內容',
            'has_emoji': 'Emoji使用',
            'has_interaction': '互動引導',
            'detailed_content': '詳細內容'
        }
        
        for feature, scores in feature_performance.items():
            if scores:
                avg_score = statistics.mean(scores)
                if avg_score > 70:
                    correlations.append(FeatureCorrelation(
                        feature_pair=feature_names[feature],
                        correlation_score=avg_score,
                        significance='high' if avg_score > 80 else 'medium',
                        description=f'{feature_names[feature]}與高成效相關',
                        recommendation=f'建議增加{feature_names[feature]}的使用'
                    ))
        
        return correlations
    
    def _analyze_kol_correlation(self, top_posts: List[TopPostAnalysis]) -> List[FeatureCorrelation]:
        """分析KOL相關性"""
        correlations = []
        
        # 統計不同KOL的成效
        kol_performance = {}
        
        for post in top_posts:
            kol_name = post.kol_nickname
            if kol_name not in kol_performance:
                kol_performance[kol_name] = []
            kol_performance[kol_name].append(post.performance_score)
        
        # 計算各KOL的平均成效
        for kol_name, scores in kol_performance.items():
            if len(scores) >= 2:  # 至少2篇貼文
                avg_score = statistics.mean(scores)
                if avg_score > 70:
                    correlations.append(FeatureCorrelation(
                        feature_pair=f'KOL-{kol_name}',
                        correlation_score=avg_score,
                        significance='high' if avg_score > 80 else 'medium',
                        description=f'{kol_name}的貼文成效較佳',
                        recommendation=f'建議增加{kol_name}的發文頻率'
                    ))
        
        return correlations
    
    async def generate_performance_insights(self, top_posts: List[TopPostAnalysis], correlations: List[FeatureCorrelation]) -> List[PerformanceInsight]:
        """生成成效洞察"""
        insights = []
        
        if not top_posts:
            return insights
        
        # 分析成效模式
        pattern_insights = self._analyze_performance_patterns(top_posts)
        insights.extend(pattern_insights)
        
        # 分析異常情況
        anomaly_insights = self._analyze_performance_anomalies(top_posts)
        insights.extend(anomaly_insights)
        
        # 分析機會
        opportunity_insights = self._analyze_opportunities(top_posts, correlations)
        insights.extend(opportunity_insights)
        
        # 分析風險
        risk_insights = self._analyze_risks(top_posts)
        insights.extend(risk_insights)
        
        return insights
    
    def _analyze_performance_patterns(self, top_posts: List[TopPostAnalysis]) -> List[PerformanceInsight]:
        """分析成效模式"""
        insights = []
        
        # 分析發文時間模式
        time_patterns = {}
        for post in top_posts:
            try:
                post_time = datetime.fromisoformat(post.create_time.replace('Z', '+00:00'))
                hour = post_time.hour
                time_slot = 'morning' if 6 <= hour < 12 else 'afternoon' if 12 <= hour < 18 else 'evening' if 18 <= hour < 24 else 'night'
                
                if time_slot not in time_patterns:
                    time_patterns[time_slot] = []
                time_patterns[time_slot].append(post.performance_score)
            except:
                continue
        
        # 找出最佳時段
        best_time_slot = max(time_patterns.keys(), key=lambda k: statistics.mean(time_patterns[k])) if time_patterns else None
        if best_time_slot:
            insights.append(PerformanceInsight(
                insight_id='pattern_1',
                insight_type='pattern',
                title='發文時間模式分析',
                description=f'{best_time_slot}時段發文成效最佳，平均分數{statistics.mean(time_patterns[best_time_slot]):.1f}',
                confidence=0.85,
                impact_score=0.8,
                evidence=[f'{best_time_slot}時段有{len(time_patterns[best_time_slot])}篇高成效貼文'],
                actionable_recommendations=[f'建議在{best_time_slot}時段增加發文頻率'],
                affected_kols=list(set(post.kol_nickname for post in top_posts))
            ))
        
        return insights
    
    def _analyze_performance_anomalies(self, top_posts: List[TopPostAnalysis]) -> List[PerformanceInsight]:
        """分析異常情況"""
        insights = []
        
        # 分析超高成效貼文
        high_performers = [post for post in top_posts if post.performance_score > 90]
        if high_performers:
            insights.append(PerformanceInsight(
                insight_id='anomaly_1',
                insight_type='anomaly',
                title='超高成效貼文分析',
                description=f'發現{len(high_performers)}篇超高成效貼文，平均分數{statistics.mean([p.performance_score for p in high_performers]):.1f}',
                confidence=0.9,
                impact_score=0.9,
                evidence=[f'超高成效貼文佔比{len(high_performers)/len(top_posts)*100:.1f}%'],
                actionable_recommendations=['分析超高成效貼文的共同特徵', '複製成功模式到其他貼文'],
                affected_kols=list(set(post.kol_nickname for post in high_performers))
            ))
        
        return insights
    
    def _analyze_opportunities(self, top_posts: List[TopPostAnalysis], correlations: List[FeatureCorrelation]) -> List[PerformanceInsight]:
        """分析機會"""
        insights = []
        
        # 分析未充分利用的特徵
        all_features = set()
        for post in top_posts:
            all_features.update(post.key_features)
        
        # 找出高相關性但使用率低的特徵
        for correlation in correlations:
            if correlation.significance == 'high':
                insights.append(PerformanceInsight(
                    insight_id='opportunity_1',
                    insight_type='opportunity',
                    title='高成效特徵機會',
                    description=f'{correlation.feature_pair}與高成效相關，建議增加使用',
                    confidence=correlation.correlation_score / 100,
                    impact_score=0.7,
                    evidence=[f'{correlation.feature_pair}相關性分數{correlation.correlation_score:.1f}'],
                    actionable_recommendations=[correlation.recommendation],
                    affected_kols=list(set(post.kol_nickname for post in top_posts))
                ))
        
        return insights
    
    def _analyze_risks(self, top_posts: List[TopPostAnalysis]) -> List[PerformanceInsight]:
        """分析風險"""
        insights = []
        
        # 分析KOL依賴風險
        kol_counts = {}
        for post in top_posts:
            kol_name = post.kol_nickname
            kol_counts[kol_name] = kol_counts.get(kol_name, 0) + 1
        
        # 找出過度依賴的KOL
        total_posts = len(top_posts)
        for kol_name, count in kol_counts.items():
            if count / total_posts > 0.5:  # 超過50%
                insights.append(PerformanceInsight(
                    insight_id='risk_1',
                    insight_type='risk',
                    title='KOL依賴風險',
                    description=f'{kol_name}佔高成效貼文{count/total_posts*100:.1f}%，存在過度依賴風險',
                    confidence=0.8,
                    impact_score=0.6,
                    evidence=[f'{kol_name}貢獻了{count}篇高成效貼文'],
                    actionable_recommendations=['分散發文風險', '培養其他KOL'],
                    affected_kols=[kol_name]
                ))
        
        return insights
    
    async def generate_performance_report(self, posts: List[Dict]) -> PerformanceReport:
        """生成成效分析報告"""
        # 分析前10%高成效貼文
        top_posts = await self.analyze_top_performers(posts)
        
        # 分析特徵相關性
        correlations = await self.analyze_feature_correlations(top_posts)
        
        # 生成洞察
        insights = await self.generate_performance_insights(top_posts, correlations)
        
        # 計算整體成效指標
        performance_metrics = self._calculate_performance_metrics(posts, top_posts)
        
        # 生成總結
        summary = self._generate_summary(top_posts, correlations, insights)
        
        return PerformanceReport(
            analysis_period=f"最近{len(posts)}篇貼文",
            total_posts_analyzed=len(posts),
            top10_percent_count=len(top_posts),
            overall_performance_score=statistics.mean([post.performance_score for post in top_posts]) if top_posts else 0,
            performance_metrics=performance_metrics,
            top_posts_analysis=top_posts,
            feature_correlations=correlations,
            insights=insights,
            summary=summary,
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_performance_metrics(self, all_posts: List[Dict], top_posts: List[TopPostAnalysis]) -> List[PerformanceMetric]:
        """計算成效指標"""
        metrics = []
        
        if not all_posts:
            return metrics
        
        # 平均互動數
        avg_interactions = statistics.mean([self._calculate_total_interactions(post) for post in all_posts])
        metrics.append(PerformanceMetric(
            metric_name='平均互動數',
            value=avg_interactions,
            unit='次',
            trend='stable',
            change_percentage=0,
            significance='medium'
        ))
        
        # 平均互動率
        avg_engagement_rate = statistics.mean([post.get('engagement_rate', 0) for post in all_posts])
        metrics.append(PerformanceMetric(
            metric_name='平均互動率',
            value=avg_engagement_rate,
            unit='%',
            trend='stable',
            change_percentage=0,
            significance='high'
        ))
        
        # 高成效貼文比例
        high_performance_ratio = len(top_posts) / len(all_posts) * 100
        metrics.append(PerformanceMetric(
            metric_name='高成效貼文比例',
            value=high_performance_ratio,
            unit='%',
            trend='stable',
            change_percentage=0,
            significance='high'
        ))
        
        return metrics
    
    def _generate_summary(self, top_posts: List[TopPostAnalysis], correlations: List[FeatureCorrelation], insights: List[PerformanceInsight]) -> str:
        """生成總結"""
        if not top_posts:
            return "暫無高成效貼文數據"
        
        summary_parts = []
        
        # 基本統計
        summary_parts.append(f"分析了{len(top_posts)}篇高成效貼文")
        
        # 最佳KOL
        kol_counts = {}
        for post in top_posts:
            kol_counts[post.kol_nickname] = kol_counts.get(post.kol_nickname, 0) + 1
        
        best_kol = max(kol_counts.keys(), key=lambda k: kol_counts[k]) if kol_counts else None
        if best_kol:
            summary_parts.append(f"最佳KOL: {best_kol}")
        
        # 關鍵特徵
        if correlations:
            top_correlation = max(correlations, key=lambda c: c.correlation_score)
            summary_parts.append(f"關鍵特徵: {top_correlation.feature_pair}")
        
        # 主要洞察
        if insights:
            high_impact_insights = [i for i in insights if i.impact_score > 0.7]
            if high_impact_insights:
                summary_parts.append(f"主要洞察: {high_impact_insights[0].title}")
        
        return "；".join(summary_parts)

# 全局服務實例
performance_service = PerformanceAnalysisService()

# ==================== API 端點 ====================

@router.get("/report")
async def get_performance_report(
    kol_serial: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_external: bool = True
):
    """獲取成效分析報告"""
    try:
        # 這裡應該從實際數據源獲取貼文數據
        # 暫時使用模擬數據
        mock_posts = [
            {
                'post_id': '1',
                'article_id': 'A001',
                'kol_nickname': '龜狗一日散戶',
                'title': '測試標題1',
                'content': '測試內容1',
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
                'title': '測試標題2',
                'content': '測試內容2',
                'create_time': '2024-12-19T14:00:00Z',
                'likes': 80,
                'comments': 30,
                'shares': 15,
                'bookmarks': 8,
                'engagement_rate': 12.3,
                'source': 'system',
                'commodity_tags': [{'key': '2317', 'type': 'stock', 'bullOrBear': '1'}]
            }
        ]
        
        report = await performance_service.generate_performance_report(mock_posts)
        
        return {
            "success": True,
            "data": report.dict()
        }
        
    except Exception as e:
        logger.error(f"獲取成效分析報告失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取成效分析報告失敗: {str(e)}")

@router.get("/top-posts")
async def get_top_performers(
    limit: int = 10,
    kol_serial: Optional[int] = None
):
    """獲取高成效貼文列表"""
    try:
        # 這裡應該從實際數據源獲取數據
        mock_posts = [
            {
                'post_id': '1',
                'article_id': 'A001',
                'kol_nickname': '龜狗一日散戶',
                'title': '測試標題1',
                'content': '測試內容1',
                'create_time': '2024-12-19T10:00:00Z',
                'likes': 50,
                'comments': 20,
                'shares': 10,
                'bookmarks': 5,
                'engagement_rate': 8.5,
                'source': 'system',
                'commodity_tags': [{'key': '2330', 'type': 'stock', 'bullOrBear': '0'}]
            }
        ]
        
        top_posts = await performance_service.analyze_top_performers(mock_posts)
        
        return {
            "success": True,
            "data": [post.dict() for post in top_posts[:limit]]
        }
        
    except Exception as e:
        logger.error(f"獲取高成效貼文失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取高成效貼文失敗: {str(e)}")

@router.get("/correlations")
async def get_feature_correlations():
    """獲取特徵相關性分析"""
    try:
        # 這裡應該從實際數據源獲取數據
        mock_posts = [
            {
                'post_id': '1',
                'article_id': 'A001',
                'kol_nickname': '龜狗一日散戶',
                'title': '測試標題1',
                'content': '測試內容1',
                'create_time': '2024-12-19T10:00:00Z',
                'likes': 50,
                'comments': 20,
                'shares': 10,
                'bookmarks': 5,
                'engagement_rate': 8.5,
                'source': 'system',
                'commodity_tags': [{'key': '2330', 'type': 'stock', 'bullOrBear': '0'}]
            }
        ]
        
        top_posts = await performance_service.analyze_top_performers(mock_posts)
        correlations = await performance_service.analyze_feature_correlations(top_posts)
        
        return {
            "success": True,
            "data": [correlation.dict() for correlation in correlations]
        }
        
    except Exception as e:
        logger.error(f"獲取特徵相關性失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取特徵相關性失敗: {str(e)}")

@router.get("/insights")
async def get_performance_insights():
    """獲取成效洞察"""
    try:
        # 這裡應該從實際數據源獲取數據
        mock_posts = [
            {
                'post_id': '1',
                'article_id': 'A001',
                'kol_nickname': '龜狗一日散戶',
                'title': '測試標題1',
                'content': '測試內容1',
                'create_time': '2024-12-19T10:00:00Z',
                'likes': 50,
                'comments': 20,
                'shares': 10,
                'bookmarks': 5,
                'engagement_rate': 8.5,
                'source': 'system',
                'commodity_tags': [{'key': '2330', 'type': 'stock', 'bullOrBear': '0'}]
            }
        ]
        
        top_posts = await performance_service.analyze_top_performers(mock_posts)
        correlations = await performance_service.analyze_feature_correlations(top_posts)
        insights = await performance_service.generate_performance_insights(top_posts, correlations)
        
        return {
            "success": True,
            "data": [insight.dict() for insight in insights]
        }
        
    except Exception as e:
        logger.error(f"獲取成效洞察失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取成效洞察失敗: {str(e)}")

@router.get("/metrics")
async def get_performance_metrics():
    """獲取成效指標"""
    try:
        # 這裡應該從實際數據源獲取數據
        mock_posts = [
            {
                'post_id': '1',
                'article_id': 'A001',
                'kol_nickname': '龜狗一日散戶',
                'title': '測試標題1',
                'content': '測試內容1',
                'create_time': '2024-12-19T10:00:00Z',
                'likes': 50,
                'comments': 20,
                'shares': 10,
                'bookmarks': 5,
                'engagement_rate': 8.5,
                'source': 'system',
                'commodity_tags': [{'key': '2330', 'type': 'stock', 'bullOrBear': '0'}]
            }
        ]
        
        top_posts = await performance_service.analyze_top_performers(mock_posts)
        metrics = performance_service._calculate_performance_metrics(mock_posts, top_posts)
        
        return {
            "success": True,
            "data": [metric.dict() for metric in metrics]
        }
        
    except Exception as e:
        logger.error(f"獲取成效指標失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取成效指標失敗: {str(e)}")





