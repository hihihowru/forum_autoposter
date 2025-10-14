# 部署監控系統技術文件

## 📋 系統概述

部署監控系統是 n8n-migration-project 的運維核心，負責監控整個系統的運行狀態、服務健康度、資源使用情況，以及任務執行狀態。系統提供實時監控、告警機制、性能分析和故障診斷功能，確保系統穩定運行。

## 🎯 核心功能

### 1. **系統狀態監控**
- 整體系統健康度監控
- KOL 和貼文統計數據
- 系統資源使用情況
- 數據庫連接狀態

### 2. **微服務監控**
- 各微服務健康狀態檢查
- 服務響應時間監控
- 服務可用性統計
- 服務間依賴關係監控

### 3. **任務執行監控**
- 定時任務執行狀態
- 任務成功率統計
- 任務執行時間分析
- 失敗任務重試機制

### 4. **數據源監控**
- 外部 API 連接狀態
- 數據同步狀態
- 數據品質監控
- 數據源可用性檢查

## 🏗️ 系統架構

### 前端監控組件

```typescript
// SystemMonitoring.tsx - 系統監控組件
interface SystemMonitoringProps {
  data: SystemMonitoringData | null;
  loading: boolean;
  error: string | null;
}

interface SystemMonitoringData {
  timestamp: string;
  system_overview: {
    total_kols: number;
    active_kols: number;
    total_posts: number;
    published_posts: number;
    success_rate: number;
  };
  microservices: {
    [key: string]: {
      status: string;
      uptime: string;
      response_time: string;
    };
  };
  task_execution: {
    hourly_tasks: { success: number; failed: number; total: number };
    daily_tasks: { success: number; failed: number; total: number };
    weekly_tasks: { success: number; failed: number; total: number };
  };
  data_sources: {
    google_sheets: string;
    cmoney_api: string;
    finlab_api: string;
  };
}
```

### 後端監控 API

```python
# 系統監控 API
@app.get("/api/dashboard/system-monitoring")
async def get_system_monitoring_data():
    """獲取系統監控儀表板數據"""
    
# 健康檢查 API
@app.get("/health")
async def health_check():
    """服務健康檢查"""
    
# 微服務狀態 API
@app.get("/api/microservices/status")
async def get_microservices_status():
    """獲取微服務狀態"""
    
# 任務執行統計 API
@app.get("/api/tasks/execution-stats")
async def get_task_execution_stats():
    """獲取任務執行統計"""
```

## 📊 監控數據模型

### 系統概覽數據

```python
@dataclass
class SystemOverview:
    """系統概覽數據"""
    total_kols: int
    active_kols: int
    total_posts: int
    published_posts: int
    success_rate: float
    system_uptime: float
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    timestamp: datetime
```

### 微服務狀態數據

```python
@dataclass
class MicroserviceStatus:
    """微服務狀態數據"""
    service_name: str
    status: str  # healthy, warning, error, unknown
    uptime: float
    response_time: float
    memory_usage: float
    cpu_usage: float
    request_count: int
    error_count: int
    last_check: datetime
    dependencies: List[str]
    health_endpoint: str
```

### 任務執行數據

```python
@dataclass
class TaskExecutionStats:
    """任務執行統計數據"""
    task_type: str  # hourly, daily, weekly
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    success_rate: float
    avg_execution_time: float
    last_execution: datetime
    next_execution: datetime
    error_details: List[str]
```

### 數據源狀態數據

```python
@dataclass
class DataSourceStatus:
    """數據源狀態數據"""
    source_name: str
    status: str  # connected, disconnected, error
    last_sync: datetime
    sync_frequency: str
    data_quality: float
    error_count: int
    response_time: float
    api_quota_used: float
    api_quota_limit: float
```

## 🔄 監控流程

### 1. **系統狀態收集**

```python
async def collect_system_status() -> SystemOverview:
    """收集系統狀態"""
    
    # 獲取 KOL 數據
    kol_service = get_kol_service()
    total_kols = kol_service.get_total_count()
    active_kols = kol_service.get_active_count()
    
    # 獲取貼文數據
    post_service = get_post_record_service()
    total_posts = post_service.get_total_count()
    published_posts = post_service.get_published_count()
    
    # 計算成功率
    success_rate = (published_posts / total_posts * 100) if total_posts > 0 else 0
    
    # 獲取系統資源使用情況
    system_metrics = get_system_metrics()
    
    return SystemOverview(
        total_kols=total_kols,
        active_kols=active_kols,
        total_posts=total_posts,
        published_posts=published_posts,
        success_rate=success_rate,
        system_uptime=system_metrics['uptime'],
        memory_usage=system_metrics['memory_usage'],
        cpu_usage=system_metrics['cpu_usage'],
        disk_usage=system_metrics['disk_usage'],
        network_io=system_metrics['network_io'],
        timestamp=datetime.now()
    )
```

### 2. **微服務健康檢查**

```python
async def check_microservices_health() -> Dict[str, MicroserviceStatus]:
    """檢查微服務健康狀態"""
    
    microservices = {
        'ohlc_api': 'http://ohlc-api:8002/health',
        'analyze_api': 'http://analyze-api:8003/health',
        'summary_api': 'http://summary-api:8004/health',
        'trending_api': 'http://trending-api:8005/health',
        'posting_service': 'http://posting-service:8001/health',
        'trainer': 'http://trainer:8006/health'
    }
    
    status_results = {}
    
    for service_name, health_url in microservices.items():
        try:
            # 發送健康檢查請求
            response = await http_client.get(health_url, timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                status_results[service_name] = MicroserviceStatus(
                    service_name=service_name,
                    status='healthy',
                    uptime=health_data.get('uptime', 0),
                    response_time=health_data.get('response_time', 0),
                    memory_usage=health_data.get('memory_usage', 0),
                    cpu_usage=health_data.get('cpu_usage', 0),
                    request_count=health_data.get('request_count', 0),
                    error_count=health_data.get('error_count', 0),
                    last_check=datetime.now(),
                    dependencies=health_data.get('dependencies', []),
                    health_endpoint=health_url
                )
            else:
                status_results[service_name] = MicroserviceStatus(
                    service_name=service_name,
                    status='error',
                    uptime=0,
                    response_time=0,
                    memory_usage=0,
                    cpu_usage=0,
                    request_count=0,
                    error_count=1,
                    last_check=datetime.now(),
                    dependencies=[],
                    health_endpoint=health_url
                )
                
        except Exception as e:
            logger.error(f"微服務 {service_name} 健康檢查失敗: {e}")
            status_results[service_name] = MicroserviceStatus(
                service_name=service_name,
                status='error',
                uptime=0,
                response_time=0,
                memory_usage=0,
                cpu_usage=0,
                request_count=0,
                error_count=1,
                last_check=datetime.now(),
                dependencies=[],
                health_endpoint=health_url
            )
    
    return status_results
```

### 3. **任務執行監控**

```python
async def monitor_task_execution() -> Dict[str, TaskExecutionStats]:
    """監控任務執行狀態"""
    
    task_types = ['hourly', 'daily', 'weekly']
    execution_stats = {}
    
    for task_type in task_types:
        # 獲取任務執行記錄
        task_records = get_task_execution_records(task_type)
        
        total_tasks = len(task_records)
        successful_tasks = len([t for t in task_records if t.status == 'success'])
        failed_tasks = total_tasks - successful_tasks
        success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 計算平均執行時間
        execution_times = [t.execution_time for t in task_records if t.execution_time]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # 獲取錯誤詳情
        error_details = [t.error_message for t in task_records if t.status == 'failed']
        
        execution_stats[task_type] = TaskExecutionStats(
            task_type=task_type,
            total_tasks=total_tasks,
            successful_tasks=successful_tasks,
            failed_tasks=failed_tasks,
            success_rate=success_rate,
            avg_execution_time=avg_execution_time,
            last_execution=get_last_execution_time(task_type),
            next_execution=get_next_execution_time(task_type),
            error_details=error_details
        )
    
    return execution_stats
```

### 4. **數據源監控**

```python
async def monitor_data_sources() -> Dict[str, DataSourceStatus]:
    """監控數據源狀態"""
    
    data_sources = {
        'google_sheets': GoogleSheetsClient(),
        'cmoney_api': CMoneyClient(),
        'finlab_api': FinLabClient()
    }
    
    source_status = {}
    
    for source_name, client in data_sources.items():
        try:
            # 測試連接
            start_time = time.time()
            test_result = await client.test_connection()
            response_time = (time.time() - start_time) * 1000  # 轉換為毫秒
            
            if test_result['success']:
                source_status[source_name] = DataSourceStatus(
                    source_name=source_name,
                    status='connected',
                    last_sync=test_result.get('last_sync'),
                    sync_frequency=test_result.get('sync_frequency', 'unknown'),
                    data_quality=test_result.get('data_quality', 0),
                    error_count=0,
                    response_time=response_time,
                    api_quota_used=test_result.get('quota_used', 0),
                    api_quota_limit=test_result.get('quota_limit', 0)
                )
            else:
                source_status[source_name] = DataSourceStatus(
                    source_name=source_name,
                    status='error',
                    last_sync=None,
                    sync_frequency='unknown',
                    data_quality=0,
                    error_count=1,
                    response_time=response_time,
                    api_quota_used=0,
                    api_quota_limit=0
                )
                
        except Exception as e:
            logger.error(f"數據源 {source_name} 監控失敗: {e}")
            source_status[source_name] = DataSourceStatus(
                source_name=source_name,
                status='error',
                last_sync=None,
                sync_frequency='unknown',
                data_quality=0,
                error_count=1,
                response_time=0,
                api_quota_used=0,
                api_quota_limit=0
            )
    
    return source_status
```

## 🚨 告警機制

### 1. **告警規則定義**

```python
class AlertRule:
    """告警規則"""
    
    def __init__(self, name: str, condition: Callable, severity: str, message: str):
        self.name = name
        self.condition = condition
        self.severity = severity  # critical, warning, info
        self.message = message
        self.enabled = True
        self.last_triggered = None

# 定義告警規則
ALERT_RULES = [
    AlertRule(
        name="微服務離線",
        condition=lambda data: any(s.status == 'error' for s in data['microservices'].values()),
        severity="critical",
        message="檢測到微服務離線"
    ),
    AlertRule(
        name="任務執行失敗率過高",
        condition=lambda data: any(s.success_rate < 90 for s in data['task_execution'].values()),
        severity="warning",
        message="任務執行失敗率超過10%"
    ),
    AlertRule(
        name="數據源連接失敗",
        condition=lambda data: any(s.status == 'error' for s in data['data_sources'].values()),
        severity="warning",
        message="數據源連接失敗"
    ),
    AlertRule(
        name="系統資源使用率過高",
        condition=lambda data: data['system_overview'].cpu_usage > 80 or data['system_overview'].memory_usage > 80,
        severity="warning",
        message="系統資源使用率超過80%"
    )
]
```

### 2. **告警處理**

```python
class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self.alert_history = []
        self.notification_channels = []
    
    async def check_alerts(self, monitoring_data: Dict[str, Any]):
        """檢查告警條件"""
        
        triggered_alerts = []
        
        for rule in ALERT_RULES:
            if not rule.enabled:
                continue
                
            try:
                if rule.condition(monitoring_data):
                    alert = Alert(
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=rule.message,
                        timestamp=datetime.now(),
                        data=monitoring_data
                    )
                    
                    triggered_alerts.append(alert)
                    rule.last_triggered = datetime.now()
                    
                    # 發送通知
                    await self.send_notification(alert)
                    
            except Exception as e:
                logger.error(f"告警規則 {rule.name} 檢查失敗: {e}")
        
        return triggered_alerts
    
    async def send_notification(self, alert: Alert):
        """發送告警通知"""
        
        for channel in self.notification_channels:
            try:
                await channel.send(alert)
            except Exception as e:
                logger.error(f"發送告警通知失敗: {e}")
```

## 📈 性能監控

### 1. **性能指標收集**

```python
class PerformanceMonitor:
    """性能監控器"""
    
    def __init__(self):
        self.metrics_history = []
        self.performance_thresholds = {
            'response_time': 1000,  # 1秒
            'memory_usage': 80,     # 80%
            'cpu_usage': 80,        # 80%
            'error_rate': 5         # 5%
        }
    
    async def collect_performance_metrics(self) -> Dict[str, Any]:
        """收集性能指標"""
        
        metrics = {
            'timestamp': datetime.now(),
            'system_metrics': self.get_system_metrics(),
            'application_metrics': self.get_application_metrics(),
            'database_metrics': self.get_database_metrics(),
            'network_metrics': self.get_network_metrics()
        }
        
        # 檢查性能閾值
        alerts = self.check_performance_thresholds(metrics)
        
        # 記錄指標歷史
        self.metrics_history.append(metrics)
        
        # 保持歷史記錄在合理範圍內
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-500:]
        
        return metrics
    
    def get_system_metrics(self) -> Dict[str, float]:
        """獲取系統指標"""
        import psutil
        
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
        }
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """獲取應用程序指標"""
        return {
            'active_connections': get_active_connections_count(),
            'request_count': get_request_count(),
            'error_count': get_error_count(),
            'response_time_avg': get_average_response_time()
        }
```

### 2. **性能分析**

```python
def analyze_performance_trends(metrics_history: List[Dict]) -> Dict[str, Any]:
    """分析性能趨勢"""
    
    if len(metrics_history) < 2:
        return {'trend': 'insufficient_data'}
    
    # 提取關鍵指標
    cpu_usage = [m['system_metrics']['cpu_usage'] for m in metrics_history]
    memory_usage = [m['system_metrics']['memory_usage'] for m in metrics_history]
    response_time = [m['application_metrics']['response_time_avg'] for m in metrics_history]
    
    # 計算趨勢
    trends = {
        'cpu_trend': calculate_trend(cpu_usage),
        'memory_trend': calculate_trend(memory_usage),
        'response_time_trend': calculate_trend(response_time)
    }
    
    # 識別異常
    anomalies = detect_anomalies(metrics_history)
    
    # 生成建議
    recommendations = generate_performance_recommendations(trends, anomalies)
    
    return {
        'trends': trends,
        'anomalies': anomalies,
        'recommendations': recommendations,
        'summary': generate_performance_summary(trends)
    }
```

## 🔧 故障診斷

### 1. **自動診斷**

```python
class FaultDiagnostic:
    """故障診斷器"""
    
    def __init__(self):
        self.diagnostic_rules = [
            self.diagnose_service_failure,
            self.diagnose_database_issues,
            self.diagnose_network_problems,
            self.diagnose_resource_exhaustion
        ]
    
    async def diagnose_issues(self, monitoring_data: Dict[str, Any]) -> List[DiagnosticResult]:
        """診斷問題"""
        
        diagnostic_results = []
        
        for rule in self.diagnostic_rules:
            try:
                result = await rule(monitoring_data)
                if result:
                    diagnostic_results.append(result)
            except Exception as e:
                logger.error(f"診斷規則 {rule.__name__} 執行失敗: {e}")
        
        return diagnostic_results
    
    async def diagnose_service_failure(self, data: Dict[str, Any]) -> Optional[DiagnosticResult]:
        """診斷服務故障"""
        
        failed_services = [
            name for name, status in data['microservices'].items() 
            if status.status == 'error'
        ]
        
        if failed_services:
            return DiagnosticResult(
                issue_type='service_failure',
                severity='critical',
                description=f"服務故障: {', '.join(failed_services)}",
                possible_causes=[
                    '服務進程崩潰',
                    '網絡連接問題',
                    '資源不足',
                    '配置錯誤'
                ],
                suggested_actions=[
                    '檢查服務日誌',
                    '重啟服務',
                    '檢查資源使用情況',
                    '驗證配置'
                ]
            )
        
        return None
```

### 2. **故障恢復**

```python
class FaultRecovery:
    """故障恢復器"""
    
    def __init__(self):
        self.recovery_strategies = {
            'service_failure': self.restart_service,
            'database_connection': self.reconnect_database,
            'memory_exhaustion': self.clear_memory_cache,
            'disk_full': self.cleanup_disk_space
        }
    
    async def attempt_recovery(self, diagnostic_result: DiagnosticResult) -> bool:
        """嘗試故障恢復"""
        
        strategy = self.recovery_strategies.get(diagnostic_result.issue_type)
        
        if not strategy:
            logger.warning(f"沒有找到 {diagnostic_result.issue_type} 的恢復策略")
            return False
        
        try:
            success = await strategy(diagnostic_result)
            if success:
                logger.info(f"成功恢復 {diagnostic_result.issue_type} 故障")
            else:
                logger.warning(f"恢復 {diagnostic_result.issue_type} 故障失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"恢復 {diagnostic_result.issue_type} 故障時發生錯誤: {e}")
            return False
    
    async def restart_service(self, diagnostic_result: DiagnosticResult) -> bool:
        """重啟服務"""
        # 實現服務重啟邏輯
        pass
    
    async def reconnect_database(self, diagnostic_result: DiagnosticResult) -> bool:
        """重新連接數據庫"""
        # 實現數據庫重連邏輯
        pass
```

## 🚀 部署配置

### 1. **Docker Compose 配置**

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 監控服務
  monitoring-service:
    build: ./monitoring-service
    ports:
      - "8007:8000"
    environment:
      - MONITORING_ENABLED=true
      - ALERT_ENABLED=true
      - PERFORMANCE_MONITORING=true
    volumes:
      - ./monitoring-data:/app/data
    depends_on:
      - postgres
      - posting-service
      - ohlc-api
      - analyze-api
      - summary-api
      - trending-api
      - trainer
  
  # 系統監控儀表板
  system-monitoring:
    build: ./system-monitoring
    ports:
      - "8008:8000"
    environment:
      - MONITORING_API_URL=http://monitoring-service:8000
    depends_on:
      - monitoring-service
  
  # 日誌聚合服務
  log-aggregator:
    build: ./log-aggregator
    ports:
      - "8009:8000"
    volumes:
      - /var/log:/var/log:ro
    depends_on:
      - monitoring-service
```

### 2. **環境變量配置**

```bash
# 監控系統配置
MONITORING_ENABLED=true
MONITORING_INTERVAL=30  # 監控間隔（秒）
ALERT_ENABLED=true
ALERT_CHANNELS=email,slack,webhook

# 性能監控配置
PERFORMANCE_MONITORING=true
PERFORMANCE_METRICS_RETENTION_DAYS=30
PERFORMANCE_THRESHOLDS_CPU=80
PERFORMANCE_THRESHOLDS_MEMORY=80
PERFORMANCE_THRESHOLDS_DISK=90

# 告警配置
ALERT_EMAIL_SMTP_HOST=smtp.gmail.com
ALERT_EMAIL_SMTP_PORT=587
ALERT_EMAIL_USERNAME=alerts@company.com
ALERT_EMAIL_PASSWORD=password
ALERT_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
ALERT_WEBHOOK_URL=https://monitoring.company.com/webhook

# 數據庫配置
MONITORING_DB_HOST=postgres
MONITORING_DB_PORT=5432
MONITORING_DB_NAME=monitoring
MONITORING_DB_USER=monitoring_user
MONITORING_DB_PASSWORD=monitoring_password
```

## 📊 使用示例

### 1. **啟動監控系統**

```python
# 啟動監控系統
async def start_monitoring_system():
    """啟動監控系統"""
    
    # 創建監控組件
    performance_monitor = PerformanceMonitor()
    alert_manager = AlertManager()
    fault_diagnostic = FaultDiagnostic()
    fault_recovery = FaultRecovery()
    
    # 啟動監控循環
    while True:
        try:
            # 收集監控數據
            monitoring_data = await collect_monitoring_data()
            
            # 檢查告警
            alerts = await alert_manager.check_alerts(monitoring_data)
            
            # 診斷問題
            diagnostic_results = await fault_diagnostic.diagnose_issues(monitoring_data)
            
            # 嘗試恢復
            for result in diagnostic_results:
                await fault_recovery.attempt_recovery(result)
            
            # 記錄監控數據
            await save_monitoring_data(monitoring_data)
            
            # 等待下次監控
            await asyncio.sleep(MONITORING_INTERVAL)
            
        except Exception as e:
            logger.error(f"監控系統運行錯誤: {e}")
            await asyncio.sleep(60)  # 錯誤時等待1分鐘
```

### 2. **監控儀表板**

```python
# 監控儀表板 API
@app.get("/api/monitoring/dashboard")
async def get_monitoring_dashboard():
    """獲取監控儀表板數據"""
    
    # 獲取最新監控數據
    latest_data = await get_latest_monitoring_data()
    
    # 獲取歷史趨勢
    historical_trends = await get_historical_trends(days=7)
    
    # 獲取告警狀態
    active_alerts = await get_active_alerts()
    
    # 獲取性能分析
    performance_analysis = await analyze_performance_trends()
    
    return {
        'current_status': latest_data,
        'historical_trends': historical_trends,
        'active_alerts': active_alerts,
        'performance_analysis': performance_analysis,
        'timestamp': datetime.now().isoformat()
    }
```

## 🔧 故障排除

### 1. **常見問題**

#### 問題：監控數據不更新
**症狀**: 儀表板顯示舊數據
**解決方案**:
```python
# 檢查監控服務狀態
async def check_monitoring_service():
    """檢查監控服務狀態"""
    try:
        response = await http_client.get('http://monitoring-service:8000/health')
        if response.status_code == 200:
            logger.info("✅ 監控服務正常")
        else:
            logger.error("❌ 監控服務異常")
    except Exception as e:
        logger.error(f"❌ 監控服務連接失敗: {e}")
```

#### 問題：告警不發送
**症狀**: 系統異常但沒有收到告警
**解決方案**:
```python
# 測試告警通道
async def test_alert_channels():
    """測試告警通道"""
    test_alert = Alert(
        rule_name="測試告警",
        severity="info",
        message="這是一個測試告警",
        timestamp=datetime.now(),
        data={}
    )
    
    for channel in alert_manager.notification_channels:
        try:
            await channel.send(test_alert)
            logger.info(f"✅ {channel.name} 告警通道正常")
        except Exception as e:
            logger.error(f"❌ {channel.name} 告警通道失敗: {e}")
```

### 2. **性能問題**

#### 問題：監控系統影響主系統性能
**解決方案**:
- 降低監控頻率
- 使用異步監控
- 優化數據收集算法

#### 問題：監控數據存儲空間不足
**解決方案**:
- 實施數據壓縮
- 設置數據保留策略
- 使用外部存儲

## 📈 未來改進

### 1. **智能監控**
- 機器學習異常檢測
- 預測性維護
- 自動化故障恢復

### 2. **可視化增強**
- 實時儀表板
- 互動式圖表
- 3D 系統拓撲圖

### 3. **多雲監控**
- 跨雲平台監控
- 混合雲環境支持
- 雲原生監控

### 4. **安全監控**
- 安全事件監控
- 威脅檢測
- 合規性檢查

## 📚 相關文檔

- [系統概述](./01-system-overview.md)
- [後端架構](./03-backend-architecture.md)
- [Bug 分析和問題清單](./07-bug-analysis-and-issues.md)
- [自我學習系統](./08-self-learning-system.md)
- [互動分析系統](./09-interaction-analysis-system.md)


