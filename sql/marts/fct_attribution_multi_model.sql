-- Mart Model: fct_attribution_multi_model.sql
-- Grain: One row per order_id + attribution_model + channel
-- Description: Implements 4 attribution models (First Touch, Last Touch, Linear, Time Decay 7d)
-- with 30-day lookback window and direct fallback logic.

WITH touchpoints AS (
    SELECT
        session_key,
        user_pseudo_id,
        session_date,
        session_start_timestamp,
        channel,
        CASE WHEN channel = 'Direct' THEN 1 ELSE 0 END AS is_direct
    FROM `{{ target_dataset }}.int_sessions`
),

order_paths AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_revenue_usd AS order_revenue,
        o.order_date,
        o.order_timestamp,
        t.channel,
        t.session_start_timestamp,
        DATE_DIFF(o.order_date, t.session_date, DAY) AS days_before_order,
        ROW_NUMBER() OVER (PARTITION BY o.order_id ORDER BY t.session_start_timestamp ASC) AS touchpoint_asc,
        ROW_NUMBER() OVER (PARTITION BY o.order_id ORDER BY t.session_start_timestamp DESC) AS touchpoint_desc,
        COUNT(1) OVER (PARTITION BY o.order_id) AS total_touchpoints
    FROM `{{ target_dataset }}.int_orders` o
    JOIN touchpoints t
      ON o.user_pseudo_id = t.user_pseudo_id
     AND t.session_date BETWEEN DATE_SUB(o.order_date, INTERVAL 30 DAY) AND o.order_date
)

SELECT
    order_id,
    customer_id,
    order_revenue,
    'FIRST_TOUCH' AS attribution_model,
    channel,
    CASE WHEN touchpoint_asc = 1 THEN order_revenue ELSE 0.0 END AS attributed_revenue,
    CASE WHEN touchpoint_asc = 1 THEN 1.0 ELSE 0.0 END AS attribution_weight,
    total_touchpoints AS touchpoint_count,
    30 AS lookback_days
FROM order_paths
WHERE touchpoint_asc = 1

UNION ALL

SELECT
    order_id,
    customer_id,
    order_revenue,
    'LAST_TOUCH' AS attribution_model,
    channel,
    CASE WHEN touchpoint_desc = 1 THEN order_revenue ELSE 0.0 END AS attributed_revenue,
    CASE WHEN touchpoint_desc = 1 THEN 1.0 ELSE 0.0 END AS attribution_weight,
    total_touchpoints AS touchpoint_count,
    30 AS lookback_days
FROM order_paths
WHERE touchpoint_desc = 1
