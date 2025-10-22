# Action Plan to 8PM - 2025/10/21

**Current Time**: 17:30
**Deadline**: 20:00
**Available Time**: 2.5 hours

---

## 🎯 Priority List (Numeric Order)

### P0 - Critical Blockers (MUST FIX)

#### 1. Add Post Approval Endpoint to unified-API (30 min)
**File**: `apps/unified-api/main.py`
**Endpoint**: `POST /api/posts/{post_id}/approve`
**Impact**: Can't approve posts for publishing
**Status**: 🔴 Not Started

#### 2. Add Post Publish Endpoint to unified-API (30 min)
**File**: `apps/unified-api/main.py`
**Endpoint**: `POST /api/posts/{post_id}/publish`
**Impact**: Can't publish posts to CMoney
**Status**: 🔴 Not Started

#### 3. Add Auto-posting Toggle Endpoint to unified-API (20 min)
**File**: `apps/unified-api/main.py`
**Endpoint**: `POST /api/schedule/{task_id}/auto-posting`
**Impact**: Can't toggle auto-posting from frontend
**Status**: 🔴 Not Started

### P1 - Important (Should Fix)

#### 4. Fix Post Edit Using Wrong API (5 min)
**File**: `apps/dashboard-frontend/.../PostReviewPage.tsx`
**Line**: 298
**Change**: Use `updatePostContent` instead of `approvePost`
**Impact**: Editing post changes status incorrectly
**Status**: 🔴 Not Started

#### 5. Add Update Post Content Endpoint to unified-API (20 min)
**File**: `apps/unified-api/main.py`
**Endpoint**: `PUT /api/posts/{post_id}/content`
**Impact**: Post edit won't work without this
**Status**: 🔴 Not Started

#### 6. Fix Timezone Datetime Error (20 min)
**File**: `apps/posting-service/schedule_service.py`
**Issue**: Mixing timezone-aware/naive datetimes
**Impact**: Schedule status API fails
**Status**: 🔴 Not Started

### P2 - Nice to Have

#### 7. Fix KOL Detail Page (30 min)
**Issue**: Frontend not making API call at all
**Root Cause**: Likely routing or component issue
**Impact**: Can't view KOL details
**Status**: 🔴 Not Started

---

## ⏱️ Time Breakdown

| Priority | Task | Est. Time | Cumulative |
|----------|------|-----------|------------|
| P0-1 | Post Approval Endpoint | 30 min | 0:30 |
| P0-2 | Post Publish Endpoint | 30 min | 1:00 |
| P0-3 | Auto-posting Endpoint | 20 min | 1:20 |
| P1-4 | Fix Post Edit (Frontend) | 5 min | 1:25 |
| P1-5 | Update Content Endpoint | 20 min | 1:45 |
| P1-6 | Fix Timezone Error | 20 min | 2:05 |
| P2-7 | KOL Detail Page | 30 min | 2:35 |

**Total Estimated**: 2:35 hours
**Buffer**: -5 minutes (tight but doable)

---

## 🚀 Execution Strategy

### Phase 1: Backend Endpoints (17:30-19:00, 1.5 hours)
1. Add `/api/posts/{id}/approve` to unified-API
2. Add `/api/posts/{id}/publish` to unified-API
3. Add `/api/posts/{id}/content` to unified-API
4. Add `/api/schedule/{task_id}/auto-posting` to unified-API
5. **Commit & Deploy** (1 commit for all endpoints)

### Phase 2: Frontend Fix (19:00-19:10, 10 min)
1. Fix post edit API call
2. **Commit & Deploy**

### Phase 3: Scheduler Fix (19:10-19:30, 20 min)
1. Fix timezone datetime error
2. **Commit & Deploy**

### Phase 4: KOL Detail (19:30-20:00, 30 min)
1. Investigate why no API call
2. Fix routing/component issue
3. **Commit & Deploy**

---

## 📋 Technical Implementation Notes

### 1. Post Approval Endpoint
```python
@app.post("/api/posts/{post_id}/approve")
async def approve_post(post_id: str, request: Request):
    body = await request.json()
    reviewer_notes = body.get('reviewer_notes')
    approved_by = body.get('approved_by', 'system')
    edited_title = body.get('edited_title')
    edited_content = body.get('edited_content')

    # Update post status to 'approved'
    # Update title/content if provided
    # Return success response
```

### 2. Post Publish Endpoint
```python
@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: str):
    # Get post from database
    # Call CMoney API to publish
    # Update status to 'published'
    # Store cmoney_post_id and url
    # Return success with article_url
```

### 3. Auto-posting Toggle Endpoint
```python
@app.post("/api/schedule/{task_id}/auto-posting")
async def toggle_auto_posting(task_id: str, request: Request):
    body = await request.json()
    enabled = body.get('enabled')

    # Update schedule_tasks.auto_posting
    # Return success response
```

### 4. Update Content Endpoint
```python
@app.put("/api/posts/{post_id}/content")
async def update_post_content(post_id: str, request: Request):
    body = await request.json()
    title = body.get('title')
    content = body.get('content')

    # Update post title and content
    # Don't change status
    # Return success response
```

### 5. Frontend Edit Fix
```typescript
// Change from:
await handleApprove(editingPost.id.toString(), title, content);

// To:
const result = await PostingManagementAPI.updatePostContent(
  editingPost.id.toString(),
  { title, content }
);
```

### 6. Timezone Fix
```python
# Ensure all datetime comparisons use timezone-aware objects
tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tz)  # Always aware
next_run = ensure_timezone_aware(next_run, tz)
time_diff = next_run - now  # Both aware
```

### 7. KOL Detail Investigation
- Check if route exists in React Router
- Check if KOLDetailPage component exists
- Check if component makes API call in useEffect
- Add missing API call if needed

---

## ✅ Success Criteria

By 20:00, all of these should work:
1. ✅ Can approve posts from review page
2. ✅ Can publish approved posts to CMoney
3. ✅ Auto-posting toggle updates immediately
4. ✅ Edit post updates content without changing status
5. ✅ Schedule status displays without errors
6. ✅ KOL detail page loads and displays data

---

## 🚨 Risk Mitigation

**If running behind schedule**:
- Skip P2-7 (KOL detail) - least critical
- P0 tasks MUST be done (core workflow)
- P1 tasks highly recommended (UX issues)

**If encounter blockers**:
- Document the issue
- Move to next task
- Come back if time permits

---

**Starting execution NOW! Will update progress as I go.**
