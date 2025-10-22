# Development Backlog
**Created**: 2025-10-22
**Status**: In Progress

---

## 🎯 HIGH PRIORITY TASKS

### 0. 🚨 FIX: Generic Default Prompt - Poor Content Quality
**Status**: ❌ Critical Bug
**Category**: Content Quality / Prompt Engineering
**Priority**: **CRITICAL**

**Problem Identified**: Generated posts are too generic and lack specific data

**Example Post Analysis** (茂矽 2342):

**Title**: "茂矽（2342）漲停背後的風險與機會：長期投資者需謹慎"

**Content Issues**:
```
❌ TOO GENERIC - NO SPECIFIC DATA:
- "全球經濟正面臨多重挑戰" - Generic macro trends
- "美國的強勁經濟數據" - Not relevant to 茂矽
- "CPI數據顯示通膨依然頑固" - Macro analysis only
- Could apply to ANY semiconductor stock

❌ MISSING CRITICAL DATA:
- No OHLC data (open, high, low, close prices)
- No technical indicators (RSI, MA5, MA20, volume)
- No fundamental data (P/E ratio, EPS, revenue)
- No recent news about 茂矽 specifically
- No explanation for WHY it hit 漲停 (limit-up)

❌ WRONG TONE:
- Title mentions "機會" but content focuses on risks
- Overly cautious: "長期投資者需謹慎"
- Discouraging: "不要被目前的漲停情況沖昏頭腦"
- Should be more balanced analysis

❌ NO TRIGGER CONTEXT:
- Title says "漲停" but doesn't explain why
- No mention of what triggered this post
- No specific event or news catalyst

❌ STRUCTURE ISSUES:
- Only "總經分析" section
- Missing: 技術分析, 基本面分析, 新聞分析, 結論
```

**Root Cause**:
Current default prompt is using a **fallback generic template** that:
1. Doesn't inject actual fetched data (OHLC, news, technical indicators)
2. Falls back to safe macro-economic analysis
3. Doesn't use Serper API results (if available)
4. Doesn't use trigger context (limit-up, trending topics, etc.)
5. No validation to reject overly generic content

**What Should Happen Instead**:

For 茂矽（2342）漲停 post, content should include:
```
✅ SPECIFIC DATA:
- "今日茂矽開盤價 XX，最高 XX，收盤漲停於 XX 元"
- "成交量放大至 X 張，較昨日增加 X%"
- "RSI 指標來到 XX，MA5 突破 MA20 形成黃金交叉"

✅ COMPANY-SPECIFIC NEWS:
- "根據最新消息，茂矽獲得 XX 大廠訂單..."
- "法人預估 Q4 營收可望成長 X%..."
- "外資連續 X 日買超，累積買超 X 張"

✅ TECHNICAL ANALYSIS:
- 具體技術指標數據
- K線型態分析
- 成交量分析

✅ FUNDAMENTAL ANALYSIS:
- 本益比、EPS、營收年增率
- 產業地位與競爭優勢
- 財務數據

✅ TRIGGER CONTEXT:
- 為何今日漲停？(訂單、財報、產業趨勢)
- 觸發器條件說明
```

**Action Items**:

1. **Audit Current Default Prompt**:
   - [ ] Locate current default prompt in codebase
   - [ ] Identify why data injection is failing
   - [ ] Check if Serper API results are being used

2. **Fix Prompt to Enforce Data Inclusion**:
   - [ ] REQUIRE OHLC data in output: "今日開盤 {open}，收盤 {close}"
   - [ ] REQUIRE technical indicators: "RSI: {rsi}, MA5: {ma5}"
   - [ ] REQUIRE news context: Use {serper_api_results} if available
   - [ ] REQUIRE trigger context: Explain why this stock was selected
   - [ ] REQUIRE fundamental data: P/E ratio, EPS, revenue

3. **Add Structured Output Format**:
   ```
   【技術分析】
   - 價格: 開盤 XX, 收盤 XX, 漲幅 X%
   - 技術指標: RSI XX, MA5 XX, MA20 XX
   - 成交量: XX 張 (增加/減少 X%)

   【基本面分析】
   - 本益比: XX, EPS: XX
   - 產業地位: ...
   - 財務狀況: ...

   【新聞分析】
   - [從 Serper API 結果提取]
   - 重要新聞: ...
   - 市場影響: ...

   【觸發原因】
   - 為何今日漲停/入選: ...
   - 觸發器條件: ...

   【投資建議】
   - 短期: ...
   - 長期: ...
   - 風險提示: ...
   ```

4. **Add Content Quality Validation**:
   - [ ] Reject posts that don't include OHLC data
   - [ ] Reject posts that only have macro analysis
   - [ ] Require at least 3 specific data points about the company
   - [ ] Check if stock code appears multiple times in content
   - [ ] Validate that content is different for each stock (not templated)

5. **Test with Multiple Scenarios**:
   - [ ] Limit-up stock (漲停)
   - [ ] Trending topic stock
   - [ ] Intraday gainer stock
   - [ ] Custom stock list
   - Ensure each uses appropriate trigger context

**Expected Outcome**:
- Posts contain specific, actionable data
- Each stock gets unique, relevant analysis
- Content uses all available data sources (OHLC, news, technical, fundamental)
- Posts explain WHY the stock was selected (trigger context)
- Balanced tone with both opportunities and risks

**Estimated Time**: 3-4 hours
- Audit current prompt: 30 mins
- Redesign prompt with data enforcement: 1.5 hours
- Add structured output format: 1 hour
- Add validation: 1 hour
- Testing: 30 mins

---

### 1. ✅ Trending Topic Trigger - Verification
**Status**: ⚠️ Needs Testing
**Category**: Core Functionality

**Description**: Ensure trending topic trigger works end-to-end

**Acceptance Criteria**:
- [ ] Can select "熱門話題" trigger when creating schedule
- [ ] Schedule executes and fetches trending topics
- [ ] Extracts stock codes from trending topics
- [ ] Generates posts for extracted stocks
- [ ] Posts contain relevant trending topic context

**API Endpoint**: `/api/trending` (already implemented)
**Execution Endpoint**: `/api/schedule/execute/{task_id}` (already supports trending_topics)

**Test Steps**:
```
1. Go to 排程管理
2. Create new schedule
3. Select "熱門話題" as trigger
4. Click "立即執行測試"
5. Verify posts generated with trending context
```

---

### 2. ❌ News Link Toggle Feature (步驟四)
**Status**: Not Implemented
**Category**: Content Enhancement
**Priority**: High

**Description**: 開啟和關閉新聞連結功能可以成功

This is a module that controls whether to add news links in the final post content. The toggle should be in Step 4 (新聞連結設定).

**Requirements**:
- [ ] Add "啟用新聞連結" toggle in Step 4 UI
- [ ] Toggle state saved to `schedule_config.news_links_enabled` (boolean)
- [ ] When enabled: Post generation includes news links
- [ ] When disabled: Post generation excludes news links
- [ ] Toggle state persists across page refresh

**Implementation Notes**:
- Add field to `schedule_tasks` table: `news_links_enabled BOOLEAN DEFAULT false`
- Update post generation logic to check this flag
- Pass flag to ChatGPT prompt (include/exclude news links section)

**Related Fields** (already exist):
- `news_enabled` - Whether to fetch news at all
- `news_links_enabled` - **NEW** - Whether to include links in final post

---

### 3. ❌ News Configuration Persistence (步驟四)
**Status**: Not Implemented
**Category**: Configuration
**Priority**: High

**Description**: 新聞時間範圍、搜尋關鍵字設定可以儲存並紀錄進去 config

**Requirements**:
- [ ] Save "新聞時間範圍" (news time range) to `schedule_config`
- [ ] Save "搜尋關鍵字" (search keywords) to `schedule_config`
- [ ] Load saved values when editing schedule
- [ ] Use saved values during post generation

**Database Schema Change**:
```sql
ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS news_time_range VARCHAR(50); -- e.g., "24h", "7d", "30d"
ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS news_search_keywords TEXT; -- JSON array of keywords
```

**Example `schedule_config` structure**:
```json
{
  "news_enabled": true,
  "news_links_enabled": true,
  "news_time_range": "24h",
  "news_search_keywords": ["財報", "營收", "擴廠"]
}
```

---

### 4. 🔄 Remove Duplicate UI Block (步驟七 vs 步驟九)
**Status**: UI Refactoring Needed
**Category**: UI/UX
**Priority**: Medium

**Description**: 步驟七和步驟九有一個類似的區塊，都是在做類似的事情

**Current Situation**:
- **步驟七**: 貼文模式
  - 一對一模式: 一篇貼文專注分析一檔股票
  - 一對多模式: 一篇貼文分析多檔股票

- **步驟九**: 生成策略
  - 1 KOL → 1 股票
  - 1 KOL → 所有股票
  - 混合模式

**Decision**: These are the same concept - KEEP 步驟九, REMOVE 步驟七

**Action Items**:
- [ ] Remove 步驟七 UI block entirely
- [ ] Keep 步驟九 "生成策略" block
- [ ] Ensure database field maps to 步驟九 options:
  - `generation_strategy: "one_kol_one_stock"` - 1 KOL → 1 股票
  - `generation_strategy: "one_kol_all_stocks"` - 1 KOL → 所有股票
  - `generation_strategy: "hybrid"` - 混合模式

**Concept Clarification**:
> 一個 KOL 可以選定某些特定產業族群分享看法，而我們可以透過觸發器找出一堆股票，而我們的貼文則是每一檔有標記到的股票，可以一個一個 section 做非常精闢簡潔有力的看法跟文章等

- KOL can focus on specific industry sectors
- Trigger finds multiple stocks
- Each marked stock gets its own section with concise, powerful analysis

**User will provide examples later** ⏳

---

### 5. 🔍 Model ID Switcher (步驟七)
**Status**: Previously Implemented, But Lost?
**Category**: Model Configuration
**Priority**: Medium

**Description**: Model ID 切換功能 - 可以選擇要使用哪些 OpenAI model ID

**Requirements**:
- [ ] Find existing model_id switcher (if it exists)
- [ ] If not found, re-implement in Step 7
- [ ] Allow user to select OpenAI model for this generation:
  - `gpt-4-turbo-preview`
  - `gpt-4-0125-preview`
  - `gpt-3.5-turbo`
  - `o1-preview` (if available)
  - `o1-mini` (if available)
- [ ] Option to use KOL profile's default `model_id`
- [ ] Show model selection before generation starts

**UI Location**: 步驟七 (or during "立即執行測試" modal)

**Database Field**:
- Check if `schedule_tasks.model_id` exists
- Check if `kol_profiles.model_id` exists
- Fallback to environment variable `OPENAI_MODEL_ID`

**Search Task**:
1. Search codebase for existing model_id UI
2. Check if it's hidden or removed
3. If missing, implement new selector

---

### 6. ✅ Trending API + Stock Publishing - Verification
**Status**: ⚠️ Needs Testing
**Category**: Integration Testing
**Priority**: High

**Description**: 確認 trending API + stock 可以發文

**Test Scenario**:
```
1. Create schedule with "熱門話題" trigger
2. Add specific stock_codes: ["2330", "2317"]
3. Execute schedule
4. Verify:
   - ✅ Trending topics fetched
   - ✅ Stock codes extracted from topics
   - ✅ Merged with stock_codes ["2330", "2317"]
   - ✅ Posts generated for all stocks
   - ✅ Posts contain trending context
   - ✅ Posts published to CMoney successfully
```

**Expected Result**: Posts combine trending topic insights + stock analysis

---

### 7. ❌ Trending Topics + News Search Integration
**Status**: Not Implemented
**Category**: Content Enhancement
**Priority**: Medium

**Description**: 確認單獨熱門話題可以結合新聞搜尋發文

**Requirements**:
- [ ] When trigger = "trending_topics" AND news_enabled = true
- [ ] For each trending topic, search for related news
- [ ] Include news insights in post generation
- [ ] Pass both trending context + news context to ChatGPT

**Implementation Flow**:
```
1. Fetch trending topics (已實作)
2. Extract stock codes from topics (已實作)
3. For each stock:
   a. Fetch news using keywords from trending topic
   b. Combine trending insight + news analysis
   c. Generate post with rich context
```

**API Enhancement Needed**:
- Modify `/api/schedule/execute/{task_id}` to support:
  - `trigger_type: "trending_topics"`
  - `news_enabled: true`
  - Fetch news for each stock based on trending keywords

---

### 8. 🧪 Prompt Engineering & Custom Prompt System
**Status**: Not Implemented
**Category**: Content Quality
**Priority**: Medium

**Description**: 研究 OpenAI Assistant 或各種 system prompt / user prompt 去讓我們優化出生成的內容

**User Requirements** (Updated 2025-10-22):
> 這個 section 就是可以去選擇走 customized user/assistant/system prompt. 選擇這個的話要確保帶入一些必要參數

**Core Feature**:
A new section in schedule creation flow where users can:
1. Choose between **Default Prompt** or **Customized Prompt**
2. If Customized: Enter custom system/user/assistant prompts
3. System automatically injects necessary parameters into the prompt

**Required Parameters to Inject**:
When user selects customized prompt mode, ensure these parameters are available:

| Parameter | Type | Source | Example |
|-----------|------|--------|---------|
| `stock_id` | string | Selected stock | "2330" |
| `stock_name` | string | Stock metadata | "台積電" |
| `stock_ohlc` | object | finlab API | `{"open": 590, "high": 595, "low": 588, "close": 592}` |
| `serper_api_results` | array | News search results | `[{title, snippet, link, date}, ...]` |
| `trending_context` | string | Trending topics API | "AI伺服器需求爆發" |
| `technical_indicators` | object | Technical analysis | `{"ma5": 585, "ma20": 580, "rsi": 65}` |
| `fundamental_data` | object | Financial data | `{"pe_ratio": 18.5, "eps": 32.5}` |
| `industry_sector` | string | Stock metadata | "半導體" |
| `kol_persona` | string | KOL profile | "技術分析專家" |

**Implementation Requirements**:

1. **UI Section (New Step or Sub-Step)**:
   ```
   [ ] 步驟 X: Prompt 設定
       ( ) 使用預設 Prompt (推薦)
       (•) 自訂 Prompt (進階)

       [Show when 自訂 Prompt selected]

       System Prompt:
       ┌─────────────────────────────────────┐
       │ You are a financial analyst...      │
       │ Stock: {stock_id} - {stock_name}    │
       │ OHLC: {stock_ohlc}                  │
       └─────────────────────────────────────┘

       User Prompt:
       ┌─────────────────────────────────────┐
       │ Analyze {stock_id} based on:        │
       │ - News: {serper_api_results}        │
       │ - Technical: {technical_indicators} │
       └─────────────────────────────────────┘

       Assistant Prompt (Optional):
       ┌─────────────────────────────────────┐
       │ I will provide...                   │
       └─────────────────────────────────────┘
   ```

2. **Parameter Injection System**:
   - [ ] Create `inject_parameters()` function
   - [ ] Replace placeholders like `{stock_id}` with actual values
   - [ ] Support nested objects: `{stock_ohlc.close}`
   - [ ] Validate all required parameters are available
   - [ ] Show preview of injected prompt before generation

3. **Database Schema**:
   ```sql
   ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS prompt_mode VARCHAR(20) DEFAULT 'default'; -- 'default' or 'custom'
   ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS custom_system_prompt TEXT;
   ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS custom_user_prompt TEXT;
   ALTER TABLE schedule_tasks ADD COLUMN IF NOT EXISTS custom_assistant_prompt TEXT;
   ```

4. **Prompt Template Library**:
   - [ ] Create preset templates for common scenarios:
     - "技術分析專家" template
     - "基本面分析師" template
     - "短線交易者" template
     - "價值投資者" template
   - [ ] Allow users to save custom templates
   - [ ] Share templates across schedules

**Example Use Case**:

**User Custom Prompt**:
```
System Prompt:
你是一位專注於{industry_sector}產業的技術分析師。

User Prompt:
請分析股票 {stock_id} ({stock_name})：
- 當前價格: {stock_ohlc.close}
- 技術指標: RSI={technical_indicators.rsi}, MA5={technical_indicators.ma5}
- 最新新聞: {serper_api_results[0].title}

請提供簡潔有力的技術分析建議。
```

**After Injection**:
```
System Prompt:
你是一位專注於半導體產業的技術分析師。

User Prompt:
請分析股票 2330 (台積電)：
- 當前價格: 592
- 技術指標: RSI=65, MA5=585
- 最新新聞: 台積電3nm製程獲蘋果大單

請提供簡潔有力的技術分析建議。
```

**Goals**:
1. ✅ Research OpenAI Assistants API vs ChatCompletion API
2. ✅ Implement customized prompt system with parameter injection
3. ⏳ A/B test prompt variations for better content quality (future)
4. ⏳ Implement prompt versioning system (future)

**Research Questions**:
- Should we use OpenAI Assistants API instead of ChatCompletion API?
- Can we create specialized assistants for different KOL personas?
- How to structure prompts for better financial analysis?
- How to reduce hallucination in stock analysis?
- What parameters are most critical for high-quality analysis?

**Acceptance Criteria**:
- [ ] User can toggle between default/custom prompt mode
- [ ] Custom prompt UI accepts system/user/assistant prompts
- [ ] All required parameters (stock_id, OHLC, serper results, etc.) are injected
- [ ] Preview shows final prompt with injected values
- [ ] Validation prevents generation if parameters are missing
- [ ] Custom prompts saved to database and persist across sessions
- [ ] Template library with at least 4 preset templates

**Estimated Time**: 4-5 hours
- UI implementation: 2 hours
- Parameter injection system: 1.5 hours
- Template library: 1 hour
- Testing: 0.5 hours

---

## 📊 TASK SUMMARY

| Task | Status | Priority | Estimated Time |
|------|--------|----------|----------------|
| **0. FIX: Generic Prompt Quality** | ❌ **Critical Bug** | **🚨 CRITICAL** | **3-4 hours** |
| 1. Trending Topic Verification | ⚠️ Testing | High | 30 mins |
| 2. News Link Toggle | ❌ Not Started | High | 2 hours |
| 3. News Config Persistence | ❌ Not Started | High | 1.5 hours |
| 4. Remove Duplicate UI | 🔄 Refactor | Medium | 1 hour |
| 5. Model ID Switcher | 🔍 Find/Implement | Medium | 1-2 hours |
| 6. Trending + Stock Publishing | ⚠️ Testing | High | 30 mins |
| 7. Trending + News Integration | ❌ Not Started | Medium | 2 hours |
| 8. Custom Prompt System | ❌ Not Started | Medium | 4-5 hours |

**Total Estimated Time**: ~17-21 hours

**Critical Path**: Task 0 should be fixed FIRST before other tasks, as it affects all generated content quality.

---

## 🔄 NEXT STEPS

### Immediate Actions:
1. ✅ Create this backlog (done)
2. ⏳ Wait for user to provide examples for Task #4 (KOL-to-stock mapping)
3. ⏳ User will continue adding more tasks to backlog

### When Ready to Start:
- User will indicate which task to work on first
- Suggested order: Task 1 → Task 6 → Task 2 → Task 3 → Task 5 → Task 4 → Task 7 → Task 8

---

## 📝 NOTES

- User mentioned: "i'll keep updating you what to add"
- User will provide examples for Task #4 concept
- Some tasks need verification (1, 6) before implementation
- Model ID switcher might already exist - need to search first

---

## 🤖 CHANGELOG

**2025-10-22 15:45**: 🚨 Added Task #0 - CRITICAL BUG: Generic Prompt Quality Issue
- Identified that generated posts are too generic and lack specific data
- Example: 茂矽（2342）post only contained macro-economic analysis
- Missing: OHLC data, technical indicators, news, fundamental data, trigger context
- Added as highest priority (CRITICAL) task
- Requires audit of current default prompt and complete redesign
- Estimated time: 3-4 hours
- **This should be fixed FIRST** before other features

**2025-10-22 15:30**: Updated Task #8 with detailed custom prompt system requirements
- Added required parameters list (stock_id, OHLC, serper_api_results, etc.)
- Defined UI mockup for prompt selection
- Specified parameter injection system
- Added template library requirements
- Updated priority from Low to Medium
- Updated estimated time from "Ongoing" to "4-5 hours"

**2025-10-22 15:00**: Initial backlog created with 8 tasks

