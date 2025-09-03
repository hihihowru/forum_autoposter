"""
智能學習服務模組
提供AI偵測、互動分析、學習引擎等核心功能
"""

from .learning_engine import LearningEngine, LearningMetrics, LearningInsight, KOLStrategy
from .ai_detection_service import AIDetectionService, AIDetectionResult, CommentAnalysis
from .engagement_analyzer import EngagementAnalyzer, EngagementMetrics, EngagementInsight, PerformanceBenchmark
from .learning_orchestrator import LearningOrchestrator, LearningSession, LearningReport

__all__ = [
    # 學習引擎
    'LearningEngine',
    'LearningMetrics', 
    'LearningInsight',
    'KOLStrategy',
    
    # AI偵測服務
    'AIDetectionService',
    'AIDetectionResult',
    'CommentAnalysis',
    
    # 互動分析器
    'EngagementAnalyzer',
    'EngagementMetrics',
    'EngagementInsight', 
    'PerformanceBenchmark',
    
    # 學習協調器
    'LearningOrchestrator',
    'LearningSession',
    'LearningReport'
]

