WITH sales_monthly AS (
    SELECT
        DATE_FORMAT(s.sale_date, 'MMM') AS month_name,
        MONTH(s.sale_date) AS month_num,
        s.platform,
        LOWER(TRIM(s.product_name)) AS product_name,

        COUNT(*) AS total_sales,
        SUM(s.sale_price) AS revenue

    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260 s

    WHERE s.sale_date IS NOT NULL
      AND s.sale_price IS NOT NULL
      AND s.platform IN ('Blinkit','Swiggy Instamart','Zepto')

    GROUP BY
        month_name,
        month_num,
        platform,
        LOWER(TRIM(s.product_name))
),

returns_monthly AS (
    SELECT
        LOWER(TRIM(r.product_name)) AS product_name,
        COUNT(*) AS total_returns

    FROM workspace.sell_near_me.amazon_flipkart_returns_mixed_220_1 r

    WHERE r.product_name IS NOT NULL

    GROUP BY LOWER(TRIM(r.product_name))
),

final_data AS (
    SELECT
        s.month_name,
        s.month_num,
        s.platform,

        SUM(s.revenue) AS revenue,
        SUM(s.total_sales) AS total_sales,

        COALESCE(SUM(r.total_returns),0) AS total_returns

    FROM sales_monthly s

    LEFT JOIN returns_monthly r
      ON s.product_name = r.product_name

    GROUP BY
        s.month_name,
        s.month_num,
        s.platform
)

SELECT
    month_name AS month,
    platform,

    ROUND(revenue,2) AS revenue,
    total_sales,
    total_returns,

    ROUND(
        (total_returns * 100.0) / NULLIF(total_sales,0),
        2
    ) AS return_rate_percent,

    CASE
        WHEN (total_returns * 100.0) / NULLIF(total_sales,0) <= 10
             AND revenue >= (
                 SELECT AVG(sale_price)
                 FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
             )
        THEN 'SELL'

        WHEN (total_returns * 100.0) / NULLIF(total_sales,0) <= 20
        THEN 'MAYBE'

        ELSE 'DO NOT SELL'
    END AS sell_decision

FROM final_data

ORDER BY
    month_num,
    platform;
