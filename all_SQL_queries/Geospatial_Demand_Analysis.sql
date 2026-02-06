WITH nearby_sales AS (
  SELECT
    r.order_id,
    r.product_name,
    r.city,

    r.lat AS return_lat,
    r.lon AS return_lon,

    s.platform,
    s.quantity,

    s.lat AS sale_lat,
    s.lon AS sale_lon,

    -- Haversine Distance (KM)
    6371 * 2 * ASIN(
      SQRT(
        POWER(SIN(RADIANS(s.lat - r.lat) / 2), 2) +
        COS(RADIANS(r.lat)) *
        COS(RADIANS(s.lat)) *
        POWER(SIN(RADIANS(s.lon - r.lon) / 2), 2)
      )
    ) AS distance_km

  FROM workspace.sell_near_me.amazon_flipkart_returns_mixed_220_1 r
  JOIN workspace.sell_near_me.instant_delivery_sales_mixed_260 s
    ON r.product_name = s.product_name

  WHERE r.lat IS NOT NULL
    AND r.lon IS NOT NULL
    AND s.lat IS NOT NULL
    AND s.lon IS NOT NULL
)

, summary AS (
  SELECT
    order_id,
    product_name,
    city,
    return_lat,
    return_lon,

    MIN(distance_km) AS min_distance_km,
    SUM(quantity) AS total_qty,
    MAX(platform) AS best_app,
    AVG(distance_km) AS avg_distance

  FROM nearby_sales

  -- Filter within 15 KM radius
  WHERE distance_km <= 15

  GROUP BY
    order_id,
    product_name,
    city,
    return_lat,
    return_lon
)

SELECT
  order_id,
  product_name,
  city,
  return_lat,
  return_lon,

  min_distance_km,
  total_qty,
  best_app,
  avg_distance,

  CASE
    WHEN total_qty < 5 THEN 'NO'

    WHEN (
      0.5 * (15 - avg_distance)/15 +
      0.3 * LEAST(total_qty/30, 1) +
      0.2 * 1.0
    ) * 100 >= 70 THEN 'YES'

    WHEN (
      0.5 * (15 - avg_distance)/15 +
      0.3 * LEAST(total_qty/30, 1) +
      0.2 * 1.0
    ) * 100 >= 40 THEN 'MAYBE'

    ELSE 'NO'
  END AS sell_near_me,

  ROUND((
    0.5 * (15 - avg_distance)/15 +
    0.3 * LEAST(total_qty/30, 1) +
    0.2 * 1.0
  ) * 100) AS sell_confidence

FROM summary;
