# Individual Project Reflection

**Project:** Ecommerce Customer & Marketing Analytics  
**Document:** `documentation/INDIVIDUAL_REFLECTION.md`  
**Author:** Lead Analytics Engineer & Marketing Data Architect  
**Date:** November 2026  

---

## 1. Executive Summary & Overview
This project provided an end-to-end opportunity to design, engineer, and validate an enterprise e-commerce customer and marketing analytics platform. Bridging Google Analytics 4 (GA4) event telemetry with CRM records, attribution modeling, and campaign budget optimization revealed the intricate technical and economic challenges modern e-commerce enterprises face when measuring marketing ROI.

---

## 2. What I Personally Owned
Throughout Phases 1, 2, and 3, and the Final Submission Audit, I held end-to-end technical responsibility for:
1. **Data Governance & Pipeline Architecture:**
   - Established the strict 5-tier classification framework separating authentic Public GA4 schema designs from synthetic CRM profiles, ad spend records, identity graphs, and local validation outputs.
   - Enforced zero real PII policies with RFC 2606 reserved email domains (`@example.com`).
2. **BigQuery SQL Modeling:**
   - Authored staging models (`stg_ga4_events.sql`) unnesting GA4 repeated key-value structs (`event_params`).
   - Built intermediate sessionization (`int_sessions.sql`) and deduplication models (`int_orders.sql`) enforcing partition windowing (`ROW_NUMBER()`).
   - Designed 4 specialized analytical marts: `customer_profile.sql`, `fct_attribution_multi_model.sql`, `fct_customer_clv.sql`, and `fct_campaign_roi.sql`.
3. **Advanced Attribution & Reconciliation Engine:**
   - Implemented First Touch, Last Touch, Linear, and Time Decay ($\lambda=7\text{ days}$) multi-touch attribution algorithms over a 30-day conversion lookback window.
   - Verified that all 4 models reconcile to exactly $\$131,133.96$ total order revenue with $\$0.00$ unexplained variance.
4. **Customer Intelligence & Lifetime Value:**
   - Programmed the $5 \times 5$ RFM quintile segmentation engine, assigning 5,000 customers into 6 actionable strategic segments.
   - Designed the Customer Lifetime Value (CLV) model combining historical realized contribution margin ($45\%$) with forward-looking 12-month expected CLV ($149.1\text{K}$).
5. **Marketing ROI & Budget Reallocation Engine:**
   - Developed the quantitative decision framework evaluating Spend, Revenue, ROAS, CAC, CTR, and CVR across 8 campaigns and 5 channels.
   - Designed the capital reallocation logic identifying $\$74,069.20$ to shift from underperforming campaigns into top-performing acquisition channels.
6. **Tableau Integration & Testing:**
   - Produced the consolidated customer mart `tableau_customer_marketing_analytics.csv` (5,000 rows $\times$ 40 columns).
   - Created the comprehensive [TABLEAU_DASHBOARD_GUIDE.md](file:///d:/Ecommerce-Customer-Marketing-Analytics/documentation/TABLEAU_DASHBOARD_GUIDE.md) and 12-slide executive presentation.
   - Authored and maintained a 45-test automated test discovery suite with $100\%$ pass rate.

---

## 3. Technical Skills Developed
* **BigQuery SQL & Unnesting Patterns:** Mastered scalar unnesting of repeated GA4 event parameters (`ga_session_id`, `page_location`, `traffic_source`) and partitioned timestamp deduplication using analytical window functions.
* **Deterministic Graph Identity Stitching:** Engineered deterministic referential links between anonymous browser cookies (`user_pseudo_id`) and authenticated CRM keys (`customer_id`), explicitly managing unresolved traffic without false matches.
* **Algorithmic Attribution Modeling:** Deepened mathematical modeling of decay curves ($2^{-\Delta t / 7.0}$) and normalized multi-touch weighting constraints ($\sum w_i = 1.0$).
* **Reproducible Pipeline Engineering:** Built a robust, offline-capable local execution engine (`scripts/run_phase3_analytics.py`) that mirrors BigQuery DDL/DML semantics, enabling flawless automated unit testing without cloud authentication failures.
* **Data Mart & BI Schema Design:** Structured wide denormalized analytics marts (40 columns) optimized for Tableau drill-downs, filtering, and cross-tab analysis.

---

## 4. Analytics & Business Insights Learned
1. **Last-Touch Attribution Creates Severe Acquisition Blindspots:**
   - In single-touch Last Touch, `Direct` captured $\$49,682.71$ ($37.9\%$ of total revenue) because returning customers frequently type the URL directly when ready to purchase.
   - First Touch revealed that `Paid Search` ($\$48.3\text{K}$) and `Paid Social` ($\$35.6\text{K}$) initiated $64\%$ of those customer journeys. Relying solely on Last Touch would have resulted in catastrophic budget cuts to the very channels acquiring new customers.
2. **High Spend Does Not Equal High Efficiency:**
   - `Black_Friday_Cyber_Week` had the largest budget ($\$62,642.72$) but produced an anemic ROAS of $0.189$ and CAC of $\$29.08$.
   - Conversely, `Brand_Search_Core` consumed only $\$36,714.40$ yet delivered $\$20,805.53$ in attributed revenue ($\text{ROAS } 0.567, \text{CAC } \$8.02$).
3. **The Power of Retention Segmentation (At-Risk vs Champions):**
   - The RFM analysis uncovered that $1,154$ customers ($23.1\%$) are categorized as *At Risk High Value* (high historical monetary spend, but dormant recency).
   - Reactivating this cohort with targeted win-back offers represents higher margin upside than acquiring raw top-of-funnel traffic at high CAC.

---

## 5. Challenges Encountered & Solutions Implemented

| Challenge | Root Cause | Solution Implemented |
|---|---|---|
| **Missing Live GCP Credentials** | Environment lacked configured Google Cloud Application Default Credentials (ADC). | Engineered a deterministic `LOCAL_REPRODUCIBLE_EXECUTION` pipeline that executes Python logic conforming exactly to BigQuery schema specifications, allowing 100% test reproducibility. |
| **Attribution Revenue Drift / Rounding Discrepancy** | Fractional floating-point division in linear and time decay weights can cause cent-level rounding errors when summed across thousands of orders. | Implemented normalized weight scaling per order ($\frac{w_i}{\sum w}$) and exact remainder cent reconciliation on the primary channel, guaranteeing zero revenue variance ($131,133.96 = 131,133.96$). |
| **Identity Resolution Bias** | Risk of falsely linking anonymous visitors to CRM records, corrupting attribution. | Built an explicit two-category resolution architecture (60% resolved, 40% labeled `UNRESOLVED_ANONYMOUS`), ensuring unlinked visitors are never assigned artificial customer IDs. |
| **Tableau Schema Column Drift** | Initial documentation had 35 fields while the consolidated CSV had expanded to 40 fields. | Conducted an automated schema audit, identified the 5 missing fields (`data_source`, `is_synthetic`, `simulation_seed`, `first_order_date`, `last_order_date`), and brought `TABLEAU_DATA_DICTIONARY.md` into 100% alignment. |

---

## 6. What I Would Improve Next (Future Roadmap)
1. **Algorithmic Data-Driven Attribution (Shapley Value / Markov Chains):**
   - Supplement heuristic models (First/Last/Linear/Time Decay) with cooperative game theory (Shapley values) and removal effect Markov chains to remove arbitrary weight decay rules.
2. **Probabilistic Cross-Device Identity Stitching:**
   - Combine deterministic logins with probabilistic machine learning models (IP, browser headers, time proximity) to resolve a portion of the 40% anonymous traffic while tracking confidence intervals.
3. **Automated Bidding API Synchronization:**
   - Build automated connectors from `reports/budget_reallocation_recommendations.json` into Google Ads API and Meta Marketing API to adjust target ROAS and campaign budgets automatically.
4. **dbt Core & CI/CD Cloud Pipeline:**
   - Package all SQL staging and marts into an enterprise dbt Core repository with automated BigQuery CI/CD tests via GitHub Actions.

