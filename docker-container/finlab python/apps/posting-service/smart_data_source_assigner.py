"""
智能數據源分配服務
負責根據KOL特性和股票特性分配最適合的數據源
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random

logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """數據源類型"""
    OHLC_API = "ohlc_api"           # 股價技術數據
    SUMMARY_API = "summary_api"     # 摘要分析
    SERPER_API = "serper_api"       # 新聞搜尋
    REVENUE_API = "revenue_api"     # 營收數據
    FINANCIAL_API = "financial_api" # 財務數據
    FUNDAMENTAL_API = "fundamental_api" # 基本面分析
    # trending_api 移除，因為它是話題提取工具，不是數據源

@dataclass
class KOLProfile:
    """KOL配置"""
    serial: int
    nickname: str
    persona: str  # technical, fundamental, news_driven, mixed
    expertise_areas: List[str]
    content_style: str
    target_audience: str
    data_preferences: List[str] = None

@dataclass
class StockProfile:
    """股票配置"""
    stock_code: str
    stock_name: str
    industry: str
    market_cap: str  # large, medium, small
    volatility: str  # high, medium, low
    news_frequency: str  # high, medium, low

@dataclass
class DataSourceAssignment:
    """數據源分配結果"""
    primary_sources: List[DataSourceType]
    secondary_sources: List[DataSourceType]
    excluded_sources: List[DataSourceType]
    assignment_reason: str
    confidence_score: float

class SmartDataSourceAssigner:
    """智能數據源分配器"""
    
    def __init__(self):
        self.data_source_weights = self._initialize_data_source_weights()
        self.kol_preferences = self._initialize_kol_preferences()
        self.stock_characteristics = self._initialize_stock_characteristics()
    
    def assign_data_sources(self, 
                           kol_profile: KOLProfile, 
                           stock_profile: StockProfile,
                           batch_context: Dict[str, Any] = None) -> DataSourceAssignment:
        """為KOL和股票組合分配最適合的數據源"""
        
        try:
            logger.info(f"為 {kol_profile.nickname}({kol_profile.persona}) 和 {stock_profile.stock_name}({stock_profile.stock_code}) 分配數據源")
            
            # 計算每個數據源的適合度分數
            source_scores = self._calculate_source_scores(kol_profile, stock_profile, batch_context)
            
            # 根據分數排序並選擇主要和次要數據源
            sorted_sources = sorted(source_scores.items(), key=lambda x: x[1], reverse=True)
            
            # 分配主要數據源（前3個）
            primary_sources = [source for source, score in sorted_sources[:3] if score > 0.5]
            
            # 分配次要數據源（第4-6個）
            secondary_sources = [source for source, score in sorted_sources[3:6] if score > 0.3]
            
            # 排除低分數據源
            excluded_sources = [source for source, score in sorted_sources if score < 0.2]
            
            # 生成分配原因
            assignment_reason = self._generate_assignment_reason(
                kol_profile, stock_profile, primary_sources, secondary_sources
            )
            
            # 計算信心分數
            confidence_score = self._calculate_confidence_score(source_scores, primary_sources)
            
            assignment = DataSourceAssignment(
                primary_sources=primary_sources,
                secondary_sources=secondary_sources,
                excluded_sources=excluded_sources,
                assignment_reason=assignment_reason,
                confidence_score=confidence_score
            )
            
            logger.info(f"數據源分配完成: 主要={len(primary_sources)}, 次要={len(secondary_sources)}, 信心分數={confidence_score:.2f}")
            return assignment
            
        except Exception as e:
            logger.error(f"數據源分配失敗: {e}")
            return self._get_default_assignment()
    
    def assign_batch_data_sources(self, 
                                 kol_stock_pairs: List[Dict[str, Any]]) -> Dict[str, DataSourceAssignment]:
        """為批量發文分配數據源"""
        
        assignments = {}
        
        for pair in kol_stock_pairs:
            kol_profile = KOLProfile(**pair['kol_profile'])
            stock_profile = StockProfile(**pair['stock_profile'])
            
            # 為每對KOL-股票分配數據源
            assignment = self.assign_data_sources(kol_profile, stock_profile, pair.get('batch_context'))
            
            key = f"{kol_profile.serial}_{stock_profile.stock_code}"
            assignments[key] = assignment
        
        # 確保多樣性：避免所有貼文使用相同的數據源組合
        assignments = self._ensure_diversity(assignments)
        
        return assignments
    
    def _calculate_source_scores(self, 
                               kol_profile: KOLProfile, 
                               stock_profile: StockProfile,
                               batch_context: Dict[str, Any] = None) -> Dict[DataSourceType, float]:
        """計算每個數據源的適合度分數"""
        
        scores = {}
        
        for source_type in DataSourceType:
            score = 0.0
            
            # 1. KOL人設匹配度
            kol_score = self._get_kol_source_match_score(kol_profile, source_type)
            score += kol_score * 0.4
            
            # 2. 股票特性匹配度
            stock_score = self._get_stock_source_match_score(stock_profile, source_type)
            score += stock_score * 0.3
            
            # 3. 數據源權重
            weight_score = self.data_source_weights.get(source_type, 0.5)
            score += weight_score * 0.2
            
            # 4. 批次上下文影響
            if batch_context:
                context_score = self._get_context_source_score(batch_context, source_type)
                score += context_score * 0.1
            
            scores[source_type] = min(score, 1.0)  # 最高1.0分
        
        return scores
    
    def _get_kol_source_match_score(self, kol_profile: KOLProfile, source_type: DataSourceType) -> float:
        """計算KOL與數據源的匹配度"""
        
        persona = kol_profile.persona.lower()
        
        # 技術分析型KOL偏好
        if persona == 'technical':
            if source_type == DataSourceType.OHLC_API:
                return 1.0
            elif source_type == DataSourceType.SUMMARY_API:
                return 0.8
            elif source_type == DataSourceType.SERPER_API:
                return 0.3
            elif source_type == DataSourceType.FUNDAMENTAL_API:
                return 0.2
        
        # 基本面分析型KOL偏好
        elif persona == 'fundamental':
            if source_type == DataSourceType.FUNDAMENTAL_API:
                return 1.0
            elif source_type == DataSourceType.REVENUE_API:
                return 0.9
            elif source_type == DataSourceType.FINANCIAL_API:
                return 0.8
            elif source_type == DataSourceType.SERPER_API:
                return 0.7
            elif source_type == DataSourceType.SUMMARY_API:
                return 0.6
            elif source_type == DataSourceType.OHLC_API:
                return 0.4
        
        # 新聞驅動型KOL偏好
        elif persona == 'news_driven':
            if source_type == DataSourceType.SERPER_API:
                return 1.0
            elif source_type == DataSourceType.SUMMARY_API:
                return 0.6
            elif source_type == DataSourceType.FUNDAMENTAL_API:
                return 0.4
            elif source_type == DataSourceType.OHLC_API:
                return 0.3
        
        # 混合型KOL偏好
        elif persona == 'mixed':
            if source_type in [DataSourceType.SUMMARY_API, DataSourceType.SERPER_API]:
                return 0.8
            elif source_type in [DataSourceType.OHLC_API, DataSourceType.FUNDAMENTAL_API]:
                return 0.6
            elif source_type in [DataSourceType.REVENUE_API]:
                return 0.5
        
        return 0.5  # 預設分數
    
    def _get_stock_source_match_score(self, stock_profile: StockProfile, source_type: DataSourceType) -> float:
        """計算股票與數據源的匹配度"""
        
        # 大市值股票適合基本面分析
        if stock_profile.market_cap == 'large':
            if source_type in [DataSourceType.FUNDAMENTAL_API, DataSourceType.FINANCIAL_API, DataSourceType.REVENUE_API]:
                return 0.9
            elif source_type == DataSourceType.SERPER_API:
                return 0.7  # 大股票新聞多
        
        # 小市值股票適合技術分析
        elif stock_profile.market_cap == 'small':
            if source_type in [DataSourceType.OHLC_API]:
                return 0.9
            elif source_type == DataSourceType.SERPER_API:
                return 0.4  # 小股票新聞少
        
        # 高波動股票適合技術分析
        if stock_profile.volatility == 'high':
            if source_type in [DataSourceType.OHLC_API]:
                return 0.8
        
        # 高新聞頻率股票適合新聞分析
        if stock_profile.news_frequency == 'high':
            if source_type == DataSourceType.SERPER_API:
                return 0.9
        
        return 0.5  # 預設分數
    
    def _get_context_source_score(self, batch_context: Dict[str, Any], source_type: DataSourceType) -> float:
        """計算批次上下文對數據源的影響"""
        
        # 如果是盤後漲停主題，增加技術分析權重
        if batch_context.get('trigger_type') == 'after_hours_limit_up':
            if source_type == DataSourceType.OHLC_API:
                return 0.8
            elif source_type == DataSourceType.SERPER_API:
                return 0.7  # 需要分析漲停原因
        
        # 如果是財報季，增加基本面分析權重
        if batch_context.get('season') == 'earnings':
            if source_type in [DataSourceType.FUNDAMENTAL_API, DataSourceType.REVENUE_API]:
                return 0.8
        
        return 0.0
    
    def _generate_assignment_reason(self, 
                                  kol_profile: KOLProfile, 
                                  stock_profile: StockProfile,
                                  primary_sources: List[DataSourceType],
                                  secondary_sources: List[DataSourceType]) -> str:
        """生成分配原因說明"""
        
        reasons = []
        
        # KOL特性原因
        if kol_profile.persona == 'technical':
            reasons.append(f"{kol_profile.nickname}為技術分析型KOL，優先使用技術指標數據")
        elif kol_profile.persona == 'fundamental':
            reasons.append(f"{kol_profile.nickname}為基本面分析型KOL，側重財務數據分析")
        elif kol_profile.persona == 'news_driven':
            reasons.append(f"{kol_profile.nickname}為新聞驅動型KOL，重視時事資訊整合")
        
        # 股票特性原因
        if stock_profile.market_cap == 'large':
            reasons.append(f"{stock_profile.stock_name}為大市值股票，適合基本面分析")
        elif stock_profile.market_cap == 'small':
            reasons.append(f"{stock_profile.stock_name}為小市值股票，適合技術分析")
        
        # 數據源原因
        if DataSourceType.SERPER_API in primary_sources:
            reasons.append("整合最新新聞資訊以提升內容時事性")
        
        if DataSourceType.OHLC_API in primary_sources:
            reasons.append("使用技術指標數據進行深度技術分析")
        
        return "；".join(reasons) if reasons else "基於KOL和股票特性進行智能分配"
    
    def _calculate_confidence_score(self, 
                                  source_scores: Dict[DataSourceType, float],
                                  primary_sources: List[DataSourceType]) -> float:
        """計算分配信心分數"""
        
        if not primary_sources:
            return 0.0
        
        # 計算主要數據源的平均分數
        avg_score = sum(source_scores[source] for source in primary_sources) / len(primary_sources)
        
        # 計算分數差異（差異越小，信心越高）
        scores = [source_scores[source] for source in primary_sources]
        score_variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
        variance_penalty = min(score_variance * 0.1, 0.2)
        
        confidence = avg_score - variance_penalty
        return max(confidence, 0.0)
    
    def _ensure_diversity(self, assignments: Dict[str, DataSourceAssignment]) -> Dict[str, DataSourceAssignment]:
        """確保批量分配的多樣性"""
        
        # 統計數據源使用頻率
        source_usage = {}
        for assignment in assignments.values():
            for source in assignment.primary_sources:
                source_usage[source] = source_usage.get(source, 0) + 1
        
        # 如果某個數據源使用過於頻繁，調整部分分配
        total_assignments = len(assignments)
        max_usage = total_assignments * 0.6  # 單一數據源最多使用60%
        
        for source, usage_count in source_usage.items():
            if usage_count > max_usage:
                # 隨機選擇部分分配進行調整
                overused_keys = [key for key, assignment in assignments.items() 
                               if source in assignment.primary_sources]
                
                # 調整過度使用的分配
                for key in random.sample(overused_keys, int(usage_count - max_usage)):
                    assignment = assignments[key]
                    # 將過度使用的數據源移到次要位置
                    if source in assignment.primary_sources:
                        assignment.primary_sources.remove(source)
                        assignment.secondary_sources.append(source)
        
        return assignments
    
    def _get_default_assignment(self) -> DataSourceAssignment:
        """獲取預設數據源分配"""
        return DataSourceAssignment(
            primary_sources=[DataSourceType.SUMMARY_API, DataSourceType.OHLC_API],
            secondary_sources=[DataSourceType.SERPER_API],
            excluded_sources=[],
            assignment_reason="使用預設數據源組合",
            confidence_score=0.5
        )
    
    def _initialize_data_source_weights(self) -> Dict[DataSourceType, float]:
        """初始化數據源權重"""
        return {
            DataSourceType.SUMMARY_API: 0.9,      # 摘要API最重要
            DataSourceType.SERPER_API: 0.8,       # 新聞API很重要
            DataSourceType.OHLC_API: 0.7,         # 技術數據重要
            DataSourceType.FUNDAMENTAL_API: 0.6,  # 基本面數據重要
            DataSourceType.REVENUE_API: 0.4,      # 營收數據中等
            DataSourceType.FINANCIAL_API: 0.3     # 財務數據較低
        }
    
    def _initialize_kol_preferences(self) -> Dict[str, List[DataSourceType]]:
        """初始化KOL偏好"""
        return {
            'technical': [DataSourceType.OHLC_API, DataSourceType.SUMMARY_API],
            'fundamental': [DataSourceType.FUNDAMENTAL_API, DataSourceType.REVENUE_API],
            'news_driven': [DataSourceType.SERPER_API],
            'mixed': [DataSourceType.SUMMARY_API, DataSourceType.SERPER_API]
        }
    
    def _initialize_stock_characteristics(self) -> Dict[str, List[DataSourceType]]:
        """初始化股票特性"""
        return {
            'large_cap': [DataSourceType.FUNDAMENTAL_API, DataSourceType.FINANCIAL_API],
            'small_cap': [DataSourceType.OHLC_API],
            'high_volatility': [DataSourceType.OHLC_API, DataSourceType.SERPER_API],
            'high_news': [DataSourceType.SERPER_API]
        }

# 全域實例
smart_assigner = SmartDataSourceAssigner()
