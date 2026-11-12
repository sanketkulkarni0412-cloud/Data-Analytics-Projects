-- Staging Model: stg_ad_spend.sql
-- Grain: One row per spend_date + campaign_id
-- Description: Staging view for synthetic advertising campaign spend and engagement.

SELECT
    spend_id,
    PARSE_DATE('%Y-%m-%d', spend_date) AS spend_date,
    campaign_id,
    channel,
    campaign_name,
    utm_source,
    utm_medium,
    utm_campaign,
    daily_spend_usd,
    impressions,
    clicks,
    conversions,
    cpm,
    ctr_pct,
    cpc_usd,
    cvr_pct,
    data_source,
    is_synthetic,
    simulation_seed
FROM `{{ target_dataset }}.synthetic_ad_spend`
