-- Prompt 模板系統
-- Created: 2025-10-22
-- Purpose: 實作靈活的 prompt 模板系統，支援不同 posting_type 和自我學習

-- ====================================
-- 1. Prompt 模板表
-- ====================================
CREATE TABLE IF NOT EXISTS prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,                      -- 模板名稱：「深度分析模板 v1」
    description TEXT,                                -- 模板說明
    posting_type VARCHAR(50) NOT NULL,               -- analysis / interaction / personalized
    system_prompt_template TEXT NOT NULL,            -- System prompt 模板（支援變數注入）
    user_prompt_template TEXT NOT NULL,              -- User prompt 模板（支援變數注入）
    created_by VARCHAR(50) DEFAULT 'system',         -- 創建者（KOL serial 或 'system'）
    is_default BOOLEAN DEFAULT FALSE,                -- 是否為預設模板
    is_active BOOLEAN DEFAULT TRUE,                  -- 是否啟用
    performance_score FLOAT DEFAULT 0,               -- 效能分數（自我學習用）
    usage_count INT DEFAULT 0,                       -- 使用次數
    avg_likes FLOAT DEFAULT 0,                       -- 平均讚數
    avg_comments FLOAT DEFAULT 0,                    -- 平均留言數
    avg_shares FLOAT DEFAULT 0,                      -- 平均分享數
    metadata JSON,                                   -- 額外元數據
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_prompt_templates_posting_type ON prompt_templates(posting_type);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_is_default ON prompt_templates(is_default);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_performance ON prompt_templates(performance_score DESC);

-- ====================================
-- 2. 修改 post_records 表 - 加入模板追蹤
-- ====================================
ALTER TABLE post_records
ADD COLUMN IF NOT EXISTS prompt_template_id INT REFERENCES prompt_templates(id),
ADD COLUMN IF NOT EXISTS prompt_system_used TEXT,           -- 實際使用的 system prompt
ADD COLUMN IF NOT EXISTS prompt_user_used TEXT,             -- 實際使用的 user prompt
ADD COLUMN IF NOT EXISTS interaction_score FLOAT DEFAULT 0; -- 互動分數

-- 索引
CREATE INDEX IF NOT EXISTS idx_post_records_template ON post_records(prompt_template_id);

-- ====================================
-- 3. 插入預設模板
-- ====================================

-- 預設分析模板
INSERT INTO prompt_templates (name, description, posting_type, system_prompt_template, user_prompt_template, is_default, is_active) VALUES
(
    '預設深度分析模板',
    '適合技術面、基本面、市場情緒的全方位分析',
    'analysis',
    '你是 {kol_nickname}，一位{persona_name}風格的股票分析師。

{writing_style}

你的目標是提供專業、深入的股票分析，包含技術面、基本面、市場情緒等多角度觀點。

請展現你的獨特分析風格，用你習慣的方式表達觀點。',
    '我想了解 {stock_name}({stock_id}) 最近的表現和投資機會。

【背景】{trigger_description}

【市場數據】
{news_summary}{ohlc_summary}{tech_summary}
請分析這檔股票，包含：
1. 為什麼值得關注
2. 你的專業看法
3. 潛在機會和風險

目標長度：約 {max_words} 字',
    TRUE,
    TRUE
),

-- 預設互動模板
(
    '預設互動提問模板',
    '適合引發讀者討論和互動的短文',
    'interaction',
    '你是 {kol_nickname}，一位{persona_name}風格的股票分析師。

{writing_style}

你的目標是與讀者互動，提出引發思考的問題，鼓勵討論。例如：「你覺得這檔股票現在適合進場嗎？留言分享你的看法！」內容要簡短有力。

請展現你的獨特風格，用你習慣的方式提問。',
    '我想了解 {stock_name}({stock_id}) 最近的表現。

【背景】{trigger_description}

【市場數據】
{news_summary}{ohlc_summary}
請針對這檔股票提出一個引發討論的問題，鼓勵讀者分享看法。

要求：
- 內容簡短（約 {max_words} 字）
- 提出單一核心問題
- 引發讀者思考和互動',
    TRUE,
    TRUE
),

-- 預設個性化模板
(
    '預設個性化風格模板',
    '充分展現 KOL 個人特色和風格',
    'personalized',
    '你是 {kol_nickname}，一位{persona_name}風格的股票分析師。

{writing_style}

你的目標是展現你獨特的個人風格和觀點，讓讀者感受到你的個性和專業。

請充分發揮你的個人特色，用你最自然、最舒服的方式表達。',
    '我想了解 {stock_name}({stock_id}) 最近的表現和投資機會。

【背景】{trigger_description}

【市場數據】
{news_summary}{ohlc_summary}{tech_summary}
請用你獨特的風格分析這檔股票，展現你的個性和專業。

要求：
- 目標長度：約 {max_words} 字
- 充分展現你的個人風格
- 用你習慣的方式組織內容',
    TRUE,
    TRUE
);

-- ====================================
-- 4. 註解說明
-- ====================================

COMMENT ON TABLE prompt_templates IS 'Prompt 模板系統 - 支援不同 posting_type 和自我學習';
COMMENT ON COLUMN prompt_templates.system_prompt_template IS 'System prompt 模板，支援變數注入如 {kol_nickname}, {persona_name} 等';
COMMENT ON COLUMN prompt_templates.user_prompt_template IS 'User prompt 模板，支援變數注入如 {stock_id}, {news_summary}, {ohlc.close} 等';
COMMENT ON COLUMN prompt_templates.performance_score IS '效能分數，基於 avg_likes, avg_comments, avg_shares 計算';

-- ====================================
-- 5. 自動更新 updated_at
-- ====================================
CREATE OR REPLACE FUNCTION update_prompt_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_prompt_templates_updated_at
BEFORE UPDATE ON prompt_templates
FOR EACH ROW
EXECUTE FUNCTION update_prompt_templates_updated_at();
