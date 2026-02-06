-- MANUAL INPUT

WITH input AS (
    SELECT
        'I phone'     AS product_name,
        'Smart Phone' AS category,
        25000         AS original_price,
        'Winter'      AS weather,
        'Ahmedabad'   AS city
),

-- AGGREGATED SALES

sales_features AS (
    SELECT
        category,
        city,
        weather,
        platform,
        AVG(sale_price) AS avg_price,
        COUNT(*)        AS total_qty
    FROM workspace.sell_near_me.instant_delivery_sales_mixed_260
    WHERE category IS NOT NULL
      AND city IS NOT NULL
      AND weather IS NOT NULL
      AND platform IS NOT NULL
      AND sale_price IS NOT NULL
    GROUP BY category, city, weather, platform
),

-- BEST PLATFORM (STRICT MATCH)

best_platform_exact AS (
    SELECT
        category,
        city,
        weather,
        platform,
        total_qty,
        RANK() OVER (
            PARTITION BY category, city, weather
            ORDER BY total_qty DESC
        ) AS rnk
    FROM sales_features
),

-- BEST PLATFORM PER CITY (FALLBACK)

best_platform_city AS (
    SELECT
        city,
        platform,
        SUM(total_qty) AS total_sales,
        RANK() OVER (
            PARTITION BY city
            ORDER BY SUM(total_qty) DESC
        ) AS rnk
    FROM sales_features
    GROUP BY city, platform
),

-- MARKET PRICE

market_price AS (
    SELECT
        category,
        city,
        weather,
        PERCENTILE_APPROX(avg_price, 0.6) AS predicted_market_price
    FROM sales_features
    GROUP BY category, city, weather
),

-- SCORING

scoring AS (
    SELECT
        i.product_name,
        i.category,
        i.city,
        i.weather,
        i.original_price,

        -- Market Price Fallback
        COALESCE(
            mp.predicted_market_price,
            i.original_price * 1.1
        ) AS predicted_market_price,

        -- Demand Score
        CASE
            WHEN COALESCE(sf.total_qty,0) >= 30 THEN 0.9
            WHEN COALESCE(sf.total_qty,0) >= 15 THEN 0.7
            WHEN COALESCE(sf.total_qty,0) >= 5  THEN 0.4
            ELSE 0.2
        END AS demand_score,

        -- Price Score
        CASE
            WHEN i.original_price <=
                 COALESCE(mp.predicted_market_price, i.original_price * 1.1)
            THEN 1.0
            ELSE 0.6
        END AS price_score,

        -- Weather Score
        CASE
            WHEN i.weather = 'Winter'
             AND i.category IN ('Heater','Blanket','Jacket','Sweater','Smart Phone')
                THEN 1.15
            WHEN i.weather = 'Summer'
             AND i.category IN ('AC','Cooler','Fan','Refrigerator')
                THEN 1.15
            ELSE 0.8
        END AS weather_score,

        -- Platform Selection (NO FAKE DEFAULT)
        COALESCE(
            bpe.platform,   -- Exact match
            bpc.platform    -- City best
        ) AS recommended_app


    FROM input i

    LEFT JOIN sales_features sf
        ON i.category = sf.category
       AND i.city     = sf.city
       AND i.weather  = sf.weather

    LEFT JOIN market_price mp
        ON i.category = mp.category
       AND i.city     = mp.city
       AND i.weather  = mp.weather

    -- Exact platform
    LEFT JOIN best_platform_exact bpe
        ON i.category = bpe.category
       AND i.city     = bpe.city
       AND i.weather  = bpe.weather
       AND bpe.rnk = 1

    -- City fallback
    LEFT JOIN best_platform_city bpc
        ON i.city = bpc.city
       AND bpc.rnk = 1
)

-- FINAL RESULT

SELECT
    product_name,
    category,
    city,
    weather,

    recommended_app,

    ROUND(predicted_market_price,2) AS predicted_market_price,

    ROUND(
        LEAST(
            GREATEST(
                (0.5*demand_score +
                 0.3*price_score +
                 0.2*weather_score),
                0.05
            ),
            0.95
        )*100,
        2
    ) AS sell_probability_percent,

    ROUND(
        predicted_market_price - original_price - 60,
        2
    ) AS estimated_profit,

    CASE
        WHEN predicted_market_price - original_price - 60 > 0
        THEN 'YES'
        ELSE 'NO'
    END AS price_acceptable

FROM scoring;
