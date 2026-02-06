
-- PROFIT IMPACT ANALYSIS (15% DISCOUNT)


WITH base_metrics AS (

    SELECT
        AVG(sale_price) AS base_price,
        AVG(quantity)   AS base_demand
    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE sale_price > 0
      AND quantity > 0
),

discount_sim AS (

    SELECT
        explode(array(0,5,10,15,20,25,30,35,40,45,50)) AS discount_pct
),

simulated AS (

    SELECT
        d.discount_pct,

        b.base_price * (1 - d.discount_pct / 100.0) AS discounted_price,

        b.base_demand *
        (1 + (d.discount_pct * 0.02)) AS predicted_demand,

        b.base_price,
        b.base_demand

    FROM discount_sim d
    CROSS JOIN base_metrics b
),

final_calc AS (

    SELECT
        discount_pct,

        discounted_price,
        predicted_demand,

        discounted_price * predicted_demand AS revenue,

        (discounted_price * predicted_demand) * 0.25 AS profit,

        base_price,
        base_demand

    FROM simulated
),

impact_calc AS (

    SELECT
        discount_pct,

        predicted_demand,
        revenue,
        profit,

        ROUND(
            (predicted_demand / base_demand) * 100, 2
        ) AS demand_impact,

        ROUND(
            (profit / ((base_price * base_demand) * 0.25)) * 100, 2
        ) AS profit_impact

    FROM final_calc
)

SELECT

    base.base_demand      AS base_demand_units,

    ROUND(
        base.base_demand * (i.demand_impact / 100)
    ) AS expected_demand_units,

    ROUND(i.revenue, 0) AS revenue_value,

    ROUND(i.profit_impact - 100, 2) AS profit_change_percent,

    CASE
        WHEN MIN(
            CASE WHEN profit_impact >= 100 THEN discount_pct END
        ) OVER () IS NULL
        THEN 'No Break-even'
        ELSE CONCAT(
            MIN(
                CASE WHEN profit_impact >= 100 THEN discount_pct END
            ) OVER (),
            '%'
        )
    END AS break_even_discount

FROM impact_calc i
CROSS JOIN base_metrics base

WHERE discount_pct = 15;
