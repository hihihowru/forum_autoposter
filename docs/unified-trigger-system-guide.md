# 🚀 統一觸發器系統使用指南

## 📋 系統概述

新的統一觸發器系統將所有觸發器整合到一個統一的架構中，支援兩種KOL分配策略：

- **固定KOL池** (Fixed Pool): 用於特定場域發文，如盤後機器人
- **配對池** (Matching Pool): 用於智能匹配發文，如熱門話題

## 🏗️ 系統架構

```
觸發器腳本 → 智能調配系統 → 數據源調度 → KOL分配策略 → 統一內容生成 → Google Sheets記錄
```

### 核心組件

1. **KOLAllocationStrategy**: KOL分配策略管理器
2. **UnifiedTriggerInterface**: 統一觸發器接口
3. **SmartAPIAllocator**: 智能API資源調配器
4. **ContentGenerator**: 統一內容生成器

## 🎯 觸發器配置

### 預設觸發器配置

| 觸發器 | 分配策略 | 最大分配數 | 說明 |
|--------|----------|------------|------|
| `after_hours_limit_up` | 固定池 | 1 | 盤後漲停股，每檔股票1個KOL |
| `intraday_surge` | 固定池 | 1 | 盤中急漲股，每檔股票1個KOL |
| `trending_topics` | 配對池 | 3 | 熱門話題，每個話題最多3個KOL |
| `limit_up_stocks` | 配對池 | 2 | 漲停股分析，每個話題最多2個KOL |
| `hot_stocks` | 配對池 | 2 | 熱門股分析，每個話題最多2個KOL |

## 🔧 使用方法

### 1. 基本使用

```python
from src.services.flow.unified_trigger_interface import execute_after_hours_limit_up

# 執行盤後機器人
result = await execute_after_hours_limit_up()
print(f"執行結果: {result}")
```

### 2. 自定義配置

```python
from src.services.flow.unified_trigger_interface import UnifiedTriggerInterface
from src.services.flow.kol_allocation_strategy import TriggerConfig, AllocationStrategy

# 創建自定義配置
config = TriggerConfig(
    trigger_type="after_hours_limit_up",
    allocation_strategy=AllocationStrategy.FIXED_POOL,
    max_assignments_per_topic=1,
    enable_content_generation=True,
    enable_publishing=False
)

# 執行觸發器
interface = UnifiedTriggerInterface()
result = await interface.execute_trigger("after_hours_limit_up", config)
```

### 3. 設定KOL池

```python
from kol_config_manager import KOLConfigManager

manager = KOLConfigManager()

# 設定盤後機器人KOL池
high_volume_kols = [201, 202, 203, 204, 205]  # 高量股票KOL
low_volume_kols = [206, 207, 208, 209, 210]   # 低量股票KOL

manager.setup_after_hours_kol_pool(high_volume_kols, low_volume_kols)
```

## 📊 KOL分配策略詳解

### 固定KOL池 (Fixed Pool)

**適用場景**: 盤後機器人、盤中急漲股等需要固定分配的場景

**特點**:
- 預先定義KOL列表
- 輪流分配，確保負載均衡
- 不進行智能匹配計算
- 適合大量股票的批量處理

**配置示例**:
```python
# 盤後機器人: 15個KOL (10個高量 + 5個低量)
after_hours_pool = {
    "high_volume": [201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
    "low_volume": [211, 212, 213, 214, 215]
}
```

### 配對池 (Matching Pool)

**適用場景**: 熱門話題、漲停股分析等需要智能匹配的場景

**特點**:
- 基於話題內容和KOL特徵進行匹配
- 計算匹配分數，選擇最佳KOL
- 支援多個KOL分配給同一話題
- 適合內容品質要求高的場景

**匹配規則**:
- 人設匹配 (權重 1.5)
- 話題偏好匹配 (權重 1.2)
- 數據偏好匹配 (權重 0.5-0.8)
- 禁講類別檢查 (強制排除)

## 🛠️ 配置管理

### 使用配置管理腳本

```bash
python3 kol_config_manager.py
```

**功能選項**:
1. 設定盤後機器人KOL池
2. 設定盤中急漲股KOL池
3. 更新觸發器策略
4. 顯示當前配置
5. 導出配置
6. 測試盤後機器人

### 手動配置

```python
# 更新固定KOL池
interface.kol_allocation.update_fixed_pool(
    "after_hours_limit_up", 
    "high_volume", 
    [201, 202, 203, 204, 205]
)

# 更新觸發器策略
config = TriggerConfig(
    trigger_type="trending_topics",
    allocation_strategy=AllocationStrategy.MATCHING_POOL,
    max_assignments_per_topic=3
)
interface.update_trigger_config("trending_topics", config)
```

## 📈 執行結果

### UnifiedTriggerResult 結構

```python
@dataclass
class UnifiedTriggerResult:
    success: bool                    # 執行是否成功
    trigger_type: str               # 觸發器類型
    allocation_strategy: str        # 分配策略
    total_topics: int              # 處理話題數
    total_assignments: int         # 分配任務數
    generated_posts: int           # 生成貼文數
    execution_time: float          # 執行時間
    errors: List[str]             # 錯誤列表
    details: Dict[str, Any]       # 詳細資訊
```

### 詳細資訊包含

- `api_allocation`: API資源分配摘要
- `kol_allocation`: KOL分配摘要
- `generated_posts`: 生成的貼文列表

## 🔄 工作流程

### 盤後機器人流程

1. **觸發器啟動**: `after_hours_limit_up`
2. **數據獲取**: 從Finlab API獲取今日漲停股
3. **智能調配**: 分配API資源 (Serper, Finlab, 技術分析等)
4. **KOL分配**: 使用固定池輪流分配KOL
5. **內容生成**: 統一內容生成器生成個人化內容
6. **記錄**: 記錄到Google Sheets

### 熱門話題流程

1. **觸發器啟動**: `trending_topics`
2. **數據獲取**: 從CMoney API獲取熱門話題
3. **智能調配**: 分配API資源 (Serper, CMoney新聞等)
4. **KOL分配**: 使用配對池智能匹配KOL
5. **內容生成**: 統一內容生成器生成個人化內容
6. **記錄**: 記錄到Google Sheets

## 🚀 快速開始

### 1. 設定新的KOL帳密

```bash
# 編輯環境變數
vim .env

# 添加新的KOL密碼
CMONEY_PASSWORD_211=your_new_password_211
CMONEY_PASSWORD_212=your_new_password_212
# ... 更多KOL密碼
```

### 2. 配置KOL池

```bash
# 運行配置管理腳本
python3 kol_config_manager.py

# 選擇選項1: 設定盤後機器人KOL池
# 輸入新的KOL序號列表
```

### 3. 測試執行

```bash
# 測試盤後機器人
python3 after_hours_limit_up_bot_v2.py

# 或使用配置管理腳本的測試功能
python3 kol_config_manager.py
# 選擇選項6: 測試盤後機器人
```

## 📝 注意事項

1. **環境變數**: 確保所有必要的API Keys已設定
2. **KOL配置**: 新的KOL需要在Google Sheets的「同學會帳號管理」中配置
3. **API配額**: 注意API使用配額，避免超出限制
4. **錯誤處理**: 系統會自動處理大部分錯誤，但建議監控執行結果
5. **日誌記錄**: 所有操作都會記錄到日誌中，便於問題排查

## 🔧 故障排除

### 常見問題

1. **KOL登入失敗**: 檢查密碼是否正確，帳號是否啟用
2. **API調用失敗**: 檢查API Key是否有效，配額是否充足
3. **內容生成失敗**: 檢查OpenAI API Key和網路連接
4. **Google Sheets記錄失敗**: 檢查憑證文件和權限設定

### 調試方法

```python
# 啟用詳細日誌
import logging
logging.basicConfig(level=logging.DEBUG)

# 檢查配置
interface = UnifiedTriggerInterface()
summary = interface.get_trigger_summary()
print(summary)
```

## 📞 支援

如有問題，請檢查：
1. 日誌文件中的錯誤訊息
2. Google Sheets中的記錄狀態
3. API配額使用情況
4. 環境變數設定

系統設計為高度自動化，大部分問題會自動處理或記錄，便於後續分析和改進。








