-- Intermediate Model: int_sessions.sql
-- Grain: One row per GA4 session (user_pseudo_id + session_id)
-- Description: Aggregates event-level GA4 activity into clean session-level journeys,
-- capturing acquisition channels, landing pages, engagement duration, and purchase indicators.

WITH staged_events AS (
    SELECT *
    FROM `{{ target_dataset }}.stg_ga4_events`
    WHERE ga_session_id IS NOT NULL
),

session_summary AS (
    SELECT
        user_pseudo_id,
        ga_session_id AS session_id,
        session_key,
        MIN(event_date) AS session_date,
        MIN(event_timestamp) AS session_start_timestamp,
        MAX(event_timestamp) AS session_end_timestamp,

        -- First touchpoint dimensions for this session
        ARRAY_AGG(traffic_source IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS traffic_source,
        ARRAY_AGG(traffic_medium IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS traffic_medium,
        ARRAY_AGG(traffic_campaign IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS traffic_campaign,
        ARRAY_AGG(page_location IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS landing_page,
        ARRAY_AGG(device_category IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS device_category,
        ARRAY_AGG(geo_country IGNORE NULLS ORDER BY event_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS country,

        -- Activity metrics
        COUNT(1) AS event_count,
        COUNTIF(event_name = 'page_view') AS page_views,
        COUNTIF(event_name = 'view_item') AS item_views,
        COUNTIF(event_name = 'add_to_cart') AS add_to_cart_count,
        COUNTIF(event_name = 'begin_checkout') AS begin_checkout_count,
        COUNTIF(event_name = 'purchase') AS purchase_count,
        MAX(COALESCE(engaged_session_event, 0)) AS reported_engagement_flag,
        COALESCE(SUM(purchase_revenue_in_usd), 0.0) AS session_revenue_usd

    FROM staged_events
    GROUP BY user_pseudo_id, ga_session_id, session_key
)

SELECT
    session_key,
    session_id,
    user_pseudo_id,
    session_date,
    session_start_timestamp,
    session_end_timestamp,
    TIMESTAMP_DIFF(session_end_timestamp, session_start_timestamp, SECOND) AS session_duration_seconds,

    -- Technology and Geography context
    device_category,
    country,

    -- Acquisition channels
    traffic_source,
    traffic_medium,
    traffic_campaign,
    landing_page,

    -- Engagement and Funnel Progression
    event_count,
    page_views,
    item_views,
    add_to_cart_count,
    begin_checkout_count,
    CASE
        WHEN reported_engagement_flag = 1
          OR TIMESTAMP_DIFF(session_end_timestamp, session_start_timestamp, SECOND) >= 10
          OR page_views >= 2
        THEN 1
        ELSE 0
    END AS is_engaged_session,

    -- E-commerce conversion indicator
    CASE WHEN purchase_count > 0 THEN 1 ELSE 0 END AS has_purchase,
    purchase_count,
    session_revenue_usd

FROM session_summary
