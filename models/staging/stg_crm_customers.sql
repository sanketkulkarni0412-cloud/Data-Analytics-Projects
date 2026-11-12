-- Staging Model: stg_crm_customers.sql
-- Grain: One row per customer_id
-- Description: Staging view for synthetic CRM customer records.

SELECT
    customer_id,
    synthetic_first_name,
    synthetic_last_name,
    synthetic_email,
    PARSE_DATE('%Y-%m-%d', signup_date) AS signup_date,
    customer_tier,
    country,
    preferred_device,
    is_loyalty_member,
    opted_in_email,
    churn_risk_level,
    data_source,
    is_synthetic,
    simulation_seed
FROM `{{ target_dataset }}.synthetic_crm_customers`
