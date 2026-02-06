WITH

sales_clean AS (

    SELECT
        product_name,
        category,
        quantity,
        weather,
        sale_date,

        MONTH(sale_date) AS month,

        CASE
            WHEN MONTH(sale_date) IN (12,1,2) THEN 'Winter'
            WHEN MONTH(sale_date) IN (3,4,5) THEN 'Summer'
            WHEN MONTH(sale_date) IN (6,7,8) THEN 'Rainy'
            ELSE 'Cloudy'
        END AS season

    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE sale_date IS NOT NULL
      AND quantity IS NOT NULL
),

-- LATEST DATE

latest_date AS (

    SELECT MAX(sale_date) AS max_date
    FROM sales_clean
),

-- RECENT (LAST 14 DAYS)

recent_sales AS (

    SELECT *
    FROM sales_clean
    WHERE sale_date >= (
        SELECT max_date - INTERVAL 14 DAYS
        FROM latest_date
    )
),

-- BASELINE (PREVIOUS 90 DAYS, EXCLUDE RECENT)

baseline_sales AS (

    SELECT *
    FROM sales_clean
    WHERE sale_date < (
        SELECT max_date - INTERVAL 14 DAYS
        FROM latest_date
    )
    AND sale_date >= (
        SELECT max_date - INTERVAL 104 DAYS
        FROM latest_date
    )
),

-- LIVE VELOCITY

live_velocity AS (

    SELECT
        product_name,
        category,
        MAX(weather) AS weather,
        SUM(quantity) AS current_velocity
    FROM recent_sales
    GROUP BY product_name, category
),

-- BASELINE VELOCITY (PER 14 DAYS WINDOW)

baseline_velocity AS (

    SELECT
        product_name,
        category,

        -- normalize to 14-day average
        AVG(quantity) * 14 AS baseline_velocity

    FROM baseline_sales
    GROUP BY product_name, category
),

-- NEXT SEASON

next_month_calc AS (

    SELECT
        (MONTH(MAX(sale_date)) % 12) + 1 AS next_month
    FROM sales_clean
),

next_season AS (

    SELECT
        CASE
            WHEN next_month IN (12,1,2) THEN 'Winter'
            WHEN next_month IN (3,4,5) THEN 'Summer'
            WHEN next_month IN (6,7,8) THEN 'Rainy'
            ELSE 'Cloudy'
        END AS next_season
    FROM next_month_calc
),

-- SEASONAL FORECAST

seasonal_forecast AS (

    SELECT
        s.product_name,
        s.category,

        CASE
            WHEN AVG(s.quantity) >= 15 THEN 'Very High'
            WHEN AVG(s.quantity) >= 8 THEN 'High'
            WHEN AVG(s.quantity) >= 4 THEN 'Moderate'
            ELSE 'Low'
        END AS forecasted_demand

    FROM sales_clean s
    CROSS JOIN next_season ns
    WHERE s.season = ns.next_season
    GROUP BY s.product_name, s.category
)

-- FINAL OUTPUT

SELECT
    l.product_name AS `Product Name`,
    l.category     AS `Category`,

    -- REAL % CHANGE
    CONCAT(
        CASE
            WHEN (l.current_velocity / b.baseline_velocity - 1) * 100 >= 0
                THEN '+'
            ELSE ''
        END,
        ROUND((l.current_velocity / b.baseline_velocity - 1) * 100, 1),
        '% vs avg'
    ) AS `Current Velocity`,

    CASE
        WHEN l.current_velocity / b.baseline_velocity >= 1.5 THEN 'High'
        WHEN l.current_velocity / b.baseline_velocity >= 1.1 THEN 'Medium'
        ELSE 'Low'
    END AS `Stock Status`,

    l.weather AS `Weather`,

    f.forecasted_demand AS `Forecasted Demand`

FROM live_velocity l
JOIN baseline_velocity b
  ON l.product_name = b.product_name
 AND l.category = b.category

LEFT JOIN seasonal_forecast f
  ON l.product_name = f.product_name
 AND l.category = f.category

WHERE b.baseline_velocity > 0

ORDER BY
    l.current_velocity DESC;
