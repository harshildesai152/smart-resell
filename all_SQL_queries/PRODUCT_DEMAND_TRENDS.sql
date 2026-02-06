-- =====================================================
-- PRODUCT DEMAND TRENDS (MONTHLY LINE DATA)
-- =====================================================

SELECT
    MONTH(sale_date) AS month,
    product_name,
    SUM(quantity) AS total_quantity
FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
WHERE sale_date IS NOT NULL
  AND quantity IS NOT NULL
GROUP BY
    MONTH(sale_date),
    product_name
ORDER BY
    month,
    product_name;
