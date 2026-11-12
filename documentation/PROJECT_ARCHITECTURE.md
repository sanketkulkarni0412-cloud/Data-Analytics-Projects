# Architecture & Technical Design: Ecommerce Customer & Marketing Analytics

**Project Directory:** `D:\Ecommerce-Customer-Marketing-Analytics`  
**Execution Runtime:** Python 3.13.1 (Windows 64-bit)  
**Data Warehouse Architecture:** Google Cloud BigQuery SQL Pattern + LOCAL_REPRODUCIBLE_EXECUTION Analytics Engine

---

## 1. End-to-End Data Pipeline Architecture

```
[ Tier A: Public GA4 Dataset Source / Design ]
  bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*
               │
               ▼ (Authored BigQuery SQL staging specification)
   [ Staging: stg_ga4_events.sql ]
   • Grain: 1 row per event occurrence (event_surrogate_key)
   • Unnests event_params, extracts session_key, traffic channel dimensions
               │
               ▼ (LOCAL_REPRODUCIBLE_EXECUTION validation engine)
        ┌──────┴──────────────────────────────────────┐
        ▼                                             ▼
  [ Intermediate: int_sessions.sql ]     [ Intermediate: int_orders.sql ]
  • Grain: 1 row per session             • Grain: 1 row per transaction_id
  • PK: session_key (12,108 rows)        • Deduplication: First timestamp wins (1,659 rows)
  • Metrics: duration, pages, purchases  • Metrics: gross revenue ($131,133.96), tax, shipping
        │                                             │
        └──────────────────────┬──────────────────────┘
                               ▼
  [ Tier D: Synthetic Identity Bridge ] ◄── [ Tier B: Synthetic CRM Data ]
    data/synthetic_identity_mapping.csv       data/synthetic_crm_customers.csv
    (7,000 visitors, 60% resolved)            (5,000 customers, RFC 2606 email)
                               │
        ┌──────────────────────┼────────────────────────┐
        ▼                      ▼                        ▼
  [ Mart 1: Customer Profile ] [ Mart 2: Multi-Model ]  [ Mart 3: Campaign ROI ]
    customer_profile.sql         fct_attribution_         fct_campaign_roi.sql
    • Grain: customer_id         multi_model.sql          • Grain: campaign (8 rows)
    • Unifies CRM + GA4          • 4 models side-by-side  • Spend ($308.8K), ROAS, CAC
    • 5,000 rows                 • Exact $131.1K match    • Rule-based recommendations
        │                      │                        │
        └──────────────────────┴───────────┬────────────┘
                                           ▼
                             [ Mart 4: Customer CLV ]
                               fct_customer_clv.sql
                               • Historical vs 12M Predicted CLV
                               • 45% margin scenario assumption
                               • 5,000 rows
                                           │
                                           ▼
                             [ Tableau Consolidated Mart ]
                               tableau_customer_marketing_analytics.csv
                               • 5,000 rows × 40 columns
                               • Powers Executive, Attribution, RFM, & ROI views
```

---

## 2. Multi-Model Attribution Design

Four distinct attribution models are implemented over a **30-day conversion lookback window** with automatic direct fallback:

1. **First Touch:** Allocates 100% of conversion credit to the initial touchpoint. ($48.3K Paid Search, $35.6K Paid Social, $11.2K Organic Search).
2. **Last Touch:** Allocates 100% of conversion credit to the final touchpoint preceding purchase. ($49.7K Direct as returning customers convert, $33.5K Paid Search).
3. **Linear:** Allocates equal $1/N$ credit across all touchpoints. ($39.8K Paid Search, $34.3K Direct, $27.6K Paid Social).
4. **Time Decay ($\lambda = 7$ Days):** Applies exponential weighting $2^{-\Delta t / 7}$. ($39.2K Direct, $37.7K Paid Search, $25.9K Paid Social).
* **Mathematical Invariant:** All 4 models reconcile to **$131,133.96** exactly with zero variance.

---

## 3. Customer Lifetime Value (CLV) Design

* **Historical CLV:** $\text{Historical Revenue} \times 0.45$ ($\$59,010.32$ total realized margin across customer base).
* **Predicted 12M CLV:** Forward-looking estimation based on annualized purchase frequency, customer tenure, AOV, and churn discount ($\$149,065.05$ total predicted forward margin).
* **Governance Note:** The 45% margin is explicitly labeled as an **illustrative scenario assumption**.

---

## 4. Rule-Based Budget Optimization Framework

* **Total Marketing Budget:** $308,808.42 USD across 8 campaigns and 5 channels.
* **Reallocation Pool:** **$74,069.20** (30% reduction from 6 underperforming campaigns with $\text{ROAS} < 0.25$).
* **Primary Beneficiary:** `Brand_Search_Core` ($\text{ROAS} = 0.567, \text{CAC} = \$8.02$, action: `SCALE_BUDGET (+20%)`).
* **Monitored Campaign:** `Dynamic_Remarketing_Banners` ($\text{ROAS} = 0.265, \text{CAC} = \$68.28$, action: `OPTIMIZE_WATCH`).
* **Campaigns Reduced:** `Affiliate_Partner_Deals` ($\text{ROAS } 0.178$), `Generic_Apparel_Promo` ($\text{ROAS } 0.231$), `Winter_Clearance_Sale` ($\text{ROAS } 0.000$), `Black_Friday_Cyber_Week` ($\text{ROAS } 0.189$), `Holiday_Gift_Guide_2020` ($\text{ROAS } 0.234$), `Brand_Awareness_Video_Q4` ($\text{ROAS } 0.201$).

---

## 5. Execution Environment & Governance Disclosure

> [!IMPORTANT]
> **Data Governance & Live BigQuery Status:**
> Because live Google Cloud Application Default Credentials (ADC) are not configured, this pipeline does not claim live BigQuery cloud query execution. All reported KPI metrics (such as the 12,108 sessions, 1,659 orders, and $131,133.96 revenue) are **LOCAL_REPRODUCIBLE_EXECUTION validation outputs** produced by `scripts/run_phase3_analytics.py` and `scripts/run_phase2_analytics.py`. The SQL models in `sql/` and `models/` provide production-ready BigQuery DDL/DML templates conforming to the authentic `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` schema.
