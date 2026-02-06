
-- PRODUCT LIFECYCLE ANALYSIS (SAFE VERSION)


WITH
sales_clean AS (

    SELECT
        product_name,
        quantity,
        sale_date,
        MONTH(sale_date) AS month
    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE sale_date IS NOT NULL
      AND quantity IS NOT NULL
),

-- MONTHLY DEMAND

monthly_demand AS (

    SELECT
        product_name,
        month,
        SUM(quantity) AS total_quantity
    FROM sales_clean
    GROUP BY product_name, month
),


-- TIME INDEX
demand_indexed AS (

    SELECT
        product_name,
        month,
        total_quantity,

        ROW_NUMBER() OVER (
            PARTITION BY product_name
            ORDER BY month
        ) AS time_index,

        COUNT(*) OVER (
            PARTITION BY product_name
        ) AS total_points

    FROM monthly_demand
),

-- SAFE TREND CALCULATION --Linear Regression

trend_calc AS (

    SELECT
        product_name,

        try_divide(
            COUNT(*) * SUM(time_index * total_quantity)
            - SUM(time_index) * SUM(total_quantity),

            COUNT(*) * SUM(time_index * time_index)
            - SUM(time_index) * SUM(time_index)
        ) AS slope,

        MAX(total_points) AS points

    FROM demand_indexed
    GROUP BY product_name
),

-- LIFECYCLE CLASSIFICATION

lifecycle AS (

    SELECT
        product_name,

        -- Demand Trend
        CASE
            WHEN points < 3 THEN 'Growing'
            WHEN slope IS NULL THEN 'Stable'
            WHEN slope > 1 THEN 'Growing'
            WHEN slope > -1 THEN 'Stable'
            ELSE 'Declining'
        END AS demand_trend,

        -- Lifecycle Stage
        CASE
            WHEN points < 3 THEN 'New'
            WHEN slope IS NULL THEN 'Mature'
            WHEN slope > 1 THEN 'New'
            WHEN slope > -1 THEN 'Mature'
            ELSE 'Declining'
        END AS lifecycle_stage,

        -- Action Recommendation
        CASE
            WHEN points < 3 THEN 'Increase inventory by 25%'
            WHEN slope IS NULL THEN 'Maintain current stock levels'
            WHEN slope > 1 THEN 'Increase inventory by 25%'
            WHEN slope > -1 THEN 'Maintain current stock levels'
            ELSE 'Reduce procurement by 40%'
        END AS action_recommendation

    FROM trend_calc
)

SELECT
    product_name,
    demand_trend,
    lifecycle_stage,
    action_recommendation
FROM lifecycle
ORDER BY product_name;
