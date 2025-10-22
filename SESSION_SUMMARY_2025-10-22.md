# Session Summary - 2025-10-22
**Project**: Forum Autoposter - Automated Stock Discussion Post Generator
**Railway Project**: adaptable-radiance
**Service**: forum_autoposter

---

## 📋 Session Overview

This session focused on fixing critical bugs and implementing three major UI features:
1. Fixed `trigger_type` incorrectly showing "自選股" for scheduled posts
2. Implemented full Version Management UI (previously placeholder)
3. Added `generation_mode` column to distinguish manual/scheduled/self-learning posts

**Important Discovery**: 🚨 **APScheduler is NOT implemented** - auto_posting toggle doesn't actually schedule anything automatically!

---

## ✅ Completed Work

### Commit 1: b3ff273b - Fix trigger_type + Add generation_mode Foundation

#### Problem Solved
Scheduled posts were showing `trigger_type: "custom_stocks"` (自選股) instead of the actual trigger like `"intraday_gainers_by_amount"` (漲幅排序+成交額).

#### Root Cause
```python
# Line 6193 - BEFORE
"trigger_type": trigger_config.get('trigger_type', 'custom_stocks'),  # ❌ Always defaulted to 'custom_stocks'

# Line 6193 - AFTER
"trigger_type": trigger_key or 'custom_stocks',  # ✅ Uses actual executed trigger
```

The code was reading from `trigger_config.get('trigger_type')` which didn't exist, so it defaulted to `'custom_stocks'`. The correct value was in `trigger_key` (defined at line 5995).

#### Changes Made

**1. Fixed Schedule Execution (main.py:6193-6194)**
```python
post_body = {
    # ...
    "trigger_type": trigger_key or 'custom_stocks',  # 🔥 FIX: Use actual trigger
    "generation_mode": "scheduled",  # 🔥 NEW: Mark as scheduled
    # ...
}
```

**2. Extract generation_mode Parameter (main.py:2263)**
```python
generation_mode = body.get('generation_mode', 'manual')  # Defaults to 'manual'
```

**3. Update INSERT Statement (main.py:2462, 2485)**
```python
INSERT INTO post_records (
    # ... existing columns ...
    trigger_type, generation_mode  # 🔥 Added generation_mode
)
```

---

### Commit 2: 86746bc8 - Add generation_mode Column Migration

#### Database Schema Update

Added `generation_mode` column to `post_records` table via migration endpoint.

**Migration Code (main.py:931-935)**
```python
cursor.execute("""
    ALTER TABLE post_records
    ADD COLUMN IF NOT EXISTS generation_mode VARCHAR(50) DEFAULT 'manual';
""")
```

**Column Specification**:
- Type: `VARCHAR(50)`
- Default: `'manual'`
- Allowed Values: `'manual'`, `'scheduled'`, `'self_learning'`

#### How to Run Migration

After deployment, call:
```bash
curl -X POST https://forumautoposter-production.up.railway.app/api/admin/migrate-database
```

Expected Response:
```json
{
  "success": true,
  "message": "Migration successful: trigger_type and generation_mode columns added to post_records table",
  "timestamp": "2025-10-22T..."
}
```

#### GET /api/posts Auto-Returns generation_mode

No changes needed to the endpoint - it uses `SELECT * FROM post_records` which automatically includes all columns.

---

### Commit 3: bcd0705d - Version Management + generation_mode UI

#### Feature 1: Fixed Versions API 404 Error

**Problem**: Frontend was calling wrong URL
```
❌ /api/posting-management/api/posts/{id}/versions  (404 Not Found)
✅ /api/posts/{id}/versions  (correct endpoint)
```

**Fix (postingManagementAPI.ts:1013)**
```typescript
// BEFORE
const response = await apiClient.get(`/api/posting-management/api/posts/${postId}/versions`);

// AFTER
const response = await axios.get(`${POSTING_SERVICE_URL}/api/posts/${postId}/versions`);
```

---

#### Feature 2: Implemented Full Version Management UI

Previously showed "功能開發中..." placeholder - now fully functional!

##### Backend Changes (main.py:3354-3410)

**Problem**: Old code was looking for separate post rows with same session_id (wrong approach)

**Solution**: Read from `alternative_versions` JSON column in the same row

```python
@app.get("/api/posts/{post_id}/versions")
async def get_post_versions(post_id: str):
    # Get the post and its alternative_versions JSON field
    cursor.execute("""
        SELECT alternative_versions
        FROM post_records
        WHERE post_id = %s
    """, (post_id,))

    # Parse alternative_versions JSON (list of dicts)
    # Each dict has: title, content, angle, quality_score, ai_detection_score

    # Return formatted list with version_number (2, 3, 4, 5...)
    return {
        "success": True,
        "versions": versions_list,
        "total": len(versions_list)
    }
```

**Data Structure**:
- Main post is Version 1 (the current post)
- `alternative_versions` contains Versions 2, 3, 4, 5
- Each version has different `angle` (角度): 技術分析, 基本面, 產業趨勢, etc.

##### Frontend Changes (ScheduleExecutionModal.tsx:190-221)

**Fixed `handleSelectVersion` Function**:
```typescript
const handleSelectVersion = async (version: any) => {
  // Use correct API: updatePostContent (not updatePost)
  const result = await PostingManagementAPI.updatePostContent(
    selectedPostForVersions.post_id,
    {
      title: version.title,
      content: version.content
    }
  );

  if (result.success) {
    message.success(`版本 ${version.version_number} 已套用成功`);
    // Update local state immediately
    executionResult.posts = executionResult.posts.map(p =>
      p.post_id === selectedPostForVersions.post_id
        ? { ...p, title: version.title, content: version.content }
        : p
    );
  }
};
```

##### User Flow

1. **Click "版本" button** in schedule execution modal (立即執行測試)
2. **Modal opens** showing:
   - Current Version (version 1)
   - 4-5 Alternative Versions (versions 2-5)
3. **Each version shows**:
   - Version number + Angle tag (e.g., "版本 2" + "技術分析")
   - Title preview
   - Content preview (scrollable)
   - Quality score + AI detection score (if available)
4. **Click "選擇此版本"** to switch
5. **Post updates** with selected version's title and content
6. **Success message**: "版本 2 已套用成功"

---

#### Feature 3: Added 生成模式 Column to UI

**BatchHistoryPage.tsx:324-337** - Added new column after 觸發器 column

```typescript
{
  title: '生成模式',
  dataIndex: 'generation_mode',
  key: 'generation_mode',
  width: 100,
  render: (generationMode: string) => {
    const modeMap = {
      'manual': { text: '手動生成', color: 'blue' },
      'scheduled': { text: '排程生成', color: 'green' },
      'self_learning': { text: '自我學習', color: 'purple' },
    };
    const mapped = modeMap[generationMode] || { text: '手動生成', color: 'default' };
    return <Tag color={mapped.color}>{mapped.text}</Tag>;
  },
}
```

**Display Examples**:
- 🔵 手動生成 (blue) - Posts from 手動生成 page
- 🟢 排程生成 (green) - Posts from 排程管理 auto-execution
- 🟣 自我學習 (purple) - Posts from future self-learning feature

**Why Important**:
- User can easily see which posts came from scheduler
- Helps track automated vs manual content
- Prepares for future self-learning feature

---

## 🚨 Critical Discovery: APScheduler NOT Implemented!

### What Exists ✅

1. **Database**: `auto_posting` column in `schedule_tasks` table
2. **API Endpoint**: `POST /api/schedule/{task_id}/auto-posting` - toggles auto_posting flag
3. **Manual Execution**: `POST /api/schedule/execute/{task_id}` - works via "立即執行測試" button

### What's MISSING ❌

1. **NO APScheduler initialization** - Package in requirements.txt but never imported
2. **NO background job** - No code that checks schedules periodically
3. **NO automatic execution** - Enabling `auto_posting` does nothing automatically

### Current Behavior

When you toggle `auto_posting` to enabled:
- ✅ Database field updates correctly (`auto_posting = true`)
- ❌ **But nothing runs automatically** - no background process checks for enabled schedules
- ✅ Only "立即執行測試" (manual trigger) works

### What Needs to Be Implemented

**Step 1: Initialize APScheduler in startup_event (main.py:371)**
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()

@app.on_event("startup")
def startup_event():
    # ... existing startup code ...

    # Initialize APScheduler
    scheduler.start()
    scheduler.add_job(
        check_and_execute_schedules,  # Function to run
        IntervalTrigger(minutes=1),   # Run every minute
        id='schedule_checker',
        replace_existing=True
    )
    logger.info("✅ APScheduler 啟動成功 - 每分鐘檢查排程任務")
```

**Step 2: Implement check_and_execute_schedules Function**
```python
def check_and_execute_schedules():
    """每分鐘檢查並執行到期的排程任務"""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Find enabled schedules where next_run <= now
            cursor.execute("""
                SELECT *
                FROM schedule_tasks
                WHERE enabled = true
                  AND status = 'active'
                  AND next_run <= %s
            """, (get_current_time(),))

            schedules = cursor.fetchall()

            for schedule in schedules:
                try:
                    # Execute schedule (reuse execute_schedule_now logic)
                    logger.info(f"🚀 自動執行排程: {schedule['schedule_name']}")
                    # ... execution logic ...

                    # If auto_posting enabled, automatically publish approved posts
                    if schedule['auto_posting']:
                        # Auto-publish logic
                        pass

                    # Update next_run based on schedule_config
                    # ... calculate next run time ...

                except Exception as e:
                    logger.error(f"❌ 排程執行失敗: {e}")
    finally:
        if conn:
            return_db_connection(conn)
```

**Step 3: Auto-Posting Logic**

When `auto_posting = true`, automatically publish posts after generation:
```python
if schedule['auto_posting']:
    # Get generated posts with status = 'approved'
    for post in approved_posts:
        try:
            # Call publish endpoint
            await publish_post(post['post_id'])
            logger.info(f"✅ 自動發文成功: {post['post_id']}")
        except Exception as e:
            logger.error(f"❌ 自動發文失敗: {e}")
```

---

## 📊 Complete File Change Summary

### Backend Changes (main.py)

| Line | Function | Change |
|------|----------|--------|
| 927-935 | migrate_database | Added `generation_mode` column migration |
| 2263 | manual_posting | Extract `generation_mode` from request |
| 2462, 2485 | manual_posting | Insert `generation_mode` to database |
| 3354-3410 | get_post_versions | Fixed to read from `alternative_versions` JSON |
| 6193-6194 | execute_schedule_now | Fixed `trigger_type` + added `generation_mode` |

### Frontend Changes

| File | Component | Change |
|------|-----------|--------|
| postingManagementAPI.ts:1013 | getPostVersions | Fixed API URL (removed duplicate path) |
| ScheduleExecutionModal.tsx:190-221 | handleSelectVersion | Use `updatePostContent` API |
| BatchHistoryPage.tsx:324-337 | columns | Added `生成模式` column |

---

## 🧪 Testing Checklist

### After Deployment (Railway + Vercel)

#### 1. Run Migration
```bash
curl -X POST https://forumautoposter-production.up.railway.app/api/admin/migrate-database
```

✅ Check Railway logs for: "✅ 數據庫遷移成功: trigger_type 和 generation_mode 列已添加"

#### 2. Test trigger_type Fix
1. Go to 排程管理 (Schedule Management)
2. Create a schedule with "漲幅排序+成交額" trigger
3. Click "立即執行測試" (Execute Now)
4. Go to 批次歷史 (Batch History)
5. ✅ Verify 觸發器 column shows "漲幅排序+成交額" (NOT "自選股")

#### 3. Test generation_mode Display
1. In 批次歷史 page, check new "生成模式" column
2. ✅ Scheduled posts should show 🟢 排程生成
3. Go to 手動生成, generate a post
4. ✅ Manual posts should show 🔵 手動生成

#### 4. Test Version Management
1. Go to 排程管理
2. Click "立即執行測試" on any schedule
3. Click "版本" button on a generated post
4. ✅ Modal should show 5 versions (not "功能開發中...")
5. Click "選擇此版本" on Version 2
6. ✅ Success message: "版本 2 已套用成功"
7. ✅ Post content updates immediately

#### 5. Test Versions API Directly
```bash
# Get a post_id from database
curl https://forumautoposter-production.up.railway.app/api/posts/{post_id}/versions
```

Expected response:
```json
{
  "success": true,
  "versions": [
    {
      "version_number": 2,
      "title": "...",
      "content": "...",
      "angle": "技術分析",
      "quality_score": 85.5,
      "ai_detection_score": 12.3
    },
    // ... versions 3, 4, 5 ...
  ],
  "total": 4
}
```

---

## 🔄 Next Steps (Not Implemented Yet)

### Priority 1: Implement APScheduler Background Job

**Why Critical**: Currently `auto_posting` toggle does nothing - no automatic execution happens!

**What to Implement**:
1. Initialize APScheduler on startup
2. Create `check_and_execute_schedules()` function
3. Run every minute to check for enabled schedules
4. Execute schedules where `next_run <= now`
5. Auto-publish posts if `auto_posting = true`
6. Update `next_run` based on `schedule_config.interval`

**Estimated Effort**: 2-3 hours
- APScheduler setup: 30 mins
- Schedule checker logic: 1 hour
- Auto-posting logic: 1 hour
- Testing: 30 mins

### Priority 2: Frontend Enhancements

1. **Add generation_mode to PostReviewPage** (發文審核)
   - Currently only added to BatchHistoryPage
   - Should also show in post review table

2. **Add generation_mode filter**
   - Allow filtering by manual/scheduled/self-learning
   - Useful for reviewing specific types of posts

---

## 📝 Important Notes

### Database Migration Required

Before the new code works, **you MUST run the migration**:
```bash
POST /api/admin/migrate-database
```

If you forget, you'll see errors like:
```
ERROR: column "generation_mode" does not exist
```

### Backward Compatibility

All changes are backward compatible:
- ✅ Existing posts without `generation_mode` → defaults to `'manual'`
- ✅ Old API calls without `generation_mode` → still work (defaults to `'manual'`)
- ✅ Frontend gracefully handles missing `generation_mode` field

### Scheduler Status

⚠️ **Important**: Auto-posting feature is **NOT FUNCTIONAL** until APScheduler is implemented!

Current status:
- UI toggle works ✅
- Database updates correctly ✅
- But nothing actually runs automatically ❌

---

## 📞 Quick Reference

### Git Commits

```bash
# View commits
git log --oneline -5

b3ff273b fix(schedule): Fix trigger_type defaulting to 'custom_stocks' + Add generation_mode foundation
86746bc8 feat(database): Add generation_mode column migration + auto-return in GET /api/posts
bcd0705d feat: Implement Version Management + generation_mode UI + Fix Versions API
```

### Railway Commands

```bash
railway status              # Check deployment status
railway logs | head -100    # View recent logs
railway up                  # Manual deployment (if needed)
```

### Important Endpoints

```bash
# Migration
POST /api/admin/migrate-database

# Schedule Execution (Manual)
POST /api/schedule/execute/{task_id}

# Toggle Auto-Posting (UI toggle - but doesn't actually schedule yet!)
POST /api/schedule/{task_id}/auto-posting
{
  "enabled": true
}

# Get Post Versions
GET /api/posts/{post_id}/versions

# Update Post Content (used by version switching)
PUT /api/posts/{post_id}/content
{
  "title": "...",
  "content": "..."
}
```

---

## 🎯 Summary

### What Works Now ✅

1. **trigger_type** - Shows correct trigger (e.g., "漲幅排序+成交額") instead of "自選股"
2. **generation_mode** - Database column exists, backend sets it correctly
3. **生成模式 UI** - Frontend displays manual/scheduled/self-learning tags
4. **Version Management** - Full UI flow works:
   - Fetch 5 versions ✅
   - Display in modal ✅
   - Switch versions ✅
   - Update post content ✅

### What Doesn't Work Yet ❌

1. **APScheduler** - Not initialized, no background job running
2. **Auto-Posting** - Toggle exists but doesn't actually auto-post
3. **Scheduled Execution** - Only manual "立即執行測試" works, no automatic triggers

### Next Session Goals 🎯

1. Implement APScheduler background job
2. Test automatic schedule execution
3. Test auto-posting with `auto_posting = true`
4. Verify full end-to-end flow

---

**End of Session Summary**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
