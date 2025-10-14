# 自我學習系統技術文件

## 📋 系統概述

自我學習系統是 n8n-migration-project 的核心智能組件，負責分析高互動貼文數據，識別成功模式，並自動生成優化的發文參數配置。系統通過分析前20%的高互動貼文，提取關鍵特徵，並將這些洞察轉化為可執行的發文策略。

## 🎯 核心功能

### 1. **高互動數據識別**
- 自動識別前20%的高互動貼文
- 多維度互動指標分析（讚數、留言、分享、收藏、打賞）
- 動態閾值調整機制

### 2. **特徵提取與分析**
- 內容特徵分析（標題模式、內容結構、情感色彩）
- KOL 人設特徵分析（發文風格、用詞習慣、互動模式）
- 時機特徵分析（發文時間、市場環境、熱點事件）

### 3. **智能參數生成**
- 基於成功模式生成2-3組不同的發文參數
- 動態權重調整機制
- A/B 測試配置生成

### 4. **自動排程整合**
- 將生成的參數自動加入排程系統
- 智能時間分配
- 風險評估與控制

## 🏗️ 系統架構

### 前端組件架構

```typescript
// SelfLearningPage.tsx - 主要組件
interface SelfLearningPage {
  // 數據狀態
  posts: InteractionPost[];
  featureRankings: FeatureRanking[];
  highPerformanceFeatures: HighPerformanceFeature[];
  generatedSettings: PostingSetting[];
  experiments: ExperimentConfig[];
  insights: SelfLearningInsight[];
  
  // 控制狀態
  autoLearningEnabled: boolean;
  showFeatureAnalysis: boolean;
  showCalculationResults: boolean;
  showHighPerformanceFeatures: boolean;
  showGeneratedSettings: boolean;
  showExperiments: boolean;
  showInsights: boolean;
}
```

### 後端 API 架構

```python
# 自我學習數據獲取 API
@app.get("/posts/{post_id}/self-learning-data")
async def get_post_self_learning_data(post_id: str):
    """獲取貼文的自我學習數據 - 用於重建相同內容"""
    
# 互動數據統計 API
@router.get("/stats")
async def get_interaction_stats():
    """獲取互動數據統計"""
    
# 批量互動數據處理 API
@router.post("/refresh-all")
async def refresh_all_interactions():
    """批量刷新所有互動數據"""
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

### 特徵排名模型

```typescript
interface FeatureRanking {
  feature: string;
  score: number;
  impact: 'high' | 'medium' | 'low';
  confidence: number;
  sample_size: number;
  trend: 'increasing' | 'stable' | 'decreasing';
}
```

### 高表現特徵模型

```typescript
interface HighPerformanceFeature {
  feature_name: string;
  feature_type: 'content' | 'timing' | 'kol' | 'market';
  performance_score: number;
  frequency: number;
  success_rate: number;
  avg_interaction: number;
  examples: string[];
  recommended_settings: PostingSetting[];
}
```

## 🔄 核心流程

### 1. **數據收集階段**

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
        post['total_interactions'] = (
            post['likes'] + post['comments'] + post['shares'] + 
            post['collections'] + post['donations']
        )
        post['engagement_rate'] = calculate_engagement_rate(post)
    
    return interaction_data
```

### 2. **高互動數據識別**

```python
def identify_top_performers(interaction_data: List[Dict], top_percentage: float = 0.2):
    """識別前20%的高互動貼文"""
    
    # 按總互動數排序
    sorted_posts = sorted(
        interaction_data, 
        key=lambda x: x['total_interactions'], 
        reverse=True
    )
    
    # 計算前20%的數量
    top_count = max(1, int(len(sorted_posts) * top_percentage))
    
    # 獲取前20%的貼文
    top_performers = sorted_posts[:top_count]
    
    # 計算閾值
    threshold = top_performers[-1]['total_interactions'] if top_performers else 0
    
    logger.info(f"🎯 識別出 {len(top_performers)} 篇高互動貼文 (前{top_percentage*100}%)")
    logger.info(f"📊 互動閾值: {threshold}")
    
    return top_performers, threshold
```

### 3. **特徵提取與分析**

```python
def extract_features(top_performers: List[Dict]) -> List[FeatureRanking]:
    """提取高互動貼文的特徵"""
    
    features = []
    
    # 內容特徵分析
    content_features = analyze_content_features(top_performers)
    features.extend(content_features)
    
    # KOL 特徵分析
    kol_features = analyze_kol_features(top_performers)
    features.extend(kol_features)
    
    # 時機特徵分析
    timing_features = analyze_timing_features(top_performers)
    features.extend(timing_features)
    
    # 市場特徵分析
    market_features = analyze_market_features(top_performers)
    features.extend(market_features)
    
    # 計算特徵排名
    ranked_features = rank_features(features)
    
    return ranked_features

def analyze_content_features(posts: List[Dict]) -> List[FeatureRanking]:
    """分析內容特徵"""
    features = []
    
    # 標題長度分析
    title_lengths = [len(post['title']) for post in posts]
    avg_title_length = sum(title_lengths) / len(title_lengths)
    
    features.append(FeatureRanking(
        feature="title_length",
        score=calculate_feature_score(title_lengths, avg_title_length),
        impact="medium",
        confidence=0.8,
        sample_size=len(posts),
        trend="stable"
    ))
    
    # 內容結構分析
    content_structures = analyze_content_structure(posts)
    for structure, score in content_structures.items():
        features.append(FeatureRanking(
            feature=f"content_structure_{structure}",
            score=score,
            impact="high",
            confidence=0.9,
            sample_size=len(posts),
            trend="increasing"
        ))
    
    return features
```

### 4. **智能參數生成**

```python
def generate_posting_settings(features: List[FeatureRanking]) -> List[PostingSetting]:
    """基於特徵分析生成發文參數"""
    
    settings = []
    
    # 生成保守策略
    conservative_setting = generate_conservative_setting(features)
    settings.append(conservative_setting)
    
    # 生成激進策略
    aggressive_setting = generate_aggressive_setting(features)
    settings.append(aggressive_setting)
    
    # 生成平衡策略
    balanced_setting = generate_balanced_setting(features)
    settings.append(balanced_setting)
    
    return settings

def generate_conservative_setting(features: List[FeatureRanking]) -> PostingSetting:
    """生成保守策略"""
    return PostingSetting(
        name="保守策略",
        description="基於穩定特徵的保守發文策略",
        content_style_probabilities={
            "technical_analysis": 0.4,
            "fundamental_analysis": 0.3,
            "market_sentiment": 0.2,
            "news_summary": 0.1
        },
        analysis_depth_probabilities={
            "thorough": 0.6,
            "moderate": 0.3,
            "brief": 0.1
        },
        content_length_probabilities={
            "long": 0.3,
            "medium": 0.5,
            "short": 0.2
        },
        risk_level="low",
        expected_performance="stable"
    )
```

### 5. **自動排程整合**

```python
async def integrate_with_schedule(generated_settings: List[PostingSetting]):
    """將生成的參數整合到排程系統"""
    
    for setting in generated_settings:
        # 創建排程任務
        schedule_task = {
            "name": f"自我學習-{setting.name}",
            "description": f"基於自我學習生成的{setting.description}",
            "trigger_config": {
                "trigger_type": "self_learning",
                "generated_setting": setting.model_dump()
            },
            "schedule_config": {
                "enabled": True,
                "execution_time": calculate_optimal_time(setting),
                "frequency": "daily"
            },
            "auto_posting": True
        }
        
        # 添加到排程系統
        await add_to_schedule(schedule_task)
        
        logger.info(f"✅ 已將 {setting.name} 添加到排程系統")
```

## 🧠 智能分析算法

### 1. **互動率計算算法**

```python
def calculate_engagement_rate(post: Dict) -> float:
    """計算互動率"""
    
    # 基礎互動指標
    likes = post.get('likes', 0)
    comments = post.get('comments', 0)
    shares = post.get('shares', 0)
    collections = post.get('collections', 0)
    donations = post.get('donations', 0)
    
    # 表情互動
    emoji_interactions = (
        post.get('dislikes', 0) + post.get('laughs', 0) + 
        post.get('money', 0) + post.get('shock', 0) + 
        post.get('cry', 0) + post.get('think', 0) + 
        post.get('angry', 0)
    )
    
    # 總互動數
    total_interactions = likes + comments + shares + collections + donations + emoji_interactions
    
    # 瀏覽數（如果有）
    views = post.get('views', 1)  # 避免除零
    
    # 計算互動率
    engagement_rate = (total_interactions / views) * 100 if views > 0 else 0
    
    return round(engagement_rate, 2)
```

### 2. **特徵權重計算算法**

```python
def calculate_feature_weight(feature: str, posts: List[Dict]) -> float:
    """計算特徵權重"""
    
    # 獲取特徵值
    feature_values = extract_feature_values(feature, posts)
    
    if not feature_values:
        return 0.0
    
    # 計算統計指標
    mean_value = sum(feature_values) / len(feature_values)
    variance = sum((x - mean_value) ** 2 for x in feature_values) / len(feature_values)
    std_dev = variance ** 0.5
    
    # 計算權重（基於變異係數）
    coefficient_of_variation = std_dev / mean_value if mean_value > 0 else 0
    
    # 權重 = 1 / (1 + 變異係數)
    weight = 1 / (1 + coefficient_of_variation)
    
    return round(weight, 3)
```

### 3. **成功模式識別算法**

```python
def identify_success_patterns(top_performers: List[Dict]) -> List[SuccessPattern]:
    """識別成功模式"""
    
    patterns = []
    
    # 分析共同特徵
    common_features = find_common_features(top_performers)
    
    for feature, frequency in common_features.items():
        if frequency >= 0.7:  # 70%以上的高互動貼文都有此特徵
            pattern = SuccessPattern(
                feature=feature,
                frequency=frequency,
                impact_score=calculate_impact_score(feature, top_performers),
                confidence=calculate_confidence(feature, top_performers),
                examples=get_examples(feature, top_performers)
            )
            patterns.append(pattern)
    
    return patterns
```

## 📈 性能優化

### 1. **並行處理優化**

```python
class SelfLearningProcessor(ParallelProcessor):
    """自我學習並行處理器"""
    
    def __init__(self, max_concurrent: int = 5, timeout: int = 60):
        super().__init__(max_concurrent, timeout)
    
    async def process_learning_pipeline(self, posts: List[Dict]) -> LearningResult:
        """並行處理自我學習管道"""
        
        # 並行執行多個分析任務
        tasks = [
            self.analyze_content_features(posts),
            self.analyze_kol_features(posts),
            self.analyze_timing_features(posts),
            self.analyze_market_features(posts)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # 合併結果
        learning_result = LearningResult(
            content_features=results[0],
            kol_features=results[1],
            timing_features=results[2],
            market_features=results[3],
            timestamp=datetime.now()
        )
        
        return learning_result
```

### 2. **數據緩存優化**

```python
class SelfLearningCache:
    """自我學習數據緩存"""
    
    def __init__(self, cache_duration: int = 3600):  # 1小時緩存
        self.cache = {}
        self.cache_duration = cache_duration
    
    def get_cached_result(self, key: str) -> Optional[Any]:
        """獲取緩存結果"""
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_duration:
                return result
            else:
                del self.cache[key]
        return None
    
    def cache_result(self, key: str, result: Any):
        """緩存結果"""
        self.cache[key] = (result, time.time())
```

## 🔍 監控與日誌

### 1. **學習進度監控**

```python
class LearningProgressMonitor:
    """學習進度監控器"""
    
    def __init__(self):
        self.progress_data = {}
    
    def update_progress(self, task_id: str, progress: float, message: str):
        """更新學習進度"""
        self.progress_data[task_id] = {
            'progress': progress,
            'message': message,
            'timestamp': datetime.now(),
            'status': 'running' if progress < 100 else 'completed'
        }
        
        logger.info(f"📊 學習進度更新 - {task_id}: {progress}% - {message}")
    
    def get_progress(self, task_id: str) -> Dict[str, Any]:
        """獲取學習進度"""
        return self.progress_data.get(task_id, {
            'progress': 0,
            'message': '未開始',
            'timestamp': None,
            'status': 'pending'
        })
```

### 2. **學習效果追蹤**

```python
class LearningEffectTracker:
    """學習效果追蹤器"""
    
    def track_experiment_result(self, experiment_id: str, result: Dict[str, Any]):
        """追蹤實驗結果"""
        
        # 記錄實驗結果
        experiment_record = {
            'experiment_id': experiment_id,
            'result': result,
            'timestamp': datetime.now(),
            'success': result.get('success', False),
            'performance_improvement': result.get('performance_improvement', 0)
        }
        
        # 保存到數據庫
        save_experiment_record(experiment_record)
        
        # 更新學習模型
        if result.get('success', False):
            self.update_learning_model(experiment_id, result)
        
        logger.info(f"📈 實驗結果追蹤 - {experiment_id}: 成功率={result.get('success', False)}")
```

## 🚀 部署與配置

### 1. **環境變量配置**

```bash
# 自我學習系統配置
SELF_LEARNING_ENABLED=true
SELF_LEARNING_INTERVAL=3600  # 學習間隔（秒）
SELF_LEARNING_TOP_PERCENTAGE=0.2  # 前20%高互動貼文
SELF_LEARNING_MIN_SAMPLE_SIZE=50  # 最小樣本數
SELF_LEARNING_CACHE_DURATION=3600  # 緩存持續時間（秒）

# 並行處理配置
MAX_CONCURRENT_ANALYSIS=5
ANALYSIS_TIMEOUT=60

# 學習效果追蹤
TRACK_LEARNING_EFFECTS=true
EXPERIMENT_DURATION_DAYS=7
```

### 2. **Docker 配置**

```yaml
# docker-compose.yml
services:
  self-learning-service:
    build: ./self-learning-service
    environment:
      - SELF_LEARNING_ENABLED=true
      - SELF_LEARNING_INTERVAL=3600
      - MAX_CONCURRENT_ANALYSIS=5
    volumes:
      - ./data/learning-cache:/app/cache
    depends_on:
      - postgres
      - posting-service
```

## 📊 使用示例

### 1. **啟動自我學習**

```python
# 啟動自我學習系統
async def start_self_learning():
    """啟動自我學習系統"""
    
    # 創建學習處理器
    processor = SelfLearningProcessor(max_concurrent=5)
    
    # 獲取互動數據
    interaction_data = await collect_interaction_data()
    
    # 識別高互動貼文
    top_performers, threshold = identify_top_performers(interaction_data)
    
    # 提取特徵
    features = await processor.extract_features(top_performers)
    
    # 生成參數
    settings = generate_posting_settings(features)
    
    # 整合到排程
    await integrate_with_schedule(settings)
    
    logger.info("🎉 自我學習系統啟動完成")
```

### 2. **監控學習進度**

```python
# 監控學習進度
async def monitor_learning_progress():
    """監控學習進度"""
    
    monitor = LearningProgressMonitor()
    
    while True:
        # 獲取所有任務進度
        for task_id in monitor.progress_data.keys():
            progress = monitor.get_progress(task_id)
            print(f"任務 {task_id}: {progress['progress']}% - {progress['message']}")
        
        await asyncio.sleep(10)  # 每10秒更新一次
```

## 🔧 故障排除

### 1. **常見問題**

#### 問題：學習數據不足
**症狀**: 系統提示樣本數不足
**解決方案**:
```python
# 檢查數據庫中的貼文數量
post_count = get_post_record_service().get_posts_count()
if post_count < MIN_SAMPLE_SIZE:
    logger.warning(f"⚠️ 樣本數不足: {post_count} < {MIN_SAMPLE_SIZE}")
    # 等待更多數據或降低閾值
```

#### 問題：特徵提取失敗
**症狀**: 特徵分析返回空結果
**解決方案**:
```python
# 檢查數據質量
def validate_data_quality(posts: List[Dict]) -> bool:
    """驗證數據質量"""
    for post in posts:
        if not post.get('title') or not post.get('content'):
            return False
    return True
```

### 2. **性能問題**

#### 問題：學習過程太慢
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

### 1. **機器學習集成**
- 集成 TensorFlow 或 PyTorch
- 實現深度學習模型
- 自動特徵工程

### 2. **實時學習**
- 實時數據流處理
- 增量學習算法
- 動態模型更新

### 3. **多維度分析**
- 情感分析
- 語義分析
- 用戶行為分析

### 4. **A/B 測試框架**
- 自動化 A/B 測試
- 統計顯著性檢驗
- 結果可視化

## 📚 相關文檔

- [觸發器系統](./05-trigger-system.md)
- [內容生成流程](./06-content-generation-flow.md)
- [互動分析系統](./09-interaction-analysis-system.md)
- [Bug 分析和問題清單](./07-bug-analysis-and-issues.md)


