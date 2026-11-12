-- Mart Model: fct_attribution.sql
-- Grain: One row per order_id with attributed channel credit
-- Model: Deterministic Last Non-Direct Touch Attribution (standard Google Analytics baseline)
-- Logic: If a session touchpoint preceding the conversion was a non-direct channel, credit that channel;
-- if only direct touches exist in the lookback window, fallback to Direct.

WITH session_touchpoints AS (
    SELECT
        session_key,
        user_pseudo_id,
        session_date,
        session_start_timestamp,
        traffic_source,
        traffic_medium,
        traffic_campaign,
        CASE
            WHEN traffic_medium IN ('cpc', 'ppc') AND traffic_source = 'google' THEN 'Paid Search'
            WHEN traffic_medium = 'social_paid' OR traffic_source IN ('facebook', 'instagram') THEN 'Paid Social'
            WHEN traffic_medium = 'display' THEN 'Display'
            WHEN traffic_medium = 'video' OR traffic_source = 'youtube' THEN 'Video'
            WHEN traffic_medium = 'affiliate' OR traffic_source = 'rakuten' THEN 'Affiliate'
            WHEN traffic_medium = 'organic' THEN 'Organic Search'
            WHEN traffic_medium = 'referral' THEN 'Referral'
            WHEN traffic_medium = 'email' THEN 'Email'
            ELSE 'Direct'
        END AS normalized_channel
    FROM `{{ target_dataset }}.int_sessions`
),

order_journeys AS (
    SELECT
        o.order_id,
        o.user_pseudo_id,
        o.order_date,
        o.order_timestamp,
        o.order_revenue_usd,
        s.normalized_channel,
        s.traffic_source,
        s.traffic_medium,
        s.traffic_campaign,
        s.session_start_timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY o.order_id
            ORDER BY
                -- Prioritize non-direct channels
                CASE WHEN s.normalized_channel != 'Direct' THEN 1 ELSE 2 END ASC,
                s.session_start_timestamp DESC
        ) AS touchpoint_rank
    FROM `{{ target_dataset }}.int_orders` o
    JOIN session_touchpoints s
      ON o.user_pseudo_id = s.user_pseudo_id
     AND s.session_start_timestamp <= o.order_timestamp
)

SELECT
    order_id,
    user_pseudo_id,
    order_date,
    order_timestamp,
    order_revenue_usd,
    normalized_channel AS attributed_channel,
    traffic_source AS attributed_source,
    traffic_medium AS attributed_medium,
    traffic_campaign AS attributed_campaign,
    'LAST_NON_DIRECT_TOUCH' AS attribution_model,
    1.0 AS conversion_credit,
    order_revenue_usd AS attributed_revenue_usd
FROM order_journeys
WHERE touchpoint_rank = 1
