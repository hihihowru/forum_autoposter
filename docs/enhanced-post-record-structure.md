# 增強版貼文記錄表結構設計

## 🎯 設計目標

### 主要改進
1. **內容多樣性** - 避免統一的貼文格式和風格
2. **完整參數記錄** - 追蹤所有生成參數和數據來源
3. **品質監控** - 記錄生成品質指標和驗證結果
4. **個性化追蹤** - 根據 KOL 人設記錄對應的專業參數

---

## 📊 新的貼文記錄表結構

### 基礎信息欄位 (A-O)
| 欄位位置 | 欄位名稱 | 說明 | 範例 |
|---------|---------|------|------|
| A | 貼文ID | 唯一標識符 | "fb1ed457-f0fc-47ce-86dd-f29056297ebf-202" |
| B | KOL序號 | KOL的序號 | "202" |
| C | KOL暱稱 | KOL的暱稱 | "梅川褲子" |
| D | KOL Member ID | KOL的會員ID | "9505548" |
| E | 人設 | KOL的人設類型 | "新聞派" |
| F | 內容類型 | 內容分類 | "investment" |
| G | 話題索引 | 話題的索引編號 | "1" |
| H | 話題ID | 話題的唯一標識符 | "fb1ed457-f0fc-47ce-86dd-f29056297ebf" |
| I | 話題標題 | 話題的標題 | "台股開紅衝155點!科技股噴爆啦!!!🚀..." |
| J | 話題關鍵字 | 話題的關鍵字 | "台股,科技股,台積電" |
| K | 內容 | 生成的貼文內容 | "台股開紅衝155點!科技股噴爆啦!!!🚀..." |
| L | 狀態 | 貼文狀態 | "已發布" |
| M | 預定時間 | 預定發布時間 | "2025-08-27 11:00:00" |
| N | 發文時間 | 實際發布時間 | "2025-08-27 11:14:50" |
| O | 錯誤訊息 | 發布失敗的錯誤訊息 | "" |

### 平台信息欄位 (P-R)
| 欄位位置 | 欄位名稱 | 說明 | 範例 |
|---------|---------|------|------|
| P | 平台發文ID | 平台上的文章ID | "173349543" |
| Q | 平台發文URL | 完整的文章URL | "https://www.cmoney.tw/forum/article/173349543" |
| R | 熱門話題標題 | 相關的熱門話題標題 | "台股開紅盤" |

### 新增：內容生成參數欄位 (S-AA)
| 欄位位置 | 欄位名稱 | 說明 | 範例 |
|---------|---------|------|------|
| S | 發文類型 | 提問型/發表看法 | "發表看法" |
| T | 內容長度 | 文章長度類型 | "100-250" |
| U | 內文字數 | 實際字數統計 | "156" |
| V | KOL權重設定 | KOL的權重配置 | "技術派:0.8,新聞派:0.2" |
| W | 內容生成時間 | 生成內容耗時 | "2.3秒" |
| X | KOL設定版本 | KOL設定的版本號 | "v2.1" |
| Y | 文章長度向量 | 長度向量的數值 | "[0.2, 0.8, 0.0]" |
| Z | 語氣向量 | 語氣向量的數值 | "[0.7, 0.2, 0.1]" |
| AA | Temperature設定 | 生成時的溫度參數 | "0.7" |

### 新增：數據來源追蹤欄位 (AB-AF)
| 欄位位置 | 欄位名稱 | 說明 | 範例 |
|---------|---------|------|------|
| AB | 調用數據來源庫 | 使用的數據來源 | "Finlab API, Google Sheets" |
| AC | OHLC數據狀態 | OHLC數據獲取狀態 | "成功" |
| AD | 技術指標計算 | 技術指標計算結果 | "RSI:65.5, MA:多頭排列" |
| AE | 股票標記驗證 | 股票標記是否正確 | "正確:台積電(2330)" |
| AF | Body Parameter | 完整的API請求參數 | "{\"stock_id\":\"2330\",\"timeframe\":\"1d\"}" |

---

## 🔧 數據類型定義

### TypeScript 接口
```typescript
interface EnhancedPostRecord {
  // 基礎信息
  post_id: string;
  kol_serial: string;
  kol_nickname: string;
  kol_member_id: string;
  persona: string;
  content_type: string;
  topic_index: number;
  topic_id: string;
  topic_title: string;
  topic_keywords: string;
  content: string;
  status: string;
  scheduled_time: string;
  post_time: string;
  error_message: string;
  
  // 平台信息
  platform_post_id: string;
  platform_post_url: string;
  trending_topic_title: string;
  
  // 內容生成參數
  post_type: '提問型' | '發表看法';
  content_length: '<100' | '100-250' | '>250';
  word_count: number;
  kol_weight_settings: string;
  content_generation_time: string;
  kol_settings_version: string;
  length_vector: number[];
  tone_vector: number[];
  temperature: number;
  
  // 數據來源追蹤
  data_sources: string[];
  ohlc_status: '成功' | '失敗' | '未調用';
  technical_indicators: string;
  stock_validation: string;
  body_parameters: string;
}
```

### Python 數據類
```python
@dataclass
class EnhancedPostRecord:
    """增強版貼文記錄"""
    # 基礎信息
    post_id: str
    kol_serial: str
    kol_nickname: str
    kol_member_id: str
    persona: str
    content_type: str
    topic_index: int
    topic_id: str
    topic_title: str
    topic_keywords: str
    content: str
    status: str
    scheduled_time: str
    post_time: str
    error_message: str
    
    # 平台信息
    platform_post_id: str
    platform_post_url: str
    trending_topic_title: str
    
    # 內容生成參數
    post_type: str  # 提問型/發表看法
    content_length: str  # <100, 100-250, >250
    word_count: int
    kol_weight_settings: str
    content_generation_time: str
    kol_settings_version: str
    length_vector: List[float]
    tone_vector: List[float]
    temperature: float
    
    # 數據來源追蹤
    data_sources: List[str]
    ohlc_status: str
    technical_indicators: str
    stock_validation: str
    body_parameters: str
```

---

## 📈 統計分析維度

### 1. 內容品質分析
- **字數分布**: <100, 100-250, >250 的分布比例
- **生成時間**: 平均生成時間，生成時間分布
- **Temperature 分布**: 不同溫度參數的使用情況

### 2. 數據來源分析
- **OHLC 調用率**: 成功調用 Finlab API 的比例
- **技術指標計算**: 不同技術指標的使用頻率
- **股票標記準確率**: 股票標記的正確率統計

### 3. KOL 表現分析
- **個性化參數**: 每個 KOL 的權重設定和偏好
- **內容風格**: 基於語氣向量的風格分析
- **專業領域**: 根據數據來源分析專業深度

---

## 🚀 實作建議

### 第一階段：基礎欄位擴展
1. 在 Google Sheets 中添加新欄位 (S-AF)
2. 更新後端 API 的數據讀取邏輯
3. 修改前端組件的數據展示

### 第二階段：數據來源整合
1. 實現 Finlab API 的 OHLC 數據獲取
2. 添加技術指標計算邏輯
3. 實現股票標記驗證功能

### 第三階段：品質監控
1. 實現生成參數的完整記錄
2. 添加內容品質評估指標
3. 建立異常檢測和報警機制

---

## 📊 儀表板更新需求

### 內容管理頁面
- 新增內容長度、發文類型等統計
- 添加數據來源使用分析
- 優化貼文表格的欄位展示

### KOL 詳細頁面
- 新增技術參數統計卡片
- 添加數據來源使用分析
- 實現生成品質趨勢圖表

### 貼文詳細頁面（未來功能）
- 完整的生成參數展示
- 數據來源追蹤和驗證結果
- 技術指標計算詳情

---

*增強版貼文記錄表結構設計版本: v2.0*  
*最後更新: 2025-08-28*  
*設計範圍: 虛擬 KOL 系統內容生成追蹤*



