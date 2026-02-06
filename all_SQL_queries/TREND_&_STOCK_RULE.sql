WITH category_sales AS (
    SELECT
        category,
        SUM(sale_price) AS sales_value
    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE category IS NOT NULL
      AND sale_price IS NOT NULL
    GROUP BY category
),

overall_avg AS (
    SELECT
        AVG(sales_value) AS avg_sales
    FROM category_sales
)

SELECT
    cs.category,
    ROUND(cs.sales_value, 0) AS sales_value,

    ROUND(
        (cs.sales_value - oa.avg_sales) * 100.0 / oa.avg_sales,
        2
    ) AS trend_vs_avg,

    CASE
        WHEN (cs.sales_value - oa.avg_sales) * 100.0 / oa.avg_sales >= 10
            THEN 'High Priority'
        WHEN (cs.sales_value - oa.avg_sales) * 100.0 / oa.avg_sales >= 0
            THEN 'Medium Priority'
        ELSE 'Low Priority'
    END AS recommended_stock

FROM category_sales cs
CROSS JOIN overall_avg oa
ORDER BY sales_value DESC;
