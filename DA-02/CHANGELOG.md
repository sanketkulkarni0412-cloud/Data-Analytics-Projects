# Changelog

All notable changes to the **Ecommerce Customer & Marketing Analytics** project are documented here.

## [1.0.0] - 2026-11-12 (Final Quality, Governance, Reproducibility, and Submission Audit)
### Completed
- **Full Test Suite Execution:** 45 of 45 tests verified passing across all 5 test modules.
- **Data Governance Audit:** Enforced explicit 5-tier classification across all docs and SQL models. Disclosed that reported metrics ($12,108$ sessions, $1,659$ orders, $\$131,133.96$ revenue) are LOCAL_REPRODUCIBLE_EXECUTION validation outputs generated via the deterministic Python analytics engine implementing the Public GA4 dataset source/design, rather than live BigQuery queries (ADC not configured).
- **Revenue Reconciliation Verification:** Confirmed that First Touch, Last Touch, Linear, and Time Decay ($\lambda=7\text{d}$) reconcile to $131,133.96 with zero variance, attribution weights sum to 1.0, and 0 duplicate records.
- **CLV & Unit Economics Audit:** Confirmed historical CLV = 45% contribution margin ($59,010.32 total realized margin), 12M predicted CLV ($149,065.05), non-negativity across all 5,000 customers, and explicit labeling of the 45% margin as an illustrative scenario assumption.
- **Campaign ROI & Budget Consistency Fix:** Fixed documentation discrepancy to align with calculated metrics: $74,069.20 reallocation pool from 6 low-ROAS campaigns shifted to `Brand_Search_Core` (ROAS 0.567, CAC $8.02, SCALE_BUDGET (+20%)) while monitoring `Dynamic_Remarketing_Banners` (ROAS 0.265, CAC $68.28, OPTIMIZE_WATCH).
- **Tableau Dataset & Data Dictionary Alignment:** Verified `tableau_customer_marketing_analytics.csv` (5,000 rows × 40 columns), resolved 5 missing column definitions in `TABLEAU_DATA_DICTIONARY.md`, and confirmed 0 nulls in critical metrics.
- **Protected Directory Verification:** Confirmed that `D:\nexvia - 1\Financial-Analytics-System` was untouched.
- **Final Submission Audit Report:** Emitted `reports/final_submission_audit.json` with status `READY_FOR_SUBMISSION`.

## [0.5.0] - 2026-11-12 (Phase 3: Multi-Model Attribution, CLV, Marketing ROI, and Tableau Dataset Completed)
### Added
- **Multi-Model Attribution Engine (`data/fct_attribution_multi_model.csv` & `sql/marts/fct_attribution_multi_model.sql`):**
  - Implements First Touch, Last Touch, Linear, and Time Decay ($\lambda = 7$ days) models over a 30-day lookback window.
  - Exactly reconciles to **$131,133.96** total order revenue across all 4 models (zero cent variance).
  - Produces 9,464 attribution records with weights summing to 1.0 per order.
- **Customer Lifetime Value Model (`data/fct_customer_clv.csv` & `sql/marts/fct_customer_clv.sql`):**
  - Calculates historical CLV ($59,010.32 total realized margin) and predicted 12-month forward CLV ($149,065.05 total expected margin).
  - Explicitly labels the 45% contribution margin as an illustrative retail scenario assumption.
  - Classifies 5,000 customers into CLV segments: High Value VIP (163), Medium Value Core (388), Low Value Nurture (1,020), Prospect / Inactive (3,429).
- **Campaign ROI & Budget Optimization (`data/fct_campaign_roi.csv` & `reports/budget_reallocation_recommendations.json`):**
  - Transparent rule-based framework calculating Spend, Impressions, Clicks, Conversions, Revenue, ROAS, CAC, CTR, CVR, and RPC.
  - Generates actionable budget recommendations, identifying a $74,069.20 pool from low-ROAS campaigns for reallocation into top performers like `Brand_Search_Core` (ROAS 0.567, CAC $8.02).
- **Consolidated Tableau Analytics Dataset (`data/tableau_customer_marketing_analytics.csv`):**
  - Comprehensive customer mart (5,000 rows × 40 columns) uniting CRM, RFM, CLV, behavioral sessions, and governance tags.
  - Supported by `documentation/TABLEAU_DATA_DICTIONARY.md` with schema definitions and visual wireframes.
- **Analytical Metric Documentation (`documentation/METRIC_DEFINITIONS.md`):**
  - Mathematical formulas and business definitions for all KPIs, attribution models, CLV, RFM, and budget rules.
- **Phase 3 Test Suite (`tests/test_phase3_analytics.py`):**
  - 14 automated unit tests; full test discovery suite now covers **45 passing tests**.
- **Phase 3 Validation Report (`reports/phase3_validation.json`):**
  - Machine-readable audit of attribution reconciliation, CLV summaries, and data invariants.

## [0.4.0] - 2026-11-12 (Phase 2 Core Analytics Implementation Completed)
- Implemented sessions, deduplicated orders, customer profile, and campaign performance.

## [0.3.0] - 2026-11-12 (Phase 2 Modeling Specification)
- Intermediate and mart SQL model definitions.

## [0.2.0] - 2026-11-12 (Phase 1 Sub-steps F, G, H)
- Synthetic CRM (5,000 rows), Synthetic ad spend (736 rows), Identity mapping (7,000 rows).

## [0.1.0] - 2026-11-12 (Phase 1 Foundation)
- Base environment, BigQuery runner, and GA4 staging model.
