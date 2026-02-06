-- PRICE vs DEMAND RELATIONSHIP

WITH base_metrics AS (

    SELECT
        AVG(sale_price) AS base_price,
        AVG(quantity)   AS base_demand
    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE sale_price > 0
      AND quantity > 0
),

discount_levels AS (

    SELECT explode(array(0,5,10,15,20,25,30,35,40,45,50)) AS discount_pct
),

simulated AS (

    SELECT
        d.discount_pct,

        b.base_price * (1 - d.discount_pct / 100.0) AS discounted_price,

        b.base_demand *
        (1 + (d.discount_pct * 0.02)) AS predicted_demand,

        b.base_price,
        b.base_demand

    FROM discount_levels d
    CROSS JOIN base_metrics b
),

final_calc AS (

    SELECT
        discount_pct,

        predicted_demand,

        discounted_price * predicted_demand AS revenue,

        (discounted_price * predicted_demand) * 0.25 AS profit,

        base_price,
        base_demand

    FROM simulated
)

SELECT
    discount_pct       AS discount_percent,

    ROUND(
        (predicted_demand / base_demand) * 100, 2
    ) AS demand_impact_percent,

    ROUND(
        (revenue / (base_price * base_demand)) * 100, 2
    ) AS revenue_impact_percent,

    ROUND(
        (profit / ((base_price * base_demand) * 0.25)) * 100, 2
    ) AS profit_impact_percent

FROM final_calc
ORDER BY discount_percent;
