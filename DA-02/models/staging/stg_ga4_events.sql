-- Staging Model: stg_ga4_events.sql
-- Source: bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*
-- Description: Flattens and cleans raw GA4 event telemetry, unnesting critical parameters
-- and standardizing data types for sessionization and attribution modeling.

WITH raw_events AS (
    SELECT
        PARSE_DATE('%Y%m%d', event_date) AS event_date,
        TIMESTAMP_MICROS(event_timestamp) AS event_timestamp,
        event_timestamp AS event_timestamp_micros,
        event_name,
        user_pseudo_id,
        user_id,
        event_previous_timestamp,
        event_value_in_usd,

        -- Unnest key event parameters
        (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
        (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_number') AS ga_session_number,
        (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location') AS page_location,
        (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_title') AS page_title,
        (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_referrer') AS page_referrer,
        (SELECT COALESCE(value.string_value, CAST(value.int_value AS STRING)) FROM UNNEST(event_params) WHERE key = 'source') AS event_param_source,
        (SELECT COALESCE(value.string_value, CAST(value.int_value AS STRING)) FROM UNNEST(event_params) WHERE key = 'medium') AS event_param_medium,
        (SELECT COALESCE(value.string_value, CAST(value.int_value AS STRING)) FROM UNNEST(event_params) WHERE key = 'campaign') AS event_param_campaign,
        (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'term') AS event_param_term,
        (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'content') AS event_param_content,
        (SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'engaged_session_event') AS engaged_session_event,

        -- Device information
        device.category AS device_category,
        device.mobile_brand_name AS device_mobile_brand,
        device.operating_system AS device_operating_system,
        device.operating_system_version AS device_os_version,
        device.web_info.browser AS device_browser,

        -- Geo information
        geo.continent AS geo_continent,
        geo.sub_continent AS geo_sub_continent,
        geo.country AS geo_country,
        geo.region AS geo_region,
        geo.city AS geo_city,
        geo.metro AS geo_metro,

        -- User acquisition traffic source
        traffic_source.name AS user_acquisition_campaign,
        traffic_source.medium AS user_acquisition_medium,
        traffic_source.source AS user_acquisition_source,

        -- Ecommerce information
        ecommerce.total_item_quantity AS total_item_quantity,
        ecommerce.purchase_revenue_in_usd AS purchase_revenue_in_usd,
        ecommerce.purchase_revenue AS purchase_revenue,
        ecommerce.refund_value_in_usd AS refund_value_in_usd,
        ecommerce.shipping_value_in_usd AS shipping_value_in_usd,
        ecommerce.tax_value_in_usd AS tax_value_in_usd,
        ecommerce.transaction_id AS transaction_id,

        -- Table suffix for date partitioning
        _TABLE_SUFFIX AS table_date_suffix

    FROM `{{ source_project }}.{{ source_dataset }}.{{ source_table_prefix }}`
)

SELECT
    -- Unique surrogate event identifier
    FARM_FINGERPRINT(CONCAT(user_pseudo_id, CAST(event_timestamp_micros AS STRING), event_name)) AS event_surrogate_key,

    -- Composite session key (user + session ID)
    CONCAT(user_pseudo_id, '-', CAST(ga_session_id AS STRING)) AS session_key,

    -- Temporal attributes
    event_date,
    event_timestamp,
    event_timestamp_micros,
    table_date_suffix,

    -- Behavioral action
    event_name,

    -- Identifiers
    user_pseudo_id,
    user_id,
    ga_session_id,
    ga_session_number,

    -- Page & Content context
    page_location,
    page_title,
    page_referrer,

    -- Channel & Attribution dimensions (coalescing event params with user acquisition fallback)
    COALESCE(event_param_source, user_acquisition_source, '(direct)') AS traffic_source,
    COALESCE(event_param_medium, user_acquisition_medium, '(none)') AS traffic_medium,
    COALESCE(event_param_campaign, user_acquisition_campaign, '(organic)') AS traffic_campaign,
    event_param_term AS traffic_term,
    event_param_content AS traffic_content,

    -- Engagement flags
    engaged_session_event,

    -- Device & Tech context
    device_category,
    device_mobile_brand,
    device_operating_system,
    device_os_version,
    device_browser,

    -- Geography context
    geo_continent,
    geo_sub_continent,
    geo_country,
    geo_region,
    geo_city,
    geo_metro,

    -- E-commerce transactions
    transaction_id,
    total_item_quantity,
    purchase_revenue_in_usd,
    purchase_revenue,
    refund_value_in_usd,
    shipping_value_in_usd,
    tax_value_in_usd,

    -- Funnel indicator flags
    CASE WHEN event_name = 'session_start' THEN 1 ELSE 0 END AS is_session_start,
    CASE WHEN event_name = 'view_item' THEN 1 ELSE 0 END AS is_view_item,
    CASE WHEN event_name = 'add_to_cart' THEN 1 ELSE 0 END AS is_add_to_cart,
    CASE WHEN event_name = 'begin_checkout' THEN 1 ELSE 0 END AS is_begin_checkout,
    CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END AS is_purchase

FROM raw_events
