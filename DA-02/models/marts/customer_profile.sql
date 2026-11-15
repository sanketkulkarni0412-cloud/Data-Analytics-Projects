-- Mart Model: customer_profile.sql
-- Grain: One row per customer_id
-- Description: Unifies synthetic CRM customer profiles, deterministic synthetic identity mappings,
-- and aggregated GA4 behavioral and transactional event histories.
-- Governance Notice: Clearly differentiates authentic GA4 metrics from synthetic CRM/mapping attributes.

WITH crm_customers AS (
    SELECT
        customer_id,
        signup_date,
        customer_tier,
        country AS crm_country,
        preferred_device AS crm_preferred_device,
        is_loyalty_member,
        opted_in_email,
        churn_risk_level,
        data_source AS crm_data_source
    FROM `{{ target_dataset }}.stg_crm_customers`
),

identity_bridge AS (
    -- Collapse multiple cookies per customer if cross-device
    SELECT
        customer_id,
        ARRAY_AGG(user_pseudo_id) AS linked_user_pseudo_ids,
        COUNT(DISTINCT user_pseudo_id) AS distinct_devices_count,
        MAX(confidence_score) AS max_identity_confidence,
        ARRAY_AGG(link_method IGNORE NULLS ORDER BY confidence_score DESC LIMIT 1)[SAFE_OFFSET(0)] AS primary_link_method,
        MIN(first_identified_date) AS first_identified_date
    FROM `{{ target_dataset }}.stg_identity_mapping`
    WHERE resolution_status = 'RESOLVED'
      AND customer_id != 'UNRESOLVED_ANONYMOUS'
    GROUP BY customer_id
),

ga4_user_sessions AS (
    SELECT
        m.customer_id,
        MIN(s.session_date) AS first_session_date,
        MAX(s.session_date) AS last_session_date,
        COUNT(DISTINCT s.session_key) AS total_sessions,
        SUM(s.is_engaged_session) AS total_engaged_sessions,
        SUM(s.page_views) AS total_page_views,
        SUM(s.session_duration_seconds) AS total_duration_seconds,
        ARRAY_AGG(s.traffic_source IGNORE NULLS ORDER BY s.session_start_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS acquisition_source,
        ARRAY_AGG(s.traffic_medium IGNORE NULLS ORDER BY s.session_start_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS acquisition_medium,
        ARRAY_AGG(s.traffic_campaign IGNORE NULLS ORDER BY s.session_start_timestamp ASC LIMIT 1)[SAFE_OFFSET(0)] AS acquisition_campaign
    FROM `{{ target_dataset }}.stg_identity_mapping` m
    JOIN `{{ target_dataset }}.int_sessions` s
      ON m.user_pseudo_id = s.user_pseudo_id
    WHERE m.resolution_status = 'RESOLVED'
    GROUP BY m.customer_id
),

ga4_user_orders AS (
    SELECT
        m.customer_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COALESCE(SUM(o.order_revenue_usd), 0.0) AS total_revenue,
        MIN(o.order_date) AS first_order_date,
        MAX(o.order_date) AS last_order_date
    FROM `{{ target_dataset }}.stg_identity_mapping` m
    JOIN `{{ target_dataset }}.int_orders` o
      ON m.user_pseudo_id = o.user_pseudo_id
    WHERE m.resolution_status = 'RESOLVED'
    GROUP BY m.customer_id
)

SELECT
    -- =========================================================================
    -- TIER 2: SYNTHETIC CRM ATTRIBUTES (Explicitly Simulated)
    -- =========================================================================
    c.customer_id,
    c.signup_date,
    c.customer_tier,
    c.crm_country,
    c.crm_preferred_device,
    c.is_loyalty_member,
    c.opted_in_email,
    c.churn_risk_level,

    -- =========================================================================
    -- TIER 4: SYNTHETIC IDENTITY-MAPPING ATTRIBUTES (Simulated Bridge)
    -- =========================================================================
    CASE WHEN b.customer_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_linked_to_ga4_visitor,
    COALESCE(b.distinct_devices_count, 0) AS linked_ga4_devices_count,
    COALESCE(b.max_identity_confidence, 0.0) AS identity_resolution_confidence,
    COALESCE(b.primary_link_method, 'UNLINKED') AS identity_link_method,
    b.first_identified_date,

    -- =========================================================================
    -- TIER 1: AUTHENTIC GA4 BEHAVIORAL ATTRIBUTES (Real Event Aggregations)
    -- =========================================================================
    s.first_session_date,
    s.last_session_date,
    COALESCE(s.total_sessions, 0) AS total_sessions,
    COALESCE(s.total_engaged_sessions, 0) AS total_engaged_sessions,
    COALESCE(s.total_page_views, 0) AS total_page_views,
    COALESCE(s.total_duration_seconds, 0) AS total_duration_seconds,
    COALESCE(s.acquisition_source, '(none)') AS acquisition_source,
    COALESCE(s.acquisition_medium, '(none)') AS acquisition_medium,
    COALESCE(s.acquisition_campaign, '(none)') AS acquisition_campaign,

    -- =========================================================================
    -- TIER 1: AUTHENTIC GA4 TRANSACTIONAL ATTRIBUTES (Real E-commerce Orders)
    -- =========================================================================
    COALESCE(o.total_orders, 0) AS total_orders,
    ROUND(COALESCE(o.total_revenue, 0.0), 2) AS total_revenue,
    o.first_order_date,
    o.last_order_date,

    -- Derived behavioral KPIs
    CASE
        WHEN COALESCE(o.total_orders, 0) > 0 THEN ROUND(o.total_revenue / o.total_orders, 2)
        ELSE 0.0
    END AS average_order_value,

    CASE
        WHEN COALESCE(s.total_sessions, 0) > 0 THEN ROUND(COALESCE(o.total_orders, 0) / s.total_sessions, 4)
        ELSE 0.0
    END AS purchase_frequency,

    -- Days since last activity (evaluated against GA4 dataset close date: 2021-01-31)
    DATE_DIFF(DATE('2021-01-31'), COALESCE(s.last_session_date, PARSE_DATE('%Y-%m-%d', c.signup_date)), DAY) AS days_since_last_activity,

    -- Data Governance Traceability Flags
    'HYBRID_AGGREGATED_MART' AS mart_type,
    'AUTHENTIC_GA4_PLUS_SYNTHETIC_CRM_BRIDGE' AS data_lineage_classification

FROM crm_customers c
LEFT JOIN identity_bridge b ON c.customer_id = b.customer_id
LEFT JOIN ga4_user_sessions s ON c.customer_id = s.customer_id
LEFT JOIN ga4_user_orders o ON c.customer_id = o.customer_id
