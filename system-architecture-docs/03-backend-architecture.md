# 後端架構

## 🎯 後端技術棧

### 核心技術
- **FastAPI** - 現代 Python Web 框架
- **Python 3.11+** - 編程語言
- **PostgreSQL** - 關係型數據庫
- **SQLAlchemy** - ORM 框架
- **Pydantic** - 數據驗證
- **Docker** - 容器化部署

### 外部依賴
- **OpenAI GPT API** - AI 內容生成
- **CMoney API** - 內容發布平台
- **Serper API** - 新聞搜尋
- **FinLab API** - 金融數據
- **HTTPX** - 異步 HTTP 客戶端

## 🏗️ 服務架構

### 微服務架構
```
┌─────────────────────────────────────────────────────────────────┐
│                    posting-service (8001)                      │
├─────────────────────────────────────────────────────────────────┤
│  - 貼文管理 API        - KOL 管理 API        - 互動分析 API     │
│  - 批次處理 API        - 排程管理 API        - 觸發器 API       │
│  - 發布管理 API        - 自我學習 API        - 並行處理 API     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  dashboard-backend (8012)                      │
├─────────────────────────────────────────────────────────────────┤
│  - 儀表板 API          - 系統監控 API        - 用戶管理 API     │
│  - 統計分析 API        - 配置管理 API        - 權限控制 API     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL (5432)                           │
├─────────────────────────────────────────────────────────────────┤
│  - post_records        - kol_profiles        - schedules        │
│  - interaction_data    - user_management     - system_logs      │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 項目結構

```
posting-service/
├── main.py                    # FastAPI 應用入口
├── requirements.txt           # Python 依賴
├── Dockerfile                # Docker 配置
├── routes/                   # API 路由模組
│   ├── __init__.py          # 路由初始化
│   ├── post_routes.py       # 貼文管理路由
│   ├── kol_routes.py        # KOL 管理路由
│   ├── kol_api_routes.py    # KOL API 路由
│   ├── publish_route.py     # 發布管理路由
│   ├── interaction_routes.py # 互動分析路由
│   ├── interaction_batch_routes.py # 批次互動路由
│   ├── schedule_routes_simple.py # 排程管理路由
│   ├── intraday_trigger_route.py # 盤中觸發器路由
│   └── parallel_intraday_route.py # 並行觸發器路由
├── services/                 # 業務邏輯服務
│   ├── post_record_service.py # 貼文記錄服務
│   ├── postgresql_service.py # PostgreSQL 服務
│   ├── parallel_processor.py # 並行處理服務
│   └── parallel_batch_generator.py # 批次生成服務
├── models/                   # 數據模型
│   ├── post_record.py       # 貼文記錄模型
│   ├── kol_profile.py       # KOL 配置模型
│   └── schedule.py          # 排程模型
├── utils/                    # 工具函數
│   ├── date_utils.py        # 日期工具
│   ├── validation_utils.py  # 驗證工具
│   └── security_utils.py    # 安全工具
├── src/                      # 外部服務客戶端
│   ├── clients/             # API 客戶端
│   │   ├── cmoney/          # CMoney 客戶端
│   │   ├── openai/          # OpenAI 客戶端
│   │   └── serper/          # Serper 客戶端
│   └── services/            # 外部服務
│       ├── news_service.py  # 新聞服務
│       └── stock_service.py # 股票服務
└── tests/                    # 測試文件
    ├── test_post_routes.py  # 貼文路由測試
    ├── test_kol_routes.py   # KOL 路由測試
    └── test_services.py     # 服務測試
```

## 🛣️ API 路由架構

### 主要路由模組

#### post_routes.py - 貼文管理
```python
router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/")
async def get_all_posts(skip: int = 0, limit: int = 100, status: Optional[str] = None)

@router.get("/{post_id}")
async def get_post_detail(post_id: str)

@router.post("/")
async def create_post(post_data: PostCreateRequest)

@router.put("/{post_id}")
async def update_post(post_id: str, update_data: PostUpdateRequest)

@router.delete("/{post_id}")
async def delete_post(post_id: str)

@router.get("/history-stats")
async def get_post_history_stats()
```

#### kol_routes.py - KOL 管理
```python
router = APIRouter(prefix="/kol", tags=["kol"])

@router.get("/list")
async def get_kol_list()

@router.get("/{kol_serial}")
async def get_kol_detail(kol_serial: int)

@router.post("/")
async def create_kol(kol_data: KOLCreateRequest)

@router.put("/{kol_serial}")
async def update_kol(kol_serial: int, update_data: KOLUpdateRequest)

@router.delete("/{kol_serial}")
async def delete_kol(kol_serial: int)
```

#### interaction_routes.py - 互動分析
```python
router = APIRouter(prefix="/interactions", tags=["interactions"])

@router.post("/update/{post_id}")
async def update_post_interactions(post_id: str, interaction_data: Dict[str, Any])

@router.get("/{post_id}")
async def get_post_interactions(post_id: str)

@router.post("/batch-update")
async def batch_update_interactions(updates: List[InteractionUpdate])

@router.get("/stats")
async def get_interaction_stats()
```

#### schedule_routes_simple.py - 排程管理
```python
router = APIRouter(prefix="/api/schedule", tags=["schedule"])

@router.get("/tasks")
async def get_schedule_tasks()

@router.get("/daily-stats")
async def get_daily_stats()

@router.post("/create")
async def create_schedule(schedule_data: ScheduleCreateRequest)

@router.put("/{schedule_id}")
async def update_schedule(schedule_id: str, update_data: ScheduleUpdateRequest)

@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str)
```

## 🗄️ 數據庫設計

### 主要數據表

#### post_records - 貼文記錄
```sql
CREATE TABLE post_records (
    post_id VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id INTEGER,
    kol_serial INTEGER,
    kol_nickname VARCHAR(100),
    kol_persona VARCHAR(50),
    stock_code VARCHAR(10),
    stock_name VARCHAR(100),
    title TEXT,
    content TEXT,
    content_md TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    reviewer_notes TEXT,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    scheduled_at TIMESTAMP,
    published_at TIMESTAMP,
    cmoney_post_id VARCHAR(255),
    cmoney_post_url TEXT,
    publish_error TEXT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    topic_id VARCHAR(255),
    topic_title VARCHAR(255),
    technical_analysis TEXT,
    serper_data JSONB,
    quality_score DECIMAL(3,2),
    ai_detection_score DECIMAL(3,2),
    risk_level VARCHAR(20),
    generation_params JSONB,
    commodity_tags JSONB
);
```

#### kol_profiles - KOL 配置
```sql
CREATE TABLE kol_profiles (
    serial INTEGER PRIMARY KEY,
    nickname VARCHAR(100) NOT NULL,
    persona VARCHAR(50) NOT NULL,
    content_style VARCHAR(50),
    target_audience VARCHAR(50),
    expertise_areas TEXT[],
    tone_settings JSONB,
    model_settings JSONB,
    statistics JSONB,
    email VARCHAR(255),
    password VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### schedules - 排程管理
```sql
CREATE TABLE schedules (
    schedule_id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50),
    trigger_config JSONB,
    kol_allocation VARCHAR(50),
    post_time TIME,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_executed_at TIMESTAMP,
    next_execution_at TIMESTAMP,
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0
);
```

## 🔧 核心服務

### PostgreSQLPostRecordService
```python
class PostgreSQLPostRecordService:
    def __init__(self):
        self.connection_string = self._get_connection_string()
        self.engine = create_engine(self.connection_string)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_all_posts(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[PostRecordInDB]
    
    def get_post_record(self, post_id: str) -> Optional[PostRecordInDB]
    
    def create_post_record(self, post_record: PostRecordInDB) -> PostRecordInDB
    
    def update_post_record(self, post_id: str, update_data: Dict[str, Any]) -> Optional[PostRecordInDB]
    
    def delete_post_record(self, post_id: str) -> bool
    
    def get_kol_profile(self, kol_serial: int) -> Optional[KOLProfile]
    
    def get_schedule_list(self) -> List[Schedule]
```

### ParallelProcessor
```python
class ParallelProcessor:
    def __init__(self, max_concurrent: int = 5, timeout: int = 30, max_retries: int = 3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def process_batch_async(self, tasks: List[Callable], progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]
    
    async def _process_task_with_retry(self, task_func: Callable, *args, **kwargs) -> Any

class InteractionDataProcessor(ParallelProcessor):
    async def fetch_interactions_parallel(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]
    
    async def _fetch_single_interaction(self, post: Dict[str, Any]) -> Dict[str, Any]

class PostGenerationProcessor(ParallelProcessor):
    async def generate_posts_parallel(self, requests: List[PostingRequest]) -> List[Dict[str, Any]]
    
    async def _generate_single_post(self, request: PostingRequest) -> Dict[str, Any]
```

## 🤖 AI 內容生成

### OpenAI 客戶端
```python
class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def generate_content(self, prompt: str, model: str = "gpt-4") -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content

class ContentGenerator:
    def __init__(self):
        self.openai_client = OpenAIClient(os.getenv("OPENAI_API_KEY"))
        self.serper_client = SerperClient(os.getenv("SERPER_API_KEY"))
    
    async def generate_post_content(self, request: PostingRequest) -> GeneratedContent:
        # 1. 收集股票數據
        stock_data = await self._get_stock_data(request.stock_code)
        
        # 2. 搜尋相關新聞
        news_data = await self._search_news(request.stock_name, request.news_config)
        
        # 3. 生成內容
        content = await self._generate_content(stock_data, news_data, request)
        
        return content
```

## 📊 觸發器系統

### 觸發器類型
```python
class TriggerType(Enum):
    INDIVIDUAL = "individual"      # 個股觸發器
    SECTOR = "sector"             # 類股觸發器
    MACRO = "macro"               # 總經觸發器
    NEWS = "news"                 # 新聞觸發器
    INTRADAY = "intraday"         # 盤中觸發器
    VOLUME = "volume"             # 成交量觸發器
    CUSTOM = "custom"             # 自定義觸發器

class TriggerConfig:
    trigger_type: TriggerType
    trigger_key: str
    stock_filter: str
    volume_filter: Optional[str] = None
    sector_filter: Optional[str] = None
    macro_filter: Optional[str] = None
    news_filter: Optional[str] = None
    custom_filters: Optional[Dict[str, Any]] = None
    news_keywords: Optional[List[str]] = None
```

### 觸發器處理
```python
class TriggerProcessor:
    def __init__(self):
        self.finlab_client = FinLabClient()
        self.serper_client = SerperClient()
    
    async def process_trigger(self, trigger_config: TriggerConfig) -> TriggerResult:
        if trigger_config.trigger_type == TriggerType.INDIVIDUAL:
            return await self._process_individual_trigger(trigger_config)
        elif trigger_config.trigger_type == TriggerType.VOLUME:
            return await self._process_volume_trigger(trigger_config)
        elif trigger_config.trigger_type == TriggerType.CUSTOM:
            return await self._process_custom_trigger(trigger_config)
    
    async def _process_individual_trigger(self, config: TriggerConfig) -> TriggerResult:
        # 處理個股觸發器邏輯
        pass
    
    async def _process_volume_trigger(self, config: TriggerConfig) -> TriggerResult:
        # 處理成交量觸發器邏輯
        pass
```

## 🔄 批次處理

### 批次生成器
```python
class ParallelBatchGenerator:
    def __init__(self, max_concurrent: int = 2, timeout: int = 120):
        self.post_generation_processor = PostGenerationProcessor(max_concurrent, timeout)
    
    async def generate_posts_parallel_stream(self, request: BatchRequest, progress_callback: Optional[Callable] = None) -> AsyncGenerator[str, None]:
        total_posts = len(request.posts)
        successful_posts = 0
        failed_posts = 0
        
        # 生成批次級別的共享 commodity tags
        batch_commodity_tags = await self._generate_batch_tags(request)
        
        yield f"data: {json.dumps({'type': 'batch_start', 'total': total_posts, 'session_id': request.session_id})}\n\n"
        
        tasks = [
            (self._generate_single_post_task, post_data, request, batch_commodity_tags)
            for post_data in request.posts
        ]
        
        async for result_event in self.post_generation_processor.process_batch_stream(tasks, progress_callback):
            if result_event.get('success'):
                successful_posts += 1
            else:
                failed_posts += 1
            
            result_event['progress'] = {
                'current': successful_posts + failed_posts,
                'total': total_posts,
                'percentage': round((successful_posts + failed_posts) / total_posts * 100, 1),
                'successful': successful_posts,
                'failed': failed_posts
            }
            yield f"data: {json.dumps(result_event)}\n\n"
        
        yield f"data: {json.dumps({'type': 'batch_end', 'total': total_posts, 'successful': successful_posts, 'failed': failed_posts})}\n\n"
```

## 📈 自我學習系統

### 互動數據分析
```python
class SelfLearningService:
    def __init__(self):
        self.post_service = PostgreSQLPostRecordService()
    
    async def analyze_top_performing_content(self, time_period: str = "7d") -> AnalysisResult:
        # 1. 獲取指定時間段內的貼文數據
        posts = await self._get_posts_by_period(time_period)
        
        # 2. 計算互動分數
        posts_with_scores = await self._calculate_interaction_scores(posts)
        
        # 3. 找出前20%的高互動內容
        top_20_percent = await self._get_top_percentile(posts_with_scores, 0.2)
        
        # 4. 分析共同特徵
        common_features = await self._analyze_common_features(top_20_percent)
        
        # 5. 生成優化建議
        optimization_suggestions = await self._generate_optimization_suggestions(common_features)
        
        return AnalysisResult(
            total_posts=len(posts),
            top_performing_count=len(top_20_percent),
            common_features=common_features,
            suggestions=optimization_suggestions
        )
    
    async def _calculate_interaction_scores(self, posts: List[PostRecord]) -> List[PostWithScore]:
        # 互動分數計算邏輯
        # 按讚 × 1 + 留言 × 1.5 + 分享 × 2 + 收藏 × 2
        pass
    
    async def _analyze_common_features(self, top_posts: List[PostRecord]) -> CommonFeatures:
        # 分析高互動內容的共同特徵
        # - KOL 人格設定
        # - 內容風格
        # - 發布時間
        # - 股票類型
        # - 新聞關鍵字
        pass
```

## 🔒 安全與認證

### API 金鑰管理
```python
class APIKeyManager:
    def __init__(self):
        self.keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'serper': os.getenv('SERPER_API_KEY'),
            'cmoney': os.getenv('CMONEY_API_KEY'),
        }
    
    def get_key(self, service: str) -> Optional[str]:
        return self.keys.get(service)
    
    def validate_key(self, service: str, key: str) -> bool:
        # 驗證 API 金鑰有效性
        pass

class SecurityMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app
        self.api_key_manager = APIKeyManager()
    
    async def __call__(self, request: Request, call_next):
        # 安全檢查邏輯
        # - API 金鑰驗證
        # - 請求頻率限制
        # - CORS 檢查
        pass
```

## 📊 監控與日誌

### 日誌配置
```python
import logging
import sys

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

# 性能監控
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"✅ {func.__name__} 執行完成，耗時: {execution_time:.2f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {func.__name__} 執行失敗，耗時: {execution_time:.2f}秒，錯誤: {e}")
            raise
    return wrapper
```

## 🚀 部署配置

### Docker 配置
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 環境變數配置
```bash
# .env
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
POSTGRES_HOST=postgres-db
POSTGRES_PORT=5432
POSTGRES_DB=posting_management
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
DATABASE_URL=postgresql://postgres:password@postgres-db:5432/posting_management
```

### 健康檢查
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "trending_api": "connected",
            "summary_api": "connected",
            "ohlc_api": "connected"
        }
    }
```


