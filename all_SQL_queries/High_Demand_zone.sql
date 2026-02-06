WITH
-- =====================================
-- SALES PER CITY
-- =====================================

city_sales AS (
    SELECT
        city,
        SUM(quantity) AS total_sales,
        AVG(lat) AS sale_lat,
        AVG(lon) AS sale_lon
    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE city IS NOT NULL
      AND lat IS NOT NULL
      AND lon IS NOT NULL
    GROUP BY city
),

-- =====================================
-- RETURNS PER CITY
-- =====================================

city_returns AS (
    SELECT
        city,
        COUNT(order_id) AS total_returns,
        AVG(lat) AS return_lat,
        AVG(lon) AS return_lon
    FROM workspace.sell_near_me.amazon_flipkart_returns_mixed_220_1
    WHERE city IS NOT NULL
      AND lat IS NOT NULL
      AND lon IS NOT NULL
    GROUP BY city
),

-- =====================================
-- MERGE SALES + RETURNS
-- =====================================

city_metrics AS (
    SELECT
        s.city,

        s.total_sales,
        COALESCE(r.total_returns,0) AS total_returns,

        s.sale_lat,
        s.sale_lon,

        r.return_lat,
        r.return_lon,

        -- Return Percentage
        ROUND(
            COALESCE(r.total_returns,0) * 100.0 /
            NULLIF(s.total_sales + COALESCE(r.total_returns,0),0),
            2
        ) AS return_pct

    FROM city_sales s
    LEFT JOIN city_returns r
      ON s.city = r.city
),

-- =====================================
-- DISTANCE CALCULATION (HAVERSINE)
-- =====================================

city_distance AS (
    SELECT
        m.*,

        -- Distance in KM
        6371 * 2 * ASIN(
            SQRT(
                POWER(SIN(RADIANS(m.sale_lat - m.return_lat) / 2), 2) +
                COS(RADIANS(m.return_lat)) *
                COS(RADIANS(m.sale_lat)) *
                POWER(SIN(RADIANS(m.sale_lon - m.return_lon) / 2), 2)
            )
        ) AS distance_km

    FROM city_metrics m
),

-- =====================================
-- GLOBAL AVERAGES
-- =====================================

global_avg AS (
    SELECT
        AVG(total_sales) AS avg_sales,
        AVG(return_pct) AS avg_return,
        AVG(distance_km) AS avg_distance
    FROM city_distance
),

-- =====================================
-- ZONE + SELL LOGIC
-- =====================================

zone_assign AS (
    SELECT
        d.city,

        d.total_sales,
        d.total_returns,
        d.return_pct,

        d.sale_lat,
        d.sale_lon,
        d.return_lat,
        d.return_lon,

        ROUND(d.distance_km,2) AS distance_km,

        CASE
            -- Best Case
            WHEN d.total_sales >= g.avg_sales
             AND d.return_pct <= g.avg_return
             AND d.distance_km <= 15
            THEN '🟢 High Demand / Low Return / Near Zone'

            -- High demand but risky
            WHEN d.total_sales >= g.avg_sales
             AND d.return_pct > g.avg_return
            THEN '🔴 High Demand / High Return'

            -- Low demand bad area
            WHEN d.total_sales < g.avg_sales
             AND d.return_pct > g.avg_return
            THEN '🟡 Low Demand / High Return'

            -- Stable
            ELSE '🟣 Stable Zone'
        END AS zone_type,


        -- SELL DECISION
        CASE
            WHEN d.distance_km <= 15
             AND d.return_pct <= 10
             AND d.total_sales >= g.avg_sales
            THEN 'SELL'

            WHEN d.distance_km <= 20
             AND d.return_pct <= 20
            THEN 'TEST SELL'

            ELSE 'DO NOT SELL'
        END AS sell_decision


    FROM city_distance d
    CROSS JOIN global_avg g
),

-- =====================================
-- RISK ANALYSIS
-- =====================================

risk_analysis AS (
    SELECT
        city,
        total_sales AS demand,
        return_pct,

        CASE
            WHEN return_pct >= 25 THEN 'High Risk'
            WHEN return_pct >= 12 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS risk_level

    FROM zone_assign
)

-- =====================================
-- FINAL OUTPUT
-- =====================================

SELECT
    z.city,

    z.total_sales,
    z.total_returns,
    z.return_pct,

    ROUND(z.sale_lat,4) AS sale_lat,
    ROUND(z.sale_lon,4) AS sale_lon,

    ROUND(z.return_lat,4) AS return_lat,
    ROUND(z.return_lon,4) AS return_lon,

    z.distance_km,

    z.zone_type,
    z.sell_decision,

    r.risk_level

FROM zone_assign z
LEFT JOIN risk_analysis r
  ON z.city = r.city

ORDER BY
    z.total_sales DESC,
    z.distance_km ASC;
