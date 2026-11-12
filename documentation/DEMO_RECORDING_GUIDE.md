# Assessment Demo & Screen-Recording Guide

**Project:** Ecommerce Customer & Marketing Analytics  
**Document:** `documentation/DEMO_RECORDING_GUIDE.md`  
**Target Duration:** 7 to 10 Minutes  
**Video Resolution:** 1080p (1920 × 1080) at 60fps  
**Audio:** Clear microphone voiceover with screen capture (OBS Studio / Loom / Camtasia)  

---

## 1. Pre-Recording Preparation Checklist

Before initiating the screen recording, ensure the following setup is complete:
1. **Terminal / Shell:** Open PowerShell in `D:\Ecommerce-Customer-Marketing-Analytics`. Clear terminal (`Clear-Host`).
2. **VS Code / Editor:** Open workspace `D:\Ecommerce-Customer-Marketing-Analytics` with font size readable (14-16pt).
3. **Open Tabs in Editor:**
   - `README.md`
   - `documentation/SYNTHETIC_DATA.md`
   - `sql/staging/stg_ga4_events.sql`
   - `sql/marts/fct_attribution_multi_model.sql`
   - `data/tableau_customer_marketing_analytics.csv`
   - `documentation/TABLEAU_DASHBOARD_GUIDE.md`
   - `reports/budget_reallocation_recommendations.json`
   - `reports/final_submission_audit.json`
4. **Environment Check:** Confirm virtual environment is ready (`.\.venv\Scripts\Activate.ps1`).

---

## 2. Minute-by-Minute Recording Script & Screen Flow

### Section 1: Introduction & Project Overview (0:00 – 1:00)
* **Screen to Show:** `README.md` in VS Code / GitHub Preview.
* **Actions on Screen:**
  - Scroll through lines 1–35 of `README.md`.
  - Highlight the project title, data engineering goals, and directory layout.
* **Speaking Points:**
  > "Welcome to the final assessment walkthrough of the Ecommerce Customer and Marketing Analytics platform. In this project, we bridge the gap between Google Analytics 4 event telemetry, synthetic CRM customer data, multi-touch attribution, and marketing ROI optimization. Our goal is to solve the critical business challenge: determining exactly where marketing budget should be allocated across paid channels to maximize customer lifetime value and enterprise profit."

---

### Section 2: Data Governance & Credential Transparency (1:00 – 2:00)
* **Screen to Show:** `documentation/SYNTHETIC_DATA.md` and `reports/phase1_bigquery_validation.json`.
* **Actions on Screen:**
  - Display the 5-Tier Data Architecture diagram in `SYNTHETIC_DATA.md`.
  - Highlight the explicit credential disclosure: Tier A (Public GA4 dataset source/design), Tier B (Synthetic CRM), Tier C (Synthetic Spend), Tier D (Synthetic Identity Resolution), and Tier E (LOCAL_REPRODUCIBLE_EXECUTION outputs).
* **Speaking Points:**
  > "Data governance and regulatory compliance are built into the core of this project. We strictly delineate between authentic GA4 schema designs and synthetic simulations. Tier A models the authentic Google Merchandise Store BigQuery public dataset (`events_*`). Because live Google Cloud Application Default Credentials were not configured, we transparently disclose that all downstream validation marts and KPIs are generated as LOCAL_REPRODUCIBLE_EXECUTION validation outputs via our deterministic engine. Zero real PII is used; all 5,000 CRM profiles strictly utilize RFC 2606 reserved example domains."

---

### Section 3: Data Engineering, SQL Models & Identity Resolution (2:00 – 3:30)
* **Screen to Show:** `sql/staging/stg_ga4_events.sql` then `sql/intermediate/int_orders.sql` and `scripts/generate_identity_mapping.py`.
* **Actions on Screen:**
  - Show the unnesting logic for repeated `event_params` in `stg_ga4_events.sql` (`ga_session_id`, `page_location`, UTM dimensions).
  - Show `ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY event_timestamp ASC)` in `int_orders.sql` highlighting first-timestamp-wins order deduplication.
  - Show `synthetic_identity_mapping.csv` showing 60% resolved (4,200) vs 40% explicitly labeled anonymous (2,800).
* **Speaking Points:**
  > "Our data engineering layer addresses the real-world complexity of GA4. We handle repeated struct unnesting in BigQuery SQL and eliminate duplicate transactions caused by browser refreshes. Furthermore, our identity resolution graph connects 4,200 pseudonymous visitor cookies to authenticated CRM profiles across high-intent touchpoints like checkout and login, while explicitly preserving 2,800 anonymous visitors to avoid corrupting attribution with false assumptions."

---

### Section 4: Multi-Touch Attribution Model Reconciliation (3:30 – 5:00)
* **Screen to Show:** `data/fct_attribution_multi_model.csv` and `reports/phase3_validation.json`.
* **Actions on Screen:**
  - Open `reports/phase3_validation.json` and highlight `"attribution_reconciliation"`.
  - Point out that First Touch, Last Touch, Linear, and Time Decay 7d all reconcile to **$131,133.96** with **$0.00 unexplained variance**.
  - Show the channel comparison table: First Touch assigning $48.3K to Paid Search and $35.6K to Paid Social vs Last Touch assigning $49.7K to Direct.
* **Speaking Points:**
  > "Here is our attribution engine. We implemented four distinct attribution models over a 30-day conversion lookback window. Notice the mathematical rigor: all four models reconcile to exactly $131,133.96 in total order revenue with zero unexplained variance, and all attribution weights sum to 1.0 per order. Crucially, this side-by-side comparison reveals the massive flaw of single-touch Last Touch attribution: Last Touch credits Direct with nearly $50,000 as returning customers convert, completely blinding leadership to the fact that Paid Search and Paid Social drove 64% of top-of-funnel customer discoveries."

---

### Section 5: Customer Analytics — RFM & Customer Lifetime Value (5:00 – 6:15)
* **Screen to Show:** `data/tableau_customer_marketing_analytics.csv` and `documentation/METRIC_DEFINITIONS.md`.
* **Actions on Screen:**
  - Scroll through `tableau_customer_marketing_analytics.csv` showing `r_score`, `f_score`, `m_score`, `rfm_segment`, `historical_clv`, `predicted_12m_clv`, and `clv_segment`.
  - Point out the 6 strategic segments: Champions (962), At Risk High Value (1,154), Loyal Customers (884), etc.
* **Speaking Points:**
  > "For customer intelligence, we scored all 5,000 customers across a 5x5 RFM quintile matrix. We identified 1,154 customers in the 'At Risk High Value' segment—high-spending customers who haven't returned recently, representing our most urgent win-back opportunity. For Customer Lifetime Value, we established historical realized margin at $59,010.32 based on an illustrative 45% contribution margin scenario, and modeled forward 12-month CLV at $149,065.05 based on annualized order frequency and retention curves."

---

### Section 6: Campaign ROI & Budget Reallocation Recommendations (6:15 – 7:45)
* **Screen to Show:** `reports/budget_reallocation_recommendations.json` and `data/fct_campaign_roi.csv`.
* **Actions on Screen:**
  - Highlight the 8 evaluated campaigns and the 4-tier recommendation framework:
    * `Brand_Search_Core`: ROAS 0.567, CAC $8.02 -> **SCALE_BUDGET (+20%)**.
    * `Dynamic_Remarketing_Banners`: ROAS 0.265, CAC $68.28 -> **OPTIMIZE_WATCH**.
    * 6 campaigns with ROAS < 0.25 -> **REDUCE_REALLOCATE (-30%)**.
  - Show the **$74,069.20** reallocation pool and the revised spend waterfall.
* **Speaking Points:**
  > "Now turning to the core business question: where should we move our marketing budget? Out of $308,808 in total ad spend, our campaign unit economics revealed clear divergence. Brand Search Core is our runaway star performer with an outstanding ROAS of 0.567 and CAC of just $8.02. Conversely, six campaigns—including Black Friday Cyber Week, Generic Apparel, and Holiday Gift Guide—demonstrated ROAS under 0.25. Our automated framework harvests a 30% reduction from these low-efficiency campaigns, creating a $74,069.20 capital reallocation pool to immediately expand Brand Search Core, without requiring a single additional dollar of enterprise budget."

---

### Section 7: Tableau Integration & Presentation Deliverables (7:45 – 8:45)
* **Screen to Show:** `documentation/TABLEAU_DASHBOARD_GUIDE.md` and `presentation/PRESENTATION_SLIDES.md` / PPTX.
* **Actions on Screen:**
  - Show the 5 interactive dashboard wireframes in `TABLEAU_DASHBOARD_GUIDE.md`.
  - Highlight that `tableau_customer_marketing_analytics.csv` (5,000 rows × 40 columns) is pre-configured with all measures, dimensions, and calculated field formulas for drag-and-drop Tableau import.
  - Briefly display the 12-slide executive presentation in `presentation/`.
* **Speaking Points:**
  > "All of these findings are prepared for visual consumption. Because Tableau Desktop is not installed in our sandbox, we authored a comprehensive Tableau Dashboard Implementation Guide detailing exact worksheet layouts, filters, calculated fields, and visual wireframes for five executive dashboards. We also generated the complete 12-slide PowerPoint presentation deck ready for stakeholder review."

---

### Section 8: Test Suite Execution & Final Audit Result (8:45 – 9:45)
* **Screen to Show:** Terminal / PowerShell console.
* **Actions on Screen:**
  - Run the complete test suite live in terminal:
    ```powershell
    python -m unittest discover -s tests -p "test_*.py" -v
    ```
  - Display the output showing 45 tests passing with `OK`.
  - Open `reports/final_submission_audit.json` showing `"overall_submission_status": "READY_FOR_SUBMISSION"`.
* **Speaking Points:**
  > "To prove complete technical reproducibility and zero regression, let's run our test discovery suite live. As you can see, all 45 automated unit and integration tests across data generation, SQL models, attribution reconciliation, CLV, and ROI pass in under one second. Our final submission audit report confirms an overall status of READY_FOR_SUBMISSION. Thank you for your time."

---

## 3. Recommended Screencast Recording Settings

* **Capture Area:** 1920 × 1080 (Primary Monitor).
* **Terminal Font:** Consolas or Cascadia Code, 16pt, dark background with high-contrast text.
* **Editor Theme:** Dark Modern or GitHub Dark High Contrast.
* **Mouse Cursor:** Highlight cursor on clicks (yellow halo) enabled.
