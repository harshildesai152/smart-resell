-- =====================================================
-- PYTHON-EQUIVALENT DEMAND MATCHING (PER RETURN)
-- =====================================================

WITH recent_returns AS (
    SELECT
        r.product_name,
        INITCAP(r.category) AS category,
        r.city,
        CAST(r.lat AS DOUBLE) AS r_lat,
        CAST(r.lon AS DOUBLE) AS r_lon,
        r.return_date,
        ROW_NUMBER() OVER (ORDER BY r.return_date DESC) AS return_rank
    FROM workspace.sell_near_me.amazon_flipkart_returns_mixed_220_1 r
    WHERE r.lat IS NOT NULL
      AND r.lon IS NOT NULL
),

-- only latest 8 (same as Python)
latest_returns AS (
    SELECT *
    FROM recent_returns
    WHERE return_rank <= 8
),

sales_clean AS (
    SELECT
        INITCAP(category) AS category,
        platform,
        CAST(lat AS DOUBLE) AS s_lat,
        CAST(lon AS DOUBLE) AS s_lon,
        sale_date,
        INITCAP(weather) AS weather,
        1 AS qty
    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE lat IS NOT NULL
      AND lon IS NOT NULL
),

distance_calc AS (
    SELECT
        r.return_rank,
        r.product_name,
        r.category,
        r.city,
        s.platform,
        s.sale_date,
        s.weather,
        s.qty,

        -- HAVERSINE (KM)
        6371 * 2 * ASIN(
            SQRT(
                POWER(SIN(RADIANS(s.s_lat - r.r_lat) / 2), 2) +
                COS(RADIANS(r.r_lat)) *
                COS(RADIANS(s.s_lat)) *
                POWER(SIN(RADIANS(s.s_lon - r.r_lon) / 2), 2)
            )
        ) AS distance_km

    FROM latest_returns r
    JOIN sales_clean s
      ON r.category = s.category
),

ranked_knn AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY return_rank
               ORDER BY distance_km
           ) AS rn
    FROM distance_calc
)

SELECT
    product_name,
    category,
    city,
    sale_date AS DATE,
    platform AS app_channel,
    ROUND(distance_km, 2) AS distance_km,
    weather,
    qty
FROM ranked_knn
WHERE rn <= 5
ORDER BY return_rank, distance_km;
