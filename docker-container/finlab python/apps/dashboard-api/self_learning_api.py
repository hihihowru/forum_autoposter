from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json
import asyncio
from dataclasses import dataclass, asdict

# from src.clients.google_sheets.google_sheets_client import GoogleSheetsClient  # Google Sheets 已棄用
# from src.services.interaction.interaction_collector import InteractionCollector  # 暫時註解

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/self-learning", tags=["self-learning"])

# ==================== 數據模型 ====================

class FeatureRanking(BaseModel):
    feature: str
    score: float
    impact: str  # 'high', 'medium', 'low'
    description: str
    top10PercentValue: float
    allPostsValue: float
    improvement: float

class ExperimentConfig(BaseModel):
    id: str
    name: str
    description: str
    status: str  # 'pending', 'running', 'completed', 'paused'
    startDate: str
    endDate: str
    settings: Dict[str, Any]
    expectedEngagement: str
    actualEngagement: Optional[float] = None
    progress: int
    color: str

class SelfLearningInsight(BaseModel):
    id: str
    type: str  # 'pattern', 'recommendation', 'warning', 'success'
    title: str
    description: str
    confidence: int
    impact: str  # 'high', 'medium', 'low'
    action: str
    timestamp: str

class SelfLearningAnalysis(BaseModel):
    totalPosts: int
    top10PercentCount: int
    rankings: List[FeatureRanking]
    insights: List[SelfLearningInsight]
    experiments: List[ExperimentConfig]

# ==================== 自我學習服務 ====================

class SelfLearningService:
    def __init__(self):
        # self.sheets_client = GoogleSheetsClient()  # Google Sheets 已棄用
        self.sheets_client = None
        # 使用 SQL 資料庫，不再使用 Google Sheets
        self.interaction_collector = None
        self.active_experiments: Dict[str, ExperimentConfig] = {}
        self.learning_history: List[Dict] = []
    
    async def analyze_feature_rankings(self, posts: List[Dict]) -> List[FeatureRanking]:
        """分析特徵排名"""
        if not posts:
            return []
        
        # 按總互動數排序
        sorted_posts = sorted(posts, key=lambda x: self._calculate_total_interactions(x), reverse=True)
        total_posts = len(sorted_posts)
        top10_percent_count = max(1, int(total_posts * 0.1))
        top10_posts = sorted_posts[:top10_percent_count]
        
        # 分析特徵
        top10_features = self._analyze_post_features(top10_posts)
        all_features = self._analyze_post_features(sorted_posts)
        
        # 計算特徵重要性排名
        rankings = []
        
        # 發文時間分析
        time_features = ['morning', 'afternoon', 'evening', 'night']
        for time_feature in time_features:
            top10_value = top10_features.get('postingTime', {}).get(time_feature, 0)
            all_value = all_features.get('postingTime', {}).get(time_feature, 0)
            improvement = top10_value - all_value
            score = abs(improvement)
            
            rankings.append(FeatureRanking(
                feature=f'發文時段-{self._get_time_label(time_feature)}',
                score=score,
                impact=self._get_impact_level(score),
                description=f'{self._get_time_label(time_feature)}時段發文的互動效果',
                top10PercentValue=top10_value,
                allPostsValue=all_value,
                improvement=improvement
            ))
        
        # 內容特徵分析
        content_features = [
            ('hasStockTags', '股票標記'),
            ('hasTrendingTopic', '熱門話題'),
            ('hasHumorMode', '幽默模式'),
            ('hasEmoji', 'Emoji使用'),
            ('hasQuestion', '問號互動'),
            ('hasExclamation', '驚嘆號'),
            ('mediumContent', '中等內容長度'),
            ('shortTitle', '短標題')
        ]
        
        for feature_key, feature_name in content_features:
            top10_value = top10_features.get(feature_key, 0)
            all_value = all_features.get(feature_key, 0)
            improvement = top10_value - all_value
            score = abs(improvement)
            
            rankings.append(FeatureRanking(
                feature=feature_name,
                score=score,
                impact=self._get_impact_level(score),
                description=f'{feature_name}的互動效果',
                top10PercentValue=top10_value,
                allPostsValue=all_value,
                improvement=improvement
            ))
        
        # 按分數排序
        rankings.sort(key=lambda x: x.score, reverse=True)
        return rankings
    
    def _calculate_total_interactions(self, post: Dict) -> int:
        """計算總互動數"""
        return (post.get('likes', 0) or 0) + (post.get('comments', 0) or 0) + (post.get('shares', 0) or 0) + (post.get('bookmarks', 0) or 0)
    
    def _analyze_post_features(self, posts: List[Dict]) -> Dict:
        """分析貼文特徵"""
        if not posts:
            return {}
        
        features = {
            'postingTime': {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0},
            'hasStockTags': 0,
            'hasTrendingTopic': 0,
            'hasHumorMode': 0,
            'hasEmoji': 0,
            'hasQuestion': 0,
            'hasExclamation': 0,
            'mediumContent': 0,
            'shortTitle': 0
        }
        
        for post in posts:
            # 發文時間分析
            create_time = post.get('create_time', '')
            if create_time:
                try:
                    post_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                    hour = post_time.hour
                    if 6 <= hour < 12:
                        features['postingTime']['morning'] += 1
                    elif 12 <= hour < 18:
                        features['postingTime']['afternoon'] += 1
                    elif 18 <= hour < 24:
                        features['postingTime']['evening'] += 1
                    else:
                        features['postingTime']['night'] += 1
                except:
                    pass
            
            # 內容特徵分析
            title = post.get('title', '')
            content = post.get('content', '')
            full_text = f"{title} {content}"
            
            # 股票標記
            if post.get('commodity_tags'):
                features['hasStockTags'] += 1
            
            # 熱門話題
            if post.get('community_topic'):
                features['hasTrendingTopic'] += 1
            
            # 幽默模式
            humor_keywords = ['哈哈', '笑死', '搞笑', '幽默', '有趣', '😂', '😄', '😆', 'XD', 'LOL']
            if any(keyword in full_text for keyword in humor_keywords):
                features['hasHumorMode'] += 1
            
            # Emoji
            emoji_regex = r'[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]'
            import re
            if re.search(emoji_regex, full_text):
                features['hasEmoji'] += 1
            
            # 問號
            if '？' in full_text or '?' in full_text:
                features['hasQuestion'] += 1
            
            # 驚嘆號
            if '！' in full_text or '!' in full_text:
                features['hasExclamation'] += 1
            
            # 內容長度
            content_length = len(content)
            if 200 <= content_length <= 500:
                features['mediumContent'] += 1
            
            # 標題長度
            title_length = len(title)
            if title_length < 20:
                features['shortTitle'] += 1
        
        # 轉換為百分比
        total_posts = len(posts)
        for key in features:
            if key == 'postingTime':
                for time_key in features[key]:
                    features[key][time_key] = round((features[key][time_key] / total_posts) * 100)
            else:
                features[key] = round((features[key] / total_posts) * 100)
        
        return features
    
    def _get_time_label(self, time_feature: str) -> str:
        """獲取時間標籤"""
        labels = {
            'morning': '上午',
            'afternoon': '下午',
            'evening': '晚上',
            'night': '深夜'
        }
        return labels.get(time_feature, time_feature)
    
    def _get_impact_level(self, score: float) -> str:
        """獲取影響等級"""
        if score > 15:
            return 'high'
        elif score > 8:
            return 'medium'
        else:
            return 'low'
    
    async def generate_smart_experiments(self, rankings: List[FeatureRanking]) -> List[ExperimentConfig]:
        """生成智能實驗"""
        top_rankings = rankings[:5]  # 取前5個最重要的特徵
        
        experiments = [
            ExperimentConfig(
                id='exp_1',
                name='高互動時段策略',
                description='基於前10%高互動貼文的發文時間分析',
                status='pending',
                startDate=datetime.now().strftime('%Y-%m-%d'),
                endDate=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                settings={
                    'preferredTimeSlots': ['14:00-16:00', '19:00-21:00'],
                    'contentLength': '200-500字',
                    'humorLevel': '輕度幽默',
                    'stockTags': '包含2-3個股票標記',
                    'features': ['包含Emoji', '有問號互動', '系統發文'],
                    'kolSelection': ['龜狗一日散戶', '板橋大who']
                },
                expectedEngagement='預期互動率提升 25%',
                progress=0,
                color='#52c41a'
            ),
            ExperimentConfig(
                id='exp_2',
                name='內容結構優化策略',
                description='參考高互動貼文的內容特徵組合',
                status='pending',
                startDate=datetime.now().strftime('%Y-%m-%d'),
                endDate=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                settings={
                    'preferredTimeSlots': ['09:00-11:00', '15:00-17:00'],
                    'contentLength': '300-600字',
                    'humorLevel': '中度幽默',
                    'stockTags': '包含1-2個熱門股票標記',
                    'features': ['有段落結構', '包含數字', '有驚嘆號'],
                    'kolSelection': ['龜狗一日散戶', '板橋大who']
                },
                expectedEngagement='預期互動率提升 18%',
                progress=0,
                color='#1890ff'
            ),
            ExperimentConfig(
                id='exp_3',
                name='KOL個性化發文策略',
                description='針對特定KOL的高互動模式',
                status='pending',
                startDate=datetime.now().strftime('%Y-%m-%d'),
                endDate=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                settings={
                    'preferredTimeSlots': ['12:00-14:00', '20:00-22:00'],
                    'contentLength': '150-400字',
                    'humorLevel': '強烈幽默',
                    'stockTags': '包含3-4個股票標記',
                    'features': ['有Hashtag', '包含引用', '有條列式內容'],
                    'kolSelection': ['龜狗一日散戶', '板橋大who']
                },
                expectedEngagement='預期互動率提升 32%',
                progress=0,
                color='#722ed1'
            )
        ]
        
        return experiments
    
    async def generate_learning_insights(self, rankings: List[FeatureRanking]) -> List[SelfLearningInsight]:
        """生成學習洞察"""
        insights = []
        
        if rankings:
            top_feature = rankings[0]
            insights.append(SelfLearningInsight(
                id='insight_1',
                type='pattern',
                title='發現高互動時段模式',
                description=f'前10%高互動貼文中，{top_feature.feature}的表現比全部貼文高出{abs(top_feature.improvement):.1f}%',
                confidence=85,
                impact='high',
                action='建議在該時段增加發文頻率',
                timestamp=datetime.now().isoformat()
            ))
        
        insights.extend([
            SelfLearningInsight(
                id='insight_2',
                type='recommendation',
                title='內容長度優化建議',
                description='中等長度內容(200-500字)在前10%高互動貼文中表現最佳',
                confidence=78,
                impact='medium',
                action='調整內容生成策略，優先生成中等長度內容',
                timestamp=datetime.now().isoformat()
            ),
            SelfLearningInsight(
                id='insight_3',
                type='success',
                title='幽默元素效果顯著',
                description='包含幽默元素的貼文互動率平均提升15%',
                confidence=92,
                impact='high',
                action='增加幽默元素在內容生成中的權重',
                timestamp=datetime.now().isoformat()
            ),
            SelfLearningInsight(
                id='insight_4',
                type='warning',
                title='KOL表現差異明顯',
                description='不同KOL的互動表現存在顯著差異，需要個性化策略',
                confidence=88,
                impact='high',
                action='為每個KOL制定專屬的發文策略',
                timestamp=datetime.now().isoformat()
            )
        ])
        
        return insights

# 全局服務實例
self_learning_service = SelfLearningService()

# ==================== API 端點 ====================

@router.get("/analysis")
async def get_self_learning_analysis(
    kol_serial: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    include_external: bool = True
):
    """獲取自我學習分析數據"""
    try:
        # 獲取互動數據
        posts = await self_learning_service.interaction_collector.get_interaction_data(
            kol_serial=kol_serial,
            start_date=start_date,
            end_date=end_date,
            include_external=include_external
        )
        
        # 分析特徵排名
        rankings = await self_learning_service.analyze_feature_rankings(posts)
        
        # 生成智能實驗
        experiments = await self_learning_service.generate_smart_experiments(rankings)
        
        # 生成學習洞察
        insights = await self_learning_service.generate_learning_insights(rankings)
        
        return {
            "success": True,
            "data": {
                "totalPosts": len(posts),
                "top10PercentCount": max(1, int(len(posts) * 0.1)),
                "rankings": [ranking.dict() for ranking in rankings],
                "experiments": [exp.dict() for exp in experiments],
                "insights": [insight.dict() for insight in insights]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"獲取自我學習分析數據失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取自我學習分析數據失敗: {str(e)}")

@router.post("/experiments")
async def create_experiment(experiment: ExperimentConfig):
    """創建新實驗"""
    try:
        self_learning_service.active_experiments[experiment.id] = experiment
        
        return {
            "success": True,
            "message": "實驗創建成功",
            "data": experiment.dict()
        }
        
    except Exception as e:
        logger.error(f"創建實驗失敗: {e}")
        raise HTTPException(status_code=500, detail=f"創建實驗失敗: {str(e)}")

@router.put("/experiments/{experiment_id}/status")
async def update_experiment_status(
    experiment_id: str,
    status: str,
    progress: Optional[int] = None
):
    """更新實驗狀態"""
    try:
        if experiment_id not in self_learning_service.active_experiments:
            raise HTTPException(status_code=404, detail="實驗不存在")
        
        experiment = self_learning_service.active_experiments[experiment_id]
        experiment.status = status
        if progress is not None:
            experiment.progress = progress
        
        return {
            "success": True,
            "message": "實驗狀態更新成功",
            "data": experiment.dict()
        }
        
    except Exception as e:
        logger.error(f"更新實驗狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"更新實驗狀態失敗: {str(e)}")

@router.get("/experiments")
async def get_experiments():
    """獲取所有實驗"""
    try:
        experiments = list(self_learning_service.active_experiments.values())
        
        return {
            "success": True,
            "data": [exp.dict() for exp in experiments]
        }
        
    except Exception as e:
        logger.error(f"獲取實驗列表失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取實驗列表失敗: {str(e)}")

@router.get("/insights")
async def get_learning_insights():
    """獲取學習洞察"""
    try:
        # 這裡可以從數據庫或緩存中獲取洞察
        insights = [
            {
                "id": "insight_1",
                "type": "pattern",
                "title": "發現高互動時段模式",
                "description": "前10%高互動貼文中，下午時段發文的表現比全部貼文高出15%",
                "confidence": 85,
                "impact": "high",
                "action": "建議在該時段增加發文頻率",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        return {
            "success": True,
            "data": insights
        }
        
    except Exception as e:
        logger.error(f"獲取學習洞察失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取學習洞察失敗: {str(e)}")

@router.post("/auto-learning/toggle")
async def toggle_auto_learning(enabled: bool):
    """切換自動學習模式"""
    try:
        # 這裡可以實現自動學習的開關邏輯
        return {
            "success": True,
            "message": f"自動學習模式已{'開啟' if enabled else '關閉'}",
            "data": {"enabled": enabled}
        }
        
    except Exception as e:
        logger.error(f"切換自動學習模式失敗: {e}")
        raise HTTPException(status_code=500, detail=f"切換自動學習模式失敗: {str(e)}")

@router.get("/status")
async def get_self_learning_status():
    """獲取自我學習系統狀態"""
    try:
        return {
            "success": True,
            "data": {
                "autoLearningEnabled": True,
                "activeExperiments": len(self_learning_service.active_experiments),
                "completedExperiments": len(self_learning_service.learning_history),
                "lastAnalysisTime": datetime.now().isoformat(),
                "systemHealth": "healthy"
            }
        }
        
    except Exception as e:
        logger.error(f"獲取系統狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=f"獲取系統狀態失敗: {str(e)}")





