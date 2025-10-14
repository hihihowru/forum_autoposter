# 觸發器系統

## 🎯 觸發器系統概覽

觸發器系統是虛擬 KOL 系統的核心組件，負責監控市場數據並自動觸發內容生成。系統支援多種觸發器類型，每種類型都有對應的檢測邏輯和新聞搜尋策略。

## 🔧 觸發器類型

### 1. 個股觸發器 (Individual Triggers)

#### 盤後漲停觸發器
```typescript
interface LimitUpAfterHoursTrigger {
  key: 'limit_up_after_hours';
  label: '盤後漲';
  description: '收盤上漲股票分析';
  stockFilter: 'limit_up_stocks';
  newsKeywords: ['上漲', '漲停', '突破', '強勢'];
  apiEndpoint: '/api/stock/limit-up';
}
```

**檢測邏輯**
- 監控收盤漲停股票
- 篩選符合條件的股票
- 搜尋相關上漲新聞
- 觸發內容生成

#### 盤後跌停觸發器
```typescript
interface LimitDownAfterHoursTrigger {
  key: 'limit_down_after_hours';
  label: '盤後跌';
  description: '收盤下跌股票分析';
  stockFilter: 'limit_down_stocks';
  newsKeywords: ['下跌', '跌停', '弱勢', '回檔'];
  apiEndpoint: '/api/stock/limit-down';
}
```

**檢測邏輯**
- 監控收盤跌停股票
- 篩選符合條件的股票
- 搜尋相關下跌新聞
- 觸發內容生成

### 2. 成交量觸發器 (Volume Triggers)

#### 成交金額高觸發器
```typescript
interface VolumeAmountHighTrigger {
  key: 'volume_amount_high';
  label: '成交金額高';
  description: '成交金額絕對值排序（由大到小）';
  stockFilter: 'volume_amount_high_stocks';
  newsKeywords: ['成交量', '爆量', '大量', '活躍'];
  apiEndpoint: '/api/stock/volume-high';
}
```

**檢測邏輯**
- 獲取所有股票成交金額數據
- 按成交金額絕對值排序（由大到小）
- 選取前 N 名股票
- 搜尋相關成交量新聞

#### 成交金額低觸發器
```typescript
interface VolumeAmountLowTrigger {
  key: 'volume_amount_low';
  label: '成交金額低';
  description: '成交金額絕對值排序（由小到大）';
  stockFilter: 'volume_amount_low_stocks';
  newsKeywords: ['量縮', '清淡', '觀望'];
  apiEndpoint: '/api/stock/volume-low';
}
```

**檢測邏輯**
- 獲取所有股票成交金額數據
- 按成交金額絕對值排序（由小到大）
- 選取前 N 名股票
- 搜尋相關量縮新聞

#### 成交金額變化率高觸發器
```typescript
interface VolumeChangeRateHighTrigger {
  key: 'volume_change_rate_high';
  label: '成交金額變化率高';
  description: '成交金額變化率排序（由大到小）';
  stockFilter: 'volume_change_rate_high_stocks';
  newsKeywords: ['放量', '增量', '活躍'];
  apiEndpoint: '/api/stock/volume-change-high';
}
```

**計算公式**
```
變化率 = (今日成交金額 - 昨日成交金額) / 昨日成交金額 × 100%
```

**檢測邏輯**
- 獲取今日和昨日成交金額數據
- 計算變化率
- 按變化率排序（由大到小）
- 選取前 N 名股票
- 搜尋相關放量新聞

#### 成交金額變化率低觸發器
```typescript
interface VolumeChangeRateLowTrigger {
  key: 'volume_change_rate_low';
  label: '成交金額變化率低';
  description: '成交金額變化率排序（由小到大）';
  stockFilter: 'volume_change_rate_low_stocks';
  newsKeywords: ['縮量', '量縮', '觀望'];
  apiEndpoint: '/api/stock/volume-change-low';
}
```

**檢測邏輯**
- 獲取今日和昨日成交金額數據
- 計算變化率
- 按變化率排序（由小到大）
- 選取前 N 名股票
- 搜尋相關縮量新聞

### 3. 盤中觸發器 (Intraday Triggers)

#### 盤中觸發器六個系列

**漲幅排序+成交額觸發器**
```typescript
interface IntradayGainersByAmountTrigger {
  key: 'intraday_gainers_by_amount';
  label: '漲幅排序+成交額';
  description: '盤中漲幅排序，結合成交額篩選';
  stockFilter: 'intraday_gainers_by_amount';
  newsKeywords: ['盤中上漲', '漲幅', '成交額', '活躍'];
  apiEndpoint: '/api/intraday/gainers-by-amount';
}
```

**成交量排序觸發器**
```typescript
interface IntradayVolumeLeadersTrigger {
  key: 'intraday_volume_leaders';
  label: '成交量排序';
  description: '盤中成交量排序，找出最活躍股票';
  stockFilter: 'intraday_volume_leaders';
  newsKeywords: ['成交量', '活躍', '交易熱絡', '盤中'];
  apiEndpoint: '/api/intraday/volume-leaders';
}
```

**成交額排序觸發器**
```typescript
interface IntradayAmountLeadersTrigger {
  key: 'intraday_amount_leaders';
  label: '成交額排序';
  description: '盤中成交額排序，找出資金流向';
  stockFilter: 'intraday_amount_leaders';
  newsKeywords: ['成交額', '資金流向', '大額交易', '盤中'];
  apiEndpoint: '/api/intraday/amount-leaders';
}
```

**跌停篩選觸發器**
```typescript
interface IntradayLimitDownTrigger {
  key: 'intraday_limit_down';
  label: '跌停篩選';
  description: '盤中跌停股票篩選';
  stockFilter: 'intraday_limit_down';
  newsKeywords: ['跌停', '盤中下跌', '弱勢', '賣壓'];
  apiEndpoint: '/api/intraday/limit-down';
}
```

**漲停篩選觸發器**
```typescript
interface IntradayLimitUpTrigger {
  key: 'intraday_limit_up';
  label: '漲停篩選';
  description: '盤中漲停股票篩選';
  stockFilter: 'intraday_limit_up';
  newsKeywords: ['漲停', '盤中上漲', '強勢', '買盤'];
  apiEndpoint: '/api/intraday/limit-up';
}
```

**跌停篩選+成交額觸發器**
```typescript
interface IntradayLimitDownByAmountTrigger {
  key: 'intraday_limit_down_by_amount';
  label: '跌停篩選+成交額';
  description: '盤中跌停股票，結合成交額分析';
  stockFilter: 'intraday_limit_down_by_amount';
  newsKeywords: ['跌停', '成交額', '賣壓', '資金流出'];
  apiEndpoint: '/api/intraday/limit-down-by-amount';
}
```

**盤中觸發器特性**
- **實時監控**: 盤中即時監控股票表現
- **多維度篩選**: 結合漲跌幅、成交量、成交額多個維度
- **動態調整**: 根據市場狀況動態調整篩選條件
- **並行處理**: 支援多個盤中觸發器並行執行

### 4. 自定義觸發器 (Custom Triggers)

#### 自定義股票觸發器
```typescript
interface CustomStockTrigger {
  key: 'custom_stocks';
  label: '自定義股票';
  description: '手動輸入股票代號，包含股票搜尋功能';
  stockFilter: 'custom_stocks';
  newsKeywords: []; // 動態生成
  apiEndpoint: '/api/stock/custom';
}
```

**功能特性**
- 支援手動輸入股票代號
- 提供股票名稱搜尋功能
- 動態生成新聞關鍵字
- 支援批量股票輸入

## 🏗️ 觸發器架構

### 前端觸發器選擇器

#### TriggerSelector.tsx
```typescript
interface TriggerConfig {
  triggerType: 'individual' | 'sector' | 'macro' | 'news' | 'intraday' | 'volume' | 'custom';
  triggerKey: string;
  stockFilter: string;
  volumeFilter?: string;
  sectorFilter?: string;
  macroFilter?: string;
  newsFilter?: string;
  customFilters?: Record<string, any>;
  apiConfig?: {
    endpoint: string;
    processing: any[];
  };
  newsKeywords?: string[];
}

interface TriggerSelectorProps {
  value: TriggerSelection;
  onChange: (value: TriggerSelection) => void;
  onNewsConfigChange?: (newsKeywords: string[]) => void;
}

const TriggerSelector: React.FC<TriggerSelectorProps> = ({ value, onChange, onNewsConfigChange }) => {
  // 觸發器選擇邏輯
  // 智能新聞搜尋關鍵字更新
  // 自定義股票處理
};
```

#### 觸發器分類
```typescript
const triggerCategories = [
  {
    key: 'trending',
    label: '熱門話題',
    icon: <FireOutlined />,
    color: '#f5222d',
    triggers: [
      {
        key: 'trending_topics',
        label: 'CMoney熱門話題',
        icon: <FireOutlined />,
        description: '獲取CMoney平台熱門話題',
        apiEndpoint: '/trending'
      }
    ]
  },
  {
    key: 'individual',
    label: '個股觸發器',
    icon: <StockOutlined />,
    color: '#1890ff',
    triggers: [
      // 盤後漲停、盤後跌停、成交量觸發器等
    ]
  }
];
```

### 後端觸發器處理

#### 觸發器處理器
```python
class TriggerProcessor:
    def __init__(self):
        self.finlab_client = FinLabClient()
        self.serper_client = SerperClient()
        self.logger = logging.getLogger(__name__)
    
    async def process_trigger(self, trigger_config: TriggerConfig) -> TriggerResult:
        """處理觸發器請求"""
        try:
            if trigger_config.trigger_type == 'individual':
                return await self._process_individual_trigger(trigger_config)
            elif trigger_config.trigger_type == 'volume':
                return await self._process_volume_trigger(trigger_config)
            elif trigger_config.trigger_type == 'custom':
                return await self._process_custom_trigger(trigger_config)
            else:
                raise ValueError(f"不支援的觸發器類型: {trigger_config.trigger_type}")
        except Exception as e:
            self.logger.error(f"觸發器處理失敗: {e}")
            raise
    
    async def _process_individual_trigger(self, config: TriggerConfig) -> TriggerResult:
        """處理個股觸發器"""
        # 1. 獲取股票數據
        stocks = await self._get_stock_data(config.stockFilter)
        
        # 2. 搜尋相關新聞
        news_data = await self._search_news(config.newsKeywords, stocks)
        
        # 3. 生成觸發結果
        return TriggerResult(
            trigger_type=config.trigger_type,
            stocks=stocks,
            news_data=news_data,
            timestamp=datetime.now()
        )
    
    async def _process_volume_trigger(self, config: TriggerConfig) -> TriggerResult:
        """處理成交量觸發器"""
        # 1. 獲取成交量數據
        volume_data = await self._get_volume_data(config.volumeFilter)
        
        # 2. 計算變化率（如果需要）
        if 'change_rate' in config.triggerKey:
            volume_data = await self._calculate_change_rate(volume_data)
        
        # 3. 排序和篩選
        sorted_stocks = await self._sort_and_filter(volume_data, config.triggerKey)
        
        # 4. 搜尋相關新聞
        news_data = await self._search_news(config.newsKeywords, sorted_stocks)
        
        return TriggerResult(
            trigger_type=config.trigger_type,
            stocks=sorted_stocks,
            news_data=news_data,
            timestamp=datetime.now()
        )
    
    async def _process_custom_trigger(self, config: TriggerConfig) -> TriggerResult:
        """處理自定義觸發器"""
        # 1. 獲取自定義股票列表
        custom_stocks = config.customFilters.get('stocks', [])
        
        # 2. 驗證股票代號
        validated_stocks = await self._validate_stock_codes(custom_stocks)
        
        # 3. 動態生成新聞關鍵字
        news_keywords = await self._generate_news_keywords(validated_stocks)
        
        # 4. 搜尋相關新聞
        news_data = await self._search_news(news_keywords, validated_stocks)
        
        return TriggerResult(
            trigger_type=config.trigger_type,
            stocks=validated_stocks,
            news_data=news_data,
            timestamp=datetime.now()
        )
```

#### 成交量變化率計算
```python
async def _calculate_change_rate(self, volume_data: List[StockVolumeData]) -> List[StockVolumeDataWithChange]:
    """計算成交量變化率"""
    results = []
    
    for stock in volume_data:
        try:
            # 獲取今日和昨日成交金額
            today_amount = stock.today_volume_amount
            yesterday_amount = stock.yesterday_volume_amount
            
            # 計算變化率
            if yesterday_amount > 0:
                change_rate = (today_amount - yesterday_amount) / yesterday_amount * 100
            else:
                change_rate = 0
            
            results.append(StockVolumeDataWithChange(
                stock_code=stock.stock_code,
                stock_name=stock.stock_name,
                today_volume_amount=today_amount,
                yesterday_volume_amount=yesterday_amount,
                change_rate=change_rate
            ))
        except Exception as e:
            self.logger.warning(f"計算股票 {stock.stock_code} 變化率失敗: {e}")
            continue
    
    return results
```

## 🔍 智能新聞搜尋

### 新聞關鍵字策略

#### 觸發器對應關鍵字
```python
TRIGGER_NEWS_KEYWORDS = {
    'limit_up_after_hours': ['上漲', '漲停', '突破', '強勢', '多頭', '買盤'],
    'limit_down_after_hours': ['下跌', '跌停', '弱勢', '回檔', '空頭', '賣盤'],
    'volume_amount_high': ['成交量', '爆量', '大量', '活躍', '熱絡', '交易'],
    'volume_amount_low': ['量縮', '清淡', '觀望', '冷清', '交易量低'],
    'volume_change_rate_high': ['放量', '增量', '活躍', '交易熱絡', '成交量增'],
    'volume_change_rate_low': ['縮量', '量縮', '觀望', '交易清淡', '成交量減']
}
```

#### 動態關鍵字生成
```python
async def _generate_news_keywords(self, stocks: List[StockInfo]) -> List[str]:
    """為自定義股票動態生成新聞關鍵字"""
    keywords = []
    
    for stock in stocks:
        # 根據股票特性生成關鍵字
        stock_keywords = [
            stock.stock_name,
            stock.stock_code,
            '股價',
            '分析',
            '投資'
        ]
        
        # 根據股票行業添加行業關鍵字
        if stock.industry:
            industry_keywords = self._get_industry_keywords(stock.industry)
            stock_keywords.extend(industry_keywords)
        
        keywords.extend(stock_keywords)
    
    # 去重並返回
    return list(set(keywords))

def _get_industry_keywords(self, industry: str) -> List[str]:
    """根據行業獲取相關關鍵字"""
    industry_keywords_map = {
        '電子': ['科技', '半導體', '電子', 'IC', '晶片'],
        '金融': ['銀行', '保險', '證券', '金融', '金控'],
        '傳產': ['傳統產業', '製造業', '工業', '機械'],
        '生技': ['生物科技', '醫療', '製藥', '健康'],
        '能源': ['能源', '石油', '天然氣', '電力']
    }
    
    return industry_keywords_map.get(industry, [])
```

### 新聞搜尋 API

#### Serper 新聞搜尋
```python
class SerperNewsSearcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/news"
    
    async def search_news(self, keywords: List[str], stock_codes: List[str] = None) -> List[NewsItem]:
        """搜尋相關新聞"""
        # 構建搜尋查詢
        query = self._build_search_query(keywords, stock_codes)
        
        # 發送搜尋請求
        response = await self._send_search_request(query)
        
        # 解析搜尋結果
        news_items = self._parse_search_results(response)
        
        return news_items
    
    def _build_search_query(self, keywords: List[str], stock_codes: List[str] = None) -> str:
        """構建搜尋查詢"""
        query_parts = []
        
        # 添加關鍵字
        query_parts.extend(keywords)
        
        # 添加股票代號
        if stock_codes:
            query_parts.extend(stock_codes)
        
        # 添加時間限制
        query_parts.append('最近7天')
        
        return ' '.join(query_parts)
    
    async def _send_search_request(self, query: str) -> Dict[str, Any]:
        """發送搜尋請求"""
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': 10,
            'tbs': 'qdr:w'  # 最近一週
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    
    def _parse_search_results(self, response: Dict[str, Any]) -> List[NewsItem]:
        """解析搜尋結果"""
        news_items = []
        
        for item in response.get('news', []):
            news_item = NewsItem(
                title=item.get('title', ''),
                snippet=item.get('snippet', ''),
                link=item.get('link', ''),
                date=item.get('date', ''),
                source=item.get('source', '')
            )
            news_items.append(news_item)
        
        return news_items
```

## 🚀 並行觸發器處理

### 並行處理架構

#### IntradayTriggerProcessor
```python
class IntradayTriggerProcessor(ParallelProcessor):
    """盤中觸發器並行處理器"""
    
    def __init__(self, max_concurrent: int = 3, timeout: int = 30):
        super().__init__(max_concurrent, timeout)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def execute_multiple_triggers_parallel(self, trigger_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """並行執行多個觸發器"""
        self.logger.info(f"🚀 收到並行執行 {len(trigger_configs)} 個觸發器的請求")
        
        # 創建任務列表
        tasks = [
            (self._process_task_with_retry, self._execute_single_trigger_with_circuit_breaker, config)
            for config in trigger_configs
        ]
        
        # 並行執行任務
        results = await self.process_batch_async(tasks)
        
        # 統計結果
        success_count = sum(1 for r in results if r.get("success"))
        failed_count = len(results) - success_count
        
        self.logger.info(f"🎉 並行觸發器執行完成: 成功 {success_count} 個，失敗 {failed_count} 個")
        
        return {
            "success": True,
            "total_triggers": len(trigger_configs),
            "successful_triggers": success_count,
            "failed_triggers": failed_count,
            "results": results
        }
    
    async def _execute_single_trigger_with_circuit_breaker(self, trigger_config: Dict[str, Any]) -> Dict[str, Any]:
        """執行單個觸發器，帶熔斷器保護"""
        if not circuit_breaker.allow_request():
            self.logger.warning("熔斷器處於 OPEN 狀態，拒絕觸發器請求")
            return {"success": False, "error": "熔斷器已開啟，服務暫不可用", "trigger_config": trigger_config}
        
        try:
            result = await single_execute_intraday_trigger(trigger_config)
            circuit_breaker.record_success()
            return {"success": True, "result": result, "trigger_config": trigger_config}
        except Exception as e:
            circuit_breaker.record_failure()
            self.logger.error(f"執行觸發器失敗 (熔斷器): {e}")
            raise
```

#### 熔斷器模式
```python
class SimpleCircuitBreaker:
    """簡單的熔斷器實現"""
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def record_success(self):
        """記錄成功"""
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None
        self.logger.info("熔斷器狀態: CLOSED (成功)")
    
    def record_failure(self):
        """記錄失敗"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.logger.warning(f"熔斷器狀態: OPEN (失敗次數達到閾值 {self.failure_threshold})")
        else:
            self.logger.warning(f"熔斷器狀態: CLOSED (失敗次數: {self.failure_count})")
    
    def allow_request(self) -> bool:
        """檢查是否允許請求"""
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            if (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "HALF_OPEN"
                self.logger.info("熔斷器狀態: HALF_OPEN (嘗試恢復)")
                return True
            return False
        
        if self.state == "HALF_OPEN":
            return True
        
        return False
```

## 📊 觸發器監控

### 觸發器統計

#### 觸發器執行統計
```python
class TriggerStatistics:
    def __init__(self):
        self.stats = {
            'total_triggers': 0,
            'successful_triggers': 0,
            'failed_triggers': 0,
            'trigger_types': {},
            'execution_times': [],
            'error_types': {}
        }
    
    def record_trigger_execution(self, trigger_type: str, success: bool, execution_time: float, error: str = None):
        """記錄觸發器執行"""
        self.stats['total_triggers'] += 1
        
        if success:
            self.stats['successful_triggers'] += 1
        else:
            self.stats['failed_triggers'] += 1
            if error:
                self.stats['error_types'][error] = self.stats['error_types'].get(error, 0) + 1
        
        # 記錄觸發器類型統計
        self.stats['trigger_types'][trigger_type] = self.stats['trigger_types'].get(trigger_type, 0) + 1
        
        # 記錄執行時間
        self.stats['execution_times'].append(execution_time)
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計數據"""
        execution_times = self.stats['execution_times']
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            'total_triggers': self.stats['total_triggers'],
            'successful_triggers': self.stats['successful_triggers'],
            'failed_triggers': self.stats['failed_triggers'],
            'success_rate': self.stats['successful_triggers'] / self.stats['total_triggers'] * 100 if self.stats['total_triggers'] > 0 else 0,
            'trigger_types': self.stats['trigger_types'],
            'average_execution_time': avg_execution_time,
            'error_types': self.stats['error_types']
        }
```

### 觸發器日誌

#### 日誌記錄
```python
class TriggerLogger:
    def __init__(self):
        self.logger = logging.getLogger('trigger_system')
        self.logger.setLevel(logging.INFO)
        
        # 創建文件處理器
        file_handler = logging.FileHandler('trigger_system.log')
        file_handler.setLevel(logging.INFO)
        
        # 創建格式器
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加處理器
        self.logger.addHandler(file_handler)
    
    def log_trigger_start(self, trigger_config: TriggerConfig):
        """記錄觸發器開始"""
        self.logger.info(f"🎯 觸發器開始執行: {trigger_config.triggerKey}")
    
    def log_trigger_success(self, trigger_config: TriggerConfig, result: TriggerResult):
        """記錄觸發器成功"""
        self.logger.info(f"✅ 觸發器執行成功: {trigger_config.triggerKey}, 股票數量: {len(result.stocks)}")
    
    def log_trigger_failure(self, trigger_config: TriggerConfig, error: Exception):
        """記錄觸發器失敗"""
        self.logger.error(f"❌ 觸發器執行失敗: {trigger_config.triggerKey}, 錯誤: {error}")
    
    def log_trigger_performance(self, trigger_config: TriggerConfig, execution_time: float):
        """記錄觸發器性能"""
        self.logger.info(f"⏱️ 觸發器執行時間: {trigger_config.triggerKey}, 耗時: {execution_time:.2f}秒")
```

## 🔧 觸發器配置

### 觸發器配置管理

#### 配置結構
```python
@dataclass
class TriggerConfig:
    trigger_type: str
    trigger_key: str
    stock_filter: str
    volume_filter: Optional[str] = None
    sector_filter: Optional[str] = None
    macro_filter: Optional[str] = None
    news_filter: Optional[str] = None
    custom_filters: Optional[Dict[str, Any]] = None
    news_keywords: Optional[List[str]] = None
    api_config: Optional[Dict[str, Any]] = None
    enabled: bool = True
    priority: int = 1
    max_stocks: int = 20
    timeout: int = 30
```

#### 配置驗證
```python
class TriggerConfigValidator:
    def __init__(self):
        self.valid_trigger_types = ['individual', 'sector', 'macro', 'news', 'intraday', 'volume', 'custom']
        self.valid_stock_filters = ['limit_up_stocks', 'limit_down_stocks', 'volume_amount_high_stocks', 
                                   'volume_amount_low_stocks', 'volume_change_rate_high_stocks', 
                                   'volume_change_rate_low_stocks', 'custom_stocks']
    
    def validate_config(self, config: TriggerConfig) -> List[str]:
        """驗證觸發器配置"""
        errors = []
        
        # 驗證觸發器類型
        if config.trigger_type not in self.valid_trigger_types:
            errors.append(f"無效的觸發器類型: {config.trigger_type}")
        
        # 驗證股票篩選器
        if config.stock_filter not in self.valid_stock_filters:
            errors.append(f"無效的股票篩選器: {config.stock_filter}")
        
        # 驗證自定義觸發器
        if config.trigger_type == 'custom':
            if not config.custom_filters or 'stocks' not in config.custom_filters:
                errors.append("自定義觸發器必須指定股票列表")
        
        # 驗證新聞關鍵字
        if config.news_keywords and not isinstance(config.news_keywords, list):
            errors.append("新聞關鍵字必須是列表格式")
        
        return errors
    
    def validate_and_fix_config(self, config: TriggerConfig) -> TriggerConfig:
        """驗證並修復配置"""
        errors = self.validate_config(config)
        
        if errors:
            raise ValueError(f"觸發器配置錯誤: {', '.join(errors)}")
        
        # 設置默認值
        if config.max_stocks <= 0:
            config.max_stocks = 20
        
        if config.timeout <= 0:
            config.timeout = 30
        
        if config.priority <= 0:
            config.priority = 1
        
        return config
```

## 🚀 觸發器優化

### 性能優化

#### 緩存策略
```python
class TriggerCache:
    def __init__(self, ttl: int = 300):  # 5分鐘緩存
        self.cache = {}
        self.ttl = ttl
        self.logger = logging.getLogger(__name__)
    
    def get_cache_key(self, trigger_config: TriggerConfig) -> str:
        """生成緩存鍵"""
        return f"{trigger_config.trigger_type}:{trigger_config.trigger_key}:{hash(str(trigger_config.custom_filters))}"
    
    def get(self, trigger_config: TriggerConfig) -> Optional[TriggerResult]:
        """獲取緩存結果"""
        cache_key = self.get_cache_key(trigger_config)
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            
            # 檢查是否過期
            if time.time() - timestamp < self.ttl:
                self.logger.info(f"🎯 使用緩存結果: {cache_key}")
                return cached_data
            else:
                # 移除過期緩存
                del self.cache[cache_key]
        
        return None
    
    def set(self, trigger_config: TriggerConfig, result: TriggerResult):
        """設置緩存結果"""
        cache_key = self.get_cache_key(trigger_config)
        self.cache[cache_key] = (result, time.time())
        self.logger.info(f"💾 緩存觸發器結果: {cache_key}")
    
    def clear(self):
        """清空緩存"""
        self.cache.clear()
        self.logger.info("🗑️ 清空觸發器緩存")
```

#### 並行優化
```python
class OptimizedTriggerProcessor:
    def __init__(self):
        self.trigger_processor = TriggerProcessor()
        self.cache = TriggerCache()
        self.semaphore = asyncio.Semaphore(5)  # 限制並發數
    
    async def process_triggers_optimized(self, trigger_configs: List[TriggerConfig]) -> List[TriggerResult]:
        """優化後的觸發器處理"""
        results = []
        
        # 並行處理觸發器
        tasks = []
        for config in trigger_configs:
            task = asyncio.create_task(self._process_single_trigger_optimized(config))
            tasks.append(task)
        
        # 等待所有任務完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 處理異常結果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"觸發器處理異常: {trigger_configs[i].trigger_key}, 錯誤: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_single_trigger_optimized(self, config: TriggerConfig) -> TriggerResult:
        """優化後的單個觸發器處理"""
        async with self.semaphore:
            # 檢查緩存
            cached_result = self.cache.get(config)
            if cached_result:
                return cached_result
            
            # 執行觸發器
            result = await self.trigger_processor.process_trigger(config)
            
            # 緩存結果
            self.cache.set(config, result)
            
            return result
```

## 📈 觸發器監控面板

### 監控指標

#### 實時監控
```typescript
interface TriggerMonitoringData {
  // 執行統計
  totalExecutions: number;
  successfulExecutions: number;
  failedExecutions: number;
  successRate: number;
  
  // 性能指標
  averageExecutionTime: number;
  maxExecutionTime: number;
  minExecutionTime: number;
  
  // 觸發器類型統計
  triggerTypeStats: {
    [key: string]: {
      count: number;
      successRate: number;
      averageTime: number;
    };
  };
  
  // 錯誤統計
  errorStats: {
    [key: string]: number;
  };
  
  // 實時狀態
  activeTriggers: number;
  queuedTriggers: number;
  processingTriggers: number;
}
```

#### 監控組件
```typescript
const TriggerMonitoringDashboard: React.FC = () => {
  const [monitoringData, setMonitoringData] = useState<TriggerMonitoringData | null>(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    const fetchMonitoringData = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/triggers/monitoring');
        const data = await response.json();
        setMonitoringData(data);
      } catch (error) {
        console.error('獲取監控數據失敗:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchMonitoringData();
    
    // 每30秒更新一次
    const interval = setInterval(fetchMonitoringData, 30000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="trigger-monitoring-dashboard">
      <Row gutter={16}>
        <Col span={6}>
          <StatisticCard
            title="總執行次數"
            value={monitoringData?.totalExecutions || 0}
            icon={<PlayCircleOutlined />}
          />
        </Col>
        <Col span={6}>
          <StatisticCard
            title="成功率"
            value={`${monitoringData?.successRate || 0}%`}
            icon={<CheckCircleOutlined />}
          />
        </Col>
        <Col span={6}>
          <StatisticCard
            title="平均執行時間"
            value={`${monitoringData?.averageExecutionTime || 0}ms`}
            icon={<ClockCircleOutlined />}
          />
        </Col>
        <Col span={6}>
          <StatisticCard
            title="活躍觸發器"
            value={monitoringData?.activeTriggers || 0}
            icon={<ThunderboltOutlined />}
          />
        </Col>
      </Row>
      
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <TriggerTypeChart data={monitoringData?.triggerTypeStats} />
        </Col>
        <Col span={12}>
          <ErrorDistributionChart data={monitoringData?.errorStats} />
        </Col>
      </Row>
    </div>
  );
};
```
