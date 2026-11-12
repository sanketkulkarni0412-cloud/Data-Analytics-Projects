-- Mart Model: fct_customer_clv.sql
-- Grain: One row per customer_id
-- Description: Computes historical customer lifetime value and predicted 12-month forward CLV.
-- Governance: Uses 45% contribution margin explicitly labeled as an ILLUSTRATIVE SCENARIO ASSUMPTION.

SELECT
    customer_id,
    customer_tier,
    signup_date,
    historical_revenue,
    order_count,
    average_order_value,
    purchase_frequency,
    customer_lifespan_days,
    ROUND(historical_revenue * 0.45, 2) AS historical_clv,
    predicted_12m_clv,
    clv_segment,
    45.0 AS illustrative_contribution_margin_pct,
    'LOCAL_VALIDATION_SCENARIO' AS data_lineage_tag
FROM `{{ target_dataset }}.customer_profile`
