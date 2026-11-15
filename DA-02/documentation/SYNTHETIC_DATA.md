# Synthetic Data Architecture & Governance Specification

**Project:** Ecommerce Customer & Marketing Analytics  
**Working Directory:** `D:\Ecommerce-Customer-Marketing-Analytics`  
**Data Governance Policy:** Strict, auditable separation between Public GA4 dataset source/design, synthetic simulations, and LOCAL_REPRODUCIBLE_EXECUTION validation outputs.

---

## 1. The Five Data & Pipeline Tiers

This project operates on five strictly differentiated tiers to ensure total transparency, auditability, and regulatory compliance.

> [!IMPORTANT]
> **Cloud Credentials & Query Lineage Disclosure:**
> Live Google Cloud Application Default Credentials (ADC) are not configured in this local execution environment. Consequently, no claims are made that downstream validation outputs were queried live from Google Cloud BigQuery. All reported session counts ($12,108$), order volumes ($1,659$), top-line revenues ($\$131,133.96$), and customer behavioral metrics are **LOCAL_REPRODUCIBLE_EXECUTION validation outputs** generated deterministically by the Python analytics engine in exact alignment with the **Public GA4 dataset source/design**.

```
+-----------------------------------------------------------------------------------------------+
| TIER A: PUBLIC GA4 DATASET SOURCE / DESIGN                                                    |
| Source: bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*                        |
| Status: Public Google Merchandise Store web analytics schema & event stream specification.     |
| Governance: Read-only schema reference. Production BigQuery SQL models (stg_ga4_events.sql)   |
| are authored against this authentic source specification.                                     |
+-----------------------------------------------------------------------------------------------+
| TIER B: SYNTHETIC CRM DATA                                                                    |
| File: data/synthetic_crm_customers.csv                                                        |
| Status: 100% SIMULATED customer profiles generated via Python Faker (Seed 42).                |
| Governance: Zero real PII, all emails use RFC 2606 (@example.com). 5,000 customer profiles.   |
+-----------------------------------------------------------------------------------------------+
| TIER C: SYNTHETIC ADVERTISING SPEND                                                           |
| File: data/synthetic_ad_spend.csv                                                             |
| Status: 100% SIMULATED marketing budget, impressions, clicks, conversions (Seed 42).          |
| Governance: Calibrated against GA4 UTM parameters with realistic seasonal dynamics. 736 rows. |
+-----------------------------------------------------------------------------------------------+
| TIER D: SYNTHETIC IDENTITY-RESOLUTION MAPPING                                                 |
| File: data/synthetic_identity_mapping.csv                                                     |
| Status: 100% SIMULATED deterministic identity bridge linking user_pseudo_id to customer_id.   |
| Governance: Explicitly preserves anonymous traffic as UNRESOLVED (zero false claims). 7k rows.|
+-----------------------------------------------------------------------------------------------+
| TIER E: LOCAL_REPRODUCIBLE_EXECUTION VALIDATION OUTPUTS                                       |
| Files: data/fct_*.csv, data/tableau_customer_marketing_analytics.csv, reports/*.json          |
| Status: LOCAL REPRODUCIBLE VALIDATION / SCENARIO OUTPUTS                                      |
| Governance: Generated deterministically via Python analytics engine when ambient BigQuery     |
| credentials are not configured. Strictly NOT claimed to be live BigQuery query results.       |
+-----------------------------------------------------------------------------------------------+
```

---

## 2. Tier A: Public GA4 Dataset Source / Design
* **Provider:** Google Cloud Public Datasets / Google Merchandise Store
* **Table:** `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
* **Period:** `2020-11-01` to `2021-01-31` (92 days)
* **Design & Schema Integrity:** SQL models in `sql/staging/stg_ga4_events.sql` reflect the exact schema, event parameters (`ga_session_id`, `page_location`, `page_referrer`), unnesting patterns, and partitioning (`_TABLE_SUFFIX`) required by authentic GA4 export tables.

---

## 3. Tier B: Synthetic CRM Data
* **Script:** `scripts/generate_synthetic_crm.py`
* **Volume:** 5,000 customer records (Seed 42)
* **Privacy:** All email addresses strictly use RFC 2606 reserved example domain (`@example.com`).
* **Attributes:** `customer_id`, `signup_date`, `customer_tier` (Bronze, Silver, Gold, Platinum), `preferred_device`, `is_loyalty_member`, `churn_risk_level`.

---

## 4. Tier C: Synthetic Advertising Spend
* **Script:** `scripts/generate_synthetic_ad_spend.py`
* **Volume:** 736 records across 8 campaigns and 5 channels (Paid Search, Paid Social, Display, Video, Affiliate)
* **Date Range:** `2020-11-01` to `2021-01-31` (92 days)
* **Total Spend:** $308,808.42 USD
* **Integrity:** Impressions $\ge$ Clicks $\ge$ Conversions $\ge 0$, Spend $> 0$.

---

## 5. Tier D: Synthetic Identity-Resolution Mapping
* **Script:** `scripts/generate_identity_mapping.py`
* **Volume:** 7,000 simulated GA4 visitor instances (`user_pseudo_id`)
* **Resolution Rate:** 60.0% resolved (4,200 records linked to CRM customers via Checkout, Login, or Signup)
* **Anonymous Rate:** 40.0% unresolved (2,800 records explicitly labeled `UNRESOLVED_ANONYMOUS`)
* **Referential Integrity:** 100% of resolved `customer_id` values exist in `synthetic_crm_customers.csv`.

---

## 6. Tier E: LOCAL_REPRODUCIBLE_EXECUTION Validation Outputs
* **Execution Scripts:** `scripts/run_phase3_analytics.py` & `scripts/run_phase2_analytics.py`
* **Outputs Generated:**
  * `data/fct_sessions.csv` (12,108 rows)
  * `data/fct_orders.csv` (1,659 rows)
  * `data/fct_attribution_multi_model.csv` (9,464 rows)
  * `data/fct_customer_clv.csv` (5,000 rows)
  * `data/fct_campaign_roi.csv` (8 rows)
  * `data/tableau_customer_marketing_analytics.csv` (5,000 rows × 40 columns)
* **Execution Governance:** In the absence of live GCP credentials, these data marts and benchmark KPIs ($12,108$ sessions, $1,659$ orders, $\$131,133.96$ revenue) are generated deterministically in a local testbed, guaranteeing complete end-to-end reproducibility, mathematical reconciliation, and test coverage without unauthenticated cloud failures.
