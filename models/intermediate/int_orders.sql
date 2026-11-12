-- Intermediate Model: int_orders.sql
-- Grain: One row per unique order (transaction_id)
-- Description: Extracts, cleans, and deduplicates e-commerce orders from GA4 purchase events.
-- Deduplication Rule: When duplicate transaction_ids occur (e.g. from confirmation page refreshes),
-- the earliest recorded event timestamp is retained (ROW_NUMBER() OVER PARTITION BY transaction_id ORDER BY event_timestamp ASC).

WITH raw_purchases AS (
    SELECT
        transaction_id,
        event_date AS order_date,
        event_timestamp AS order_timestamp,
        user_pseudo_id,
        ga_session_id AS session_id,
        session_key,
        COALESCE(purchase_revenue_in_usd, purchase_revenue, 0.0) AS order_revenue_usd,
        COALESCE(tax_value_in_usd, 0.0) AS tax_usd,
        COALESCE(shipping_value_in_usd, 0.0) AS shipping_usd,
        COALESCE(total_item_quantity, 1) AS total_item_quantity,
        device_category,
        traffic_source,
        traffic_medium,
        traffic_campaign,
        ROW_NUMBER() OVER (
            PARTITION BY transaction_id
            ORDER BY event_timestamp ASC, purchase_revenue_in_usd DESC
        ) AS transaction_instance_rank
    FROM `{{ target_dataset }}.stg_ga4_events`
    WHERE event_name = 'purchase'
      AND transaction_id IS NOT NULL
      AND transaction_id != '(not set)'
      AND transaction_id != ''
)

SELECT
    transaction_id AS order_id,
    order_date,
    order_timestamp,
    user_pseudo_id,
    session_id,
    session_key,

    -- Financial attributes
    order_revenue_usd,
    tax_usd,
    shipping_usd,
    total_item_quantity,
    ROUND(order_revenue_usd - tax_usd - shipping_usd, 2) AS net_merchandise_revenue_usd,

    -- Context attributes
    device_category,
    traffic_source,
    traffic_medium,
    traffic_campaign

FROM raw_purchases
WHERE transaction_instance_rank = 1
