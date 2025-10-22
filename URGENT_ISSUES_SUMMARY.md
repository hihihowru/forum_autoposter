# Urgent Issues Summary - 2025/10/21 17:30

## 🔴 Critical Blocking Issues (Must Fix to Use System)

### 1. Missing `/api/schedule/{task_id}/auto-posting` in unified-API
**Status**: Identified
**Impact**: Cannot toggle auto-posting from frontend
**Root Cause**:
- Frontend calls: `forumautoposter-production.up.railway.app/api/schedule/{task_id}/auto-posting`
- This URL points to unified-API
- But the endpoint only exists in posting-service
- unified-API needs to add this endpoint OR proxy to posting-service

**OPTIONS Request**: ✅ 200 (CORS works)
**POST Request**: ❌ 404 (Endpoint doesn't exist)

**Solution Options**:
A. Add `/auto-posting` endpoint to unified-API
B. Configure unified-API to proxy `/api/schedule/*` to posting-service
C. Change frontend to call posting-service directly for schedule APIs

**Recommended**: Option A - Add endpoint to unified-API for consistency

---

### 2. Missing Post Management Endpoints in unified-API
**Status**: Identified
**Impact**: Cannot approve or publish posts
**Root Cause**:
- Frontend calls: `/api/posts/{id}/approve` → 404
- Frontend calls: `/api/posts/{id}/publish` → 404
- These endpoints exist in posting-service but not unified-API

**Solution**: Same as Issue #1 - need to add or proxy these endpoints

---

### 3. Timezone Datetime Error in Schedule Status
**Status**: Identified, Not Yet Fixed
**Impact**: Schedule status API fails
**Error**: `"can't subtract offset-naive and offset-aware datetimes"`

**Root Cause**: Mixing timezone-aware and timezone-naive datetimes in subtraction
**Location**: Likely in status calculation when computing time differences

**Solution**: Ensure all datetimes are timezone-aware before subtraction:
```python
# Bad
time_diff = next_run - datetime.now()  # May mix aware/naive

# Good
tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tz)  # Timezone-aware
time_diff = next_run - now  # Both aware
```

---

## ⚠️ Important Issues (Affects UX)

### 4. Post Edit Using Wrong API
**Status**: Fix Ready
**Impact**: Editing a post changes its status to "approved"
**Expected**: Edit should only update content, not change status

**Current Code** (PostReviewPage.tsx:298):
```typescript
await handleApprove(editingPost.id.toString(), title, content);
```

**Should Be**:
```typescript
const result = await PostingManagementAPI.updatePostContent(
  editingPost.id.toString(),
  { title, content }
);
```

**Fix Complexity**: Easy - 5 minutes

---

### 5. KOL Detail Page Infinite Loading
**Status**: Not Yet Investigated
**Impact**: Cannot view KOL details
**Symptoms**: Shows "載入 KOL 詳情中..." forever

**Need to Check**:
- Does `/api/kol/{id}` endpoint exist?
- What error appears in Network tab?
- Does the API return correct data structure?

---

## 📋 Architecture Issue: Service Separation

**Current Setup**:
- **unified-API** (forumautoposter-production.up.railway.app):
  - Has SOME schedule endpoints (`/api/schedule/tasks`, `/api/schedule/create`)
  - Missing post management endpoints (`/approve`, `/publish`)
  - Missing auto-posting endpoint

- **posting-service**:
  - Has ALL endpoints
  - But frontend doesn't call it directly

**Problem**: Inconsistent - some features work, others don't

**Solutions**:

### Option A: Make unified-API Complete (Recommended)
**Pros**:
- Frontend has single endpoint
- Simpler deployment
- Better for Vercel proxy setup

**Cons**:
- Need to add missing endpoints to unified-API
- Some code duplication

**Steps**:
1. Add `/api/schedule/{task_id}/auto-posting` to unified-API
2. Add `/api/posts/{id}/approve` to unified-API
3. Add `/api/posts/{id}/publish` to unified-API
4. Add `/api/posts/{id}/content` to unified-API (for edit)

### Option B: Proxy to posting-service
**Pros**:
- No code duplication
- posting-service has all features

**Cons**:
- More complex routing
- Potential performance overhead
- Need to configure proxy correctly

---

## 🎯 Immediate Action Plan

### For You (User):
1. **Clarify Architecture Decision**:
   - Do you want unified-API to have all endpoints? (Option A)
   - Or proxy certain routes to posting-service? (Option B)

2. **Test Current Deployment**:
   - Verify the 6 fixes from earlier are working
   - Confirm which issues are most critical for your workflow

### For Me (Assistant):
1. **Fix Post Edit API** (5 min) - Easy win
2. **Add Missing Endpoints** based on your architecture decision
3. **Fix Timezone Error** once I find exact location
4. **Investigate KOL Detail Loading**

---

## ⏱️ Time Estimates

| Issue | Priority | Complexity | Time |
|-------|----------|------------|------|
| Post Edit API | P1 | Easy | 5 min |
| Add auto-posting endpoint | P0 | Medium | 30 min |
| Add approve/publish endpoints | P0 | Medium | 30 min |
| Fix timezone error | P1 | Easy-Medium | 15-30 min |
| KOL detail loading | P2 | Unknown | 15-60 min |

**Total Estimated**: 1.5 - 2.5 hours

---

## 📊 Current Status

**Working**:
- ✅ Schedule creation
- ✅ Schedule listing
- ✅ Trigger type display
- ✅ Auto-posting toggle (backend works, frontend shows wrong state)
- ✅ KOL list
- ✅ Post generation

**Broken**:
- ❌ Auto-posting toggle (404 from frontend)
- ❌ Post approval (404)
- ❌ Post publishing (404)
- ❌ Post editing (wrong API call)
- ❌ Schedule status (timezone error)
- ❌ KOL detail page

---

## 🚀 Next Steps

**Please answer**:
1. Which architecture approach do you prefer? (A or B)
2. Which 2-3 issues are most critical for you right now?
3. Can you share the Network tab error for KOL detail page?

Once you clarify, I can fix the critical issues within 1-2 hours!
