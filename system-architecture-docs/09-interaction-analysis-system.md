# 互動分析系統技術文件

## 📋 系統概述

互動分析系統是 n8n-migration-project 的數據分析核心，負責收集、處理和分析所有貼文的互動數據。系統提供多維度的互動分析功能，包括1小時、1日、7日數據分析，內容特徵分析，以及基於互動數據的智能洞察。

## 🎯 核心功能

### 1. **多時間維度分析**
- **1小時數據**: 實時互動監控，快速響應熱點
- **1日數據**: 日間互動趨勢分析，優化發文時機
- **7日數據**: 週期性互動模式分析，長期策略制定

### 2. **內容特徵分析**
- 標題特徵分析（長度、關鍵詞、情感色彩）
- 內容結構分析（段落、列表、引用）
- 互動元素分析（表情、標籤、連結）

### 3. **KOL 表現分析**
- 個人互動表現統計
- 發文風格與互動關係
- 最佳發文時機識別

### 4. **市場趨勢分析**
- 熱點話題追蹤
- 市場情緒分析
- 競爭對手分析

## 🏗️ 系統架構

### 前端組件架構

```typescript
// InteractionAnalysisPage.tsx - 主要組件
interface InteractionAnalysisPage {
  // 數據狀態
  posts: InteractionPost[];
  kolStats: Record<number, KOLStats>;
  overallStats: OverallStats | null;
  
  // 篩選條件
  selectedKOL: number | undefined;
  dateRange: [any, any] | null;
  includeExternal: boolean;
  searchKeyword: string;
  
  // 分析狀態
  showFeatureAnalysis: boolean;
  showSchedulingSuggestions: boolean;
  schedulingSuggestions: any[];
}

// 互動貼文數據模型
interface InteractionPost {
  post_id: string;
  article_id: string;
  kol_serial: number;
  kol_nickname: string;
  title: string;
  content: string;
  article_url: string;
  create_time: string;
  commodity_tags: Array<{key: string, type: string, bullOrBear: string}>;
  community_topic?: string;
  source: 'system' | 'external';
  status: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  bookmarks: number;
  donations?: number;
  engagement_rate: number;
}
```

### 後端 API 架構

```python
# 互動數據統計 API
@router.get("/stats")
async def get_interaction_stats():
    """獲取互動數據統計"""
    
# 批量互動數據更新 API
@router.post("/refresh-all")
async def refresh_all_interactions():
    """批量刷新所有互動數據"""
    
# 互動數據獲取 API
@router.get("/interactions")
async def get_interactions(
    kol_serial: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    include_external: bool = True
):
    """獲取互動數據"""
```

## 📊 數據模型

### 互動數據模型

```python
@dataclass
class InteractionData:
    """互動數據"""
    post_id: str
    member_id: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    click_rate: float = 0.0
    engagement_rate: float = 0.0
    
    # 詳細表情統計
    dislikes: int = 0
    laughs: int = 0
    money: int = 0
    shock: int = 0
    cry: int = 0
    think: int = 0
    angry: int = 0
    total_emojis: int = 0
    
    # 其他互動數據
    collections: int = 0
    donations: int = 0
    total_interactions: int = 0
    
    raw_data: Optional[Dict[str, Any]] = None
```

### KOL 統計模型

```typescript
interface KOLStats {
  kol_nickname: string;
  post_count: number;
  total_interactions: number;
  avg_interactions_per_post: number;
  best_performing_post: string;
  avg_engagement_rate: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
}
```

### 整體統計模型

```typescript
interface OverallStats {
  total_posts: number;
  total_interactions: number;
  total_views: number;
  total_likes: number;
  total_comments: number;
  total_shares: number;
  avg_interactions_per_post: number;
  avg_engagement_rate: number;
}
```

## 🔄 核心流程

### 1. **數據收集流程**

```python
async def collect_interaction_data():
    """收集互動數據"""
    
    # 1. 獲取所有已發布貼文
    published_posts = get_post_record_service().get_all_posts(status='published')
    
    # 2. 並行獲取互動數據
    interaction_processor = InteractionDataProcessor(max_concurrent=3)
    interaction_data = await interaction_processor.fetch_interactions_parallel(
        published_posts, 
        progress_callback=update_progress
    )
    
    # 3. 計算互動指標
    for post in interaction_data:
        post['total_interactions'] = calculate_total_interactions(post)
        post['engagement_rate'] = calculate_engagement_rate(post)
    
    return interaction_data

def calculate_total_interactions(post: Dict) -> int:
    """計算總互動數"""
    return (
        post.get('likes', 0) + 
        post.get('comments', 0) + 
        post.get('shares', 0) + 
        post.get('collections', 0) + 
        post.get('donations', 0) +
        post.get('total_emojis', 0)
    )

def calculate_engagement_rate(post: Dict) -> float:
    """計算互動率"""
    total_interactions = calculate_total_interactions(post)
    views = post.get('views', 1)  # 避免除零
    
    return (total_interactions / views) * 100 if views > 0 else 0
```

### 2. **多時間維度分析**

```python
def analyze_time_dimensions(interaction_data: List[Dict]) -> Dict[str, Any]:
    """多時間維度分析"""
    
    now = datetime.now()
    
    # 1小時數據分析
    one_hour_ago = now - timedelta(hours=1)
    one_hour_data = filter_by_time_range(interaction_data, one_hour_ago, now)
    
    # 1日數據分析
    one_day_ago = now - timedelta(days=1)
    one_day_data = filter_by_time_range(interaction_data, one_day_ago, now)
    
    # 7日數據分析
    seven_days_ago = now - timedelta(days=7)
    seven_days_data = filter_by_time_range(interaction_data, seven_days_ago, now)
    
    return {
        '1hour': analyze_interaction_trends(one_hour_data),
        '1day': analyze_interaction_trends(one_day_data),
        '7days': analyze_interaction_trends(seven_days_data)
    }

def filter_by_time_range(data: List[Dict], start_time: datetime, end_time: datetime) -> List[Dict]:
    """按時間範圍過濾數據"""
    filtered_data = []
    
    for post in data:
        post_time = datetime.fromisoformat(post['create_time'].replace('Z', '+00:00'))
        if start_time <= post_time <= end_time:
            filtered_data.append(post)
    
    return filtered_data
```

### 3. **內容特徵分析**

```python
def analyze_content_features(posts: List[Dict]) -> Dict[str, Any]:
    """內容特徵分析"""
    
    features = {
        'title_features': analyze_title_features(posts),
        'content_features': analyze_content_structure(posts),
        'interaction_features': analyze_interaction_features(posts)
    }
    
    return features

def analyze_title_features(posts: List[Dict]) -> Dict[str, Any]:
    """標題特徵分析"""
    
    titles = [post['title'] for post in posts]
    
    # 標題長度分析
    title_lengths = [len(title) for title in titles]
    avg_title_length = sum(title_lengths) / len(title_lengths)
    
    # 關鍵詞分析
    keywords = extract_keywords(titles)
    
    # 情感分析
    sentiment_scores = analyze_sentiment(titles)
    
    return {
        'avg_length': avg_title_length,
        'length_distribution': {
            'short': len([l for l in title_lengths if l < 20]),
            'medium': len([l for l in title_lengths if 20 <= l < 40]),
            'long': len([l for l in title_lengths if l >= 40])
        },
        'top_keywords': keywords[:10],
        'sentiment_distribution': sentiment_scores
    }

def analyze_content_structure(posts: List[Dict]) -> Dict[str, Any]:
    """內容結構分析"""
    
    structures = {
        'paragraph_count': [],
        'list_count': [],
        'emoji_count': [],
        'hashtag_count': [],
        'link_count': []
    }
    
    for post in posts:
        content = post['content']
        
        # 段落數
        paragraphs = content.split('\n\n')
        structures['paragraph_count'].append(len(paragraphs))
        
        # 列表數
        lists = content.count('•') + content.count('-') + content.count('*')
        structures['list_count'].append(lists)
        
        # 表情數
        emojis = count_emojis(content)
        structures['emoji_count'].append(emojis)
        
        # 標籤數
        hashtags = content.count('#')
        structures['hashtag_count'].append(hashtags)
        
        # 連結數
        links = content.count('http')
        structures['link_count'].append(links)
    
    # 計算統計數據
    result = {}
    for key, values in structures.items():
        result[key] = {
            'avg': sum(values) / len(values),
            'max': max(values),
            'min': min(values)
        }
    
    return result
```

### 4. **KOL 表現分析**

```python
def analyze_kol_performance(interaction_data: List[Dict]) -> Dict[int, KOLStats]:
    """KOL 表現分析"""
    
    kol_stats = {}
    
    # 按 KOL 分組
    kol_groups = group_by_kol(interaction_data)
    
    for kol_serial, posts in kol_groups.items():
        stats = calculate_kol_stats(kol_serial, posts)
        kol_stats[kol_serial] = stats
    
    return kol_stats

def calculate_kol_stats(kol_serial: int, posts: List[Dict]) -> KOLStats:
    """計算 KOL 統計數據"""
    
    if not posts:
        return KOLStats(
            kol_nickname="",
            post_count=0,
            total_interactions=0,
            avg_interactions_per_post=0,
            best_performing_post="",
            avg_engagement_rate=0,
            total_views=0,
            total_likes=0,
            total_comments=0,
            total_shares=0
        )
    
    # 基本統計
    post_count = len(posts)
    total_interactions = sum(post['total_interactions'] for post in posts)
    total_views = sum(post.get('views', 0) for post in posts)
    total_likes = sum(post.get('likes', 0) for post in posts)
    total_comments = sum(post.get('comments', 0) for post in posts)
    total_shares = sum(post.get('shares', 0) for post in posts)
    
    # 平均數據
    avg_interactions_per_post = total_interactions / post_count
    avg_engagement_rate = sum(post['engagement_rate'] for post in posts) / post_count
    
    # 最佳表現貼文
    best_post = max(posts, key=lambda x: x['total_interactions'])
    best_performing_post = best_post['title']
    
    return KOLStats(
        kol_nickname=posts[0]['kol_nickname'],
        post_count=post_count,
        total_interactions=total_interactions,
        avg_interactions_per_post=avg_interactions_per_post,
        best_performing_post=best_performing_post,
        avg_engagement_rate=avg_engagement_rate,
        total_views=total_views,
        total_likes=total_likes,
        total_comments=total_comments,
        total_shares=total_shares
    )
```

## 🧠 智能分析算法

### 1. **互動趨勢分析算法**

```python
def analyze_interaction_trends(posts: List[Dict]) -> Dict[str, Any]:
    """互動趨勢分析"""
    
    if not posts:
        return {
            'trend': 'stable',
            'growth_rate': 0,
            'peak_hours': [],
            'recommendations': []
        }
    
    # 按時間排序
    sorted_posts = sorted(posts, key=lambda x: x['create_time'])
    
    # 計算增長率
    if len(sorted_posts) >= 2:
        early_interactions = sum(post['total_interactions'] for post in sorted_posts[:len(sorted_posts)//2])
        late_interactions = sum(post['total_interactions'] for post in sorted_posts[len(sorted_posts)//2:])
        growth_rate = ((late_interactions - early_interactions) / early_interactions) * 100 if early_interactions > 0 else 0
    else:
        growth_rate = 0
    
    # 識別趨勢
    if growth_rate > 10:
        trend = 'increasing'
    elif growth_rate < -10:
        trend = 'decreasing'
    else:
        trend = 'stable'
    
    # 分析高峰時段
    peak_hours = analyze_peak_hours(posts)
    
    # 生成建議
    recommendations = generate_recommendations(trend, growth_rate, peak_hours)
    
    return {
        'trend': trend,
        'growth_rate': growth_rate,
        'peak_hours': peak_hours,
        'recommendations': recommendations
    }
```

### 2. **熱點話題識別算法**

```python
def identify_hot_topics(posts: List[Dict], time_window: int = 24) -> List[Dict[str, Any]]:
    """識別熱點話題"""
    
    # 提取話題標籤
    topics = []
    for post in posts:
        if post.get('commodity_tags'):
            for tag in post['commodity_tags']:
                topics.append({
                    'topic': tag['key'],
                    'type': tag['type'],
                    'interactions': post['total_interactions'],
                    'timestamp': post['create_time']
                })
    
    # 按話題分組
    topic_groups = {}
    for topic in topics:
        key = f"{topic['topic']}_{topic['type']}"
        if key not in topic_groups:
            topic_groups[key] = []
        topic_groups[key].append(topic)
    
    # 計算話題熱度
    hot_topics = []
    for key, topic_posts in topic_groups.items():
        total_interactions = sum(t['interactions'] for t in topic_posts)
        post_count = len(topic_posts)
        avg_interactions = total_interactions / post_count
        
        # 計算熱度分數
        heat_score = (total_interactions * 0.7) + (post_count * 0.3)
        
        hot_topics.append({
            'topic': topic_posts[0]['topic'],
            'type': topic_posts[0]['type'],
            'total_interactions': total_interactions,
            'post_count': post_count,
            'avg_interactions': avg_interactions,
            'heat_score': heat_score
        })
    
    # 按熱度排序
    hot_topics.sort(key=lambda x: x['heat_score'], reverse=True)
    
    return hot_topics[:10]  # 返回前10個熱點話題
```

### 3. **發文時機優化算法**

```python
def optimize_posting_timing(kol_serial: int, historical_data: List[Dict]) -> Dict[str, Any]:
    """優化發文時機"""
    
    # 按小時分組
    hourly_data = {}
    for post in historical_data:
        if post['kol_serial'] == kol_serial:
            hour = datetime.fromisoformat(post['create_time'].replace('Z', '+00:00')).hour
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(post)
    
    # 計算每小時的平均互動
    hourly_performance = {}
    for hour, posts in hourly_data.items():
        avg_interactions = sum(post['total_interactions'] for post in posts) / len(posts)
        hourly_performance[hour] = {
            'avg_interactions': avg_interactions,
            'post_count': len(posts),
            'success_rate': len([p for p in posts if p['total_interactions'] > 10]) / len(posts)
        }
    
    # 找出最佳時段
    best_hours = sorted(
        hourly_performance.items(), 
        key=lambda x: x[1]['avg_interactions'], 
        reverse=True
    )[:3]
    
    return {
        'best_hours': [hour for hour, _ in best_hours],
        'hourly_performance': hourly_performance,
        'recommendations': generate_timing_recommendations(best_hours)
    }
```

## 📈 性能優化

### 1. **並行處理優化**

```python
class InteractionAnalysisProcessor(ParallelProcessor):
    """互動分析並行處理器"""
    
    def __init__(self, max_concurrent: int = 5, timeout: int = 60):
        super().__init__(max_concurrent, timeout)
    
    async def analyze_interactions_parallel(self, posts: List[Dict]) -> Dict[str, Any]:
        """並行分析互動數據"""
        
        # 並行執行多個分析任務
        tasks = [
            self.analyze_content_features(posts),
            self.analyze_kol_performance(posts),
            self.analyze_time_dimensions(posts),
            self.identify_hot_topics(posts)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return {
            'content_features': results[0],
            'kol_performance': results[1],
            'time_dimensions': results[2],
            'hot_topics': results[3]
        }
```

### 2. **數據緩存優化**

```python
class InteractionCache:
    """互動數據緩存"""
    
    def __init__(self, cache_duration: int = 1800):  # 30分鐘緩存
        self.cache = {}
        self.cache_duration = cache_duration
    
    def get_cached_analysis(self, key: str) -> Optional[Any]:
        """獲取緩存的分析結果"""
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_duration:
                return result
            else:
                del self.cache[key]
        return None
    
    def cache_analysis(self, key: str, result: Any):
        """緩存分析結果"""
        self.cache[key] = (result, time.time())
```

## 🔍 監控與日誌

### 1. **分析進度監控**

```python
class AnalysisProgressMonitor:
    """分析進度監控器"""
    
    def __init__(self):
        self.progress_data = {}
    
    def update_progress(self, task_id: str, progress: float, message: str):
        """更新分析進度"""
        self.progress_data[task_id] = {
            'progress': progress,
            'message': message,
            'timestamp': datetime.now(),
            'status': 'running' if progress < 100 else 'completed'
        }
        
        logger.info(f"📊 分析進度更新 - {task_id}: {progress}% - {message}")
    
    def get_progress(self, task_id: str) -> Dict[str, Any]:
        """獲取分析進度"""
        return self.progress_data.get(task_id, {
            'progress': 0,
            'message': '未開始',
            'timestamp': None,
            'status': 'pending'
        })
```

### 2. **分析結果追蹤**

```python
class AnalysisResultTracker:
    """分析結果追蹤器"""
    
    def track_analysis_result(self, analysis_id: str, result: Dict[str, Any]):
        """追蹤分析結果"""
        
        # 記錄分析結果
        analysis_record = {
            'analysis_id': analysis_id,
            'result': result,
            'timestamp': datetime.now(),
            'data_quality': self.assess_data_quality(result),
            'insights_count': len(result.get('insights', []))
        }
        
        # 保存到數據庫
        save_analysis_record(analysis_record)
        
        logger.info(f"📈 分析結果追蹤 - {analysis_id}: 數據品質={analysis_record['data_quality']}")
    
    def assess_data_quality(self, result: Dict[str, Any]) -> str:
        """評估數據品質"""
        sample_size = result.get('sample_size', 0)
        
        if sample_size >= 100:
            return 'high'
        elif sample_size >= 50:
            return 'medium'
        else:
            return 'low'
```

## 🚀 部署與配置

### 1. **環境變量配置**

```bash
# 互動分析系統配置
INTERACTION_ANALYSIS_ENABLED=true
ANALYSIS_INTERVAL=1800  # 分析間隔（秒）
CACHE_DURATION=1800  # 緩存持續時間（秒）
MAX_CONCURRENT_ANALYSIS=5
ANALYSIS_TIMEOUT=60

# 數據收集配置
COLLECT_EXTERNAL_DATA=true
EXTERNAL_DATA_SOURCES=cmoney,facebook,instagram
DATA_RETENTION_DAYS=90

# 性能配置
ENABLE_PARALLEL_PROCESSING=true
MAX_BATCH_SIZE=1000
MEMORY_LIMIT=2GB
```

### 2. **Docker 配置**

```yaml
# docker-compose.yml
services:
  interaction-analysis-service:
    build: ./interaction-analysis-service
    environment:
      - INTERACTION_ANALYSIS_ENABLED=true
      - ANALYSIS_INTERVAL=1800
      - MAX_CONCURRENT_ANALYSIS=5
    volumes:
      - ./data/analysis-cache:/app/cache
    depends_on:
      - postgres
      - posting-service
```

## 📊 使用示例

### 1. **啟動互動分析**

```python
# 啟動互動分析系統
async def start_interaction_analysis():
    """啟動互動分析系統"""
    
    # 創建分析處理器
    processor = InteractionAnalysisProcessor(max_concurrent=5)
    
    # 獲取互動數據
    interaction_data = await collect_interaction_data()
    
    # 並行分析
    analysis_result = await processor.analyze_interactions_parallel(interaction_data)
    
    # 生成洞察
    insights = generate_insights(analysis_result)
    
    # 保存結果
    await save_analysis_result(analysis_result, insights)
    
    logger.info("🎉 互動分析系統啟動完成")
```

### 2. **監控分析進度**

```python
# 監控分析進度
async def monitor_analysis_progress():
    """監控分析進度"""
    
    monitor = AnalysisProgressMonitor()
    
    while True:
        # 獲取所有任務進度
        for task_id in monitor.progress_data.keys():
            progress = monitor.get_progress(task_id)
            print(f"任務 {task_id}: {progress['progress']}% - {progress['message']}")
        
        await asyncio.sleep(10)  # 每10秒更新一次
```

## 🔧 故障排除

### 1. **常見問題**

#### 問題：數據收集失敗
**症狀**: 無法獲取互動數據
**解決方案**:
```python
# 檢查 API 連接
async def check_api_connection():
    """檢查 API 連接"""
    try:
        response = await cmoney_client.health_check()
        if response.status_code == 200:
            logger.info("✅ API 連接正常")
        else:
            logger.error("❌ API 連接失敗")
    except Exception as e:
        logger.error(f"❌ API 連接異常: {e}")
```

#### 問題：分析結果不準確
**症狀**: 分析結果與實際情況不符
**解決方案**:
```python
# 驗證數據品質
def validate_data_quality(data: List[Dict]) -> bool:
    """驗證數據品質"""
    if not data:
        return False
    
    # 檢查必要欄位
    required_fields = ['post_id', 'likes', 'comments', 'shares']
    for post in data:
        for field in required_fields:
            if field not in post:
                return False
    
    return True
```

### 2. **性能問題**

#### 問題：分析過程太慢
**解決方案**:
- 增加並行處理數量
- 使用數據緩存
- 優化算法複雜度

#### 問題：內存使用過高
**解決方案**:
- 分批處理數據
- 使用生成器而非列表
- 及時清理緩存

## 📈 未來改進

### 1. **實時分析**
- 實時數據流處理
- 即時洞察生成
- 動態告警系統

### 2. **機器學習集成**
- 預測模型
- 異常檢測
- 自動優化建議

### 3. **多平台整合**
- 跨平台數據整合
- 統一分析視圖
- 綜合表現評估

### 4. **可視化增強**
- 互動式圖表
- 實時儀表板
- 自定義報告

## 📚 相關文檔

- [自我學習系統](./08-self-learning-system.md)
- [觸發器系統](./05-trigger-system.md)
- [內容生成流程](./06-content-generation-flow.md)
- [Bug 分析和問題清單](./07-bug-analysis-and-issues.md)


