-- Mart Model: fct_campaign_roi.sql
-- Grain: One row per channel + campaign
-- Description: Reconciles advertising spend, clicks, conversions, attributed revenue, ROAS, CAC, and rule-based budget recommendations.

SELECT
    campaign,
    channel,
    spend,
    impressions,
    clicks,
    conversions,
    revenue,
    ROAS,
    CAC,
    CTR,
    CVR,
    revenue_per_click,
    recommended_action,
    'RULE_BASED_OPTIMIZATION' AS optimization_engine
FROM `{{ target_dataset }}.fct_campaign_roi`
