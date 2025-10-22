# Testing Checklist - Quick Reference

## ✅ What We Built Today

1. **APScheduler Infrastructure** - Runs every minute to check for due schedules ✅
2. **Schedule Creation** - Create schedules from Batch History ✅
3. **Schedule Management Display** - Fixed "n/a" issues ✅
4. **Alternative Versions** - All posting types generate 4 alternatives ✅
5. **KOL Management** - Serial extraction, DELETE, confirmation modals ✅

**Deployment Status:** ✅ **LIVE ON RAILWAY**

---

## 🧪 Testing Checklist (In Order)

### ☐ Phase 1: Schedule Creation (MOST CRITICAL)

#### ☐ 1.1 Open Batch Schedule Modal
- [ ] Go to Batch History page
- [ ] Click "加入排程" on any batch
- [ ] Modal opens without errors
- [ ] Trigger type shows real value (not "n/a")
- [ ] Stock settings show real value (not "n/a")
- [ ] KOL assignment shows strategy (not "208")

#### ☐ 1.2 Create Schedule
- [ ] Fill schedule name: "測試排程 1"
- [ ] Set time: "14:30"
- [ ] Check "僅工作日執行"
- [ ] Click "確認創建"
- [ ] Success message appears
- [ ] NO 500 error

#### ☐ 1.3 Verify in Schedule Management
- [ ] Navigate to Schedule Management page
- [ ] Find "測試排程 1" in the list
- [ ] 觸發器類型: Shows trigger (not "n/a")
- [ ] 股票設定: Shows "5檔" or similar (not "n/a")
- [ ] KOL分配: Shows "隨機分配" (not "n/a")
- [ ] 下次執行: Shows "2025-10-21 14:30:00"
- [ ] 狀態: Shows "active"

**If all ✅ → Phase 1 COMPLETE!**

---

### ☐ Phase 2: Alternative Versions

#### ☐ 2.1 API Test
Run in terminal:
```bash
curl -X POST "https://forumautoposter-production.up.railway.app/api/manual-posting" \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "2330", "stock_name": "台積電", "kol_serial": 208, "posting_type": "personalized", "max_words": 200}'
```

Check response:
- [ ] Has `alternative_versions` field
- [ ] Array has 4 items
- [ ] Each has: version_type, angle, title, content

---

### ☐ Phase 3: KOL Management

#### ☐ 3.1 Create KOL with Email Serial Extraction
- [ ] Go to KOL Management page
- [ ] Click "創建角色"
- [ ] Email: `forum_300@cmoney.com.tw`
- [ ] Password: `test123`
- [ ] Nickname: `測試 KOL 300`
- [ ] Click "創建角色"
- [ ] Confirmation modal appears
- [ ] Click "確認創建"
- [ ] KOL created with serial = 300 (extracted from email)

#### ☐ 3.2 Delete KOL
- [ ] Find KOL 300 in list
- [ ] Click red "刪除" button
- [ ] Confirm deletion
- [ ] KOL removed from list

#### ☐ 3.3 Personalization Save Modal
- [ ] Click "編輯" on any KOL
- [ ] Go to "個人化設定" tab
- [ ] Adjust probability sliders
- [ ] Click "保存設定"
- [ ] SUCCESS modal pops up (not just toast)
- [ ] Shows KOL nickname and serial

---

### ☐ Phase 4: Posting Type Override

#### ☐ 4.1 Check Duplicate Selector Removed
- [ ] Go to PostingGenerator
- [ ] Step 7: NO posting_type selector
- [ ] Step 9: HAS posting_type selector with 3 options

#### ☐ 4.2 Verify Posting Type Preserved
- [ ] In Step 9, select "互動發問"
- [ ] Generate post
- [ ] Open DevTools → Network tab
- [ ] Find `/api/generate-posts` call
- [ ] Payload shows: `posting_type: "interaction"` (not "analysis")

---

### ☐ Phase 5: Trending Topics

#### ☐ 5.1 Fetch Trending Topics
- [ ] Go to PostingGenerator
- [ ] Click "獲取熱門話題"
- [ ] Success message appears
- [ ] Topics display
- [ ] NO purple "點擊選擇" tag
- [ ] NO "熱度" or category tags
- [ ] "全選" button appears

#### ☐ 5.2 Select All
- [ ] Click "全選" button
- [ ] All topics selected
- [ ] Success message: "已全選 X 個話題"

---

### ☐ Phase 6: Batch History Timestamps

#### ☐ 6.1 Check Timestamps
- [ ] Go to Batch History page
- [ ] 創建時間 shows Taipei time (GMT+8)
- [ ] NOT 8 hours behind
- [ ] Newest batches appear first

---

## 🚨 Report Format

When reporting to Claude in new session:

**If SUCCESS:**
```
Phase 1: ✅ PASS
- Schedule created successfully
- Appears in Schedule Management
- All fields display correctly (no "n/a")
```

**If FAILURE:**
```
Phase 1: ❌ FAIL
- Step: Creating schedule
- Error: 500 Internal Server Error
- Details: [paste error message]
- Screenshot: [if available]
```

---

## 🔗 Quick Links

- Railway Backend: https://forumautoposter-production.up.railway.app
- Health Check: https://forumautoposter-production.up.railway.app/health
- Session Summary: `SESSION_SUMMARY_2025-10-21.md` (detailed info)

---

## 💡 Expected Issues

1. **Schedule execution doesn't generate posts** → ✅ EXPECTED
   - Reason: Batch generation logic not implemented yet (TODO)
   - Status: Phase 3 work (after Phase 1 testing passes)

2. **Vercel frontend not deployed** → Wait for deployment
   - Check: https://vercel.com/dashboard

3. **"n/a" still appears** → Report to Claude
   - May need additional JSON parsing

---

## 🎯 Success Criteria

**Minimum to proceed:**
- ✅ Phase 1 complete (schedule creation works)
- ✅ Phase 2 complete (alternative versions work)

**Nice to have:**
- ✅ Phase 3-6 complete (all features working)

---

**Start with Phase 1! Good luck! 🚀**
