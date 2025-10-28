-- =====================================================
-- 永久修復 kol_profiles ID 序列問題
--
-- 這個腳本做兩件事:
-- 1. 修復當前的序列問題
-- 2. 創建觸發器，自動防止未來出現同樣問題
-- =====================================================

-- Step 1: 修復當前序列
SELECT setval('kol_profiles_id_seq', (SELECT COALESCE(MAX(id), 0) FROM kol_profiles));

-- Step 2: 創建觸發器函數
CREATE OR REPLACE FUNCTION sync_kol_profiles_sequence()
RETURNS TRIGGER AS $$
BEGIN
    -- 在每次 INSERT 後，自動同步序列到最大 ID
    PERFORM setval('kol_profiles_id_seq', (SELECT COALESCE(MAX(id), 0) FROM kol_profiles));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 3: 創建觸發器（如果不存在）
DROP TRIGGER IF EXISTS sync_kol_sequence_trigger ON kol_profiles;
CREATE TRIGGER sync_kol_sequence_trigger
    AFTER INSERT ON kol_profiles
    FOR EACH STATEMENT
    EXECUTE FUNCTION sync_kol_profiles_sequence();

-- =====================================================
-- 驗證
-- =====================================================
SELECT
    'Current Max ID' as description,
    COALESCE(MAX(id), 0) as value
FROM kol_profiles

UNION ALL

SELECT
    'Current Sequence Value' as description,
    last_value as value
FROM kol_profiles_id_seq

UNION ALL

SELECT
    'Trigger Exists' as description,
    COUNT(*)::INTEGER as value
FROM pg_trigger
WHERE tgname = 'sync_kol_sequence_trigger';

-- =====================================================
-- 測試觸發器
-- =====================================================
-- 執行完上面的 SQL 後，你可以測試創建 KOL
-- 觸發器會自動確保序列同步，防止未來出現 duplicate key 錯誤

-- 說明:
-- ✅ 每次 INSERT 新 KOL 後，序列會自動更新到最大 ID
-- ✅ 即使有人手動 INSERT 帶 ID 的記錄，觸發器也會修復序列
-- ✅ 這是一次性設置，永久生效
-- =====================================================
