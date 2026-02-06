-- =====================================================
-- PAGE 2: WEATHER IMPACT STATISTICS
-- =====================================================
WITH base AS (
    SELECT
        weather,
        category,
        sale_price
    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE weather IS NOT NULL
      AND category IS NOT NULL
      AND sale_price IS NOT NULL
),

total_txn AS (
    SELECT
        COUNT(*) AS total_transactions
    FROM base
)

SELECT
    b.weather,
    COUNT(*) AS total_transactions,
    ROUND(AVG(b.sale_price), 0) AS avg_order_value,
    ROUND(
        COUNT(*) * 100.0 / t.total_transactions,
        2
    ) AS market_share_percent
FROM base b
CROSS JOIN total_txn t
GROUP BY b.weather, t.total_transactions
ORDER BY total_transactions DESC;
