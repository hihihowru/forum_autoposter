# Reaction Logs - Verification System

## Summary

Every reaction attempt is now logged to the database so you can verify if reactions are working!

## What's New

### 1. Database Logging ✅
- **Table**: `reaction_logs`
- **Auto-cleanup**: Logs older than 2 days are automatically deleted
- **Data saved**:
  - Article ID
  - KOL serial & nickname
  - Success/failure status
  - HTTP status code
  - Error messages (if failed)
  - Response time in milliseconds
  - Timestamp

### 2. API Endpoint for Railway UI ✅
**Endpoint**: `GET /api/reaction-bot/logs`

**Query parameters**:
- `limit` - Max logs to return (default 100, max 1000)
- `success_only` - Filter: `true` (successes only), `false` (failures only), or omit (all)
- `kol_serial` - Filter by specific KOL
- `article_id` - Filter by specific article

**Example requests**:
```bash
# Get latest 100 logs
curl https://forumautoposter-production.up.railway.app/api/reaction-bot/logs

# Get only successful reactions
curl https://forumautoposter-production.up.railway.app/api/reaction-bot/logs?success_only=true

# Get failures only
curl https://forumautoposter-production.up.railway.app/api/reaction-bot/logs?success_only=false&limit=50

# Get logs for specific KOL
curl https://forumautoposter-production.up.railway.app/api/reaction-bot/logs?kol_serial=1000

# Get logs for specific article
curl https://forumautoposter-production.up.railway.app/api/reaction-bot/logs?article_id=174912268
```

**Response format**:
```json
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
  "count": 100,
  "stats_24h": {
    "total_attempts": 500,
    "successful": 498,
    "success_rate": 99.6,
    "avg_response_time_ms": 125.3
  }
}
```

## How It Works

### When Local Cronjob Runs:
1. **Fetch articles** from CMoney Kafka
2. **For each article**:
   - Attempt to like it
   - **Log to database** (success or failure)
   - Record response time
3. **Save hourly summary** stats
4. **Auto-cleanup** logs older than 2 days

### Log Entry Example:
```
Article: 174912268
KOL: 威廉本尊 (serial=1000)
Status: ✅ Success
HTTP: 204 No Content
Response time: 133ms
Time: 2025-11-14 09:13:02
```

## Verifying Reactions Work

### Method 1: Check Railway UI Logs Page
Once the frontend is built, you'll see a logs table with:
- Recent reactions
- Success/failure indicators
- Which KOL liked which article
- Error messages for failures
- 24-hour success rate stats

### Method 2: Direct API Call
```bash
# Quick check - see latest 10 reactions
curl "https://forumautoposter-production.up.railway.app/api/reaction-bot/logs?limit=10" | json_pp

# Check if any failures in last 100 attempts
curl "https://forumautoposter-production.up.railway.app/api/reaction-bot/logs?success_only=false" | json_pp
```

### Method 3: Database Query
```sql
-- See latest 20 logs
SELECT
    attempted_at,
    kol_nickname,
    article_id,
    success,
    response_time_ms,
    error_message
FROM reaction_logs
ORDER BY attempted_at DESC
LIMIT 20;

-- Success rate in last 24 hours
SELECT
    COUNT(*) as total,
    COUNT(CASE WHEN success THEN 1 END) as successful,
    ROUND(COUNT(CASE WHEN success THEN 1 END)::numeric / COUNT(*) * 100, 2) as success_rate
FROM reaction_logs
WHERE attempted_at >= NOW() - INTERVAL '24 hours';
```

## Auto-Cleanup

Logs are automatically deleted after **2 days** to save database space.

This happens after each hourly task completes:
```
🧹 [Cleanup] Deleted 150 old reaction logs (>2 days)
```

## Files Modified

1. **`migrations/create_reaction_logs.sql`** - Created table schema
2. **`hourly_reaction_service.py`** - Added logging to `_log_reaction_to_db()` method
3. **`reaction_bot_routes.py`** - Added `GET /logs` endpoint

## Testing

To test the logging system:

1. **Enable the bot** in Railway UI (`enabled=true`)
2. **Wait for cronjob** to run (every hour at minute 0)
3. **Check logs API**:
   ```bash
   curl https://forumautoposter-production.up.railway.app/api/reaction-bot/logs
   ```
4. **Verify** you see:
   - Article IDs that were liked
   - KOL nicknames used
   - Success status
   - Response times

## Benefits

✅ **Verify reactions work** - See exactly what's happening
✅ **Debug failures** - Error messages for failed attempts
✅ **Monitor performance** - Response times, success rates
✅ **Audit trail** - Know which KOL liked which article
✅ **Automatic cleanup** - No manual maintenance needed

## Next Steps

When you're ready to use this:
1. Turn on the bot via Railway UI
2. Wait for the next hourly cronjob (runs every hour at :00)
3. Check the logs API to verify reactions are working
4. Build a UI page to display these logs in a nice table

The system is ready! Just waiting for you to enable it.
