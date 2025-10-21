# 🧪 Testing Checklist - 5 Critical Bugfixes

**Deployment Status**: ⏳ In Progress (Commit: b841268f)
**Last Push**: Just now (~01:38 UTC)
**Railway Backend**: Deploying pytz + KOL endpoint
**Vercel Frontend**: Deploying posting_type fix + modal dropdowns

---

## 📋 Quick Summary of Fixes

| # | Bug | Fix Applied | Files Changed |
|---|-----|-------------|---------------|
| 1 | Schedule 500 Error | Added pytz>=2024.1 to requirements.txt | requirements.txt:11 |
| 2 | Posting Type Override | Added top-level posting_type parameter + TypeScript interface | PostingGenerator.tsx:581, postingManagementAPI.ts:259-262 |
| 3 | Trigger Type Wrong | Changed from triggerKey to selectedTrigger | PostingGenerator.tsx:583 |
| 4 | KOL Edit 404 | Created PUT /api/kol/{serial}/personalization endpoint | main.py:4200-4285 |
| 5 | Batch Schedule Modal | Added 13 triggers + 3 posting types, comprehensive prefill | BatchScheduleModal.tsx:404-430, 98-152 |

---

## ✅ Test 1: Posting Type Preservation (Bug #2)

**Issue**: Selected "互動發問" but got posting_type: "analysis"

### Testing Steps:

1. **Navigate to PostingGenerator**
2. **Step 1**: Select workflow (any trigger)
3. **Step 2**: Select KOL
4. **Step 7 (生成設定)**: Select **"互動發問" (interaction)**
5. **Click "批量生成"**

### Expected Results:

✅ Browser console should show: `posting_type: "interaction"`
✅ Backend should receive: `posting_type: "interaction"` (check Railway logs or response)
✅ Generated post should be SHORT question (~50 words)
✅ Content should end with "？" (question mark)

### Test All 3 Posting Types:

| Posting Type | Chinese Name | Expected max_words | Expected Content Style |
|--------------|--------------|-------------------|------------------------|
| interaction | 互動發問 | 50 | Short question with "？" |
| analysis | 發表分析 | 150 | Analytical content with data |
| personalized | 個人化內容 | 200 | KOL-branded + 4 alternative versions |

### Copy-Paste Test Script:

```bash
# Test interaction type
curl -s -X POST "https://forumautoposter-production.up.railway.app/api/manual-posting" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "2330",
    "stock_name": "台積電",
    "kol_serial": 208,
    "kol_persona": "fundamental",
    "session_id": 1761300000001,
    "trigger_type": "test_interaction_fix",
    "posting_type": "interaction",
    "max_words": 50
  }' | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('success'):
    content = d.get('content', {})
    title = content.get('title', '')
    body = content.get('content', '')
    print(f'✅ Post Created: {d.get(\"post_id\")}')
    print(f'Title ({len(title)} chars): {title}')
    print(f'Content ({len(body)} chars): {body}')
    print()
    if len(body) < 100 and '？' in (title + body):
        print('✅ PASS: Short interaction question')
    else:
        print('❌ FAIL: Content too long or not a question')
else:
    print(f'❌ Failed: {d}')
"
```

---

## ✅ Test 2: Trigger Type Correct (Bug #3)

**Issue**: Payload showed trigger_type: "individual" instead of "limit_up_after_hours"

### Testing Steps:

1. **Navigate to PostingGenerator**
2. **Step 1**: Select **"盤後漲停" (After-Hours Limit Up)** trigger
3. **Complete all steps and generate**
4. **Check browser console** for payload

### Expected Results:

✅ Payload should show: `trigger_type: "limit_up_after_hours"`
❌ Should NOT show: `trigger_type: "individual"`

### Test Script:

```bash
# Check browser console output when generating posts
# Look for line with: "Batch generation started with config:"
# Verify trigger_type field
```

---

## ✅ Test 3: KOL Edit Button Works (Bug #4)

**Issue**: PUT /api/kol/196/personalization returned 404

### Testing Steps:

1. **Navigate to KOL Management page (KOL 管理系統)**
2. **Click "編輯" (Edit)** on any KOL
3. **Go to "個人化設定" tab**
4. **Adjust probability sliders** for:
   - 內容風格機率分布 (content_style_probabilities)
   - 分析深度機率分布 (analysis_depth_probabilities)
   - 內容長度機率分布 (content_length_probabilities)
5. **Click "保存設定" (Save Settings)**

### Expected Results:

✅ Should show success message: "KOL 個人化設定更新成功"
✅ Network tab should show: `PUT /api/kol/{serial}/personalization` → 200 OK
❌ Should NOT show: 404 Not Found

### Test Script:

```bash
# Test KOL personalization endpoint directly
curl -s -X PUT "https://forumautoposter-production.up.railway.app/api/kol/208/personalization" \
  -H "Content-Type: application/json" \
  -d '{
    "content_style_probabilities": {"casual": 0.3, "professional": 0.7},
    "analysis_depth_probabilities": {"basic": 0.2, "detailed": 0.8},
    "content_length_probabilities": {"short": 0.1, "medium": 0.6, "long": 0.3}
  }' | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('success'):
    print(f'✅ SUCCESS: {d.get(\"message\")}')
else:
    print(f'❌ FAILED: {d.get(\"error\", \"Unknown error\")}')
"
```

---

## ✅ Test 4: Schedule Creation Works (Bug #1)

**Issue**: POST /api/schedule/create returned 500 Internal Server Error (missing pytz)

### Testing Steps:

1. **Navigate to Batch History page (批次歷史)**
2. **Click "加入排程" button** on any batch
3. **Configure schedule** in modal:
   - Schedule name (auto-generated)
   - Execution time (e.g., "14:30")
   - Trigger type (e.g., "盤後漲停")
   - Max stocks (e.g., 5)
4. **Click "確認創建"**

### Expected Results:

✅ Should show success message: "排程創建成功！任務 ID: {uuid}"
✅ Modal should close
✅ Network tab should show: `POST /api/schedule/create` → 200 OK
❌ Should NOT show: 500 Internal Server Error

### Test Script:

```bash
# Test schedule creation directly
curl -s -X POST "https://forumautoposter-production.up.railway.app/api/schedule/create" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_name": "測試排程_盤後漲停_五日漲幅",
    "description": "測試用排程",
    "schedule_type": "weekday_daily",
    "daily_execution_time": "14:30",
    "weekdays_only": true,
    "timezone": "Asia/Taipei",
    "enabled": true,
    "generation_config": {
      "trigger_type": "limit_up_after_hours",
      "posting_type": "analysis",
      "max_stocks": 5,
      "stock_sorting": "five_day_change_desc"
    }
  }' | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('success'):
    print(f'✅ SUCCESS: Schedule created')
    print(f'Task ID: {d.get(\"task_id\")}')
    print(f'Next Run: {d.get(\"next_run\")}')
else:
    print(f'❌ FAILED: {d.get(\"error\", \"Unknown error\")}')
"
```

---

## ✅ Test 5: Batch Schedule Modal Complete (Bug #5)

**Issue**:
- Trigger dropdown only had 6 options (should have 13)
- Posting type dropdown only had 2 options (should have 3)
- Modal didn't prefill with batch configuration

### Testing Steps:

1. **Navigate to Batch History page (批次歷史)**
2. **Click "加入排程" button** on any batch
3. **Check Trigger Type dropdown**:

### Expected Trigger Types (13 total):

**盤後 (After-Hours) - 6 types:**
- ✅ 盤後漲停 (limit_up_after_hours)
- ✅ 盤後跌停 (limit_down_after_hours)
- ✅ 盤後爆量 (volume_surge_after_hours)
- ✅ 盤後新聞 (news_hot_after_hours)
- ✅ 盤後外資買超 (foreign_buy_after_hours)
- ✅ 盤後投信買超 (institutional_buy_after_hours)

**盤中 (Intraday) - 6 types:**
- ✅ 盤中漲停 (intraday_limit_up)
- ✅ 盤中跌停 (intraday_limit_down)
- ✅ 盤中爆量 (intraday_volume_surge)
- ✅ 盤中新聞 (intraday_news_hot)
- ✅ 盤中外資買超 (intraday_foreign_buy)
- ✅ 盤中投信買超 (intraday_institutional_buy)

**其他 (Other) - 1 type:**
- ✅ 熱門話題 (trending_topics)

### Expected Posting Types (3 total):

- ✅ 互動發問 (interaction)
- ✅ 發表分析 (analysis)
- ✅ 個人化內容 (personalized)

### Prefill Verification:

4. **Check if modal prefills correctly**:
   - Schedule name should be auto-generated: e.g., "排程_盤後漲停_五日漲幅_1761300000001"
   - Trigger type should match batch's original trigger
   - Posting type should match batch's original posting_type
   - Max stocks should match batch's max_stocks_per_post

5. **Open browser console** and look for debug logs:
   ```
   🔍 批次數據分析:
     - batchData: {...}
     - originalConfig: {...}
     - defaultTriggerType: "limit_up_after_hours"
     - defaultStockSorting: "five_day_change_desc"
     - originalMaxStocks: 5
   ```

---

## 🔄 Deployment Monitoring

### Check Railway Deployment:

```bash
# Check if new deployment is live (look for timestamp AFTER push)
curl -s "https://forumautoposter-production.up.railway.app/health" | python3 -c "
import sys, json
d = json.load(sys.stdin)
ts = d.get('timestamp', '')[:19]
print(f'Current Deployment:')
print(f'  Timestamp: {ts}')
print(f'  Status: {d.get(\"status\")}')
print()
# Check if after 01:38 (when we pushed b841268f)
if ts > '2025-10-21T01:38':
    print('✅ NEW DEPLOYMENT - Commit b841268f is LIVE!')
else:
    print('⏳ Old deployment - waiting for build...')
"
```

### Check Vercel Deployment:

- Go to: https://vercel.com/dashboard
- Check if latest commit (b841268f) has finished building
- Look for "Ready" status with green checkmark

---

## 📊 Final Verification Matrix

After all tests, fill this out:

| Test | Status | Notes |
|------|--------|-------|
| ✅ Test 1: Posting Type (interaction) | ⬜ PASS / ⬜ FAIL |  |
| ✅ Test 1: Posting Type (analysis) | ⬜ PASS / ⬜ FAIL |  |
| ✅ Test 1: Posting Type (personalized) | ⬜ PASS / ⬜ FAIL |  |
| ✅ Test 2: Trigger Type Correct | ⬜ PASS / ⬜ FAIL |  |
| ✅ Test 3: KOL Edit Button | ⬜ PASS / ⬜ FAIL |  |
| ✅ Test 4: Schedule Creation | ⬜ PASS / ⬜ FAIL |  |
| ✅ Test 5: Modal has 13 triggers | ⬜ PASS / ⬜ FAIL |  |
| ✅ Test 5: Modal has 3 posting types | ⬜ PASS / ⬜ FAIL |  |
| ✅ Test 5: Modal prefills correctly | ⬜ PASS / ⬜ FAIL |  |

---

## 🚨 If Any Test Fails

1. **Check Deployment Status**: Make sure both Railway and Vercel have deployed the latest commit (b841268f)
2. **Check Browser Console**: Look for errors or unexpected payload values
3. **Check Network Tab**: Verify API calls are reaching the correct endpoints
4. **Check Railway Logs**: Look for backend errors or exceptions
5. **Report Back**: Provide specific error messages and screenshots

---

## ✅ Success Criteria

**All 5 bugs are considered FIXED when**:

1. ✅ Interaction posting type generates short questions (~50 words)
2. ✅ Trigger type shows actual trigger (e.g., "limit_up_after_hours") not "individual"
3. ✅ KOL edit button saves personalization settings without 404 error
4. ✅ Schedule creation completes without 500 error
5. ✅ Batch schedule modal shows all 13 triggers + 3 posting types + prefills correctly

---

**Generated**: 2025-10-21 01:38 UTC
**Commit**: b841268f
**Status**: Ready for Testing
