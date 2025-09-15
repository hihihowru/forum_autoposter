# 互動分析表格設計

## 🎯 目標
創建一個綜合的互動分析表格，展示所有 KOL 的貼文表現和互動數據。

## 📊 表格結構

### **主要欄位**
| 欄位名稱 | 類型 | 說明 | 範例 |
|---------|------|------|------|
| `post_id` | UUID | 貼文唯一識別碼 | `0b1770f2-3802-4ad4-b475-bc0c83395aa5` |
| `kol_name` | String | KOL 名稱 | `川川哥` |
| `kol_serial` | Integer | KOL 編號 | `1` |
| `title` | String | 貼文標題 | `大盤淺見` |
| `trigger_type` | String | 觸發器類型 | `trending_topic`, `limit_up_after_hours` |
| `topic_title` | String | 熱門話題標題 | `AI 概念股大漲` |
| `stock_symbols` | Array | 相關股票代碼 | `["2330", "2454"]` |
| `cmoney_post_id` | String | CMoney 文章 ID | `173746398` |
| `cmoney_post_url` | String | CMoney 文章連結 | `https://forum.cmoney.tw/...` |
| `publish_date` | DateTime | 發布日期 | `2024-01-15 10:30:00` |
| `status` | String | 貼文狀態 | `published`, `draft`, `deleted` |

### **互動數據欄位**
| 欄位名稱 | 類型 | 說明 | 範例 |
|---------|------|------|------|
| `views` | Integer | 瀏覽數 | `150` |
| `likes` | Integer | 讚數 | `25` |
| `comments` | Integer | 留言數 | `8` |
| `shares` | Integer | 分享數 | `3` |
| `engagement_rate` | Float | 互動率 | `24.0` |
| `emoji_count` | JSON | 表情符號統計 | `{"like": 25, "money": 2}` |
| `last_updated` | DateTime | 最後更新時間 | `2024-01-15 15:30:00` |

### **分析欄位**
| 欄位名稱 | 類型 | 說明 | 範例 |
|---------|------|------|------|
| `performance_score` | Float | 表現評分 | `85.5` |
| `trending_rank` | Integer | 熱門排行 | `3` |
| `category` | String | 內容分類 | `技術分析`, `市場評論` |
| `sentiment` | String | 情感分析 | `positive`, `neutral`, `negative` |

## 🔧 技術實現

### **1. 數據庫表格**
```sql
CREATE TABLE interaction_analysis (
    id SERIAL PRIMARY KEY,
    post_id UUID NOT NULL,
    kol_name VARCHAR(100) NOT NULL,
    kol_serial INTEGER NOT NULL,
    title TEXT NOT NULL,
    trigger_type VARCHAR(50),
    topic_title TEXT,
    stock_symbols TEXT[], -- PostgreSQL Array
    cmoney_post_id VARCHAR(50),
    cmoney_post_url TEXT,
    publish_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'draft',
    
    -- 互動數據
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    engagement_rate FLOAT DEFAULT 0.0,
    emoji_count JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 分析數據
    performance_score FLOAT,
    trending_rank INTEGER,
    category VARCHAR(50),
    sentiment VARCHAR(20),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **2. API 端點設計**
```python
# 獲取互動分析數據
GET /interactions/analysis
- 支援分頁、排序、篩選
- 支援按 KOL、觸發器、時間範圍篩選

# 更新分析數據
POST /interactions/analysis/update
- 批量更新表現評分
- 更新情感分析結果

# 獲取 KOL 表現統計
GET /interactions/analysis/kol-stats
- 每個 KOL 的總體表現
- 平均互動率、最佳貼文等
```

### **3. 前端表格組件**
```typescript
interface InteractionAnalysisTable {
  // 表格配置
  columns: TableColumn[];
  filters: FilterConfig[];
  sorting: SortConfig[];
  
  // 數據操作
  refreshData: () => Promise<void>;
  exportData: (format: 'csv' | 'excel') => void;
  updateAnalysis: (postIds: string[]) => Promise<void>;
}
```

## 📈 分析功能

### **1. 即時統計**
- 總貼文數、總互動數
- 平均互動率、最佳表現貼文
- KOL 排行榜、觸發器效果比較

### **2. 趨勢分析**
- 時間序列圖表
- 互動率變化趨勢
- 熱門話題效果分析

### **3. 比較分析**
- KOL 間表現比較
- 觸發器效果比較
- 股票標籤效果分析

## 🚀 實施計劃

### **階段 1: 基礎表格 (2小時)**
1. 創建數據庫表格
2. 實現基本 API 端點
3. 創建前端表格組件

### **階段 2: 分析功能 (2小時)**
1. 實現統計計算
2. 添加篩選和排序
3. 創建圖表組件

### **階段 3: 進階功能 (2小時)**
1. 情感分析整合
2. 表現評分算法
3. 數據導出功能

## 📋 下一步行動
1. 確認表格結構設計
2. 開始實施數據庫表格
3. 實現基礎 API 端點
4. 創建前端表格組件
