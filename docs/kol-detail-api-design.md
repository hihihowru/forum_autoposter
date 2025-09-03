# KOL 個人詳情頁面 API 設計

## 概述
設計 KOL 個人詳情頁面的 API 接口，從 Google Sheets 獲取真實數據並提供給前端使用。

## 數據來源分析

### Google Sheets 結構
根據提供的 Google Sheets 連結，主要數據表包括：

1. **同學會帳號管理** (Sheet ID: 1638472912)
   - 包含所有 KOL 的基本設定和配置
   - 欄位：序號、暱稱、認領人、人設、MemberId、Email、密碼等

2. **貼文記錄表** (Sheet ID: 工作表9)
   - 包含所有貼文的記錄
   - 欄位：貼文ID、KOL Serial、KOL 暱稱、生成內容、發文狀態等

3. **互動回饋_1hr** (Sheet ID: 互動回饋_1hr)
   - 1小時後的互動數據
   - 欄位：article_id、member_id、likes_count、comments_count等

4. **互動回饋_1day** (Sheet ID: 互動回饋_1day)
   - 1天後的互動數據
   - 欄位：同上

5. **互動回饋_7days** (Sheet ID: 互動回饋_7days)
   - 7天後的互動數據
   - 欄位：同上

## API 設計

### 1. 獲取 KOL 詳情
```
GET /api/dashboard/kols/{memberId}
```

**功能**: 獲取指定 KOL 的完整資訊

**參數**:
- `memberId` (path): KOL 的 Member ID

**Response**:
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "success": true,
  "data": {
    "kol_info": {
      "serial": "200",
      "nickname": "川川哥",
      "member_id": "9505546",
      "persona": "技術派",
      "status": "active",
      "owner": "9505546",
      "email": "forum_200@cmoney.com.tw",
      "password": "N9t1kY3x",
      "whitelist": true,
      "notes": "威廉用",
      "post_times": "08:00,14:30",
      "target_audience": "active_traders",
      "interaction_threshold": 0.7,
      "content_types": ["technical", "chart"],
      "common_terms": "黃金交叉、均線糾結、三角收斂、K棒爆量、跳空缺口、支撐帶、壓力線、爆量突破、假突破、牛熊交替、短多、日K、週K、月K、EMA、MACD背離、成交量暴增、突破拉回、停利、移動停損",
      "colloquial_terms": "穩了啦、爆啦、開高走低、嘎到、這根要噴、笑死、抄底啦、套牢啦、老師來了、要噴啦、破線啦、還在盤整、穩穩的、這樣嘎死、快停損、這裡進場、紅K守不住、買爆、賣壓炸裂、等回測、睡醒漲停",
      "tone_style": "自信直球，有時會狂妄，有時又碎碎念，像版上常見的「嘴很臭但有料」帳號",
      "typing_habit": "不打標點.....全部用省略號串起來,偶爾英文逗號亂插",
      "backstory": "大學就開始玩技術分析，曾經靠抓到台積電一根漲停翻身，信奉「K線就是人生」，常常半夜盯圖到三點。",
      "expertise": "技術分析,圖表解讀",
      "data_source": "ohlc,indicators",
      "created_time": "2024-01-01",
      "last_updated": "2024-01-15",
      "prompt_persona": "技術分析老玩家，嘴臭但有料，堅信「K線就是人生」。",
      "prompt_style": "自信直球，偶爾狂妄，版上嘴炮卻常常講中關鍵位",
      "prompt_guardrails": "只使用提供之數據，不得捏造或留白；避免投資建議式語氣；口吻要像真人在社群發文；不能出現「標題/導言/主體」這種 AI 結構字樣；所有數字必須帶實際值。",
      "prompt_skeleton": "【${nickname}】技術面快報 ${EmojiPack}\\n收盤 ${kpis.close}（${kpis.chg}/${kpis.chgPct}%）…..這波是 ${kpis.trend}\\n觀察：支撐 ${kpis.support} / 壓力 ${kpis.resistance}\\nRSI=${kpis.rsi14}, SMA20=${kpis.sma20}, SMA60=${kpis.sma60}\\n${PromptCTA}\\n${PromptHashtags}\\n${Signature}",
      "prompt_cta": "想看我後續追蹤與進出點，留言「追蹤${stock_id}」",
      "prompt_hashtags": "#台股,#${stock_id},#技術分析,#投資,#K線",
      "signature": "—— 川普插三劍變州普",
      "emoji_pack": "🚀🔥😂📈",
      "model_id": "gpt-4o-mini",
      "model_temp": 0.55,
      "max_tokens": 700
    },
    "statistics": {
      "total_posts": 25,
      "published_posts": 23,
      "draft_posts": 2,
      "avg_interaction_rate": 0.045,
      "best_performing_post": "post-001",
      "total_interactions": 1250,
      "avg_likes_per_post": 45,
      "avg_comments_per_post": 8
    }
  }
}
```

### 2. 獲取 KOL 發文歷史
```
GET /api/dashboard/kols/{memberId}/posts
```

**功能**: 獲取指定 KOL 的發文歷史

**參數**:
- `memberId` (path): KOL 的 Member ID
- `page` (query): 頁碼，預設 1
- `page_size` (query): 每頁數量，預設 10
- `status` (query): 發文狀態篩選 (published|draft|all)
- `start_date` (query): 開始日期
- `end_date` (query): 結束日期

**Response**:
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "success": true,
  "data": {
    "posts": [
      {
        "post_id": "post-001",
        "topic_id": "topic-001",
        "topic_title": "測試話題1",
        "topic_keywords": "技術,圖表",
        "content": "這是測試內容1",
        "status": "已發布",
        "scheduled_time": "2024-01-01T10:00:00Z",
        "post_time": "2024-01-01T10:00:00Z",
        "error_message": "",
        "platform_post_id": "platform-001",
        "platform_post_url": "https://www.cmoney.tw/forum/articles/173337593",
        "interactions": {
          "1hr": {
            "likes_count": 45,
            "comments_count": 8,
            "total_interactions": 53,
            "engagement_rate": 0.053,
            "growth_rate": 0.15
          },
          "1day": {
            "likes_count": 52,
            "comments_count": 12,
            "total_interactions": 64,
            "engagement_rate": 0.064,
            "growth_rate": 0.12
          },
          "7days": {
            "likes_count": 68,
            "comments_count": 18,
            "total_interactions": 86,
            "engagement_rate": 0.086,
            "growth_rate": 0.08
          }
        }
      }
    ],
    "pagination": {
      "current_page": 1,
      "page_size": 10,
      "total_pages": 3,
      "total_items": 25
    }
  }
}
```

### 3. 獲取 KOL 互動數據
```
GET /api/dashboard/kols/{memberId}/interactions
```

**功能**: 獲取指定 KOL 的互動數據分析

**參數**:
- `memberId` (path): KOL 的 Member ID
- `timeframe` (query): 時間範圍 (1hr|1day|7days)
- `start_date` (query): 開始日期
- `end_date` (query): 結束日期
- `group_by` (query): 分組方式 (day|week|month)

**Response**:
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "success": true,
  "data": {
    "interaction_summary": {
      "total_posts": 25,
      "avg_interaction_rate": 0.045,
      "total_likes": 1125,
      "total_comments": 200,
      "total_interactions": 1325,
      "best_performing_post": "post-001",
      "worst_performing_post": "post-015"
    },
    "interaction_trend": [
      {
        "date": "2024-01-01",
        "posts_count": 2,
        "total_interactions": 150,
        "avg_engagement_rate": 0.05,
        "likes": 120,
        "comments": 30
      },
      {
        "date": "2024-01-02",
        "posts_count": 1,
        "total_interactions": 85,
        "avg_engagement_rate": 0.042,
        "likes": 70,
        "comments": 15
      }
    ],
    "performance_by_topic": [
      {
        "topic_id": "topic-001",
        "topic_title": "技術分析",
        "posts_count": 8,
        "avg_interaction_rate": 0.052,
        "total_interactions": 420
      },
      {
        "topic_id": "topic-002",
        "topic_title": "圖表解讀",
        "posts_count": 6,
        "avg_interaction_rate": 0.048,
        "total_interactions": 290
      }
    ]
  }
}
```

### 4. 獲取 KOL 設定
```
GET /api/dashboard/kols/{memberId}/settings
```

**功能**: 獲取指定 KOL 的詳細設定

**Response**:
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "success": true,
  "data": {
    "basic_settings": {
      "post_times": "08:00,14:30",
      "target_audience": "active_traders",
      "interaction_threshold": 0.7,
      "content_types": ["technical", "chart"],
      "trending_topics": 0,
      "topic_preferences": "技術派,籌碼派",
      "forbidden_topics": "無",
      "data_preferences": "kline資料"
    },
    "persona_settings": {
      "common_terms": "黃金交叉、均線糾結、三角收斂...",
      "colloquial_terms": "穩了啦、爆啦、開高走低...",
      "tone_style": "自信直球，有時會狂妄...",
      "typing_habit": "不打標點.....全部用省略號串起來...",
      "backstory": "大學就開始玩技術分析...",
      "expertise": "技術分析,圖表解讀",
      "strength_keywords": "圖表分析、突破",
      "hook_tone": "強烈號召"
    },
    "prompt_settings": {
      "prompt_persona": "技術分析老玩家，嘴臭但有料...",
      "prompt_style": "自信直球，偶爾狂妄...",
      "prompt_guardrails": "只使用提供之數據...",
      "prompt_skeleton": "【${nickname}】技術面快報...",
      "prompt_cta": "想看我後續追蹤與進出點...",
      "prompt_hashtags": "#台股,#${stock_id},#技術分析...",
      "signature": "—— 川普插三劍變州普",
      "emoji_pack": "🚀🔥😂📈"
    },
    "model_settings": {
      "model_id": "gpt-4o-mini",
      "template_variant": "default",
      "model_temp": 0.55,
      "max_tokens": 700
    }
  }
}
```

## 後端實現

### 1. 數據獲取邏輯

```python
# 在 dashboard-api/main.py 中添加新的路由

@app.get("/api/dashboard/kols/{member_id}")
async def get_kol_detail(member_id: str):
    try:
        # 從同學會帳號管理表獲取 KOL 基本資訊
        kol_data = sheets_client.read_sheet("同學會帳號管理")
        kol_info = None
        
        for row in kol_data[1:]:  # 跳過標題行
            if len(row) > 5 and row[5] == member_id:  # MemberId 在第6列
                kol_info = {
                    "serial": row[0],
                    "nickname": row[1],
                    "member_id": row[5],
                    "persona": row[3],
                    "status": row[9] if len(row) > 9 else "unknown",
                    "owner": row[2],
                    "email": row[6] if len(row) > 6 else "",
                    "password": row[7] if len(row) > 7 else "",
                    "whitelist": row[8] == "TRUE" if len(row) > 8 else False,
                    "notes": row[9] if len(row) > 9 else "",
                    # ... 其他欄位
                }
                break
        
        if not kol_info:
            raise HTTPException(status_code=404, detail="KOL not found")
        
        # 從貼文記錄表獲取發文統計
        post_data = sheets_client.read_sheet("貼文記錄表")
        kol_posts = [row for row in post_data[1:] if len(row) > 3 and row[3] == member_id]
        
        # 解析貼文記錄
        post_history = []
        for row in kol_posts:
            if len(row) >= 17:  # 確保有足夠的欄位
                post_record = {
                    "post_id": row[0],
                    "kol_serial": row[1],
                    "kol_nickname": row[2],
                    "kol_member_id": row[3],
                    "persona": row[4],
                    "content_type": row[5],
                    "topic_index": row[6],
                    "topic_id": row[7],
                    "topic_title": row[8],
                    "topic_keywords": row[9],
                    "content": row[10],
                    "status": row[11],
                    "scheduled_time": row[12],
                    "post_time": row[13],
                    "error_message": row[14],
                    "platform_post_id": row[15],
                    "platform_post_url": row[16],
                    "trending_topic_title": row[17] if len(row) > 17 else ""
                }
                post_history.append(post_record)
        
        statistics = {
            "total_posts": len(kol_posts),
            "published_posts": len([p for p in kol_posts if len(p) > 11 and p[11] == "已發布"]),
            "draft_posts": len([p for p in kol_posts if len(p) > 11 and p[11] == "草稿"]),
            "avg_interaction_rate": 0.045,  # 需要從互動表計算
            "best_performing_post": "post-001",  # 需要從互動表計算
            "total_interactions": 1250,  # 需要從互動表計算
            "avg_likes_per_post": 45,  # 需要從互動表計算
            "avg_comments_per_post": 8  # 需要從互動表計算
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "data": {
                "kol_info": kol_info,
                "statistics": statistics
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting KOL detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. 數據處理優化

```python
# 添加數據緩存和優化
from functools import lru_cache
import pandas as pd

@lru_cache(maxsize=128)
def get_kol_data_cached():
    """緩存 KOL 數據，避免重複讀取 Google Sheets"""
    return sheets_client.read_sheet("同學會帳號管理")

@lru_cache(maxsize=128)
def get_post_data_cached():
    """緩存貼文數據"""
    return sheets_client.read_sheet("貼文記錄表")

def calculate_interaction_stats(member_id: str):
    """計算互動統計數據"""
    try:
        # 讀取互動數據表
        interactions_1hr = sheets_client.read_sheet("互動回饋_1hr")
        interactions_1day = sheets_client.read_sheet("互動回饋_1day")
        interactions_7days = sheets_client.read_sheet("互動回饋_7days")
        
        # 篩選該 KOL 的互動數據
        kol_interactions_1hr = [row for row in interactions_1hr[1:] if len(row) > 1 and row[1] == member_id]
        kol_interactions_1day = [row for row in interactions_1day[1:] if len(row) > 1 and row[1] == member_id]
        kol_interactions_7days = [row for row in interactions_7days[1:] if len(row) > 1 and row[1] == member_id]
        
        # 計算統計數據
        total_likes = sum(int(row[9]) for row in kol_interactions_7days if len(row) > 9 and row[9].isdigit())
        total_comments = sum(int(row[10]) for row in kol_interactions_7days if len(row) > 10 and row[10].isdigit())
        total_interactions = sum(int(row[11]) for row in kol_interactions_7days if len(row) > 11 and row[11].isdigit())
        
        return {
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_interactions": total_interactions,
            "avg_likes_per_post": total_likes / len(kol_interactions_7days) if kol_interactions_7days else 0,
            "avg_comments_per_post": total_comments / len(kol_interactions_7days) if kol_interactions_7days else 0,
            "avg_interaction_rate": total_interactions / len(kol_interactions_7days) if kol_interactions_7days else 0
        }
        
    except Exception as e:
        logger.error(f"Error calculating interaction stats: {str(e)}")
        return {
            "total_likes": 0,
            "total_comments": 0,
            "total_interactions": 0,
            "avg_likes_per_post": 0,
            "avg_comments_per_post": 0,
            "avg_interaction_rate": 0
        }
```

## 錯誤處理

### 1. 常見錯誤情況
- KOL 不存在 (404)
- Google Sheets API 錯誤 (500)
- 數據格式錯誤 (400)
- 權限不足 (403)

### 2. 錯誤響應格式
```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "success": false,
  "error": {
    "code": "KOL_NOT_FOUND",
    "message": "指定的 KOL 不存在",
    "details": "Member ID 9505546 在系統中找不到"
  }
}
```

## 性能優化

### 1. 數據緩存
- 使用 LRU 緩存減少 Google Sheets API 調用
- 設定合理的緩存過期時間
- 實現數據變更時的緩存失效

### 2. 分頁處理
- 實現分頁載入大量數據
- 使用虛擬滾動處理長列表
- 按需載入非關鍵數據

### 3. 並行處理
- 並行讀取多個 Google Sheets
- 使用異步處理提高響應速度
- 實現數據預載入

## 測試策略

### 1. 單元測試
- 測試數據解析邏輯
- 測試統計計算函數
- 測試錯誤處理機制

### 2. 集成測試
- 測試 Google Sheets API 集成
- 測試完整的 API 流程
- 測試數據一致性

### 3. 性能測試
- 測試大量數據的處理性能
- 測試並發請求的處理能力
- 測試緩存效果

## 部署考慮

### 1. 環境變數
- Google Sheets API 憑證
- 緩存配置
- 日誌級別

### 2. 監控
- API 響應時間監控
- 錯誤率監控
- Google Sheets API 使用量監控

### 3. 備份
- 定期備份 Google Sheets 數據
- 實現數據恢復機制
- 監控數據完整性
