# Project Plan: Ecommerce Customer & Marketing Analytics

**Project Root:** `D:\Ecommerce-Customer-Marketing-Analytics`  
**Status:** Planning Phase (Pending User Review)  
**Safety Isolation:** Completely decoupled from `D:\nexvia - 1` (Nexvia Financial-Analytics-System).

---

## 1. Project Overview & Scope

This project implements an end-to-end e-commerce customer intelligence, identity resolution, multi-touch attribution, and marketing ROI analytics pipeline. 

### Core Objectives:
1. Ingest real-world behavioral event stream data from the public Google Merchandise Store GA4 BigQuery dataset.
2. Synthesize realistic CRM customer records and multi-channel advertising spend tables using reproducible Python (`Faker`) scripts.
3. Construct a robust identity-resolution graph bridging GA4 anonymous visitor sessions (`user_pseudo_id`) with authenticated CRM customer identities.
4. Build modular dbt transformation models for sessions, orders, customer profiles, RFM scoring, Customer Lifetime Value (CLV), and customer segmentation.
5. Implement and contrast four marketing attribution models (First Touch, Last Touch, Linear, Time Decay).
6. Calculate channel and campaign performance metrics (Cost per Acquisition - CAC, Return on Investment - ROI).
7. Prepare clean, documented analytical marts ready for Tableau executive dashboarding and budget reallocation decisioning.

---

## 2. Environment & Tooling Baseline

- **Operating System:** Windows 11 (64-bit)
- **Local Workspace:** `D:\Ecommerce-Customer-Marketing-Analytics` (217+ GB free disk space)
- **Python Version:** 3.13.1
- **Version Control:** Git 2.50.1
- **Package Management:** Dedicated Python virtual environment (`.venv`)
- **Key Python Packages:** `dbt-core`, `dbt-bigquery`, `google-cloud-bigquery`, `Faker`, `pandas`, `numpy`, `scipy`, `pyarrow`, `db-dtypes`
- **Warehouse:** Google Cloud BigQuery (utilizing BigQuery Sandbox for zero-billing compliance)
- **Visualization:** Tableau Desktop / Tableau Public / Data Extracts

---

## 3. Data Architecture & Schema Plan

### Source Layer
1. **Public GA4 Events (`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`):**
   - Real, authentic web behavioral event telemetry (page views, session start, view item, add to cart, begin checkout, purchase).
   - Partitioned by date (`_TABLE_SUFFIX`).
   - Granular event params (e.g., `ga_session_id`, `page_location`, `page_referrer`, `medium`, `source`, `campaign`, `value`, `currency`).
   - **Integrity Rule:** GA4 source data is never fabricated, modified, or polluted.

2. **Synthetic CRM Customers (`synthetic_crm_customers`):**
   - Generated reproducibly via Python (`Faker` with fixed random seed).
   - **Fields:** `customer_id`, `email`, `first_name`, `last_name`, `registration_date`, `country`, `preferred_device`, `customer_tier`, `churn_risk_flag`, `opted_in_email`.
   - **Labeling:** Explicitly stamped as `data_source = 'SYNTHETIC_SIMULATION'`.

3. **Synthetic Advertising Spend (`synthetic_ad_spend`):**
   - Generated reproducibly via Python to align with GA4 campaign UTM parameters (`utm_source`, `utm_medium`, `utm_campaign`).
   - **Fields:** `spend_id`, `spend_date`, `channel`, `campaign_id`, `campaign_name`, `utm_source`, `utm_medium`, `utm_campaign`, `daily_ad_spend_usd`, `impressions`, `clicks`.
   - Realistic cost structures reflecting Google Search, Meta Ads, YouTube, Display, and Organic/Referral channels over the active GA4 date range.

---

## 4. Identity Resolution Architecture

### The Business Problem
GA4 tracks unauthenticated user traffic via `user_pseudo_id` (cookie-level client ID). CRM tracks authenticated users via `customer_id`. Users often interact across multiple sessions anonymously before logging in or completing a purchase.

### Resolution Logic & Bridging:
1. **Extraction of Identification Events:** Extract GA4 `purchase`, `login`, and `sign_up` events where an identity link can be established.
2. **Deterministic Linking:** Construct an identity bridge (`int_identity_resolution`) mapping `user_pseudo_id` to `customer_id`.
3. **Session Stitching:** Propagate resolved `customer_id` backwards and forwards across all historical sessions associated with the resolved `user_pseudo_id`.
4. **Identity Graph Table:**
   - `user_pseudo_id`: Cookie ID
   - `customer_id`: Resolved CRM Customer ID
   - `first_identified_at`: Timestamp of earliest resolution
   - `identification_method`: e.g., `ORDER_MATCH`, `LOGIN_EVENT`, `ANONYMOUS_UNRESOLVED`
   - `resolution_confidence`: Categorical confidence indicator (`HIGH`, `MEDIUM`, `UNRESOLVED`)

---

## 5. Planned dbt Transformation Models

```text
dbt_project/
├── models/
│   ├── staging/
│   │   ├── stg_ga4_events.sql        # Flatten nested record fields, unnest params
│   │   ├── stg_crm_customers.sql     # Staged synthetic customer profile
│   │   └── stg_ad_spend.sql          # Staged marketing spend by channel/date
│   │
│   ├── intermediate/
│   │   ├── int_identity_resolution.sql   # Deterministic user stitching
│   │   ├── int_sessions_stitched.sql     # Session aggregation with unified customer ID
│   │   └── int_touchpoints.sql           # Marketing touchpoint sequencing for attribution
│   │
│   └── marts/
│       ├── fct_sessions.sql              # Cleaned session mart (traffic, duration, bounce)
│       ├── fct_orders.sql                # Order mart with resolved customer ID & cart values
│       ├── dim_customer_profile.sql      # Unified 360 customer dimension
│       ├── fct_rfm_clv_segments.sql      # RFM scoring, quintiles, and CLV metrics
│       ├── fct_attribution_comparison.sql# 4-model multi-touch attribution credit per channel
│       └── fct_campaign_performance.sql  # Blended spend vs attributed revenue (ROI & CAC)
```

---

## 6. Analytical Formulations & Mathematical Logic

### A. RFM Scoring & Segmentation
- **Recency ($R$):** Days between snapshot reference date and customer's latest order date. Divided into 5 quintiles (5 = most recent, 1 = oldest).
- **Frequency ($F$):** Total number of completed orders in customer lifecycle. Divided into 5 quintiles (5 = highest order count).
- **Monetary ($M$):** Total lifetime revenue generated by customer. Divided into 5 quintiles (5 = highest spending).
- **Composite Score:** $\text{RFM} = \text{Concat}(R, F, M)$ or $\text{Avg}(R, F, M)$.
- **Segment Mapping:**
  - *Champions:* R=5, F=5, M=5
  - *Loyal Customers:* R=4-5, F=3-5, M=3-5
  - *Potential Loyalists:* R=4-5, F=1-2, M=1-2
  - *At Risk:* R=1-2, F=3-5, M=3-5
  - *Hibernating / Lost:* R=1-2, F=1-2, M=1-2

### B. Customer Lifetime Value (CLV)
- **Historic CLV:** $\sum \text{Total Net Revenue per Customer}$
- **Predictive / Model-Based CLV:**
  $$\text{CLV} = \text{AOV} \times \text{Purchase Frequency} \times \text{Gross Margin \%} \times \text{Customer Lifespan}$$
  where:
  - $\text{AOV} = \frac{\text{Total Revenue}}{\text{Total Orders}}$
  - $\text{Purchase Frequency} = \frac{\text{Total Orders}}{\text{Distinct Customers}}$
  - $\text{Gross Margin} = \text{Baseline assumption (e.g. 45\%)}$
  - $\text{Customer Lifespan} = \frac{1}{\text{Churn Rate}}$

### C. Multi-Touch Attribution Models
Evaluated across a conversion window (e.g., 30-day lookback prior to purchase event):
1. **First Touch:** $100\%$ conversion credit assigned to the earliest touchpoint in the journey.
2. **Last Touch:** $100\%$ conversion credit assigned to the most recent touchpoint immediately preceding the purchase.
3. **Linear:** Equal weight distribution across all $N$ touchpoints in the conversion journey:
   $$\text{Weight}_i = \frac{1}{N}$$
4. **Time Decay:** Exponential decay placing higher weight on touchpoints closer in time to purchase:
   $$\text{Weight}_i = 2^{-\frac{\Delta t_i}{\lambda}}$$
   where $\Delta t_i$ is days before conversion and $\lambda = 7$ days (half-life parameter). Normalized so $\sum \text{Weight}_i = 1.0$.

### D. Campaign ROI & Cost Per Acquisition (CAC)
For each marketing channel and campaign:
- **Cost Per Acquisition:**
  $$\text{CAC}_{\text{model}} = \frac{\text{Total Campaign Ad Spend}}{\text{Attributed Conversions}_{\text{model}}}$$
- **Return On Ad Spend (ROAS) / ROI:**
  $$\text{ROAS}_{\text{model}} = \frac{\text{Attributed Revenue}_{\text{model}}}{\text{Total Campaign Ad Spend}}$$
  $$\text{ROI}_{\text{model}} = \frac{\text{Attributed Revenue}_{\text{model}} - \text{Total Ad Spend}}{\text{Total Ad Spend}} \times 100\%$$

---

## 7. Tableau Integration Plan

The final dbt analytical marts will be exported or connected directly to Tableau to produce an executive-ready dashboard:
1. **Executive Summary:** Blended CAC, overall ROAS, conversion rate, total revenue, active customers.
2. **Attribution Comparison Matrix:** Side-by-side waterfall / bar charts showing how First Touch, Last Touch, Linear, and Time Decay reallocate credit across channels.
3. **Customer Segmentation & RFM Grid:** Heatmap of RFM quintiles, segment migration, and CLV distribution.
4. **Budget Reallocation Recommendations:** Visual scenario tool comparing over-credited vs under-credited channels to guide ad-spend reallocation.

---

## 8. Implementation Phases & Quality Gates

| Phase | Milestone | Deliverables | Verification Gate |
|---|---|---|---|
| **Phase 1** | Setup & Cloud Access | `.venv`, BigQuery credentials / sandbox profile, `profiles.yml` | `dbt debug` succeeds |
| **Phase 2** | Synthetic Data & Ingestion | `generate_synthetic_crm.py`, `generate_synthetic_ad_spend.py`, BigQuery loader | Data verified in BigQuery tables |
| **Phase 3** | dbt Modeling & Staging | `stg_*`, `int_identity_resolution`, `fct_sessions`, `fct_orders`, `dim_customer_profile` | `dbt test` passes 100% |
| **Phase 4** | Advanced Analytics | RFM scoring, CLV calculation, 4 attribution models, ROI/CAC marts | SQL query assertions match expected formulas |
| **Phase 5** | Tableau & Reporting | Tableau dashboard workbook, exported visualizations, `README.md`, presentation deck | Complete review against project rubric |

---

## 9. Blockers & Access Dependencies

1. **GCP Project Configuration:** BigQuery project ID and authentication credentials must be designated (Sandbox or standard service account JSON).
2. **Tableau Desktop / Public Client:** Local installation or cloud authoring link is needed for final `.twbx` workbook packaging.
