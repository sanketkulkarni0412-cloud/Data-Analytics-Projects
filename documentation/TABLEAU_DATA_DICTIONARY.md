# Tableau Data Dictionary & Visualization Guide

**Project:** Ecommerce Customer & Marketing Analytics  
**Primary Dataset:** `data/tableau_customer_marketing_analytics.csv` (5,000 rows × 40 columns)  
**Attribution Dataset:** `data/fct_attribution_multi_model.csv` (9,464 rows)  
**Campaign ROI Dataset:** `data/fct_campaign_roi.csv` (8 rows)  
**Grain:** 1 row per `customer_id` (Primary Dataset) | 1 row per `order_id` + `model` + `channel` (Attribution) | 1 row per `channel` + `campaign` (ROI)  
**Governance Notice:** All metrics reflect **LOCAL_REPRODUCIBLE_EXECUTION validation outputs** calibrated against the **Public GA4 dataset source/design**; not claimed to be live BigQuery cloud query results.

---

## 1. Consolidated Customer Analytics Dataset (`tableau_customer_marketing_analytics.csv`)

### Schema & Data Dictionary (All 40 Columns)

| Column Name | Data Type | Classification | Description & Analytical Usage |
|---|---|---|---|
| `customer_id` | STRING | Dimension (PK) | Unique customer identifier (`CRM-CUST-000001`). Key for joins and count distinct. |
| `synthetic_first_name` | STRING | Dimension | Simulated customer first name (RFC 2606 compliant). |
| `synthetic_last_name` | STRING | Dimension | Simulated customer surname (RFC 2606 compliant). |
| `synthetic_email` | STRING | Dimension | Synthetic email address (`@example.com`). Zero real PII. |
| `signup_date` | DATE | Dimension | Customer account registration date (`YYYY-MM-DD`). Used for cohort retention curves. |
| `customer_tier` | STRING | Dimension | Loyalty status: `Bronze`, `Silver`, `Gold`, `Platinum`. Filter / Slice dimension. |
| `country` | STRING | Dimension | Customer declared country. Geographic map visualization. |
| `preferred_device` | STRING | Dimension | Primary browsing hardware: `Desktop`, `Mobile`, `Tablet`. |
| `is_loyalty_member` | BOOLEAN | Dimension | Flag indicating participation in retailer loyalty rewards program. |
| `opted_in_email` | BOOLEAN | Dimension | Email marketing consent flag for segmentation. |
| `churn_risk_level` | STRING | Dimension | Pre-calculated churn risk category: `Low`, `Medium`, `High`. |
| `data_source` | STRING | Governance | Synthetic data origin identifier (`SYNTHETIC_CRM_FAKER_SEED_42`). |
| `is_synthetic` | BOOLEAN | Governance | Explicit flag denoting synthetic generation (`TRUE`). |
| `simulation_seed` | INTEGER | Governance | Deterministic random seed used for reproducibility (`42`). |
| `customer_total_sessions` | INTEGER | Measure | Cumulative number of GA4 sessions recorded for this customer. |
| `total_engaged_sessions` | INTEGER | Measure | Number of sessions lasting $\ge 10$ seconds or recording $\ge 2$ page views. |
| `total_page_views` | INTEGER | Measure | Cumulative product and navigation page views. |
| `total_duration_seconds`| INTEGER | Measure | Cumulative on-site browsing time in seconds. |
| `first_session_date` | DATE | Dimension | Earliest recorded web session date (nullable for unvisited customers). |
| `last_session_date` | DATE | Dimension | Most recent recorded web session date (nullable for unvisited customers). |
| `acquisition_channel` | STRING | Dimension | First touchpoint marketing channel that acquired the customer (nullable for unvisited customers). |
| `customer_total_orders` | INTEGER | Measure | Total completed purchases across the customer lifecycle. |
| `customer_total_revenue`| FLOAT | Measure | Total monetary spend in USD. Primary top-line revenue metric. |
| `first_order_date` | DATE | Dimension | Date of customer's first completed purchase (nullable for non-buyers). |
| `last_order_date` | DATE | Dimension | Date of customer's most recent completed purchase (nullable for non-buyers). |
| `average_order_value` | FLOAT | Measure | Average spend per order: $\text{Total Revenue} / \text{Total Orders}$. |
| `purchase_frequency` | FLOAT | Measure | Order conversion intensity: $\text{Total Orders} / \text{Total Sessions}$. |
| `days_since_last_activity`| INTEGER | Measure | Inactivity recency: days between snapshot date (2021-01-31) and last touchpoint. |
| `r_score` | INTEGER | Dimension/Measure | Recency score (1 = stale, 5 = highly recent). |
| `f_score` | INTEGER | Dimension/Measure | Frequency score (1 = infrequent, 5 = top repeat purchaser). |
| `m_score` | INTEGER | Dimension/Measure | Monetary score (1 = lowest spend, 5 = top spender). |
| `rfm_cell` | STRING | Dimension | Concatenated 3-digit score cell (e.g. `555`, `111`, `455`). |
| `composite_rfm` | FLOAT | Measure | Average of R, F, and M scores: $(R + F + M) / 3.0$. |
| `rfm_segment` | STRING | Dimension | Strategic lifecycle segment: `Champions`, `Loyal Customers`, `At Risk High Value`, `Recent Potential Loyalists`, `Hibernating / Inactive`, `Promising / General`. |
| `historical_clv` | FLOAT | Measure | Realized customer margin: $\text{Historical Revenue} \times 0.45$ (45% illustrative scenario margin assumption). |
| `predicted_12m_clv` | FLOAT | Measure | Forward-looking 12-month expected customer value based on tenure, frequency, and retention probability. |
| `clv_segment` | STRING | Dimension | Tiered lifetime value segment: `High Value VIP` ($>\$120$), `Medium Value Core` ($\$50-\$120$), `Low Value Nurture` ($\$20-\$50$), `Prospect / Inactive` ($<\$20$). |
| `data_source_crm` | STRING | Governance | Tag: `SYNTHETIC_SIMULATION` |
| `data_source_ga4` | STRING | Governance | Tag: `GA4_OBFUSCATED_SAMPLE` |
| `pipeline_execution_mode`| STRING | Governance | Tag: `LOCAL_REPRODUCIBLE_EXECUTION` |

---

## 2. Multi-Model Attribution Dataset (`fct_attribution_multi_model.csv`)

| Column Name | Data Type | Classification | Description |
|---|---|---|---|
| `order_id` | STRING | Dimension | Unique e-commerce order identifier (`GA4-ORD-0000001`). |
| `customer_id` | STRING | Dimension | Associated CRM customer ID. |
| `order_revenue` | FLOAT | Measure | Total order transaction revenue ($USD$). |
| `attribution_model` | STRING | Dimension | Model applied: `FIRST_TOUCH`, `LAST_TOUCH`, `LINEAR`, `TIME_DECAY`. |
| `channel` | STRING | Dimension | Marketing channel receiving credit. |
| `attributed_revenue` | FLOAT | Measure | Revenue allocated to this channel under the specific model. Reconciles to $131,133.96 per model. |
| `attribution_weight` | FLOAT | Measure | Fractional credit allocated ($0.0$ to $1.0$). Sums to $1.0$ per order per model. |
| `touchpoint_count` | INTEGER | Measure | Number of marketing touchpoints in the 30-day conversion lookback window. |
| `lookback_days` | INTEGER | Dimension | Attribution lookback window length ($30$ days). |

---

## 3. Campaign Performance & ROI Dataset (`fct_campaign_roi.csv`)

| Column Name | Data Type | Classification | Description |
|---|---|---|---|
| `campaign` | STRING | Dimension | Campaign name (e.g. `Brand_Search_Core`, `Black_Friday_Cyber_Week`). |
| `channel` | STRING | Dimension | Channel grouping (`Paid Search`, `Paid Social`, `Display`, `Video`, `Affiliate`). |
| `spend` | FLOAT | Measure | Total advertising spend incurred ($USD$). |
| `impressions` | INTEGER | Measure | Total ad impressions delivered. |
| `clicks` | INTEGER | Measure | Total ad link clicks. |
| `conversions` | INTEGER | Measure | Platform-reported conversions. |
| `revenue` | FLOAT | Measure | Attributed e-commerce revenue ($USD$). |
| `ROAS` | FLOAT | Measure | Return on Ad Spend: $\text{Revenue} / \text{Spend}$. |
| `CAC` | FLOAT | Measure | Cost Per Acquisition: $\text{Spend} / \text{Conversions}$. |
| `CTR` | FLOAT | Measure | Click-Through Rate: $(\text{Clicks} / \text{Impressions}) \times 100\%$. |
| `CVR` | FLOAT | Measure | Conversion Rate: $(\text{Conversions} / \text{Clicks}) \times 100\%$. |
| `revenue_per_click` | FLOAT | Measure | RPC: $\text{Revenue} / \text{Clicks}$. |
| `recommended_action` | STRING | Dimension | Rule-based budget action (`SCALE_BUDGET (+20%)`, `MAINTAIN_EFFICIENT`, `OPTIMIZE_WATCH`, `REDUCE_REALLOCATE (-30%)`). |

---

## 4. Tableau Dashboard Wireframes & Visual Layout

### Dashboard 1: Executive Marketing & Revenue Overview
* **KPI Scorecards:** Total Revenue (\$131,133.96), Total Orders (1,659), Average Order Value (\$79.04), Blended ROAS (0.42 / 0.24), Blended CAC (\$186.14).
* **Revenue Trend:** Daily order volume and revenue bar/line chart over the Nov 2020 – Jan 2021 window.
* **Channel Mix:** Donut chart of revenue share by acquisition channel.

### Dashboard 2: Multi-Touch Attribution Model Comparison
* **Side-by-Side Bar Chart:** Compares revenue credit across `FIRST_TOUCH`, `LAST_TOUCH`, `LINEAR`, and `TIME_DECAY` for each channel.
* **Key Visual Finding:** First Touch heavily credits top-of-funnel discovery channels (`Paid Search` \$48.3K, `Paid Social` \$35.6K, `Video` \$9.7K), whereas Last Touch assigns \$49.7K to `Direct` as returning customers navigate straight to checkout.

### Dashboard 3: Customer Intelligence & RFM Segmentation
* **Heatmap Matrix:** $5 \times 5$ grid of Recency ($R$) vs Frequency ($F$) shaded by Monetary ($M$) value.
* **Customer Value Distribution:** Treemap of customer counts and revenue across `Champions`, `Loyal Customers`, `At Risk High Value`, and `Hibernating`.
* **Predicted 12M CLV vs Historical CLV:** Scatter plot showing customer expansion potential.

### Dashboard 4: Campaign ROI & Budget Reallocation Engine
* **Performance Matrix:** Scatter plot of ROAS ($Y$-axis) vs CAC ($X$-axis), sized by Ad Spend, colored by `recommended_action`.
* **Budget Optimization Waterfall:** Visual scenario tool depicting the \$74,069.20 budget reallocation pool shifted from 6 low-ROAS campaigns ($\text{ROAS} < 0.25$) into top-performing `Brand_Search_Core` ($\text{ROAS } 0.567, \text{CAC } \$8.02$, action: `SCALE_BUDGET (+20%)`), while monitoring `Dynamic_Remarketing_Banners` ($\text{ROAS } 0.265, \text{CAC } \$68.28$, action: `OPTIMIZE_WATCH`).
