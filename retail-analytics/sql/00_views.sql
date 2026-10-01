-- Cleaned order header: the raw file contains exact duplicate rows.
CREATE VIEW clean_orders AS
SELECT DISTINCT order_id, customer_id, order_date, status, promised_days,
       ship_date, delivery_date, rating
FROM orders;

-- One row per delivered order line, with revenue and cost worked out.
CREATE VIEW sales_lines AS
SELECT o.order_id, o.customer_id, o.order_date, p.category, i.discount_pct, i.quantity,
       p.list_price * i.quantity * (1 - i.discount_pct / 100.0) AS revenue,
       p.unit_cost  * i.quantity                                  AS cost
FROM order_items i
JOIN clean_orders o ON o.order_id = i.order_id
JOIN products p     ON p.product_id = i.product_id
WHERE o.status = 'Delivered';
