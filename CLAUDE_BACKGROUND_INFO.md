# Claude CLI Background Information
**Project**: Forum Autoposter - Automated Stock Discussion Post Generator
**Last Updated**: 2025-10-22 (Session 2)
**Railway Project**: adaptable-radiance
**Service**: forum_autoposter

---

## 📋 Latest Session Summary (2025-10-22 - Session 2)

**See detailed summary**: `SESSION_SUMMARY_2025-10-22.md`

### What We Accomplished

#### 1. ✅ Fixed trigger_type Bug (Commit: b3ff273b)
**Problem**: Scheduled posts showing "自選股" instead of actual trigger (e.g., "漲幅排序+成交額")

**Root Cause**: Line 6193 used `trigger_config.get('trigger_type', 'custom_stocks')` which defaulted to 'custom_stocks'

**Fix**: Changed to use `trigger_key` which contains the actual executed trigger

**File**: `apps/unified-api/main.py:6193`

#### 2. ✅ Added generation_mode Foundation (Commit: b3ff273b, 86746bc8)
**Purpose**: Distinguish between 手動生成, 排程生成, 自我學習

**Changes**:
- Added `generation_mode` parameter extraction (main.py:2263)
- Updated INSERT to include generation_mode (main.py:2462, 2485)
- Added database migration for generation_mode column (main.py:931-935)

**Values**: `'manual'`, `'scheduled'`, `'self_learning'`

#### 3. ✅ Fixed Versions API + Implemented Version Management (Commit: bcd0705d)
**Problem**: Versions API returned 404, and UI showed "功能開發中..."

**Fixes**:
- Fixed API URL in frontend (postingManagementAPI.ts:1013)
- Fixed backend to read from `alternative_versions` JSON column (main.py:3354-3410)
- Updated version selection logic (ScheduleExecutionModal.tsx:190-221)

**Now Works**: Users can view and switch between 5 generated versions

#### 4. ✅ Added 生成模式 Column to UI (Commit: bcd0705d)
**File**: `apps/dashboard-frontend/src/components/.../BatchHistoryPage.tsx:324-337`

**Display**:
- 🔵 手動生成 (blue) - Manual posts
- 🟢 排程生成 (green) - Scheduled posts
- 🟣 自我學習 (purple) - Self-learning posts

---

## 🚨 CRITICAL DISCOVERY: APScheduler NOT Implemented!

**Status**: ❌ auto_posting toggle does NOTHING automatically

**What Exists**:
- ✅ Database column: `auto_posting` in `schedule_tasks`
- ✅ API endpoint: `POST /api/schedule/{task_id}/auto-posting`
- ✅ Manual execution: "立即執行測試" button works

**What's Missing**:
- ❌ NO APScheduler initialization in startup
- ❌ NO background job checking schedules
- ❌ NO automatic execution

**What Needs to Be Done**:
1. Import and initialize APScheduler in `startup_event()` (main.py:371)
2. Create `check_and_execute_schedules()` function
3. Run every minute to check `next_run <= now`
4. Auto-publish posts if `auto_posting = true`

**See**: `SESSION_SUMMARY_2025-10-22.md` for implementation details

---

## 📋 Previous Session Summary (2025-10-22 - Session 1)

### What We Accomplished

#### 1. ✅ Fixed Stock Mapping Lookup Bug (Commit: 4a54474e)
**Problem**: Schedule execution failed with `"can't adapt type 'dict'"` error for stocks 2481, 6182, 2472, 5425

**Root Cause**:
- `stock_mapping` structure: `{stock_code: {company_name: str, industry: str}}`
- Code incorrectly did: `stock_name = stock_mapping.get(stock_code, stock_code)`
- This returned entire dict `{'company_name': '強茂', 'industry': '半導體業'}` instead of just `'強茂'`
- PostgreSQL couldn't insert the dict, causing psycopg2.ProgrammingError

**Fix**:
```python
# Before (main.py:5987)
stock_name = stock_mapping.get(stock_code, stock_code)

# After
stock_info = stock_mapping.get(stock_code, {})
stock_name = stock_info.get('company_name', stock_code) if isinstance(stock_info, dict) else stock_code
```

**File**: `apps/unified-api/main.py:5987`

#### 2. ✅ Added Action Buttons to Schedule Execution Modal (Commit: 158c9c25)
**Changes**:
- Added header message: "會一次回傳生成的貼文，請稍微耐心等候，謝謝！"
- Added 6 action buttons matching 發文審核頁面:
  1. 預覽 (Preview)
  2. 查看內容 (View body message)
  3. 審核 (Approve)
  4. 拒絕 (Reject)
  5. 發布 (Publish)
  6. 版本 (Versions - shows "功能開發中...")

**File**: `apps/dashboard-frontend/src/components/PostingManagement/ScheduleManagement/ScheduleExecutionModal.tsx`

#### 3. ✅ Fixed Timezone Datetime Comparison Bug (Commit: e10580a2)
**Problem**: Intraday API endpoints failed with 500 error when using "應用篩選"
```json
{
    "detail": "漲幅排序+成交額 執行失敗: 500: 認證失敗: can't compare offset-naive and offset-aware datetimes"
}
```

**Root Cause**:
- `get_current_time()` returns timezone-aware datetime (Asia/Taipei)
- `login_result.expires_at` from cmoney_client returns timezone-naive datetime
- Python cannot compare these two types

**Fix**:
```python
# Handle timezone-naive datetime from cmoney_client
if expires_at.tzinfo is None:
    taipei_tz = pytz.timezone('Asia/Taipei')
    expires_at = taipei_tz.localize(expires_at)
```

**File**: `apps/unified-api/main.py:1814-1817`

---

## 🔍 To Verify

1. **Stock Name Display**: Verify logs show `Stock: 2481 → 強茂` instead of `Stock: 2481 → {'company_name': '強茂', 'industry': '半導體業'}`
2. **Schedule Execution Modal**: Confirm header message appears and all 6 buttons are visible and functional
3. **Intraday Filters**: Test that "應用篩選" works without 500 error on all intraday triggers

---

## 🚧 Yet to Implement

1. **APScheduler Background Job** 🚨 CRITICAL
   - Initialize APScheduler on startup
   - Create background job to check schedules every minute
   - Auto-execute schedules where `next_run <= now`
   - Auto-publish posts if `auto_posting = true`
   - **Current Status**: auto_posting toggle does nothing automatically!

2. **Frontend Enhancements** (Optional)
   - Add generation_mode to PostReviewPage (發文審核)
   - Add generation_mode filter to batch history

---

## 🏗️ Project Architecture

### Repository Structure
```
/Users/williamchen/Documents/autoposter/docker-container/finlab python/
├── apps/
│   ├── unified-api/          # Main FastAPI backend (deployed to Railway)
│   │   ├── main.py           # 258KB+ monolithic API server
│   │   ├── posting-service/  # Content generation modules
│   │   └── query_db.py       # Database utilities
│   ├── dashboard-frontend/   # React frontend (Vercel)
│   │   └── src/
│   │       ├── components/
│   │       │   └── PostingManagement/
│   │       └── services/
│   └── auto-publisher/       # Legacy service
└── src/                      # Shared utilities
```

### Key Technologies
- **Backend**: FastAPI, PostgreSQL (psycopg2), FinLab API, CMoney API
- **Frontend**: React, TypeScript, Ant Design
- **Deployment**: Railway (backend), Vercel (frontend)
- **Timezone**: All operations use Asia/Taipei (GMT+8)

---

## 📁 Critical Files Reference

### Backend (apps/unified-api/)

#### `main.py` (258KB+)
**Purpose**: Monolithic FastAPI server handling all backend operations

**Key Sections**:
- **Lines 39-41**: `get_current_time()` - Returns timezone-aware datetime
- **Lines 481-484**: `stock_mapping` initialization (dict structure)
- **Lines 508-528**: `get_stock_name()`, `get_stock_industry()` helper functions
- **Lines 1805-1844**: `get_dynamic_auth_token()` - CMoney authentication with token caching
- **Lines 1942-2018**: `execute_cmoney_intraday_trigger()` - Intraday stock triggers
- **Lines 2022-2127**: Intraday API endpoints (6 endpoints)
- **Lines 2465**: Database INSERT for posts (critical error location)
- **Lines 5985-5989**: Stock name extraction (fixed bug location)

**Global Variables**:
- `stock_mapping: dict` - Stock metadata from FinLab API
- `_token_cache: dict` - CMoney API token cache with expires_at

**Database Tables**:
- `post_records` - Generated posts
- `schedule_tasks` - Scheduled posting tasks

#### `posting-service/`
Contains modules for content generation:
- `gpt_content_generator.py` - GPT-based content generation
- `personalization_module.py` - KOL personalization
- `random_content_generator.py` - Alternative version generation

### Frontend (apps/dashboard-frontend/)

#### Key Components:
- `ScheduleManagement/ScheduleManagementPage.tsx` - Schedule list and management
- `ScheduleManagement/ScheduleExecutionModal.tsx` - Execution results modal (updated)
- `PostingReview/PostingReview.tsx` - Post approval/review page (reference for buttons)
- `PostingGenerator/TriggerSelector.tsx` - Trigger configuration

---

## 🗄️ Database Schema

### `post_records` Table
```sql
Columns:
- post_id (PK)
- created_at, updated_at
- session_id
- kol_serial, kol_nickname, kol_persona
- stock_code, stock_name  ⚠️ stock_name must be STRING not dict
- title, content, content_preview
- status (draft, pending_review, approved, published, rejected)
- commodity_tags (JSON)
- generation_params (JSON)
- alternative_versions (JSON) - Stores 4 alternative versions
- trigger_type
```

### `schedule_tasks` Table
```sql
Columns:
- task_id (PK)
- schedule_name, schedule_description
- schedule_type, schedule_config (JSON)
- trigger_config (JSON)
- enabled, status
- created_at, updated_at
- next_run, last_run
```

---

## 🔑 Environment Variables

**Required**:
- `FINLAB_API_KEY` - FinLab market data API key
- `FORUM_200_EMAIL` - CMoney forum account email
- `FORUM_200_PASSWORD` - CMoney forum account password
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Server port (default: 8080)

---

## 🚨 Common Issues & Solutions

### Issue 1: "can't adapt type 'dict'"
**Symptom**: Database INSERT fails for posts
**Cause**: Passing Python dict to PostgreSQL without JSON encoding
**Solution**: Extract primitive values (str, int, float) or use `json.dumps()` for complex objects

### Issue 2: "can't compare offset-naive and offset-aware datetimes"
**Symptom**: Authentication/token comparison fails
**Cause**: Mixing timezone-aware and naive datetimes
**Solution**:
```python
if dt.tzinfo is None:
    dt = pytz.timezone('Asia/Taipei').localize(dt)
```

### Issue 3: stock_mapping returns wrong data type
**Symptom**: Expecting string but got dict
**Structure**: `{stock_code: {'company_name': str, 'industry': str}}`
**Solution**: Always use `stock_info.get('company_name', fallback)`

### Issue 4: Intraday API 500 errors
**Common Causes**:
1. CMoney token expired
2. Timezone comparison error
3. Processing filters not properly formatted
**Check**: Railway logs for authentication errors

---

## ✅ DOs and ❌ DON'Ts

### Database Operations

✅ **DO**:
- Always use timezone-aware datetimes with `get_current_time()`
- Extract primitive values from dicts before INSERT
- Use `json.dumps()` for storing complex objects
- Read files before editing with Edit tool

❌ **DON'T**:
- Never pass Python dicts directly to PostgreSQL (use json.dumps)
- Never compare timezone-naive and timezone-aware datetimes
- Never commit without testing locally first
- Never modify Railway environment variables without backup

### Code Modifications

✅ **DO**:
- Use `get_stock_name(stock_code)` helper function
- Check if `stock_mapping` is loaded before accessing
- Handle both timezone-aware and naive datetimes
- Use Read tool before Edit tool
- Commit with descriptive messages

❌ **DON'T**:
- Don't directly access `stock_mapping[code]` - use `.get()` with fallback
- Don't assume datetime objects have timezone info
- Don't edit main.py without reading the section first (file is 258KB+)
- Don't push to main without testing

### Frontend Development

✅ **DO**:
- Import PostingManagementAPI for all API calls
- Use Ant Design components consistently
- Handle loading and error states
- Display user feedback with message.success/error

❌ **DON'T**:
- Don't make direct fetch() calls - use API service
- Don't ignore TypeScript type errors
- Don't hardcode API URLs - use environment variables

### Railway Deployment

✅ **DO**:
- Use `railway up` for manual deployment
- Check `railway logs` after deployment
- Verify deployment timestamp matches commit time
- Test critical paths after deployment

❌ **DON'T**:
- Don't force push to main branch
- Don't deploy during peak hours without warning
- Don't modify database schema without migration plan
- Don't skip testing schedule execution after deployment

---

## 🔄 Deployment Workflow

### Backend (Railway)

1. **Auto-deploy** (GitHub integration):
   ```bash
   git add .
   git commit -m "Description"
   git push origin main
   # Railway auto-detects and deploys
   ```

2. **Manual deploy**:
   ```bash
   railway up
   # Wait for deployment
   railway logs | head -100
   ```

3. **Verify deployment**:
   ```bash
   railway status
   # Check main.py file size in logs (should be ~258KB)
   ```

### Frontend (Vercel)
- Auto-deploys on push to main branch
- Check Vercel dashboard for deployment status

---

## 🧪 Testing Checklist

After each deployment, verify:

1. **Health Check**: `GET /health` returns 200
2. **Stock Mapping**: Check logs show correct stock names (strings, not dicts)
3. **Schedule Execution**: "立即執行測試" completes without errors
4. **Intraday Triggers**: All 6 endpoints work with filters
5. **Post Actions**: Approve, Reject, Publish buttons functional
6. **Database Inserts**: No "can't adapt type" errors in logs

---

## 📊 API Endpoints Reference

### Intraday Triggers (6 endpoints)
1. `GET /api/intraday/gainers-by-amount` - 漲幅排序+成交額
2. `GET /api/intraday/volume-leaders` - 成交量排序
3. `GET /api/intraday/amount-leaders` - 成交額排序
4. `GET /api/intraday/limit-down` - 跌停篩選
5. `GET /api/intraday/limit-up` - 漲停篩選
6. `GET /api/intraday/limit-down-by-amount` - 跌停篩選+成交額

### Post Management
- `GET /api/posts` - Get posts with filters
- `POST /api/posts/{post_id}/approve` - Approve post
- `POST /api/posts/{post_id}/reject` - Reject post
- `POST /api/posts/{post_id}/publish` - Publish to CMoney

### Schedule Management
- `GET /api/schedule/tasks` - List schedules
- `POST /api/schedule/execute/{task_id}` - Execute schedule immediately
- `POST /api/schedule/create` - Create new schedule

---

## 🐛 Debugging Tips

### Check Railway Logs
```bash
railway logs | grep "ERROR"
railway logs | grep "Stock:"
railway logs | grep "手動貼文失敗"
```

### Common Log Patterns

**Success**:
```
INFO:main:📊 Stock: 2481 → 強茂
INFO:main:✅ 排程執行完成: 成功=4, 失敗=0
```

**Failure**:
```
ERROR:main:❌ 手動貼文失敗: ProgrammingError: can't adapt type 'dict'
INFO:main:📊 Stock: 2481 → {'company_name': '強茂', 'industry': '半導體業'}
```

### Database Queries
```python
# apps/unified-api/query_db.py
SELECT * FROM post_records WHERE stock_code = '2481' ORDER BY created_at DESC LIMIT 10;
SELECT * FROM schedule_tasks WHERE enabled = true;
```

---

## 📝 File Modification Guidelines

### Before Editing main.py:
1. **Read first**: File is 258KB+, always use Read tool to check current state
2. **Find exact location**: Use Grep to find the exact line numbers
3. **Small changes**: Edit only the specific section needed
4. **Test locally**: If possible, test before pushing

### Before Editing Frontend Components:
1. **Check imports**: Ensure all required modules are imported
2. **Type safety**: Fix any TypeScript errors
3. **Consistent styling**: Match existing Ant Design patterns
4. **Handle states**: Loading, error, success states

---

## 🔐 Security Notes

- **Never commit** `.env` files or credentials
- **Token caching**: CMoney tokens are cached for performance
- **Database**: Use parameterized queries (psycopg2 handles this)
- **CORS**: Frontend allowed via environment variable

---

## 📞 Quick Reference

### Railway CLI Commands
```bash
railway status              # Check deployment status
railway logs                # View logs
railway up                  # Manual deployment
railway variables           # List env variables
railway link               # Link to project
```

### Git Workflow
```bash
git add <files>
git commit -m "Description with 🤖 Generated with Claude Code"
git push origin main
```

### Important File Paths
```
Backend:  /Users/williamchen/Documents/autoposter/docker-container/finlab python/apps/unified-api/
Frontend: /Users/williamchen/Documents/autoposter/docker-container/finlab python/apps/dashboard-frontend/
```

---

## 🎯 Next Session Checklist

When continuing work:
1. Check Railway deployment status
2. Read READY_FOR_TESTING.md for context
3. Review recent commits (`git log -5`)
4. Verify any pending bug fixes
5. Check this file for project knowledge

---

**End of Background Information**
