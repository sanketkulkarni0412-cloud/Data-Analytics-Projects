-- Mart Model: fct_campaign_performance.sql
-- Grain: One row per channel + campaign_name
-- Description: Blends synthetic marketing ad spend with attributed GA4 order revenue and conversions.
-- Computes core unit economics: CAC, ROAS, ROI, CTR, CPC, CPA.

WITH campaign_spend AS (
    SELECT
        channel,
        campaign_name,
        utm_source,
        utm_medium,
        utm_campaign,
        SUM(daily_spend_usd) AS total_ad_spend_usd,
        SUM(impressions) AS total_impressions,
        SUM(clicks) AS total_clicks,
        SUM(conversions) AS reported_platform_conversions
    FROM `{{ target_dataset }}.stg_ad_spend`
    GROUP BY channel, campaign_name, utm_source, utm_medium, utm_campaign
),

attributed_revenue AS (
    SELECT
        attributed_channel AS channel,
        attributed_campaign AS campaign_name,
        COUNT(DISTINCT order_id) AS attributed_conversions,
        SUM(attributed_revenue_usd) AS attributed_revenue_usd
    FROM `{{ target_dataset }}.fct_attribution`
    GROUP BY attributed_channel, attributed_campaign
)

SELECT
    s.channel,
    s.campaign_name,
    s.utm_source,
    s.utm_medium,
    s.utm_campaign,

    -- Financial Spend & Revenue
    s.total_ad_spend_usd,
    COALESCE(r.attributed_revenue_usd, 0.0) AS attributed_revenue_usd,

    -- Volume Metrics
    s.total_impressions,
    s.total_clicks,
    s.reported_platform_conversions,
    COALESCE(r.attributed_conversions, 0) AS attributed_conversions,

    -- Unit Economics & Performance KPIs
    ROUND((s.total_clicks / NULLIF(s.total_impressions, 0)) * 100, 3) AS ctr_pct,
    ROUND(s.total_ad_spend_usd / NULLIF(s.total_clicks, 0), 2) AS cpc_usd,
    ROUND(s.total_ad_spend_usd / NULLIF(COALESCE(r.attributed_conversions, 0), 0), 2) AS cac_usd,
    ROUND(COALESCE(r.attributed_revenue_usd, 0.0) / NULLIF(s.total_ad_spend_usd, 0), 2) AS roas,
    ROUND(((COALESCE(r.attributed_revenue_usd, 0.0) - s.total_ad_spend_usd) / NULLIF(s.total_ad_spend_usd, 0)) * 100, 2) AS roi_pct

FROM campaign_spend s
LEFT JOIN attributed_revenue r
  ON s.channel = r.channel
 AND s.campaign_name = r.campaign_name
