# Forum AutoPoster - Feature Verification Checklist

**Date**: 2025-10-21
**Railway Deployment**: 2025-10-20T23:14:52
**Commits to Verify**:
- 9916d70d: KOL serial extraction from email
- 6d1107a5: KOL DELETE endpoint + button
- 0fd360ab: Trending topics UI improvements

---

## 🔥 PRIORITY 1: Features You Haven't Reported Back On

### ✅ Feature 1: Alternative Versions Generation (From Previous Session)
**Status**: ⏳ **PENDING YOUR VERIFICATION**

**What to Test**:
All 3 posting types should generate 4 alternative versions with different angles.

**Test Steps**:
1. Go to PostingGenerator page
2. Create a post with:
   - posting_type: `interaction` (max_words: 50)
   - posting_type: `analysis` (max_words: 150)
   - posting_type: `personalized` (max_words: 200)
3. Check database or API for each post's `alternative_versions` field

**Expected Results**:
- ✅ Each post should have 4 alternative versions in JSON array
- ✅ Each version has: `title`, `content`, `angle`, `version_type`
- ✅ Interaction versions: Short questions (30-50 chars)
- ✅ Analysis versions: Long analytical content (150+ chars)
- ✅ Personalized versions: KOL-branded analysis with persona

**Session IDs Used in Testing** (you can retrieve these):
- Interaction: `1761270000001`
- Analysis: `1761270000002`
- Personalized: `1761270000003`

**API Check**:
```bash
curl "https://forumautoposter-production.up.railway.app/api/posts?session_id=1761270000001&limit=1"
curl "https://forumautoposter-production.up.railway.app/api/posts?session_id=1761270000002&limit=1"
curl "https://forumautoposter-production.up.railway.app/api/posts?session_id=1761270000003&limit=1"
```

**Verification**: Look at the `alternative_versions` field in each response.

---

## 🆕 PRIORITY 2: Today's New Features (Need Testing)

### ✅ Feature 2: KOL Serial Extraction from Email
**Commit**: 9916d70d
**Status**: ⏳ **NEEDS TESTING**

**What Changed**:
- KOL serial is now extracted from email instead of auto-increment
- Email format: `forum_XXX@cmoney.com.tw` → serial becomes `XXX`

**Test Steps**:
1. Navigate to KOL Management page
2. Click "創建KOL角色" button
3. Fill in email: `forum_300@cmoney.com.tw`
4. Fill in password, nickname, member_id
5. Click "創建 KOL"

**Expected Results**:
- ✅ KOL should be created with serial = `300` (not auto-increment)
- ✅ If email format is wrong (e.g., `test@gmail.com`), should show error message
- ✅ If serial 300 already exists, should show "Serial already exists" error

**Validation**:
- Frontend: Email input should show tooltip with format requirement
- Backend: Should reject invalid email formats

---

### ✅ Feature 3: KOL Delete Functionality
**Commit**: 6d1107a5
**Status**: ⏳ **NEEDS TESTING**

**What Changed**:
- Added DELETE button next to Edit button in KOL table
- Red danger button with confirmation dialog

**Test Steps**:
1. Navigate to KOL Management page
2. Find a test KOL in the table (NOT a production KOL!)
3. Click the red "刪除" button
4. Read confirmation dialog (should show KOL nickname and serial)
5. Click "確定刪除"

**Expected Results**:
- ✅ Confirmation dialog appears with KOL details
- ✅ After confirming, KOL is removed from the table
- ✅ Success message shows: "KOL 刪除成功 (Serial: X, Nickname: Y)"
- ✅ Table refreshes automatically

**BE CAREFUL**: Test with a dummy KOL, not production data!

**Backend Endpoint Test** (manual API call):
```bash
# First, create a test KOL
curl -X POST "https://forumautoposter-production.up.railway.app/api/kol/create" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "forum_999@cmoney.com.tw",
    "password": "test123",
    "nickname": "測試刪除用",
    "member_id": "999999"
  }'

# Then delete it
curl -X DELETE "https://forumautoposter-production.up.railway.app/api/kol/999"
```

**Expected Response**:
```json
{
  "success": true,
  "message": "KOL 刪除成功 (Serial: 999, Nickname: 測試刪除用)",
  "deleted_kol": {
    "serial": "999",
    "nickname": "測試刪除用"
  }
}
```

---

### ✅ Feature 4: Trending Topics UI Improvements
**Commit**: 0fd360ab
**Status**: ⏳ **NEEDS TESTING**

**What Changed**:
1. Removed duplicate "點擊選擇" purple tag
2. Removed mock data tags ("熱度", "市場熱議")
3. Added "全選" (Select All) button

**Test Steps**:

#### A. Remove Duplicate Button Test
1. Navigate to PostingGenerator page
2. Click "獲取熱門話題" button
3. **Verify**: Each topic card should have ONLY ONE blue "選擇" button at bottom right
4. **Verify**: No purple "📝 點擊選擇" tag should appear

#### B. Remove Mock Data Test
1. Look at the topic cards
2. **Verify**: No "熱度: X%" tag
3. **Verify**: No category tag (e.g., "市場熱議")
4. **Only visible tags should be**:
   - "純話題" (orange) - for topics without stocks
   - "✅ 已選擇" (green) - when selected
   - "📊 生成 X 篇貼文" (cyan) - post count

#### C. Select All Button Test
1. After fetching trending topics, look at top right control area
2. **Verify**: Blue "全選" button appears next to "清空選擇"
3. Click "全選" button
4. **Expected**:
   - All topics should be selected (blue border, ✅ tag)
   - Success message: "已全選 X 個話題"
   - Post count should update (e.g., "將生成 15 篇貼文")
5. Click "清空選擇"
6. **Expected**: All selections cleared

#### D. Batch Generation Logic Test
**Scenario 1**: 2 topics, one with 0 stocks, one with 5 stocks
- Topic 1 (純話題, no stocks): 1 post
- Topic 2 (5 stock tags): 1 + 5 = 6 posts
- **Total**: 7 posts

**Scenario 2**: 3 topics, all with stocks
- Topic 1 (2 stocks): 1 + 2 = 3 posts
- Topic 2 (3 stocks): 1 + 3 = 4 posts
- Topic 3 (1 stock): 1 + 1 = 2 posts
- **Total**: 9 posts

**Verify**: The post count estimate matches this logic

---

## 📋 OPTIONAL: Additional Checks

### ✅ Feature 5: KOL Prompt Fields AI Prefill ⚠️ **NOT IMPLEMENTED**
**Status**: 🟡 **INVESTIGATION COMPLETE**

**User Report**: "kol 人設、流派、 prompt 人設等欄位都沒有 fill. not sure openai model are implemented here"

**Investigation Findings**:
1. ✅ Frontend HAS form fields (prompt_persona, prompt_style, prompt_guardrails, prompt_skeleton)
2. ✅ Frontend HAS default values (added in commit 9c7bcdbe)
3. ❌ Frontend DOES NOT send these fields to backend in payload
4. ❌ Backend DOES NOT accept or store these fields
5. ❌ Database probably doesn't have columns for these fields

**Issue**: When user fills in prompt fields, they are **lost** when creating KOL.

**Detailed Report**: See `KOL_AI_PREFILL_INVESTIGATION.md`

**User's Expected Behavior**:
- User provides ai_description
- System uses LLM to auto-generate prompt fields
- User can review and modify before final submission

**Current Behavior**:
- User manually fills prompt fields
- Fields are lost (not sent to backend)
- Database doesn't store them

**Recommended Fix** (Phase 1 - Basic):
1. Add database columns for prompt fields
2. Frontend: Include prompt fields in API payload
3. Backend: Accept and store prompt fields

**Enhancement** (Phase 2 - AI):
4. Backend: Call OpenAI to generate prompt fields from ai_description
5. Frontend: Display AI-generated values for review

**Decision Required**: Implement now or defer to post-scheduling?

**You can skip this** for now - needs database migration and backend changes.

---

## 🎯 Summary Verification Matrix

| Feature | Priority | Status | Testing Required |
|---------|----------|--------|------------------|
| **Alternative Versions** | 🔥 HIGH | Previous session | ⏳ PENDING YOUR REPORT |
| **KOL Serial Extraction** | 🔥 HIGH | Deployed (9916d70d) | ⏳ NEEDS TESTING |
| **KOL Delete Button** | 🔥 HIGH | Deployed (6d1107a5) | ⏳ NEEDS TESTING |
| **Trending Topics UI** | 🔥 HIGH | Deployed (0fd360ab) | ⏳ NEEDS TESTING |
| **KOL Creation Button** | 🔥 HIGH | Deployed (33be8599) | ⏳ NEEDS TESTING |
| **Trending Topics Summary** | 🔥 HIGH | Deployed (33be8599) | ⏳ NEEDS TESTING |
| **Posting Type Handler** | 🔥 HIGH | Deployed (e34aec20) | ⏳ NEEDS TESTING |
| **KOL Prompt AI Prefill** | 🟡 MEDIUM | NOT IMPLEMENTED | 🟡 OPTIONAL (needs DB migration) |

---

## 🚀 Quick Test Script (Copy-Paste Ready)

### Test 1: Alternative Versions (From Previous Session)
```bash
# Check if alternative versions exist for the 3 test posts
curl -s "https://forumautoposter-production.up.railway.app/api/posts?session_id=1761270000001&limit=1" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('posts'):
    p = d['posts'][0]
    alt = json.loads(p.get('alternative_versions', '[]'))
    print(f'✅ Interaction post has {len(alt)} alternative versions')
else:
    print('❌ Post not found')
"

curl -s "https://forumautoposter-production.up.railway.app/api/posts?session_id=1761270000002&limit=1" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('posts'):
    p = d['posts'][0]
    alt = json.loads(p.get('alternative_versions', '[]'))
    print(f'✅ Analysis post has {len(alt)} alternative versions')
else:
    print('❌ Post not found')
"

curl -s "https://forumautoposter-production.up.railway.app/api/posts?session_id=1761270000003&limit=1" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('posts'):
    p = d['posts'][0]
    alt = json.loads(p.get('alternative_versions', '[]'))
    print(f'✅ Personalized post has {len(alt)} alternative versions')
else:
    print('❌ Post not found')
"
```

### Test 2: KOL DELETE Endpoint
```bash
# Test DELETE endpoint with a dummy KOL (serial 999)
curl -X DELETE "https://forumautoposter-production.up.railway.app/api/kol/999" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('success'):
    print(f'✅ DELETE works: {d.get(\"message\")}')
else:
    print(f'Expected behavior: {d.get(\"error\")}')
"
```

---

## 📝 What to Report Back

After testing, please report:

1. **Alternative Versions** (from previous session):
   - [ ] Confirmed all 3 posting types generate 4 alternative versions
   - [ ] Quality is good (different angles, appropriate lengths)
   - [ ] OR: Issues found (describe)

2. **KOL Serial Extraction**:
   - [ ] Email validation works (rejects invalid formats)
   - [ ] Serial extraction works (e.g., forum_300@cmoney.com.tw → serial 300)
   - [ ] Duplicate serial check works
   - [ ] OR: Issues found (describe)

3. **KOL Delete**:
   - [ ] Delete button appears in table
   - [ ] Confirmation dialog shows correct info
   - [ ] Deletion works, table refreshes
   - [ ] OR: Issues found (describe)

4. **Trending Topics UI**:
   - [ ] No duplicate buttons (only blue "選擇")
   - [ ] No mock data tags (熱度, 市場熱議)
   - [ ] "全選" button works
   - [ ] Post count calculation is correct
   - [ ] OR: Issues found (describe)

---

**Generated**: 2025-10-21
**Railway**: https://forumautoposter-production.up.railway.app
**Vercel**: (your frontend URL)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
