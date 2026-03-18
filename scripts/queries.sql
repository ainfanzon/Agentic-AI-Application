
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
