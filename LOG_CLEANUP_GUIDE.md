# Log Cleanup Guide - Reduce Token Usage

## 📊 Current Problem
A single manual post generation creates **~200 log lines**, consuming excessive tokens when debugging.

## 🎯 Log Analysis from Recent Deployment

### Example Log Sequence (Current):
```
INFO:main:收到 manual_posting 請求
INFO:main:手動貼文參數: stock_code=2330, kol_serial=208, session_id=1761000000001
INFO:main:使用 GPT 生成器生成內容: stock_code=2330, kol_persona=technical
INFO:openai._base_client:Retrying request to /chat/completions in 0.423036 seconds
INFO:openai._base_client:Retrying request to /chat/completions in 0.836628 seconds
ERROR:gpt_content_generator:GPT內容生成失敗: Connection error.
WARNING:gpt_content_generator:使用備用模板生成內容: 台積電(2330)
INFO:main:✅ GPT 內容生成成功: title=台積電(2330) 技術面分析與操作策略...
INFO:main:🎯 開始生成 5 個隨機版本: KOL=208, posting_type=analysis
INFO:personalization_module:🎨 開始增強版個人化處理 KOL 208
INFO:personalization_module:🔍 個人化模組 INPUT - 標題: 台積電(2330) 技術面分析與操作策略
INFO:personalization_module:🔍 個人化模組 INPUT - 內容長度: 263 字
INFO:personalization_module:🔍 個人化模組 INPUT - 觸發器類型: test_fallback
INFO:personalization_module:🔍 個人化模組 INPUT - 發文類型: analysis
INFO:personalization_module:⚠️ 沒有即時股價數據，使用原始內容
INFO:personalization_module:🎲 開始隨機化內容生成 - 發文類型: analysis
INFO:personalization_module:🎲 沒有 serper_analysis 數據
INFO:personalization_module:🎲 開始調用隨機化生成器...
INFO:random_content_generator:🎲 開始隨機化內容生成 - 類型: analysis
INFO:random_content_generator:📊 KOL: 長線韭韭 (208)
INFO:random_content_generator:📈 股票: ()
INFO:random_content_generator:🎯 KOL 特色 - 暱稱: 長線韭韭, 人設: 總經+價值派, 風格: 穩健理性，價值導向，長期思維
INFO:random_content_generator:🔄 生成版本 1/5...
INFO:random_content_generator:🤖 調用 LLM API 生成 analysis_v1...
ERROR:random_content_generator:❌ LLM API 調用失敗: Invalid header value b'Bearer ...\n'
INFO:random_content_generator:✅ 版本 1 生成完成: 專業觀點 - 值得關注的投資機會...
[... repeats for versions 2-5 ...]
INFO:random_content_generator:================================================================================
INFO:random_content_generator:🎲 隨機化內容生成結果
INFO:random_content_generator:================================================================================
INFO:random_content_generator:🎯 選中 版本 5:
INFO:random_content_generator:   標題: 技術分析 - 值得關注的投資機會
INFO:random_content_generator:   內容: 作為專業分析師，我對當前市場走勢有以下觀察：

1. 技術面顯示強勢突破
2. 基本面支撐穩健
3. 市場情緒積極

建議投資人密切關注後續發展，適時調整策略。

#投資分析 #市場觀察
INFO:random_content_generator:   類型: analysis
INFO:random_content_generator:   角度: 風險評估提醒
INFO:random_content_generator:----------------------------------------
INFO:random_content_generator:📝 備選 版本 1:
INFO:random_content_generator:   標題: 專業觀點 - 值得關注的投資機會
[... repeats for all 4 alternative versions with full content ...]
```

---

## ✂️ Recommended Deletions

### 1. **Remove Verbose Input Logging** (Lines: ~8)
**File:** `personalization_module.py` (around line 762-778)

**DELETE:**
```python
self.logger.info(f"🔍 個人化模組 INPUT - 標題: {standard_title}")
self.logger.info(f"🔍 個人化模組 INPUT - 內容長度: {len(standard_content)} 字")
self.logger.info(f"🔍 個人化模組 INPUT - 觸發器類型: {trigger_type}")
self.logger.info(f"🔍 個人化模組 INPUT - 發文類型: {posting_type}")
```

**KEEP:**
```python
self.logger.info(f"🎨 開始增強版個人化處理 KOL {kol_serial}")
```

**Reason:** We don't need to log every input parameter. The start message is enough.

---

### 2. **Remove Full Content Display in Logs** (Lines: ~60)
**File:** `random_content_generator.py` (around line 363-380)

**DELETE:** The entire content display section:
```python
INFO:random_content_generator:   內容: 作為專業分析師，我對當前市場走勢有以下觀察：

1. 技術面顯示強勢突破
2. 基本面支撐穩健
3. 市場情緒積極

建議投資人密切關注後續發展，適時調整策略。

#投資分析 #市場觀察
```

**REPLACE WITH:**
```python
self.logger.info(f"   內容: {version['content'][:50]}...")  # Only first 50 chars
```

**Reason:** Full content takes 5-10 lines per version × 5 versions = 50+ lines. Just show preview.

---

### 3. **Reduce Alternative Versions Logging** (Lines: ~40)
**File:** `random_content_generator.py` `_log_generation_results()`

**CURRENT:** Logs all 5 versions with full details
```python
for i, version in enumerate(versions):
    status = "🎯 選中" if i == selected_index else "📝 備選"
    self.logger.info(f"{status} 版本 {i+1}:")
    self.logger.info(f"   標題: {version['title']}")
    self.logger.info(f"   內容: {version['content']}")
    self.logger.info(f"   類型: {version['version_type']}")
    self.logger.info(f"   角度: {version['angle']}")
    self.logger.info("----------------------------------------")
```

**REPLACE WITH:**
```python
# Only log selected version
self.logger.info(f"🎯 選中 版本 {selected_index + 1}: {selected_version['title']}")
self.logger.info(f"   角度: {selected_version['angle']}")
# Log alternatives titles only (not full content)
alt_titles = [f"V{i+1}: {v['title'][:30]}..." for i, v in enumerate(alternative_versions)]
self.logger.info(f"📝 備選版本: {', '.join(alt_titles)}")
```

**Reason:** Reduces from 40 lines to 3 lines. Only show what's actually used + titles of alternatives.

---

### 4. **Remove Redundant Progress Messages** (Lines: ~10)
**File:** `random_content_generator.py`

**DELETE:**
```python
INFO:random_content_generator:🔄 生成版本 1/5...
INFO:random_content_generator:🔄 生成版本 2/5...
INFO:random_content_generator:🔄 生成版本 3/5...
INFO:random_content_generator:🔄 生成版本 4/5...
INFO:random_content_generator:🔄 生成版本 5/5...
```

**REPLACE WITH:**
```python
self.logger.info(f"🔄 生成 5 個版本...")  # Single line
```

**Reason:** We don't need to see each iteration. Just log start and completion.

---

### 5. **Consolidate OpenAI Retry Logs** (Lines: ~4 per call)
**File:** OpenAI library (external, can't modify directly)

**CURRENT:**
```python
INFO:openai._base_client:Retrying request to /chat/completions in 0.423036 seconds
INFO:openai._base_client:Retrying request to /chat/completions in 0.836628 seconds
```

**WORKAROUND:** Set OpenAI log level to WARNING in main.py:
```python
import logging
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
```

**Reason:** We don't need to see every retry. Only errors matter.

---

### 6. **Remove Separator Lines** (Lines: ~5)
**File:** `random_content_generator.py`

**DELETE:**
```python
self.logger.info("=" * 80)
self.logger.info("🎲 隨機化內容生成結果")
self.logger.info("=" * 80)
```

**REPLACE WITH:**
```python
self.logger.info("🎲 隨機化內容生成結果")
```

**Reason:** Visual separators waste lines. Not needed in production logs.

---

### 7. **Reduce Output Logging** (Lines: ~10)
**File:** `personalization_module.py` (around line 826-838)

**DELETE:**
```python
self.logger.info(f"🔍 個人化模組 OUTPUT - 標題: {personalized_title}")
self.logger.info(f"🔍 個人化模組 OUTPUT - 內容長度: {len(personalized_content)} 字")
self.logger.info(f"🔍 個人化模組 OUTPUT - 內容前100字: {personalized_content[:100]}...")
```

**REPLACE WITH:**
```python
self.logger.info(f"✅ 個人化完成: {personalized_title[:40]}... ({len(personalized_content)}字)")
```

**Reason:** Single line summary instead of 3+ lines of output.

---

## 📊 Expected Reduction

| Component | Current Lines | After Cleanup | Savings |
|-----------|--------------|---------------|---------|
| Input logging | 8 | 1 | -7 |
| Full content display | 60 | 10 | -50 |
| Alternative versions | 40 | 3 | -37 |
| Progress messages | 10 | 1 | -9 |
| OpenAI retries | 10 | 0 | -10 |
| Separator lines | 5 | 0 | -5 |
| Output logging | 10 | 1 | -9 |
| **TOTAL** | **~200** | **~70** | **-130 (65%)** |

---

## 🔧 Implementation Priority

### High Priority (Implement First):
1. ✅ Full content display removal (-50 lines)
2. ✅ Alternative versions reduction (-37 lines)
3. ✅ OpenAI retry suppression (-10 lines)

### Medium Priority:
4. Input/Output logging consolidation (-16 lines)
5. Progress message consolidation (-9 lines)

### Low Priority:
6. Separator line removal (-5 lines)

---

## 🚀 Quick Implementation Script

Create a new commit with these changes:

**File:** `main.py` (Add at startup)
```python
# Suppress verbose external library logging
import logging
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
```

**File:** `random_content_generator.py` - Update `_log_generation_results()`
```python
def _log_generation_results(self, versions, selected_version, selected_index):
    """記錄生成結果 - SIMPLIFIED"""

    # Only log selected version
    self.logger.info(f"🎯 選中版本 {selected_index + 1}: {selected_version['title']}")
    self.logger.info(f"   角度: {selected_version['angle']}")

    # Log alternative titles only (not full content)
    alt_titles = [f"V{i+1}: {v['title'][:25]}" for i, v in enumerate(versions) if i != selected_index]
    self.logger.info(f"📝 備選: {' | '.join(alt_titles)}")
```

**File:** `personalization_module.py` - Simplify input/output logs
```python
# REPLACE lines 762-778 with:
self.logger.info(f"🎨 個人化 KOL{kol_serial} | {posting_type} | {trigger_type or 'manual'}")

# REPLACE lines 826-838 with:
self.logger.info(f"✅ 完成: {personalized_title[:40]}... ({len(personalized_content)}字, {len(alternative_versions)}個替代版本)")
```

---

## ✅ Benefits

1. **65% token reduction** - From ~200 lines to ~70 lines per post
2. **Easier debugging** - Less noise, key info stands out
3. **Cost savings** - Fewer tokens when providing logs to Claude
4. **Faster log reading** - Easier to spot actual errors

Would you like me to implement these changes now?
