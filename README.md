# Ecommerce Customer & Marketing Analytics

An enterprise data analytics, identity-resolution, multi-touch attribution, and marketing ROI project built on the Google Analytics 4 (GA4) e-commerce schema and Google Cloud BigQuery design pattern.

---

## 1. Data Governance & Credential Disclosure

> [!IMPORTANT]
> **Data Governance & Execution Mode Disclosure:**
> Live Google Cloud Application Default Credentials (ADC) are not configured in this local environment (as documented in `reports/phase1_bigquery_validation.json`). Consequently, downstream validation outputs are **not** claimed to be queried live from BigQuery.
> 
> The project maintains five strictly differentiated data tiers:
> * **Tier A (Public GA4 dataset source/design):** `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` (schema & model target).
> * **Tier B (Synthetic CRM data):** `data/synthetic_crm_customers.csv` (5,000 simulated customer records, RFC 2606 email).
> * **Tier C (Synthetic advertising spend):** `data/synthetic_ad_spend.csv` (736 daily spend records across 8 campaigns, $308,808.42 total spend).
> * **Tier D (Synthetic identity-resolution mapping):** `data/synthetic_identity_mapping.csv` (7,000 visitors, 60% resolved).
> * **Tier E (LOCAL_REPRODUCIBLE_EXECUTION validation outputs):** All data marts (`data/fct_*.csv`, `data/tableau_customer_marketing_analytics.csv`, `reports/*.json`) and benchmark metrics ($12,108$ sessions, $1,659$ orders, $\$131,133.96$ revenue) are generated deterministically by the local Python analytics engine.

---

## 2. Quick Start & Execution

### Environment Activation
```powershell
& "D:\Ecommerce-Customer-Marketing-Analytics\.venv\Scripts\Activate.ps1"
```

### Running Test Discovery Suite (All 45 Tests)
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

### Running Phase 3 Advanced Analytics Engine
```powershell
python scripts/run_phase3_analytics.py
```
This executes:
1. Multi-Model Attribution (`fct_attribution_multi_model.csv`, 9,464 rows across 4 models).
2. Customer Lifetime Value (`fct_customer_clv.csv`, 5,000 customer records).
3. Campaign ROI & Budget Optimization (`fct_campaign_roi.csv` & `reports/budget_reallocation_recommendations.json`).
4. Consolidated Tableau Dataset (`tableau_customer_marketing_analytics.csv`, 5,000 rows × 40 columns).
5. Comprehensive validation JSON report (`reports/phase3_validation.json`).

### Connecting to Tableau
1. Open **Tableau Desktop** or **Tableau Public**.
2. Select **Connect -> To a File -> Text File**.
3. Navigate to and select `data/tableau_customer_marketing_analytics.csv`.
4. Verify all 40 fields load with correct data types as specified in [TABLEAU_DATA_DICTIONARY.md](file:///d:/Ecommerce-Customer-Marketing-Analytics/documentation/TABLEAU_DATA_DICTIONARY.md).
5. (Optional) For multi-touch attribution and campaign ROI deep-dives, connect `data/fct_attribution_multi_model.csv` and `data/fct_campaign_roi.csv` as secondary datasources or relations.
6. Follow [TABLEAU_DASHBOARD_GUIDE.md](file:///d:/Ecommerce-Customer-Marketing-Analytics/documentation/TABLEAU_DASHBOARD_GUIDE.md) for exact sheet configurations, calculated fields, interactive filters, and dashboard visual layouts.

---

## 3. Directory Layout & Deliverables

```text
D:\Ecommerce-Customer-Marketing-Analytics\
├── sql/
│   ├── staging/        # stg_ga4_events.sql, stg_crm_customers.sql, stg_identity_mapping.sql, stg_ad_spend.sql
│   ├── intermediate/   # int_sessions.sql, int_orders.sql
│   └── marts/          # customer_profile.sql, fct_attribution_multi_model.sql, fct_customer_clv.sql, fct_campaign_roi.sql
├── scripts/
│   ├── run_phase3_analytics.py       # Phase 3 advanced analytics engine
│   ├── run_phase2_analytics.py       # Phase 2 core analytics engine
│   ├── bigquery_runner.py            # BigQuery DDL/DML runner
│   ├── config.py                     # Centralized environment configuration
│   ├── generate_synthetic_crm.py     # Faker CRM generator (5,000 rows)
│   ├── generate_synthetic_ad_spend.py# Multi-channel ad spend generator (736 rows)
│   └── generate_identity_mapping.py  # Deterministic identity bridge (7,000 rows)
├── data/
│   ├── tableau_customer_marketing_analytics.csv # Consolidated Tableau dataset (5k rows × 40 cols)
│   ├── fct_attribution_multi_model.csv          # 4 attribution models (9,464 rows)
│   ├── fct_customer_clv.csv                     # Historical vs Predicted CLV (5k rows)
│   ├── fct_campaign_roi.csv                     # Campaign unit economics & actions (8 rows)
│   ├── fct_sessions.csv                         # Session journeys (12,108 rows)
│   ├── fct_orders.csv                           # Deduplicated orders (1,659 rows)
│   ├── synthetic_crm_customers.csv              # Synthetic CRM base
│   ├── synthetic_ad_spend.csv                   # Synthetic marketing spend
│   └── synthetic_identity_mapping.csv           # Identity resolution bridge
├── tests/
│   ├── test_phase3_analytics.py      # Phase 3 attribution, CLV, and ROI tests (14 tests)
│   ├── test_phase2_analytics.py      # Phase 2 core analytics tests (7 tests)
│   ├── test_phase2_models.py         # Phase 2 SQL models tests (6 tests)
│   ├── test_synthetic_data.py        # Phase 1 synthetic data tests (13 tests)
│   └── test_bigquery_runner.py       # BigQuery runner & staging tests (5 tests)
├── documentation/
│   ├── TABLEAU_DATA_DICTIONARY.md    # Tableau schema (40 cols), metrics, and wireframe guide
│   ├── METRIC_DEFINITIONS.md         # Comprehensive formulas for KPIs, attribution, CLV, and ROI
│   ├── PROJECT_ARCHITECTURE.md       # Technical pipeline architecture & governance
│   ├── GA4_SOURCE_DOCUMENTATION.md   # GA4 event stream reference & schema guide
│   └── SYNTHETIC_DATA.md             # Five-tier data governance specification
├── reports/
│   ├── final_submission_audit.json   # Machine-readable final submission audit
│   ├── phase3_validation.json        # Machine-readable Phase 3 validation audit
│   ├── budget_reallocation_recommendations.json # Campaign reallocation recommendations
│   ├── phase2_validation.json
│   ├── phase1_synthetic_validation.json
│   └── phase1_bigquery_validation.json
├── CHANGELOG.md
├── requirements.txt
└── PROJECT_PLAN.md
```

---

## 4. Core KPI & Attribution Summary (LOCAL_REPRODUCIBLE_EXECUTION)

* **Total Revenue:** $131,133.96 across 1,659 completed purchases (AOV: $79.04, CVR: 13.7%).
* **Attribution Reconciliation:** All 4 models (First Touch, Last Touch, Linear, Time Decay 7d) reconcile to **$131,133.96** exactly (zero variance, weights sum to 1.0).
* **Customer CLV:** Total historical margin realized is $59,010.32; forward 12-month predicted CLV is $149,065.05 (45% illustrative scenario margin assumption).
* **Budget Optimization:** $74,069.20 reallocation pool identified from 6 low-ROAS campaigns ($\text{ROAS} < 0.25$) for reallocation to high-ROAS `Brand_Search_Core` ($\text{ROAS } 0.567, \text{CAC } \$8.02$, action: `SCALE_BUDGET (+20%)`).
