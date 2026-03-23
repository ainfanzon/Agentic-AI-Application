CREATE TABLE revenue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    month DATE,
    amount DECIMAL(12,2),
    product_category STRING
);
INSERT INTO revenue (month, amount, product_category) VALUES 
('2025-09-01', 5000.00, 'Software'),
('2025-10-01', 7200.00, 'Hardware'),
('2025-11-01', 8500.00, 'Software'),
('2025-12-01', 12000.00, 'Software'),
('2026-01-01', 9500.00, 'Hardware'),
('2026-02-01', 11000.00, 'Software');
-- 1. Clear the old messy data
TRUNCATE TABLE revenue;

-- 2. Populate with a clean, single-category 6-month trend for March 2026
INSERT INTO revenue (month, amount, product_category) VALUES 
('2025-10-01', 52000.00, 'SaaS'),
('2025-11-01', 54500.00, 'SaaS'),
('2025-12-01', 53000.00, 'SaaS'),
('2026-01-01', 58000.00, 'SaaS'),
('2026-02-01', 61500.00, 'SaaS'),
('2026-03-01', 65000.00, 'SaaS');

CREATE TABLE conversation_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id STRING NOT NULL,         -- Links multiple turns in one session
    user_id STRING DEFAULT 'default',  -- Multi-user support
    role STRING NOT NULL,              -- 'user', 'assistant', or 'system'
    content TEXT NOT NULL,             -- The actual message or report
    data_snapshot JSONB,               -- The 'last_df_data' for quick re-plotting
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    INDEX idx_thread (thread_id)
);

CREATE TABLE swarm_memory (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id STRING NOT NULL,
    memory_key STRING NOT NULL,        -- e.g., 'preference', 'anomaly', 'market_context'
    memory_value TEXT NOT NULL,        -- The insight itself
    importance INT DEFAULT 1,          -- 1-10 scale to help agents prioritize
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT now(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE (user_id, memory_key)
);

-- 1. Add a GIST index for faster keyword searching (Optional but recommended for performance)
CREATE INDEX idx_memory_value_search ON public.swarm_memory USING GIST (memory_value gist_trgm_ops);

-- 2. Add an 'insight_type' or 'source' column (Optional)
-- This helps the planner distinguish between "DB Insights" and "User Preferences"
ALTER TABLE public.swarm_memory ADD COLUMN IF NOT EXISTS source_agent STRING DEFAULT 'unknown';

SELECT
    TO_CHAR(month, 'YYYY-MM-DD') AS month_str,
    amount
FROM
    revenue
WHERE
    month >= CURRENT_DATE - INTERVAL '6 months'
ORDER BY
    month ASC;

select * from revenue;

SELECT memory_key, memory_value, created_at 
FROM swarm_memory 
ORDER BY created_at DESC;

SELECT memory_value FROM swarm_memory WHERE memory_key ILIKE '%revenue%';
