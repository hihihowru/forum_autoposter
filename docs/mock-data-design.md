# 互動數據模擬數據設計

## 🎯 模擬數據策略

### 設計原則
- **真實性**: 模擬數據要符合真實的互動模式
- **多樣性**: 包含不同 KOL 和內容類型的互動表現
- **時間維度**: 體現 1hr/1day/7days 的成長趨勢
- **可配置性**: 可以調整模擬參數來測試不同場景

---

## 📊 模擬數據結構

### 基礎數據模型
```python
@dataclass
class MockInteractionData:
    """模擬互動數據"""
    article_id: str              # 文章ID
    member_id: str               # KOL會員ID
    nickname: str                # KOL暱稱
    title: str                   # 文章標題
    content: str                 # 文章內容
    topic_id: str                # 話題ID
    is_trending_topic: bool      # 是否為熱門話題
    post_time: str               # 發文時間
    last_update_time: str        # 最後更新時間
    
    # 互動數據
    likes_count: int             # 按讚數
    comments_count: int          # 留言數
    shares_count: int            # 分享數 (模擬)
    views_count: int             # 瀏覽數 (模擬)
    
    # 計算欄位
    total_interactions: int      # 總互動數
    engagement_rate: float       # 互動率
    growth_rate: float           # 成長率
```

### 時間維度數據
```python
@dataclass
class MockTimelineData:
    """時間維度模擬數據"""
    article_id: str
    member_id: str
    nickname: str
    title: str
    
    # 1小時後數據
    interactions_1hr: int
    likes_1hr: int
    comments_1hr: int
    
    # 1日後數據
    interactions_1day: int
    likes_1day: int
    comments_1day: int
    growth_rate_1day: float
    
    # 7日後數據
    interactions_7days: int
    likes_7days: int
    comments_7days: int
    growth_rate_7days: float
    
    # 時間戳記
    post_time: str
    update_1hr: str
    update_1day: str
    update_7days: str
```

---

## 🎲 模擬數據生成邏輯

### KOL 表現基線
```python
# 不同 KOL 的互動表現基線
KOL_PERFORMANCE_BASELINE = {
    "9505546": {  # 川川哥 (技術派)
        "base_likes": 45,
        "base_comments": 8,
        "engagement_multiplier": 1.2,
        "growth_rate_1hr": 0.15,
        "growth_rate_1day": 0.35,
        "growth_rate_7days": 0.65
    },
    "9505547": {  # 韭割哥 (總經派)
        "base_likes": 38,
        "base_comments": 12,
        "engagement_multiplier": 1.0,
        "growth_rate_1hr": 0.12,
        "growth_rate_1day": 0.28,
        "growth_rate_7days": 0.55
    },
    "9505548": {  # 梅川褲子 (新聞派)
        "base_likes": 52,
        "base_comments": 15,
        "engagement_multiplier": 1.4,
        "growth_rate_1hr": 0.18,
        "growth_rate_1day": 0.42,
        "growth_rate_7days": 0.75
    },
    "9505549": {  # 龜狗一日散戶 (籌碼派)
        "base_likes": 41,
        "base_comments": 18,
        "engagement_multiplier": 1.1,
        "growth_rate_1hr": 0.14,
        "growth_rate_1day": 0.32,
        "growth_rate_7days": 0.58
    },
    "9505550": {  # 板橋大who (情緒派)
        "base_likes": 48,
        "base_comments": 22,
        "engagement_multiplier": 1.3,
        "growth_rate_1hr": 0.16,
        "growth_rate_1day": 0.38,
        "growth_rate_7days": 0.68
    }
}
```

### 內容類型影響因子
```python
# 不同內容類型的互動影響因子
CONTENT_TYPE_MULTIPLIER = {
    "technical": 1.0,      # 技術分析
    "macro": 0.9,          # 總經分析
    "news": 1.3,           # 新聞快訊
    "chips": 1.1,          # 籌碼分析
    "meme": 1.4,           # 情緒/迷因
    "value": 0.8,          # 價值投資
    "quant": 0.7           # 量化分析
}
```

### 熱門話題加成
```python
# 熱門話題的互動加成
TRENDING_TOPIC_BOOST = {
    "TRUE": 1.5,   # 熱門話題
    "FALSE": 1.0   # 一般話題
}
```

---

## 🔢 模擬數據生成算法

### 互動數據生成
```python
def generate_mock_interaction_data(article_data, time_period="1hr"):
    """生成模擬互動數據"""
    
    # 獲取 KOL 基線數據
    kol_id = article_data["member_id"]
    baseline = KOL_PERFORMANCE_BASELINE.get(kol_id, KOL_PERFORMANCE_BASELINE["9505546"])
    
    # 獲取內容類型加成
    content_type = article_data.get("content_type", "technical")
    content_multiplier = CONTENT_TYPE_MULTIPLIER.get(content_type, 1.0)
    
    # 獲取熱門話題加成
    is_trending = article_data.get("is_trending_topic", "FALSE")
    trending_boost = TRENDING_TOPIC_BOOST.get(is_trending, 1.0)
    
    # 計算基礎互動數
    base_likes = int(baseline["base_likes"] * content_multiplier * trending_boost)
    base_comments = int(baseline["base_comments"] * content_multiplier * trending_boost)
    
    # 添加隨機變異 (±20%)
    likes_variation = random.uniform(0.8, 1.2)
    comments_variation = random.uniform(0.8, 1.2)
    
    final_likes = int(base_likes * likes_variation)
    final_comments = int(base_comments * comments_variation)
    
    # 根據時間週期調整
    if time_period == "1hr":
        growth_rate = baseline["growth_rate_1hr"]
    elif time_period == "1day":
        growth_rate = baseline["growth_rate_1day"]
    elif time_period == "7days":
        growth_rate = baseline["growth_rate_7days"]
    else:
        growth_rate = 0
    
    # 計算成長後的數據
    final_likes = int(final_likes * (1 + growth_rate))
    final_comments = int(final_comments * (1 + growth_rate))
    
    return {
        "likes_count": max(0, final_likes),
        "comments_count": max(0, final_comments),
        "total_interactions": final_likes + final_comments,
        "growth_rate": growth_rate
    }
```

### 時間維度數據生成
```python
def generate_timeline_data(article_data):
    """生成時間維度模擬數據"""
    
    # 生成三個時間點的數據
    data_1hr = generate_mock_interaction_data(article_data, "1hr")
    data_1day = generate_mock_interaction_data(article_data, "1day")
    data_7days = generate_mock_interaction_data(article_data, "7days")
    
    # 計算成長率
    growth_rate_1day = calculate_growth_rate(data_1hr["total_interactions"], data_1day["total_interactions"])
    growth_rate_7days = calculate_growth_rate(data_1day["total_interactions"], data_7days["total_interactions"])
    
    return {
        "interactions_1hr": data_1hr["total_interactions"],
        "likes_1hr": data_1hr["likes_count"],
        "comments_1hr": data_1hr["comments_count"],
        
        "interactions_1day": data_1day["total_interactions"],
        "likes_1day": data_1day["likes_count"],
        "comments_1day": data_1day["comments_count"],
        "growth_rate_1day": growth_rate_1day,
        
        "interactions_7days": data_7days["total_interactions"],
        "likes_7days": data_7days["likes_count"],
        "comments_7days": data_7days["comments_count"],
        "growth_rate_7days": growth_rate_7days
    }
```

---

## 📈 模擬數據範例

### 互動回饋_1hr 模擬數據
```json
[
  {
    "article_id": "8d37cb0d-3901-4a04-a182-3dc4e09d570e-200",
    "member_id": "9505546",
    "nickname": "川川哥",
    "title": "台積電技術面深度解析",
    "content": "【川川哥】技術面快報 🚀🔥😂📈\n收盤 580.0（+15.0/+2.65%）…..這波是 上升趨勢\n觀察：支撐 575.0 / 壓力 585.0\nRSI=54.2, SMA20=572.3, SMA60=568.1",
    "topic_id": "8d37cb0d-3901-4a04-a182-3dc4e09d570e",
    "is_trending_topic": "TRUE",
    "post_time": "2024-01-15T14:30:25Z",
    "last_update_time": "2024-01-15T15:30:25Z",
    "likes_count": 68,
    "comments_count": 12,
    "total_interactions": 80,
    "engagement_rate": 0.125
  },
  {
    "article_id": "136405de-3cfb-4112-8124-af4f0d42bdd8-202",
    "member_id": "9505548",
    "nickname": "梅川褲子",
    "title": "聯發科5G晶片市占率提升",
    "content": "【梅川褲子】快訊速報 ⚡️📰📢🔥\n14:30 2454 爆出消息：5G晶片市占率提升\n股價 890.0 (+2.1%)\n短線觀察：技術面強勢",
    "topic_id": "136405de-3cfb-4112-8124-af4f0d42bdd8",
    "is_trending_topic": "TRUE",
    "post_time": "2024-01-15T14:25:10Z",
    "last_update_time": "2024-01-15T15:25:10Z",
    "likes_count": 78,
    "comments_count": 18,
    "total_interactions": 96,
    "engagement_rate": 0.142
  }
]
```

### 互動回饋_1day 模擬數據
```json
[
  {
    "article_id": "8d37cb0d-3901-4a04-a182-3dc4e09d570e-200",
    "member_id": "9505546",
    "nickname": "川川哥",
    "title": "台積電技術面深度解析",
    "content": "【川川哥】技術面快報 🚀🔥😂📈\n收盤 580.0（+15.0/+2.65%）…..這波是 上升趨勢\n觀察：支撐 575.0 / 壓力 585.0\nRSI=54.2, SMA20=572.3, SMA60=568.1",
    "topic_id": "8d37cb0d-3901-4a04-a182-3dc4e09d570e",
    "is_trending_topic": "TRUE",
    "post_time": "2024-01-15T14:30:25Z",
    "last_update_time": "2024-01-16T14:30:25Z",
    "likes_count": 92,
    "comments_count": 16,
    "total_interactions": 108,
    "growth_rate": 0.35
  }
]
```

### 互動回饋_7days 模擬數據
```json
[
  {
    "article_id": "8d37cb0d-3901-4a04-a182-3dc4e09d570e-200",
    "member_id": "9505546",
    "nickname": "川川哥",
    "title": "台積電技術面深度解析",
    "content": "【川川哥】技術面快報 🚀🔥😂📈\n收盤 580.0（+15.0/+2.65%）…..這波是 上升趨勢\n觀察：支撐 575.0 / 壓力 585.0\nRSI=54.2, SMA20=572.3, SMA60=568.1",
    "topic_id": "8d37cb0d-3901-4a04-a182-3dc4e09d570e",
    "is_trending_topic": "TRUE",
    "post_time": "2024-01-15T14:30:25Z",
    "last_update_time": "2024-01-22T14:30:25Z",
    "likes_count": 132,
    "comments_count": 26,
    "total_interactions": 158,
    "growth_rate": 0.65
  }
]
```

---

## 🛠️ 模擬數據實作

### Dashboard API 中的模擬數據服務
```python
# services/mock_data_service.py
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

class MockDataService:
    """模擬數據服務"""
    
    def __init__(self):
        self.kol_baseline = KOL_PERFORMANCE_BASELINE
        self.content_multiplier = CONTENT_TYPE_MULTIPLIER
        self.trending_boost = TRENDING_TOPIC_BOOST
    
    def generate_engagement_1hr(self, limit: int = 50) -> List[Dict]:
        """生成1小時後互動數據"""
        return self._generate_engagement_data("1hr", limit)
    
    def generate_engagement_1day(self, limit: int = 50) -> List[Dict]:
        """生成1日後互動數據"""
        return self._generate_engagement_data("1day", limit)
    
    def generate_engagement_7days(self, limit: int = 50) -> List[Dict]:
        """生成7日後互動數據"""
        return self._generate_engagement_data("7days", limit)
    
    def _generate_engagement_data(self, time_period: str, limit: int) -> List[Dict]:
        """生成指定時間週期的互動數據"""
        # 從貼文記錄表獲取基礎數據
        post_data = self._get_post_data(limit)
        
        engagement_data = []
        for post in post_data:
            interaction = self._calculate_interaction(post, time_period)
            engagement_data.append({
                "article_id": post["貼文ID"],
                "member_id": post["KOL ID"],
                "nickname": post["KOL 暱稱"],
                "title": post.get("已派發TopicTitle", "技術分析報告"),
                "content": post.get("生成內容", ""),
                "topic_id": post["已派發TopicID"],
                "is_trending_topic": "TRUE" if random.random() > 0.7 else "FALSE",
                "post_time": post["發文時間戳記"],
                "last_update_time": self._calculate_update_time(post["發文時間戳記"], time_period),
                "likes_count": interaction["likes_count"],
                "comments_count": interaction["comments_count"],
                "total_interactions": interaction["total_interactions"],
                "engagement_rate": interaction["engagement_rate"]
            })
        
        return engagement_data
    
    def get_engagement_statistics(self) -> Dict[str, Any]:
        """獲取互動統計數據"""
        data_1hr = self.generate_engagement_1hr()
        data_1day = self.generate_engagement_1day()
        data_7days = self.generate_engagement_7days()
        
        return {
            "total_interactions": sum(item["total_interactions"] for item in data_7days),
            "engagement_rate": 0.123,  # 模擬值
            "kol_ranking": self._calculate_kol_ranking(data_7days),
            "growth_rate": 0.152,  # 模擬值
            "user_activity": 0.85,  # 模擬值
            "timeline_data": {
                "1hr": data_1hr,
                "1day": data_1day,
                "7days": data_7days
            }
        }
    
    def _calculate_interaction(self, post: Dict, time_period: str) -> Dict:
        """計算互動數據"""
        # 實作互動計算邏輯
        pass
    
    def _get_post_data(self, limit: int) -> List[Dict]:
        """從貼文記錄表獲取數據"""
        # 實作數據獲取邏輯
        pass
```

### API 端點實作
```python
# main.py
from fastapi import FastAPI
from services.mock_data_service import MockDataService

app = FastAPI()
mock_service = MockDataService()

@app.get("/api/v1/engagement/mock/1hr")
async def get_engagement_1hr(limit: int = 50):
    """獲取1小時後互動數據 (模擬)"""
    return {
        "success": True,
        "data": mock_service.generate_engagement_1hr(limit),
        "timestamp": datetime.now().isoformat(),
        "note": "這是模擬數據，實際數據需要等待互動回饋表創建"
    }

@app.get("/api/v1/engagement/mock/1day")
async def get_engagement_1day(limit: int = 50):
    """獲取1日後互動數據 (模擬)"""
    return {
        "success": True,
        "data": mock_service.generate_engagement_1day(limit),
        "timestamp": datetime.now().isoformat(),
        "note": "這是模擬數據，實際數據需要等待互動回饋表創建"
    }

@app.get("/api/v1/engagement/mock/7days")
async def get_engagement_7days(limit: int = 50):
    """獲取7日後互動數據 (模擬)"""
    return {
        "success": True,
        "data": mock_service.generate_engagement_7days(limit),
        "timestamp": datetime.now().isoformat(),
        "note": "這是模擬數據，實際數據需要等待互動回饋表創建"
    }

@app.get("/api/v1/engagement/mock/statistics")
async def get_engagement_statistics():
    """獲取互動統計數據 (模擬)"""
    return {
        "success": True,
        "data": mock_service.get_engagement_statistics(),
        "timestamp": datetime.now().isoformat(),
        "note": "這是模擬數據，實際數據需要等待互動回饋表創建"
    }
```

---

## 🔄 模擬數據切換機制

### 環境變數控制
```python
# 環境變數控制模擬數據
USE_MOCK_DATA = os.getenv("USE_MOCK_ENGAGEMENT_DATA", "true").lower() == "true"

@app.get("/api/v1/engagement/statistics")
async def get_engagement_statistics():
    """獲取互動統計數據"""
    if USE_MOCK_DATA:
        return await get_mock_engagement_statistics()
    else:
        return await get_real_engagement_statistics()
```

### 前端標示
```typescript
// 前端顯示模擬數據標示
interface EngagementData {
  data: any;
  isMockData: boolean;
  note?: string;
}

// 在儀表板上顯示模擬數據標示
{data.isMockData && (
  <Alert
    message="模擬數據"
    description="當前顯示的是模擬互動數據，實際數據需要等待互動回饋表創建"
    type="info"
    showIcon
    closable
  />
)}
```

---

## 📋 實作檢查清單

### 後端實作
- [ ] 創建模擬數據服務類
- [ ] 實作互動數據生成算法
- [ ] 添加模擬數據 API 端點
- [ ] 實作環境變數控制
- [ ] 添加模擬數據標示

### 前端實作
- [ ] 整合模擬數據 API 調用
- [ ] 添加模擬數據標示
- [ ] 實作模擬數據圖表顯示
- [ ] 添加數據切換提示

### 測試驗證
- [ ] 驗證模擬數據真實性
- [ ] 測試不同 KOL 表現差異
- [ ] 驗證時間維度成長趨勢
- [ ] 測試模擬數據切換機制

---

## 🎯 優勢和注意事項

### 優勢
- **快速上線**: 不需要等待互動回饋表創建
- **完整測試**: 可以測試所有儀表板功能
- **真實模擬**: 基於真實 KOL 和內容類型
- **易於切換**: 可以輕鬆切換到真實數據

### 注意事項
- **數據標示**: 清楚標示這是模擬數據
- **參數調整**: 可以調整模擬參數來測試不同場景
- **切換準備**: 為將來切換到真實數據做好準備
- **性能考慮**: 模擬數據生成不要影響系統性能

---

*模擬數據設計版本: v1.0*  
*最後更新: 2024-01-01*  
*適用於: 虛擬 KOL 儀表板系統*
