-- Staging Model: stg_identity_mapping.sql
-- Grain: One row per user_pseudo_id
-- Description: Staging view for the deterministic synthetic identity mapping bridge.

SELECT
    mapping_id,
    user_pseudo_id,
    customer_id,
    resolution_status,
    link_method,
    confidence_score,
    PARSE_DATE('%Y-%m-%d', first_identified_date) AS first_identified_date,
    device_category,
    data_source,
    is_synthetic,
    simulation_seed
FROM `{{ target_dataset }}.synthetic_identity_mapping`
