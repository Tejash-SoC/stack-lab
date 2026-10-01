-- name: 01 Total revenue, profit and margin
SELECT ROUND(SUM(revenue), 0)                          AS revenue,
       ROUND(SUM(revenue - cost), 0)                   AS profit,
       ROUND(100.0 * SUM(revenue - cost) / SUM(revenue), 1) AS margin_pct
FROM sales_lines;

-- name: 02 Monthly revenue with month-over-month growth (CTE + LAG)
WITH monthly AS (
    SELECT substr(order_date, 1, 7) AS month, SUM(revenue) AS revenue
    FROM sales_lines
    GROUP BY 1
)
SELECT month,
       ROUND(revenue, 0) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- name: 03 Category revenue vs margin
SELECT category,
       ROUND(SUM(revenue), 0) AS revenue,
       ROUND(100.0 * SUM(revenue - cost) / SUM(revenue), 1) AS margin_pct,
       ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM sales_lines), 1) AS revenue_share_pct
FROM sales_lines
GROUP BY category
ORDER BY revenue DESC;

-- name: 04 Margin by discount level
SELECT discount_pct,
       COUNT(*) AS order_lines,
       ROUND(100.0 * SUM(revenue - cost) / SUM(revenue), 1) AS margin_pct
FROM sales_lines
GROUP BY discount_pct
ORDER BY discount_pct;

-- name: 05 Top 10 customers by revenue (window RANK)
SELECT RANK() OVER (ORDER BY SUM(revenue) DESC) AS rnk,
       customer_id,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(revenue), 0)   AS revenue
FROM sales_lines
GROUP BY customer_id
ORDER BY rnk
LIMIT 10;

-- name: 06 Repeat-customer rate
WITH per_customer AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS orders
    FROM sales_lines
    GROUP BY customer_id
)
SELECT COUNT(*)                                             AS customers,
       SUM(orders >= 2)                                     AS repeat_customers,
       ROUND(100.0 * SUM(orders >= 2) / COUNT(*), 1)        AS repeat_rate_pct
FROM per_customer;

-- name: 07 Repeat rate by acquisition channel
WITH per_customer AS (
    SELECT s.customer_id, c.acquisition_channel, COUNT(DISTINCT s.order_id) AS orders
    FROM sales_lines s
    JOIN customers c ON c.customer_id = s.customer_id
    GROUP BY s.customer_id, c.acquisition_channel
)
SELECT acquisition_channel,
       COUNT(*) AS customers,
       ROUND(100.0 * SUM(orders >= 2) / COUNT(*), 1) AS repeat_rate_pct
FROM per_customer
GROUP BY acquisition_channel
ORDER BY repeat_rate_pct DESC;

-- name: 08 Customers at risk: 2+ orders but nothing in the last 90 days
WITH last_seen AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS orders, MAX(order_date) AS last_order
    FROM sales_lines
    GROUP BY customer_id
)
SELECT COUNT(*) AS at_risk_customers
FROM last_seen
WHERE orders >= 2
  AND julianday((SELECT MAX(order_date) FROM sales_lines)) - julianday(last_order) > 90;

-- name: 09 Average rating by days late
WITH d AS (
    SELECT rating,
           MAX(CAST(julianday(delivery_date) - julianday(order_date) AS INTEGER) - promised_days, 0) AS days_late
    FROM clean_orders
    WHERE status = 'Delivered' AND rating IS NOT NULL
)
SELECT CASE WHEN days_late = 0  THEN '1 On time'
            WHEN days_late <= 2 THEN '2 1-2 days late'
            WHEN days_late <= 4 THEN '3 3-4 days late'
            ELSE '4 5+ days late' END AS bucket,
       COUNT(*)              AS rated_orders,
       ROUND(AVG(rating), 2) AS avg_rating
FROM d
GROUP BY bucket
ORDER BY bucket;
