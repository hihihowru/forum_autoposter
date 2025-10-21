# KOL AI Prefill Investigation Report

**Date**: 2025-10-21
**Issue**: User reported prompt fields not auto-filled when creating KOL
**User Quote**: "kol 人設、流派、 prompt 人設等欄位都沒有 fill. not sure openai model are implemented here"

---

## Investigation Findings

### 1. Frontend Status ✅ PARTIAL

**File**: `KOLManagementPage.tsx`

**Fields Exist in Form**:
- Line 795: `prompt_persona` (Prompt人設)
- Line 824: `prompt_style` (Prompt風格)
- Line 844: `prompt_guardrails` (Prompt守則)
- Line 862: `prompt_skeleton` (Prompt骨架)

**Default Values Added** (Commit: 9c7bcdbe):
- prompt_persona: "技術分析師（技術派）..." (initialValue set)
- prompt_style: "邏輯清晰（理性風格）..." (initialValue set)
- prompt_guardrails: "標準守則（合規）..." (initialValue set)
- prompt_skeleton: "技術分析骨架..." (initialValue set)

**BUT - Fields NOT Sent to Backend** ❌:

Lines 362-368 in `proceedWithCreation()`:
```typescript
const payload = {
  email: values.email,
  password: values.password,
  nickname: values.nickname,
  member_id: values.member_id || '',
  ai_description: values.ai_description || ''
  // ❌ prompt_persona NOT included
  // ❌ prompt_style NOT included
  // ❌ prompt_guardrails NOT included
  // ❌ prompt_skeleton NOT included
};
```

---

### 2. Backend Status ❌ NOT IMPLEMENTED

**File**: `main.py`

**Search Results**:
```bash
$ grep "prompt_persona\|prompt_style\|prompt_guardrails\|prompt_skeleton" main.py
# No results found
```

**Conclusion**: Backend does NOT handle these fields at all.

**Current KOL Creation Flow**:

Lines 4068-4093 - INSERT SQL:
```sql
INSERT INTO kol_profiles (
    serial, nickname, member_id, persona, status, owner, email, password,
    whitelist, notes, post_times, target_audience, interaction_threshold,
    common_terms, colloquial_terms, tone_style, typing_habit, backstory,
    expertise, signature, emoji_pack, tone_formal, tone_emotion,
    tone_confidence, tone_urgency, tone_interaction, question_ratio,
    content_length, created_time, last_updated
) VALUES (...)
```

**Fields Stored**:
- ✅ persona (基本人設 - "casual", "technical", etc.)
- ✅ tone_style (語氣風格 - "友善、親切")
- ✅ backstory (背景故事)
- ❌ prompt_persona (NOT stored)
- ❌ prompt_style (NOT stored)
- ❌ prompt_guardrails (NOT stored)
- ❌ prompt_skeleton (NOT stored)

---

### 3. Database Schema Status ❌ UNKNOWN

**Columns Probably Don't Exist**:
- No code references to these fields in INSERT statements
- No code references in SELECT statements
- Likely need ALTER TABLE migration to add columns

**Required Columns**:
```sql
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS prompt_persona TEXT;
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS prompt_style TEXT;
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS prompt_guardrails TEXT;
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS prompt_skeleton TEXT;
ALTER TABLE kol_profiles ADD COLUMN IF NOT EXISTS model_id TEXT DEFAULT 'gpt-4o-mini';
```

---

## User's Expected Behavior

**Quote**: "expected next step verify all ai prefilled value for all in the column using llm with the provided prompt"

**Expected Flow**:
1. User fills in `ai_description` (e.g., "This KOL is a technical trader who loves MACD")
2. Click "創建 KOL" button
3. **Backend calls OpenAI** to generate:
   - prompt_persona (based on ai_description)
   - prompt_style (based on ai_description)
   - prompt_guardrails (based on ai_description)
   - prompt_skeleton (based on ai_description)
4. **Frontend receives AI-generated values** and auto-fills form fields
5. User can **review and modify** before final submission
6. Click "確認創建" to save to database

**Current Flow** (Broken):
1. User fills in form (all fields manually)
2. Click "創建 KOL" → sends only: email, password, nickname, member_id, ai_description
3. Backend creates KOL without prompt fields
4. ❌ Prompt fields are lost

---

## Recommended Fix

### Phase 1: Basic Fix (Store User-Provided Values) ✅

**Frontend Changes** (`KOLManagementPage.tsx:356-368`):
```typescript
const payload = {
  email: values.email,
  password: values.password,
  nickname: values.nickname,
  member_id: values.member_id || '',
  ai_description: values.ai_description || '',
  // ✅ Add prompt fields
  prompt_persona: values.prompt_persona || '',
  prompt_style: values.prompt_style || '',
  prompt_guardrails: values.prompt_guardrails || '',
  prompt_skeleton: values.prompt_skeleton || '',
  model_id: values.model_id || 'gpt-4o-mini'
};
```

**Backend Changes** (`main.py`):

1. Accept prompt fields in request (lines ~3900):
```python
prompt_persona = data.get('prompt_persona', '')
prompt_style = data.get('prompt_style', '')
prompt_guardrails = data.get('prompt_guardrails', '')
prompt_skeleton = data.get('prompt_skeleton', '')
model_id = data.get('model_id', 'gpt-4o-mini')
```

2. Add columns to INSERT SQL (lines 4068-4093):
```python
INSERT INTO kol_profiles (
    ...,
    prompt_persona, prompt_style, prompt_guardrails, prompt_skeleton, model_id,
    ...
) VALUES (
    ...,
    %s, %s, %s, %s, %s,
    ...
)
```

3. Add to execute parameters (lines 4087-4093):
```python
cursor.execute(insert_sql, (
    ...,
    prompt_persona, prompt_style, prompt_guardrails, prompt_skeleton, model_id,
    ...
))
```

### Phase 2: AI Auto-Fill (Enhancement) 🔮

**Add LLM Call to Generate Prompt Fields**:

```python
if ai_description:
    # Call OpenAI to generate prompt fields
    prompt = f"""Based on this KOL description:
    "{ai_description}"

    Generate the following prompt components in JSON format:
    - prompt_persona: Character persona and background (200 chars)
    - prompt_style: Writing style and tone (150 chars)
    - prompt_guardrails: Content guidelines and rules (200 chars)
    - prompt_skeleton: Content structure template (300 chars)
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    ai_prompts = json.loads(response.choices[0].message.content)
    prompt_persona = ai_prompts.get('prompt_persona', '')
    prompt_style = ai_prompts.get('prompt_style', '')
    prompt_guardrails = ai_prompts.get('prompt_guardrails', '')
    prompt_skeleton = ai_prompts.get('prompt_skeleton', '')
```

---

## Implementation Priority

| Task | Priority | Effort | Impact |
|------|----------|--------|--------|
| **Add database columns** | 🔥 HIGH | Low | Required for any fix |
| **Frontend: Send prompt fields** | 🔥 HIGH | Low | Required for any fix |
| **Backend: Accept & store fields** | 🔥 HIGH | Medium | Required for any fix |
| **AI auto-fill (Phase 2)** | 🟡 MEDIUM | High | Nice-to-have enhancement |

---

## Testing Plan

### Phase 1 Testing (Basic Fix):

1. Create test KOL:
   - Fill in all fields including prompt templates
   - Click "創建 KOL"
   - **Expected**: Prompt fields are saved to database

2. Verify database:
   - Check kol_profiles table
   - **Expected**: prompt_persona, prompt_style, prompt_guardrails, prompt_skeleton columns exist with values

3. Edit KOL:
   - Click edit button
   - **Expected**: Form shows saved prompt values

### Phase 2 Testing (AI Auto-Fill):

1. Create KOL with AI description only:
   - Fill in: email, password, nickname, ai_description
   - Leave prompt fields empty
   - Click "創建 KOL"
   - **Expected**: Backend generates prompt fields using LLM
   - **Expected**: Frontend shows generated values for review

2. Verify AI quality:
   - Check if generated prompts match ai_description
   - Check if prompts are coherent and useful

---

## Decision Required

**Should we implement**:
- [ ] Phase 1 only (store user-provided values) - Quick fix
- [ ] Phase 1 + Phase 2 (AI auto-fill) - Full solution
- [ ] Skip for now, focus on scheduling

**Recommendation**: Implement **Phase 1** now (1-2 hours), defer Phase 2 to post-scheduling.

---

**Generated**: 2025-10-21
**Status**: Investigation Complete, Awaiting Decision

🤖 Generated with [Claude Code](https://claude.com/claude-code)
