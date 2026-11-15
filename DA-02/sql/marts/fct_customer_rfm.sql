-- Mart Model: fct_customer_rfm.sql
-- Grain: One row per customer_id
-- Description: Computes Recency, Frequency, and Monetary scores (NTILE 1-5) and assigns
-- strategic customer lifecycle segments (Champions, Loyal, Potential Loyalists, At Risk, Hibernating).

WITH customer_metrics AS (
    SELECT
        customer_id,
        signup_date,
        total_sessions,
        total_orders,
        total_revenue,
        days_since_last_activity,
        average_order_value,
        is_linked_to_ga4_visitor
    FROM `{{ target_dataset }}.customer_profile`
),

rfm_scoring AS (
    SELECT
        customer_id,
        signup_date,
        total_sessions,
        total_orders,
        total_revenue,
        days_since_last_activity,
        average_order_value,
        is_linked_to_ga4_visitor,

        -- Recency: fewer days since last activity = higher score (5 = most recent)
        NTILE(5) OVER (ORDER BY days_since_last_activity DESC) AS r_score,

        -- Frequency: more orders = higher score (5 = most frequent)
        NTILE(5) OVER (ORDER BY total_orders ASC) AS f_score,

        -- Monetary: higher revenue = higher score (5 = top spender)
        NTILE(5) OVER (ORDER BY total_revenue ASC) AS m_score

    FROM customer_metrics
)

SELECT
    customer_id,
    signup_date,
    total_sessions,
    total_orders,
    total_revenue,
    days_since_last_activity,
    average_order_value,
    is_linked_to_ga4_visitor,
    r_score,
    f_score,
    m_score,
    CONCAT(CAST(r_score AS STRING), CAST(f_score AS STRING), CAST(m_score AS STRING)) AS rfm_cell,
    ROUND((r_score + f_score + m_score) / 3.0, 2) AS composite_rfm_score,

    -- Strategic Segment Assignment
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Potential Loyalists'
        WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk High Value'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'At Risk Spenders'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating / Inactive'
        ELSE 'Promising / General'
    END AS rfm_segment

FROM rfm_scoring
