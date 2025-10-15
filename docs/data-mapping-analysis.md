# 數據映射分析報告

## 📊 數據來源對應檢查

### 第一張：系統運營監控儀表板

#### ✅ 可對應的數據
| 儀表板需求 | 數據來源 | 對應欄位/API | 狀態 |
|------------|----------|--------------|------|
| 服務健康狀態 | 微服務健康檢查 | `/health` 端點 | ✅ 可用 |
| 任務隊列狀態 | Celery 監控 | Celery 監控 API | ✅ 可用 |
| CPU/記憶體使用率 | 系統監控 | 系統資源 API | ✅ 可用 |
| API 響應時間 | 微服務監控 | 各服務響應時間 | ✅ 可用 |
| 實時日誌 | 系統日誌 | 日誌收集系統 | ✅ 可用 |

#### ❌ 需要新增的數據
| 儀表板需求 | 建議解決方案 | 優先級 |
|------------|--------------|--------|
| 錯誤率統計 | 從日誌分析計算 | 高 |
| 網路流量監控 | 系統監控 API | 中 |
| 磁碟空間使用 | 系統監控 API | 中 |

---

### 第二張：內容生成與發布儀表板

#### ✅ 可對應的數據 (同學會帳號管理表)
| 儀表板需求 | 對應欄位 | 數據類型 | 狀態 |
|------------|----------|----------|------|
| Member ID | `MemberId` | 文字 | ✅ 可用 |
| 暱稱 | `暱稱` | 文字 | ✅ 可用 |
| 人設 | `人設` | 文字 | ✅ 可用 |
| 狀態 | `狀態` | 文字 | ✅ 可用 |
| 內容類型 | `內容類型` | 文字 | ✅ 可用 |
| 發文時間 | `發文時間` | 文字 | ✅ 可用 |
| 目標受眾 | `目標受眾` | 文字 | ✅ 可用 |
| 互動閾值 | `互動閾值` | 數字 | ✅ 可用 |
| 創建時間 | `創建時間` | 日期 | ✅ 可用 |
| 最後更新 | `最後更新` | 日期 | ✅ 可用 |

#### ✅ 可對應的數據 (貼文記錄表)
| 儀表板需求 | 對應欄位 | 數據類型 | 狀態 |
|------------|----------|----------|------|
| Article ID | `貼文ID` | 文字 | ✅ 可用 |
| KOL Serial | `KOL Serial` | 文字 | ✅ 可用 |
| KOL 暱稱 | `KOL 暱稱` | 文字 | ✅ 可用 |
| KOL ID | `KOL ID` | 文字 | ✅ 可用 |
| Persona | `Persona` | 文字 | ✅ 可用 |
| Content Type | `Content Type` | 文字 | ✅ 可用 |
| 生成內容 | `生成內容` | 文字 | ✅ 可用 |
| 發文狀態 | `發文狀態` | 文字 | ✅ 可用 |
| 上次排程時間 | `上次排程時間` | 日期時間 | ✅ 可用 |
| 發文時間戳記 | `發文時間戳記` | 日期時間 | ✅ 可用 |
| 錯誤訊息 | `最近錯誤訊息` | 文字 | ✅ 可用 |
| 平台發文ID | `平台發文ID` | 文字 | ✅ 可用 |
| 平台發文URL | `平台發文URL` | 文字 | ✅ 可用 |

#### ❌ 需要計算的數據
| 儀表板需求 | 計算方式 | 優先級 |
|------------|----------|--------|
| 今日生成數量 | 統計 `發文時間戳記` 為今日的記錄 | 高 |
| 發布成功率 | 統計 `發文狀態` 為 "已發布" 的比例 | 高 |
| KOL 使用分布 | 統計各 `Persona` 的使用次數 | 高 |
| 內容品質評分 | 需要新增評分機制 | 中 |

---

### 第三張：互動數據分析儀表板

#### ❌ 缺少的數據來源
**問題：互動回饋表尚未創建**

根據代碼分析，系統設計了三個互動數據表格：
- `互動回饋_1hr` - 1小時後互動數據
- `互動回饋_1day` - 1日後互動數據  
- `互動回饋_7days` - 7日後互動數據

#### 📋 需要創建的互動回饋表結構

**互動回饋_1hr 表格欄位：**
```
article_id: str              # Article ID (平台文章ID)
member_id: str               # Member ID (KOL會員ID)
nickname: str                # 暱稱
title: str                   # 標題
content: str                 # 生成內文
topic_id: str                # Topic ID
is_trending_topic: str       # 是否為熱門話題 (TRUE/FALSE)
post_time: str               # 發文時間
last_update_time: str        # 最後更新時間 (收集時間)
likes_count: int             # 按讚數
comments_count: int          # 留言數
collection_error: str        # 收集錯誤訊息
```

**互動回饋_1day 表格欄位：**
```
article_id: str              # Article ID (平台文章ID)
member_id: str               # Member ID (KOL會員ID)
nickname: str                # 暱稱
title: str                   # 標題
content: str                 # 生成內文
topic_id: str                # Topic ID
is_trending_topic: str       # 是否為熱門話題 (TRUE/FALSE)
post_time: str               # 發文時間
last_update_time: str        # 最後更新時間 (收集時間)
likes_count: int             # 按讚數
comments_count: int          # 留言數
collection_error: str        # 收集錯誤訊息
```

**互動回饋_7days 表格欄位：**
```
article_id: str              # Article ID (平台文章ID)
member_id: str               # Member ID (KOL會員ID)
nickname: str                # 暱稱
title: str                   # 標題
content: str                 # 生成內文
topic_id: str                # Topic ID
is_trending_topic: str       # 是否為熱門話題 (TRUE/FALSE)
post_time: str               # 發文時間
last_update_time: str        # 最後更新時間 (收集時間)
likes_count: int             # 按讚數
comments_count: int          # 留言數
collection_error: str        # 收集錯誤訊息
```

#### ✅ 可對應的數據 (互動回饋表創建後)
| 儀表板需求 | 對應欄位 | 數據類型 | 狀態 |
|------------|----------|----------|------|
| 總互動數 | `likes_count + comments_count` | 計算值 | ⏳ 待創建 |
| 互動率 | 需要計算公式 | 計算值 | ⏳ 待創建 |
| KOL 排名 | 按 `member_id` 統計互動數 | 計算值 | ⏳ 待創建 |
| 成長率 | 比較不同時間點的數據 | 計算值 | ⏳ 待創建 |
| 用戶活躍度 | 需要額外數據源 | 計算值 | ⏳ 待創建 |

---

## 🚨 關鍵問題和解決方案

### 問題 1：互動數據表格尚未創建
**影響：** 第三張儀表板無法顯示互動數據
**解決方案：**
1. 手動在 Google Sheets 中創建三個互動回饋表
2. 配置互動數據收集服務
3. 設置定時任務收集互動數據

### 問題 2：部分計算指標需要實作
**影響：** 儀表板顯示的統計數據需要後端計算
**解決方案：**
1. 在 Dashboard API 中實作數據聚合邏輯
2. 使用 Redis 緩存計算結果
3. 設置定時任務更新統計數據

### 問題 3：系統監控數據需要整合
**影響：** 第一張儀表板的系統監控數據需要從多個來源整合
**解決方案：**
1. 整合現有微服務的健康檢查
2. 添加系統資源監控
3. 實作日誌收集和分析

---

## 📋 實作優先級

### 高優先級 (必須完成)
1. **創建互動回饋表** - 第三張儀表板的基礎
2. **實作數據聚合邏輯** - 計算統計指標
3. **整合現有 Google Sheets 數據** - 第二張儀表板

### 中優先級 (重要功能)
1. **系統監控整合** - 第一張儀表板
2. **實時數據更新** - 所有儀表板
3. **錯誤處理和日誌** - 系統穩定性

### 低優先級 (優化功能)
1. **高級統計分析** - 深度數據分析
2. **預測功能** - 基於歷史數據的預測
3. **自定義報表** - 用戶自定義功能

---

## 🛠️ 實作建議

### 第一階段：基礎數據整合
```python
# 1. 創建互動回饋表
# 2. 實作 Google Sheets 數據讀取
# 3. 實作基本統計計算

# 示例：讀取同學會帳號管理表
def get_member_list():
    data = sheets_client.read_sheet('同學會帳號管理', 'A:Z')
    return [
        {
            'member_id': row[4],  # MemberId
            'nickname': row[1],   # 暱稱
            'persona': row[3],    # 人設
            'status': row[9],     # 狀態
            'content_type': row[10], # 內容類型
        }
        for row in data[1:]  # 跳過標題行
    ]
```

### 第二階段：統計計算實作
```python
# 實作統計計算邏輯
def calculate_content_statistics():
    # 讀取貼文記錄表
    post_data = sheets_client.read_sheet('貼文記錄表', 'A:Q')
    
    # 計算今日生成數量
    today = datetime.now().date()
    today_posts = [
        row for row in post_data[1:]
        if row[13] and datetime.fromisoformat(row[13].replace('Z', '+00:00')).date() == today
    ]
    
    # 計算發布成功率
    total_posts = len(post_data[1:])
    published_posts = len([row for row in post_data[1:] if row[11] == '已發布'])
    success_rate = (published_posts / total_posts * 100) if total_posts > 0 else 0
    
    return {
        'today_generated': len(today_posts),
        'publishing_success_rate': success_rate,
        'total_posts': total_posts
    }
```

### 第三階段：互動數據整合
```python
# 實作互動數據統計
def calculate_engagement_statistics():
    # 讀取三個互動回饋表
    engagement_1hr = sheets_client.read_sheet('互動回饋_1hr', 'A:L')
    engagement_1day = sheets_client.read_sheet('互動回饋_1day', 'A:L')
    engagement_7days = sheets_client.read_sheet('互動回饋_7days', 'A:L')
    
    # 計算總互動數
    total_interactions = sum(
        int(row[9]) + int(row[10])  # likes_count + comments_count
        for table in [engagement_1hr, engagement_1day, engagement_7days]
        for row in table[1:]  # 跳過標題行
        if len(row) > 10
    )
    
    return {
        'total_interactions': total_interactions,
        'engagement_1hr_count': len(engagement_1hr[1:]),
        'engagement_1day_count': len(engagement_1day[1:]),
        'engagement_7days_count': len(engagement_7days[1:])
    }
```

---

## ✅ 結論

### 數據可用性總結
- **第一張儀表板 (系統監控)**: 80% 數據可用，需要整合現有監控
- **第二張儀表板 (內容管理)**: 95% 數據可用，主要來自現有 Google Sheets
- **第三張儀表板 (互動分析)**: 30% 數據可用，需要創建互動回饋表

### 建議實作順序
1. **先實作第二張儀表板** - 數據最完整
2. **創建互動回饋表** - 為第三張儀表板做準備
3. **實作第一張儀表板** - 整合系統監控
4. **完善第三張儀表板** - 基於互動數據

### 風險評估
- **低風險**: 第二張儀表板，數據來源完整
- **中風險**: 第一張儀表板，需要整合多個系統
- **高風險**: 第三張儀表板，依賴互動數據收集

---

*數據映射分析版本: v1.0*  
*最後更新: 2024-01-01*  
*分析範圍: 虛擬 KOL 儀表板系統*
