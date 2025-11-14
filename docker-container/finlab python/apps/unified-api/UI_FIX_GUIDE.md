# 互動管理頁面 - Fix Guide

## Current Problems & Solutions

### ✅ What WORKS (No changes needed):

1. **`GET /api/reaction-bot/config`** - Get/update settings ✅
2. **`GET /api/reaction-bot/hourly-stats/summary?hours=24`** - Get article stats from DB ✅
3. **`GET /api/reaction-bot/logs?limit=100`** - Get reaction logs ✅
4. **CORS** - Already configured, no issues ✅

### ❌ What's BROKEN:

1. **`GET /api/reaction-bot/stats?days=7`** - Returns 500 error
   - **Why**: Tries to query CMoney directly (no VPN on Railway)
   - **Fix**: UI should use `/hourly-stats/summary` instead

### 🔧 Required UI Changes:

## 1. Article Stats Section (文章數據統計)

**Current (broken)**:
```typescript
// ❌ Don't use this
GET /api/reaction-bot/stats?days=7
```

**Use instead**:
```typescript
// ✅ Use this
GET /api/reaction-bot/hourly-stats/summary?hours=168  // 7 days = 168 hours
```

**Response format**:
```json
{
  "success": true,
  "summary": {
    "hours_analyzed": 168,
    "total_hours_with_data": 150,
    "total_new_articles": 15000,        // Show this!
    "total_like_attempts": 14500,
    "total_successful_likes": 14200,
    "total_unique_articles_liked": 14200,
    "average_success_rate": 97.93,
    "earliest_hour": "2025-11-07T00:00:00",
    "latest_hour": "2025-11-14T09:00:00",
    "articles_per_hour": 100,           // Show this!
    "likes_per_hour": 94.67
  }
}
```

**Display mapping**:
```
過去 1 小時   → GET /hourly-stats/summary?hours=1
過去 2 小時   → GET /hourly-stats/summary?hours=2
過去 3 小時   → GET /hourly-stats/summary?hours=3
過去 6 小時   → GET /hourly-stats/summary?hours=6
過去 12 小時  → GET /hourly-stats/summary?hours=12
過去 24 小時  → GET /hourly-stats/summary?hours=24
```

Show: `summary.total_new_articles` for each time period.

## 2. Settings Panel (機器人配置)

**Already works!** Just needs proper error handling:

```typescript
// Get current config
GET /api/reaction-bot/config

// Update config
PATCH /api/reaction-bot/config
{
  "enabled": true,              // ON/OFF switch
  "reaction_percentage": 100,   // 反應倍數 (100 = 100%)
  "selected_kol_serials": [1000, 200],  // KOL選擇 (empty = all)
  "min_delay_seconds": 0.5,
  "max_delay_seconds": 2.0,
  "max_reactions_per_kol_per_hour": 100
}
```

## 3. Activity Logs (活動日誌)

**Already works!** Use the new `/logs` endpoint:

```typescript
GET /api/reaction-bot/logs?limit=50&success_only=true

Response:
{
  "logs": [
    {
      "id": 123,
      "article_id": "174912268",
      "kol_serial": 1000,
      "kol_nickname": "威廉本尊",
      "reaction_type": 1,
      "success": true,
      "http_status_code": 204,
      "error_message": null,
      "attempted_at": "2025-11-14T09:13:02",
      "response_time_ms": 133
    }
  ],
  "count": 50,
  "stats_24h": {
    "total_attempts": 500,
    "successful": 498,
    "success_rate": 99.6,
    "avg_response_time_ms": 125.3
  }
}
```

**Table columns**:
- 文章 ID: `article_id`
- KOL: `kol_nickname` (serial=`kol_serial`)
- 反應類型: `reaction_type` (1=讚, 2=噓, etc.)
- 狀態: `success ? "✅成功" : "❌失敗"`
- 時間: `attempted_at`
- 回應時間: `response_time_ms` ms
- 錯誤: `error_message` (if failed)

## 4. Remove Unnecessary Sections

These don't make sense for local cronjob architecture:

- ❌ **批次執行記錄** - Not needed (cronjob runs automatically)
- ❌ **測試分佈** button - Not needed
- ❌ **刷新** for article stats - Data updates every hour automatically

## 5. Add Bot Status Indicator

Show if the bot is actually running:

```typescript
GET /api/reaction-bot/config

{
  "enabled": true,  // Show: "✅ 機器人已啟用" or "⏸️ 機器人已停用"
  ...
}

GET /api/reaction-bot/hourly-stats/summary?hours=1

{
  "summary": {
    "latest_hour": "2025-11-14T09:00:00",  // Show: "最後執行: 14:00"
    ...
  }
}
```

## Summary of API Endpoints to Use

| Feature | Endpoint | Status |
|---------|----------|--------|
| Get settings | `GET /api/reaction-bot/config` | ✅ Works |
| Update settings | `PATCH /api/reaction-bot/config` | ✅ Works |
| Article stats | `GET /api/reaction-bot/hourly-stats/summary?hours=X` | ✅ Works |
| Reaction logs | `GET /api/reaction-bot/logs?limit=50` | ✅ Works |
| ~~Old stats~~ | ~~`GET /api/reaction-bot/stats?days=7`~~ | ❌ Don't use |

## Example Frontend Code

```typescript
// Article Stats Component
const fetchArticleStats = async (hours: number) => {
  const res = await fetch(
    `${POSTING_SERVICE_URL}/api/reaction-bot/hourly-stats/summary?hours=${hours}`
  );
  const data = await res.json();

  if (data.success) {
    return data.summary.total_new_articles || 0;
  }
  return 0;
};

// Activity Logs Component
const fetchActivityLogs = async () => {
  const res = await fetch(
    `${POSTING_SERVICE_URL}/api/reaction-bot/logs?limit=50`
  );
  const data = await res.json();

  return {
    logs: data.logs || [],
    stats: data.stats_24h || {}
  };
};

// Settings Component
const updateSettings = async (settings) => {
  const res = await fetch(
    `${POSTING_SERVICE_URL}/api/reaction-bot/config`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    }
  );
  return await res.json();
};
```

## What Data is Available

Because your local Mac fetches data every hour and saves to PostgreSQL:

✅ **Available from DB**:
- Hourly article counts (how many articles found each hour)
- Reaction attempts & success rates
- Which articles were liked
- Which KOLs were used
- Error logs for failures
- Response times

❌ **NOT available** (Railway can't access CMoney):
- Real-time article counts from CMoney
- Live article content
- Direct CMoney queries

But you have everything you need in the database!

## Next Steps

1. Update frontend to use `/hourly-stats/summary` instead of `/stats`
2. Add activity logs table using `/logs` endpoint
3. Remove "批次執行記錄" section
4. Add bot status indicator (enabled/disabled + last run time)
5. Test with real data after enabling the bot

All the backend APIs work! Just need frontend changes.
