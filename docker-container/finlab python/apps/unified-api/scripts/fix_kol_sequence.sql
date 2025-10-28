-- =====================================================
-- 修復 kol_profiles ID 序列不同步問題
--
-- 問題：duplicate key value violates unique constraint "kol_profiles_pkey"
-- 原因：序列值落後於實際最大 ID
--
-- 執行方式：
-- 1. 登入 Railway Dashboard (https://railway.app/)
-- 2. 選擇 PostgreSQL 服務
-- 3. 點擊 "Query" 或 "Connect"
-- 4. 複製貼上下面的 SQL 並執行
-- =====================================================

-- 查看當前狀況
SELECT
    '當前最大 ID' as description,
    MAX(id) as value
FROM kol_profiles

UNION ALL

SELECT
    '當前序列值' as description,
    last_value as value
FROM kol_profiles_id_seq;

-- 修復序列（重置到最大 ID）
SELECT setval('kol_profiles_id_seq', (SELECT MAX(id) FROM kol_profiles));

-- 驗證修復結果
SELECT
    '修復後序列值' as description,
    last_value as value
FROM kol_profiles_id_seq;

-- =====================================================
-- 預期結果：
-- =====================================================
-- description      | value
-- -----------------|-------
-- 當前最大 ID       | 15
-- 當前序列值        | 9      (問題：小於最大 ID！)
-- 修復後序列值      | 15     (修復：等於最大 ID，下次插入會用 16)
