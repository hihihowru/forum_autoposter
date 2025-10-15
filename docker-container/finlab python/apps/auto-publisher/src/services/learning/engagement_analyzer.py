"""
互動成效分析模組
分析KOL內容的互動表現，識別成功模式和改進機會
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class EngagementMetrics:
    """互動指標"""
    content_id: str
    kol_id: str
    content_type: str
    topic_category: str
    posting_time: datetime
    
    # 基礎互動數據
    likes_count: int
    comments_count: int
    shares_count: int
    saves_count: int
    views_count: int
    
    # 計算指標
    engagement_rate: float
    comment_rate: float
    share_rate: float
    save_rate: float
    
    # 品質指標
    avg_comment_length: float
    positive_sentiment_ratio: float
    reply_rate: float
    
    # 時間指標
    peak_engagement_hour: int
    engagement_decay_rate: float
    
    analyzed_at: datetime

@dataclass
class EngagementInsight:
    """互動洞察"""
    insight_type: str  # 'performance', 'timing', 'content', 'audience'
    kol_id: str
    description: str
    confidence: float
    data_points: int
    recommendation: str
    expected_impact: float
    created_at: datetime

@dataclass
class PerformanceBenchmark:
    """表現基準"""
    metric_name: str
    kol_id: str
    current_value: float
    benchmark_value: float
    percentile: float
    trend: str  # 'improving', 'stable', 'declining'
    comparison_period: str

class EngagementAnalyzer:
    """互動成效分析器"""
    
    def __init__(self):
        self.engagement_history = []
        self.benchmarks = {}
        self.performance_trends = {}
        
        # 行業基準值
        self.industry_benchmarks = {
            'engagement_rate': 0.05,  # 5%
            'comment_rate': 0.01,     # 1%
            'share_rate': 0.005,      # 0.5%
            'save_rate': 0.002,       # 0.2%
            'avg_comment_length': 20,
            'positive_sentiment_ratio': 0.6,
            'reply_rate': 0.3
        }
    
    async def analyze_engagement_data(self, interaction_data: List[Dict]) -> List[EngagementMetrics]:
        """
        分析互動數據
        
        Args:
            interaction_data: 互動數據列表
            
        Returns:
            互動指標列表
        """
        metrics_list = []
        
        for data in interaction_data:
            try:
                metrics = self._calculate_engagement_metrics(data)
                metrics_list.append(metrics)
                
            except Exception as e:
                logger.error(f"分析互動數據失敗: {e}")
                continue
        
        # 更新歷史數據
        self.engagement_history.extend(metrics_list)
        
        return metrics_list
    
    def _calculate_engagement_metrics(self, data: Dict) -> EngagementMetrics:
        """計算互動指標"""
        # 基礎數據
        likes = data.get('likes_count', 0)
        comments = data.get('comments_count', 0)
        shares = data.get('shares_count', 0)
        saves = data.get('saves_count', 0)
        views = max(data.get('views_count', 1), 1)  # 避免除零
        
        # 計算比率
        engagement_rate = (likes + comments + shares + saves) / views
        comment_rate = comments / views
        share_rate = shares / views
        save_rate = saves / views
        
        # 分析留言品質
        comments_data = data.get('comments', [])
        avg_comment_length = self._calculate_avg_comment_length(comments_data)
        positive_sentiment_ratio = self._calculate_sentiment_ratio(comments_data)
        reply_rate = self._calculate_reply_rate(comments_data)
        
        # 分析時間模式
        posting_time = datetime.fromisoformat(data.get('posting_time', datetime.now().isoformat()))
        peak_hour = self._find_peak_engagement_hour(data)
        decay_rate = self._calculate_engagement_decay(data)
        
        return EngagementMetrics(
            content_id=data.get('content_id', ''),
            kol_id=data.get('kol_id', ''),
            content_type=data.get('content_type', ''),
            topic_category=data.get('topic_category', ''),
            posting_time=posting_time,
            likes_count=likes,
            comments_count=comments,
            shares_count=shares,
            saves_count=saves,
            views_count=views,
            engagement_rate=engagement_rate,
            comment_rate=comment_rate,
            share_rate=share_rate,
            save_rate=save_rate,
            avg_comment_length=avg_comment_length,
            positive_sentiment_ratio=positive_sentiment_ratio,
            reply_rate=reply_rate,
            peak_engagement_hour=peak_hour,
            engagement_decay_rate=decay_rate,
            analyzed_at=datetime.now()
        )
    
    def _calculate_avg_comment_length(self, comments: List[Dict]) -> float:
        """計算平均留言長度"""
        if not comments:
            return 0.0
        
        total_length = sum(len(comment.get('content', '')) for comment in comments)
        return total_length / len(comments)
    
    def _calculate_sentiment_ratio(self, comments: List[Dict]) -> float:
        """計算正面情感比例"""
        if not comments:
            return 0.5
        
        positive_count = 0
        for comment in comments:
            content = comment.get('content', '').lower()
            if self._is_positive_sentiment(content):
                positive_count += 1
        
        return positive_count / len(comments)
    
    def _is_positive_sentiment(self, content: str) -> bool:
        """判斷是否為正面情感"""
        positive_words = ['好', '棒', '讚', '厲害', '支持', '認同', '同意', '喜歡', '愛', '感謝']
        negative_words = ['爛', '差', '反對', '不同意', '質疑', '懷疑', '討厭', '恨', '垃圾']
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        return positive_count > negative_count
    
    def _calculate_reply_rate(self, comments: List[Dict]) -> float:
        """計算回覆率"""
        if not comments:
            return 0.0
        
        reply_count = sum(1 for comment in comments if comment.get('is_reply', False))
        return reply_count / len(comments)
    
    def _find_peak_engagement_hour(self, data: Dict) -> int:
        """找出互動高峰時段"""
        # 簡化實現，返回發文時間的小時
        posting_time = datetime.fromisoformat(data.get('posting_time', datetime.now().isoformat()))
        return posting_time.hour
    
    def _calculate_engagement_decay(self, data: Dict) -> float:
        """計算互動衰減率"""
        # 簡化實現，基於時間間隔計算
        posting_time = datetime.fromisoformat(data.get('posting_time', datetime.now().isoformat()))
        current_time = datetime.now()
        hours_elapsed = (current_time - posting_time).total_seconds() / 3600
        
        if hours_elapsed == 0:
            return 0.0
        
        # 假設互動在24小時內衰減
        decay_rate = min(hours_elapsed / 24, 1.0)
        return decay_rate
    
    async def generate_engagement_insights(self, metrics: List[EngagementMetrics]) -> List[EngagementInsight]:
        """生成互動洞察"""
        insights = []
        
        # 按KOL分組分析
        kol_groups = {}
        for metric in metrics:
            if metric.kol_id not in kol_groups:
                kol_groups[metric.kol_id] = []
            kol_groups[metric.kol_id].append(metric)
        
        for kol_id, kol_metrics in kol_groups.items():
            # 表現分析
            performance_insights = self._analyze_performance(kol_id, kol_metrics)
            insights.extend(performance_insights)
            
            # 時機分析
            timing_insights = self._analyze_timing(kol_id, kol_metrics)
            insights.extend(timing_insights)
            
            # 內容分析
            content_insights = self._analyze_content_performance(kol_id, kol_metrics)
            insights.extend(content_insights)
            
            # 受眾分析
            audience_insights = self._analyze_audience_behavior(kol_id, kol_metrics)
            insights.extend(audience_insights)
        
        return insights
    
    def _analyze_performance(self, kol_id: str, metrics: List[EngagementMetrics]) -> List[EngagementInsight]:
        """分析表現"""
        insights = []
        
        if len(metrics) < 3:
            return insights
        
        # 計算平均表現
        avg_engagement = np.mean([m.engagement_rate for m in metrics])
        avg_comment_rate = np.mean([m.comment_rate for m in metrics])
        avg_share_rate = np.mean([m.share_rate for m in metrics])
        
        # 與基準比較
        if avg_engagement > self.industry_benchmarks['engagement_rate'] * 1.5:
            insights.append(EngagementInsight(
                insight_type='performance',
                kol_id=kol_id,
                description=f"互動率表現優異 ({avg_engagement:.3f})，超越行業基準50%",
                confidence=0.9,
                data_points=len(metrics),
                recommendation="保持現有策略，可考慮增加發文頻率",
                expected_impact=0.1,
                created_at=datetime.now()
            ))
        elif avg_engagement < self.industry_benchmarks['engagement_rate'] * 0.5:
            insights.append(EngagementInsight(
                insight_type='performance',
                kol_id=kol_id,
                description=f"互動率偏低 ({avg_engagement:.3f})，低於行業基準50%",
                confidence=0.8,
                data_points=len(metrics),
                recommendation="需要調整內容策略，增加互動元素",
                expected_impact=0.3,
                created_at=datetime.now()
            ))
        
        # 分析趨勢
        if len(metrics) >= 5:
            recent_metrics = metrics[-3:]
            older_metrics = metrics[:-3]
            
            recent_avg = np.mean([m.engagement_rate for m in recent_metrics])
            older_avg = np.mean([m.engagement_rate for m in older_metrics])
            
            if recent_avg > older_avg * 1.2:
                insights.append(EngagementInsight(
                    insight_type='performance',
                    kol_id=kol_id,
                    description="互動率呈上升趨勢，最近表現提升20%",
                    confidence=0.7,
                    data_points=len(metrics),
                    recommendation="繼續保持當前策略",
                    expected_impact=0.05,
                    created_at=datetime.now()
                ))
            elif recent_avg < older_avg * 0.8:
                insights.append(EngagementInsight(
                    insight_type='performance',
                    kol_id=kol_id,
                    description="互動率呈下降趨勢，最近表現下降20%",
                    confidence=0.7,
                    data_points=len(metrics),
                    recommendation="需要重新評估內容策略",
                    expected_impact=0.2,
                    created_at=datetime.now()
                ))
        
        return insights
    
    def _analyze_timing(self, kol_id: str, metrics: List[EngagementMetrics]) -> List[EngagementInsight]:
        """分析時機"""
        insights = []
        
        if len(metrics) < 5:
            return insights
        
        # 分析最佳發文時段
        hour_performance = {}
        for metric in metrics:
            hour = metric.posting_time.hour
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(metric.engagement_rate)
        
        # 找出最佳時段
        best_hour = None
        best_avg = 0
        
        for hour, rates in hour_performance.items():
            avg_rate = np.mean(rates)
            if avg_rate > best_avg:
                best_avg = avg_rate
                best_hour = hour
        
        if best_hour is not None:
            insights.append(EngagementInsight(
                insight_type='timing',
                kol_id=kol_id,
                description=f"最佳發文時段為 {best_hour}:00，平均互動率 {best_avg:.3f}",
                confidence=0.8,
                data_points=len(metrics),
                recommendation=f"建議在 {best_hour}:00 前後發文",
                expected_impact=0.15,
                created_at=datetime.now()
            ))
        
        return insights
    
    def _analyze_content_performance(self, kol_id: str, metrics: List[EngagementMetrics]) -> List[EngagementInsight]:
        """分析內容表現"""
        insights = []
        
        if len(metrics) < 3:
            return insights
        
        # 按內容類型分組
        content_performance = {}
        for metric in metrics:
            content_type = metric.content_type
            if content_type not in content_performance:
                content_performance[content_type] = []
            content_performance[content_type].append(metric.engagement_rate)
        
        # 找出最佳內容類型
        best_type = None
        best_avg = 0
        worst_type = None
        worst_avg = 1
        
        for content_type, rates in content_performance.items():
            avg_rate = np.mean(rates)
            if avg_rate > best_avg:
                best_avg = avg_rate
                best_type = content_type
            if avg_rate < worst_avg:
                worst_avg = avg_rate
                worst_type = content_type
        
        if best_type and worst_type and best_avg - worst_avg > 0.02:
            insights.append(EngagementInsight(
                insight_type='content',
                kol_id=kol_id,
                description=f"'{best_type}' 類型內容表現最佳 ({best_avg:.3f})，'{worst_type}' 類型表現較差 ({worst_avg:.3f})",
                confidence=0.8,
                data_points=len(metrics),
                recommendation=f"增加 {best_type} 類型內容，減少 {worst_type} 類型內容",
                expected_impact=best_avg - worst_avg,
                created_at=datetime.now()
            ))
        
        return insights
    
    def _analyze_audience_behavior(self, kol_id: str, metrics: List[EngagementMetrics]) -> List[EngagementInsight]:
        """分析受眾行為"""
        insights = []
        
        if len(metrics) < 3:
            return insights
        
        # 分析留言品質
        avg_comment_length = np.mean([m.avg_comment_length for m in metrics])
        avg_sentiment = np.mean([m.positive_sentiment_ratio for m in metrics])
        avg_reply_rate = np.mean([m.reply_rate for m in metrics])
        
        # 留言品質分析
        if avg_comment_length > 30:
            insights.append(EngagementInsight(
                insight_type='audience',
                kol_id=kol_id,
                description=f"受眾留言品質高，平均長度 {avg_comment_length:.1f} 字",
                confidence=0.7,
                data_points=len(metrics),
                recommendation="繼續保持深度內容，激發深度討論",
                expected_impact=0.05,
                created_at=datetime.now()
            ))
        elif avg_comment_length < 10:
            insights.append(EngagementInsight(
                insight_type='audience',
                kol_id=kol_id,
                description=f"受眾留言較短，平均長度 {avg_comment_length:.1f} 字",
                confidence=0.7,
                data_points=len(metrics),
                recommendation="考慮調整內容風格，增加互動性",
                expected_impact=0.1,
                created_at=datetime.now()
            ))
        
        # 情感分析
        if avg_sentiment > 0.7:
            insights.append(EngagementInsight(
                insight_type='audience',
                kol_id=kol_id,
                description=f"受眾情感正面，正面比例 {avg_sentiment:.1%}",
                confidence=0.8,
                data_points=len(metrics),
                recommendation="保持現有風格，受眾反應良好",
                expected_impact=0.02,
                created_at=datetime.now()
            ))
        elif avg_sentiment < 0.4:
            insights.append(EngagementInsight(
                insight_type='audience',
                kol_id=kol_id,
                description=f"受眾情感偏負面，正面比例 {avg_sentiment:.1%}",
                confidence=0.8,
                data_points=len(metrics),
                recommendation="需要調整內容策略，改善受眾情感",
                expected_impact=0.2,
                created_at=datetime.now()
            ))
        
        return insights
    
    def calculate_benchmarks(self, metrics: List[EngagementMetrics]) -> Dict[str, PerformanceBenchmark]:
        """計算表現基準"""
        benchmarks = {}
        
        if not metrics:
            return benchmarks
        
        # 按KOL分組
        kol_groups = {}
        for metric in metrics:
            if metric.kol_id not in kol_groups:
                kol_groups[metric.kol_id] = []
            kol_groups[metric.kol_id].append(metric)
        
        for kol_id, kol_metrics in kol_groups.items():
            # 計算各項指標
            engagement_rates = [m.engagement_rate for m in kol_metrics]
            comment_rates = [m.comment_rate for m in kol_metrics]
            share_rates = [m.share_rate for m in kol_metrics]
            
            # 互動率基準
            current_engagement = np.mean(engagement_rates)
            industry_engagement = self.industry_benchmarks['engagement_rate']
            percentile = self._calculate_percentile(current_engagement, engagement_rates)
            
            benchmarks[f"{kol_id}_engagement"] = PerformanceBenchmark(
                metric_name='engagement_rate',
                kol_id=kol_id,
                current_value=current_engagement,
                benchmark_value=industry_engagement,
                percentile=percentile,
                trend=self._calculate_trend(engagement_rates),
                comparison_period='30_days'
            )
            
            # 留言率基準
            current_comment = np.mean(comment_rates)
            industry_comment = self.industry_benchmarks['comment_rate']
            percentile = self._calculate_percentile(current_comment, comment_rates)
            
            benchmarks[f"{kol_id}_comment"] = PerformanceBenchmark(
                metric_name='comment_rate',
                kol_id=kol_id,
                current_value=current_comment,
                benchmark_value=industry_comment,
                percentile=percentile,
                trend=self._calculate_trend(comment_rates),
                comparison_period='30_days'
            )
        
        return benchmarks
    
    def _calculate_percentile(self, value: float, data: List[float]) -> float:
        """計算百分位數"""
        if not data:
            return 50.0
        
        sorted_data = sorted(data)
        rank = sum(1 for x in sorted_data if x <= value)
        return (rank / len(sorted_data)) * 100
    
    def _calculate_trend(self, data: List[float]) -> str:
        """計算趨勢"""
        if len(data) < 3:
            return 'stable'
        
        # 簡單線性回歸
        x = np.arange(len(data))
        y = np.array(data)
        
        # 計算斜率
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.01:
            return 'improving'
        elif slope < -0.01:
            return 'declining'
        else:
            return 'stable'
    
    def get_performance_summary(self, kol_id: str = None) -> Dict[str, Any]:
        """獲取表現摘要"""
        if kol_id:
            metrics = [m for m in self.engagement_history if m.kol_id == kol_id]
        else:
            metrics = self.engagement_history
        
        if not metrics:
            return {}
        
        # 計算統計數據
        engagement_rates = [m.engagement_rate for m in metrics]
        comment_rates = [m.comment_rate for m in metrics]
        share_rates = [m.share_rate for m in metrics]
        
        return {
            'total_posts': len(metrics),
            'avg_engagement_rate': np.mean(engagement_rates),
            'avg_comment_rate': np.mean(comment_rates),
            'avg_share_rate': np.mean(share_rates),
            'best_performing_content': self._find_best_content(metrics),
            'worst_performing_content': self._find_worst_content(metrics),
            'performance_trend': self._calculate_overall_trend(metrics),
            'last_updated': datetime.now().isoformat()
        }
    
    def _find_best_content(self, metrics: List[EngagementMetrics]) -> Dict[str, Any]:
        """找出最佳表現內容"""
        if not metrics:
            return {}
        
        best_metric = max(metrics, key=lambda m: m.engagement_rate)
        return {
            'content_id': best_metric.content_id,
            'content_type': best_metric.content_type,
            'engagement_rate': best_metric.engagement_rate,
            'posting_time': best_metric.posting_time.isoformat()
        }
    
    def _find_worst_content(self, metrics: List[EngagementMetrics]) -> Dict[str, Any]:
        """找出最差表現內容"""
        if not metrics:
            return {}
        
        worst_metric = min(metrics, key=lambda m: m.engagement_rate)
        return {
            'content_id': worst_metric.content_id,
            'content_type': worst_metric.content_type,
            'engagement_rate': worst_metric.engagement_rate,
            'posting_time': worst_metric.posting_time.isoformat()
        }
    
    def _calculate_overall_trend(self, metrics: List[EngagementMetrics]) -> str:
        """計算整體趨勢"""
        if len(metrics) < 3:
            return 'stable'
        
        # 按時間排序
        sorted_metrics = sorted(metrics, key=lambda m: m.posting_time)
        engagement_rates = [m.engagement_rate for m in sorted_metrics]
        
        return self._calculate_trend(engagement_rates)

