# Schedule Management Bug Fix Session - 2025-10-22

## Session Overview
Fixed critical bugs in schedule creation and execution system for the autoposter forum project. Issues included incomplete configuration storage, API response parsing, and trigger execution logic.

---

## Issues Identified & Fixed

### ✅ Issue #1: Field Name Mismatch in API Response Mapping
**Problem:** Frontend receiving `generation_config` from API but reading `generation_params`

**Root Cause:**
- Backend renamed field: `generation_params` → `generation_config`
- Frontend (postingManagementAPI.ts:656) still reading old field name
- Result: `undefined` → empty object `{}`

**Fix:**
- **File:** `apps/dashboard-frontend/src/services/postingManagementAPI.ts`
- **Line:** 656, 660
- **Change:** Read `post.generation_config` instead of `post.generation_params`

**Commit:** `5aa8bcee` - "Fix field name mismatch: use generation_config instead of generation_params"

---

### ✅ Issue #2: SelfLearningPage Sending Incomplete Payload
**Problem:** Schedule creation from SelfLearningPage missing `trigger_config` and `schedule_config`

**Root Cause:**
- SelfLearningPage built complete `scheduleConfig` object
- But only sent minimal fields to `/api/schedule/create` (lines 1761-1773)
- Missing: `trigger_config`, `schedule_config`, `generation_config`
- Backend used fallback logic, creating incomplete config

**Fix:**
- **File:** `apps/dashboard-frontend/src/pages/SelfLearningPage.tsx`
- **Lines:** 1751-1770, 1777-1762
- **Changes:**
  1. Added `trigger_config` to scheduleConfig object
  2. Added `schedule_config` to scheduleConfig object
  3. Changed API request to send complete `scheduleConfig` object instead of cherry-picking fields

**Commit:** `89e5dcf1` - "Fix schedule creation: SelfLearningPage now sends complete config"

---

### ✅ Issue #3: GET /api/schedule/tasks Returns NULL for JSONB Fields
**Problem:** API response showed `null` for all config fields even though database had complete data

**Root Cause:**
- Database columns are **JSONB type** (not TEXT)
- PostgreSQL `psycopg2` with `RealDictCursor` returns JSONB as **Python dict** (already parsed)
- Code tried `json.loads(dict_object)` → threw `TypeError`
- Exception caught → field set to `None`
- Result: API returned `null` for `trigger_config`, `schedule_config`, `generation_config`, `batch_info`

**Fix:**
- **File:** `apps/unified-api/main.py`
- **Lines:** 5143-5165
- **Logic:**
  ```python
  if isinstance(field_value, dict):
      continue  # Already parsed by psycopg2
  elif isinstance(field_value, str):
      task_dict[field] = json.loads(field_value)  # Parse if string
  ```

**Commit:** `25378f04` - "Fix GET /api/schedule/tasks: Handle JSONB fields correctly"

---

### ✅ Issue #4: Trigger Type Column Shows "N/A"
**Problem:** New schedules showed "N/A" for trigger type while old ones showed "盤後漲停"

**Root Cause:**
- Frontend reading `trigger_config.trigger_type` (old structure)
- New schedules use `trigger_config.triggerKey`

**Fix:**
- **File:** `apps/dashboard-frontend/src/components/PostingManagement/ScheduleManagement/ScheduleManagementPage.tsx`
- **Line:** 707
- **Change:** Check both locations:
  ```typescript
  const triggerType = triggerConfig?.triggerKey ||
                      triggerConfig?.trigger_type ||
                      record.trigger_config?.triggerKey ||
                      record.trigger_config?.trigger_type ||
                      'N/A';
  ```

**Commit:** `2d8c2cf5` - "Fix trigger type display: Support new trigger_config.triggerKey"

---

### ✅ Issue #5: "立即執行測試" Button Fails
**Problem:** Execute button failed with error "排程未配置股票列表"

**Root Cause:**
- Execute endpoint expected pre-configured `stock_codes` list
- New schedules use **trigger logic** (`triggerKey` + `filters`) instead
- Schedules need to execute trigger to fetch stocks dynamically

**Fix:**
- **File:** `apps/unified-api/main.py`
- **Lines:** 5797-5830
- **Logic:**
  1. Check for `triggerKey` in addition to `stock_codes`
  2. If `triggerKey` exists, execute trigger function (e.g., `get_after_hours_limit_up_stocks()`)
  3. Apply `max_stocks` limit to results
  4. Support both old format (stock_codes) and new format (triggerKey)

**Example execution flow:**
```python
if trigger_key == 'limit_up_after_hours':
    trigger_result = await get_after_hours_limit_up_stocks(
        limit=1000,
        changeThreshold=9.5,
        industries=""
    )
    if 'stocks' in trigger_result:
        stock_codes = [stock['stock_id'] for stock in trigger_result['stocks']]
        stock_codes = stock_codes[:max_stocks]  # Apply limit
```

**Commit:** `2d8c2cf5` - (Same commit as Issue #4)

---

## Backend Variable Scope Errors (Fixed During Session)

### Error 1: json.dumps() Before Import
**Problem:** Used `json.dumps()` before `import json` statement

**Fix:** Changed to `str()` instead

**Commit:** `2126a11c` - "Hotfix: Remove json.dumps() before import"

---

### Error 2: daily_execution_time Scope Issue
**Problem:** Variable defined inside `if` block but used outside

**Fix:** Moved definition before all conditional blocks (line 5542)

**Commit:** `13aa2e83` - "Fix variable scope: define daily_execution_time before conditional blocks"

---

## Files Modified

### Frontend
1. **postingManagementAPI.ts**
   - Fixed field name: `generation_params` → `generation_config`
   - Added debug logging

2. **BatchScheduleModal.tsx**
   - Added debug logging for `fullTriggersConfig` tracking

3. **BatchHistoryPage.tsx**
   - Added debug logging for API request payload

4. **SelfLearningPage.tsx**
   - Added `trigger_config` to scheduleConfig
   - Added `schedule_config` to scheduleConfig
   - Send complete config object to API

5. **ScheduleManagementPage.tsx**
   - Support both `triggerKey` and `trigger_type` field names

6. **ScheduleExecutionModal.tsx** (NEW)
   - Modal component to display schedule execution results
   - Shows generated posts, success/failure counts, errors

### Backend
1. **main.py**
   - Fixed JSONB field parsing in `get_schedule_tasks` endpoint
   - Fixed `create_schedule` to use frontend-sent configs
   - Added trigger execution logic to `execute_schedule_now` endpoint
   - Fixed variable scope issues
   - Added comprehensive debug logging

---

## All Commits (In Order)

1. `b239f17b` - Add detailed logging for generation_params parsing in get_posts
2. `1d472ca1` - Debug: Add logging to verify full_triggers_config in API request
3. `b61a56bc` - Fix: Add debug logging for full_triggers_config and fix execute schedule
4. `5aa8bcee` - Fix field name mismatch: use generation_config instead of generation_params
5. `496dfcfd` - Implement schedule execution logic with post generation
6. `bab919f8` - Add schedule execution modal for testing schedule results
7. `68d946b2` - Add enhanced debug logging for fullTriggersConfig tracking
8. `176ebe50` - Fix create_schedule to use frontend trigger_config and schedule_config
9. `2126a11c` - Hotfix: Remove json.dumps() before import
10. `13aa2e83` - Fix variable scope: define daily_execution_time before conditional blocks
11. `fd948d10` - Add debug logging to track trigger_config and schedule_config from frontend
12. `89e5dcf1` - Fix schedule creation: SelfLearningPage now sends complete config
13. `25378f04` - Fix GET /api/schedule/tasks: Handle JSONB fields correctly
14. `2d8c2cf5` - Fix trigger type display: Support new trigger_config.triggerKey

**Latest Commit:** `2d8c2cf5` (Pushed to GitHub main)

---

## Deployment Status

### Auto-Deployment in Progress
- ✅ **GitHub:** All commits pushed to main branch
- 🚀 **Railway:** Backend auto-deploying (2-3 minutes)
- 🚀 **Vercel:** Frontend auto-deploying (1-2 minutes)

### Services
- **Backend:** Railway - `https://forumautoposter-production.up.railway.app`
- **Frontend:** Vercel - (dashboard-frontend)
- **Database:** PostgreSQL on Railway

---

## Testing Checklist

### ✅ Already Verified
- [x] Database correctly stores complete `trigger_config` with all filters
- [x] Database correctly stores complete `schedule_config` with `full_triggers_config`
- [x] Direct PostgreSQL query shows complete data
- [x] Code changes compile without errors
- [x] All commits pushed successfully

### 🔄 Needs Testing (After Deployment)

#### Test 1: API Response Contains Complete Data
**Action:** Refresh 排程管理頁面

**Expected Result:**
- GET `/api/schedule/tasks` returns all schedules
- `trigger_config` field has complete filter data (not `null`)
- `schedule_config` field has `full_triggers_config` (not `null`)
- `generation_config` field has all parameters (not `null`)
- `batch_info` field has stock codes and KOL names (not `null`)

**Check in Browser DevTools:**
```javascript
// Response should look like:
{
  "trigger_config": {
    "filters": {
      "priceFilter": {...},
      "sectorFilter": {...},
      "volumeFilter": {...}
    },
    "triggerKey": "limit_up_after_hours",
    "threshold": 20
  },
  "schedule_config": {
    "full_triggers_config": {...complete config...}
  }
}
```

---

#### Test 2: Trigger Type Column Display
**Action:** Look at the "觸發器類型" column in the schedule table

**Expected Result:**
- Old schedules (ID: `f7ac8036`, `e5e1a6a9`): Show "盤後漲停" ✅ (already working)
- New schedules (ID: `8b103f5f`, `5d668891`, `90396b36`): Show "盤後漲停" (instead of "N/A")

**Current Status:** BEFORE fix shows "N/A" → AFTER fix should show "盤後漲停"

---

#### Test 3: Schedule Creation from Batch History
**Action:**
1. Go to "批次歷史" page
2. Click "加入排程" on any batch
3. Fill in schedule details
4. Click "確認加入排程"

**Expected Result:**
- Success message: "排程創建成功"
- New schedule appears in 排程管理
- All config fields populated (not N/A)
- Database contains complete `trigger_config` and `schedule_config`

---

#### Test 4: Schedule Creation from Self Learning
**Action:**
1. Go to Self Learning page
2. Click "創建排程" on any feature
3. Fill in schedule details
4. Click confirm

**Expected Result:**
- Success message: "排程創建成功"
- New schedule appears in 排程管理
- `trigger_config` includes filters and trigger logic (not just basic fields)
- `schedule_config` includes generation settings

---

#### Test 5: Execute Test Button - Critical Test
**Action:**
1. Go to 排程管理頁面
2. Find a schedule with trigger type "盤後漲停" (limit_up_after_hours)
3. Click "立即執行測試" button

**Expected Behavior:**
1. Modal opens with loading spinner
2. Backend logs show (check Railway logs):
   ```
   🎯 執行觸發器: limit_up_after_hours
   ✅ 觸發器返回 X 檔股票
   📊 最終選定 20 檔股票: [...]
   ```
3. Posts are generated
4. Modal shows results:
   - Success count (e.g., "已生成 20 篇")
   - Failed count (if any)
   - List of generated posts with preview buttons
   - Each post shows: stock code, KOL, title, content preview

**Previous Error (Should NOT Happen):**
```json
{"success": false, "error": "排程未配置股票列表"}
```

**What Should Happen:**
- Trigger executes → fetches stocks → generates posts → shows results

---

#### Test 6: Generated Post Preview
**Action:** In the execution result modal, click "預覽" on any generated post

**Expected Result:**
- Post preview modal opens
- Shows complete post details:
  - Stock code
  - KOL serial number
  - Title
  - Full content

---

#### Test 7: Posts Appear in Review Page
**Action:**
1. After executing a schedule (Test 5)
2. Go to "發文審核" page
3. Look for posts with the session_id from execution

**Expected Result:**
- Generated posts appear in review queue
- Each post marked as "pending" or "ready for review"
- All posts have unique post_id
- No duplicate posts (session_id prevents duplicates)

---

## Known Limitations / Future Improvements

### 1. Limited Trigger Types
**Current Support:** Only `limit_up_after_hours` trigger is implemented

**Missing Triggers:**
- `limit_down_after_hours`
- `intraday_limit_up`
- `volume_leaders`
- `price_breakout`
- etc.

**Next Step:** Add support for other trigger types in `execute_schedule_now` endpoint

---

### 2. Filter Application Not Yet Implemented
**Current Behavior:** Trigger fetches stocks, but filters from `trigger_config.filters` are not applied

**Example Filters Not Yet Used:**
- `priceFilter` (min/max price)
- `sectorFilter` (include/exclude sectors)
- `volumeFilter` (volume threshold)
- `marketCapFilter` (market cap threshold)
- `technicalFilter` (RSI, MACD, Bollinger)

**Next Step:** Apply filters to trigger results before generating posts

---

### 3. Stock Sorting Not Implemented
**Current Behavior:** Uses stocks in order returned by trigger

**Missing:** Sort by `trigger_config.stock_sorting`:
- `five_day_change_desc` (5-day price change descending)
- `volume_desc` (volume descending)
- `price_asc` (price ascending)
- etc.

**Next Step:** Apply sorting logic before selecting top N stocks

---

### 4. KOL Assignment Strategy
**Current:** Uses hardcoded list `[200, 201, 202]` and random assignment

**Next Step:**
- Get KOL list from database
- Support different assignment strategies:
  - `random`: Random assignment
  - `round_robin`: Rotate through KOLs
  - `specific`: Use specific KOL list from config

---

### 5. Scheduled Execution (Background)
**Current:** Only manual "立即執行測試" works

**Missing:** Automatic background execution based on `next_run` time

**Next Step:**
- Implement scheduler daemon/cron job
- Monitor `schedule_tasks` table
- Execute schedules when `next_run` time is reached
- Update `last_run`, `run_count`, `success_count`

---

## Data Structure Reference

### trigger_config (New Structure)
```json
{
  "triggerType": "individual",
  "triggerKey": "limit_up_after_hours",
  "stockFilter": "limit_up_stocks",
  "threshold": 20,
  "max_stocks": 20,
  "filters": {
    "priceFilter": {
      "type": "above",
      "minPrice": 50,
      "maxPrice": 1000
    },
    "sectorFilter": {
      "exclude": false,
      "sectors": ["半導體", "電子", "金融"]
    },
    "volumeFilter": {
      "type": "high",
      "threshold": 50000000,
      "percentile": 70
    },
    "marketCapFilter": {
      "type": "large",
      "threshold": 10000000000
    },
    "technicalFilter": {
      "rsi": {"enabled": false, "min": 30, "max": 70},
      "macd": {"enabled": false, "bullish": true},
      "bollinger": {"enabled": false, "breakout": true}
    }
  }
}
```

### trigger_config (Old Structure - Still Supported)
```json
{
  "trigger_type": "limit_up_after_hours",
  "stock_codes": [],
  "kol_assignment": "random",
  "max_stocks": 1,
  "stock_sorting": "five_day_change_desc"
}
```

### schedule_config
```json
{
  "enabled": true,
  "posting_time_slots": ["23:37"],
  "timezone": "Asia/Taipei",
  "weekdays_only": true,
  "posting_type": "analysis",
  "content_style": "chart_analysis",
  "content_length": "medium",
  "max_words": 1000,
  "full_triggers_config": {
    // Complete trigger configuration including all filters
  }
}
```

---

## Debugging Tips

### Check Backend Logs
```bash
railway logs --service forum_autoposter | grep "執行排程\|觸發器\|選定"
```

### Check Database Directly
```sql
-- Connect to Railway PostgreSQL
SELECT
  schedule_id,
  schedule_name,
  trigger_config::jsonb->'triggerKey' as trigger_key,
  trigger_config::jsonb->'filters' as filters,
  schedule_config::jsonb->'full_triggers_config' as full_config
FROM schedule_tasks
WHERE created_at > '2025-10-22'
ORDER BY created_at DESC;
```

### Check API Response
```javascript
// In browser console on 排程管理頁面
fetch('https://forumautoposter-production.up.railway.app/api/schedule/tasks')
  .then(r => r.json())
  .then(d => console.log(JSON.stringify(d.tasks[0], null, 2)))
```

---

## Contact Information

**Project:** Forum Autoposter
**Session Date:** 2025-10-22
**Environment:** Railway (Backend) + Vercel (Frontend) + PostgreSQL
**Repository:** https://github.com/hihihowru/forum_autoposter

---

## Quick Reference Commands

### Frontend Development
```bash
cd /Users/williamchen/Documents/autoposter/docker-container/finlab\ python/apps/dashboard-frontend
npm run dev  # Local development
```

### Backend Development
```bash
cd /Users/williamchen/Documents/autoposter/docker-container/finlab\ python/apps/unified-api
python3 main.py  # Local development
```

### Check Deployments
```bash
railway status  # Backend status
railway logs    # Backend logs
```

### Git Operations
```bash
git status
git add .
git commit -m "message"
git push
```

---

## Session End Notes

All critical bugs have been fixed and code has been deployed. The main functionality should now work end-to-end:

1. ✅ Create schedules from Batch History with complete configuration
2. ✅ Create schedules from Self Learning with complete configuration
3. ✅ API returns complete JSONB data to frontend
4. ✅ Trigger type displays correctly in table
5. ✅ Execute test button fetches stocks via trigger and generates posts

Please test all scenarios in the Testing Checklist after deployments complete (~5 minutes).

If any issues arise, check:
1. Railway logs for backend errors
2. Browser console for frontend errors
3. Database directly to verify data storage
4. API responses to verify data retrieval
