-- =====================================================
-- PLATFORM PERFORMANCE METRICS (BASED ON AVAILABLE DATA)
-- =====================================================

SELECT
    platform,

    COUNT(transaction_id) AS total_orders,

    COUNT(DISTINCT product_name) AS unique_products,

    ROUND(AVG(sale_price), 2) AS avg_order_value,

    ROUND(SUM(sale_price), 2) AS total_sales

FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
WHERE platform IS NOT NULL
  AND sale_price IS NOT NULL
GROUP BY platform
ORDER BY total_sales DESC;
