-- =====================================================
-- MARKET SHARE (%) BY PLATFORM
-- =====================================================

WITH revenue_by_channel AS (
    SELECT
        platform,
        SUM(sale_price) AS revenue
    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE sale_price IS NOT NULL
    GROUP BY platform
),

total_revenue AS (
    SELECT
        SUM(revenue) AS total_revenue
    FROM revenue_by_channel
)

SELECT
    r.platform,
    ROUND((r.revenue / t.total_revenue) * 100, 2) AS market_share_percentage
FROM revenue_by_channel r
CROSS JOIN total_revenue t
ORDER BY market_share_percentage DESC;
