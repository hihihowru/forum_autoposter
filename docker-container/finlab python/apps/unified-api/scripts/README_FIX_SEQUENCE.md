# KOL Sequence Fix - 執行說明

## 問題描述

創建 KOL 時出現錯誤：
```
duplicate key value violates unique constraint "kol_profiles_pkey"
DETAIL: Key (id)=(12) already exists.
```

**原因**：PostgreSQL 的 `kol_profiles_id_seq` 序列值落後於實際資料的最大 ID 值。

## 為什麼會發生這個問題？

序列不同步通常發生在：
1. **初始數據導入** - 導入數據時指定了 ID 值
2. **資料庫還原** - 從備份還原後沒有更新序列
3. **手動 SQL 插入** - 執行了帶有明確 ID 值的 INSERT 語句

## ⭐ 永久解決方案（推薦）

使用帶觸發器的方案，一次設置，永久生效！

### 什麼是觸發器方案？

創建一個 PostgreSQL 觸發器，在每次插入新 KOL 後自動同步序列。這樣即使未來有人手動插入帶 ID 的記錄，也不會再出現這個問題。

### 如何執行

1. 登入 Railway Dashboard: https://railway.app/
2. 選擇 PostgreSQL 服務
3. 點擊 **"Query"** 標籤
4. 複製 `fix_kol_sequence_permanent.sql` 的內容並執行

或者直接執行這段 SQL：

```sql
-- 修復當前序列
SELECT setval('kol_profiles_id_seq', (SELECT COALESCE(MAX(id), 0) FROM kol_profiles));

-- 創建觸發器函數
CREATE OR REPLACE FUNCTION sync_kol_profiles_sequence()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM setval('kol_profiles_id_seq', (SELECT COALESCE(MAX(id), 0) FROM kol_profiles));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 創建觸發器
DROP TRIGGER IF EXISTS sync_kol_sequence_trigger ON kol_profiles;
CREATE TRIGGER sync_kol_sequence_trigger
    AFTER INSERT ON kol_profiles
    FOR EACH STATEMENT
    EXECUTE FUNCTION sync_kol_profiles_sequence();
```

**效果**：
- ✅ 立即修復當前問題
- ✅ 自動防止未來再次發生
- ✅ 一次設置，永久生效
- ✅ 無需修改應用程式碼

---

## 臨時解決方法（只修復當前問題）

如果你只想快速修復當前問題（不推薦，因為未來可能再次發生）：

### 方法 1：使用 Railway CLI（推薦）

```bash
# 1. 進入專案目錄
cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api"

# 2. 登入 Railway（在瀏覽器中完成）
railway login

# 3. 選擇專案（如果有多個專案）
railway link

# 4. 執行修復腳本
railway run python3 scripts/fix_kol_sequence.py
```

### 方法 2：從 Railway Dashboard 獲取 DATABASE_URL

1. 登入 Railway Dashboard: https://railway.app/
2. 選擇你的專案
3. 點擊 PostgreSQL 服務
4. 點擊 "Variables" 標籤
5. 複製 `DATABASE_URL` 的值

然後執行：

```bash
cd "/Users/willchen/Documents/autoposter/forum_autoposter/docker-container/finlab python/apps/unified-api"

# 方式 A: 使用環境變數
export DATABASE_URL="postgresql://postgres:password@..."
python3 scripts/fix_kol_sequence.py

# 方式 B: 使用命令行參數
python3 scripts/fix_kol_sequence.py "postgresql://postgres:password@..."
```

### 方法 3：手動執行 SQL（最簡單）

1. 登入 Railway Dashboard
2. 點擊 PostgreSQL 服務
3. 點擊 "Query" 或 "Connect"
4. 執行以下 SQL：

```sql
SELECT setval('kol_profiles_id_seq', (SELECT MAX(id) FROM kol_profiles));
```

## 驗證修復

修復後，你應該會看到：

```
📊 當前狀況:
   最大 ID: 15
   序列值: 15

✅ 序列已修復！下一個 ID 將是: 16
```

然後再次嘗試創建 KOL，應該就可以成功了！

## 腳本說明

- **位置**: `scripts/fix_kol_sequence.py`
- **功能**: 自動檢測並修復 kol_profiles 表的 ID 序列
- **安全**: 只讀取數據並更新序列，不會修改或刪除任何資料
