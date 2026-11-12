# Tableau Dashboard Architecture & Implementation Guide

**Project:** Ecommerce Customer & Marketing Analytics  
**Primary Data Source:** `data/tableau_customer_marketing_analytics.csv` (5,000 rows × 40 columns)  
**Secondary Data Sources:**
- `data/fct_attribution_multi_model.csv` (9,464 rows across 4 models)
- `data/fct_campaign_roi.csv` (8 campaigns across 5 channels)  
**Governance Notice:** All metrics reflect **LOCAL_REPRODUCIBLE_EXECUTION validation outputs** calibrated against the **Public GA4 dataset source/design** (`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`).
**Environment Disclosure:** Tableau Desktop is not installed in the local execution sandbox. This document serves as the complete, step-by-step production workbook specification, containing exact worksheet configurations, calculated fields, filter cards, layout containers, and design wireframes ready for direct import into Tableau Desktop or Tableau Public.

---

## 1. Data Connection & Modeling Setup

### Step 1: Connecting Data Sources
1. Launch Tableau Desktop / Tableau Public.
2. Select **Connect -> To a File -> Text File** and choose `data/tableau_customer_marketing_analytics.csv`.
3. In the Data Source canvas, add two additional connections or relationships:
   * **Attribution Mart:** `data/fct_attribution_multi_model.csv` linked via `customer_id` (Relationship: Many-to-One).
   * **Campaign ROI Mart:** `data/fct_campaign_roi.csv` linked via `acquisition_channel` = `channel` (Relationship: Many-to-One).
4. Verify data types:
   * `customer_id`, `synthetic_first_name`, `synthetic_last_name`, `synthetic_email`, `customer_tier`, `country`, `preferred_device`, `acquisition_channel`, `rfm_cell`, `rfm_segment`, `clv_segment`: **String**.
   * `signup_date`, `first_session_date`, `last_session_date`, `first_order_date`, `last_order_date`: **Date**.
   * `is_loyalty_member`, `opted_in_email`, `is_synthetic`: **Boolean**.
   * `customer_total_sessions`, `total_engaged_sessions`, `total_page_views`, `total_duration_seconds`, `customer_total_orders`, `days_since_last_activity`, `r_score`, `f_score`, `m_score`: **Number (Whole)**.
   * `customer_total_revenue`, `average_order_value`, `purchase_frequency`, `composite_rfm`, `historical_clv`, `predicted_12m_clv`: **Number (Decimal)**.

### Step 2: Key Tableau Calculated Fields
Create these calculated fields in Tableau:

```tableau
// 1. Blended E-Commerce Conversion Rate
[CVR %] = 
SUM([customer_total_orders]) / SUM([customer_total_sessions])

// 2. Average Order Value (AOV)
[Calculated AOV] = 
SUM([customer_total_revenue]) / IIF(SUM([customer_total_orders]) = 0, 1, SUM([customer_total_orders]))

// 3. Repeat Buyer Flag
[Is Repeat Buyer] = 
[customer_total_orders] >= 2

// 4. Repeat Purchase Rate
[Repeat Purchase Rate %] = 
COUNTD(IIF([customer_total_orders] >= 2, [customer_id], NULL)) / 
COUNTD(IIF([customer_total_orders] >= 1, [customer_id], NULL))

// 5. Historical CLV (45% Margin Scenario)
[Calculated Historical CLV] = 
SUM([customer_total_revenue]) * 0.45

// 6. CLV Expansion Potential (Upside)
[CLV Expansion Potential] = 
[predicted_12m_clv] - [historical_clv]

// 7. ROAS Color Indicator
[ROAS Efficiency Tier] = 
IF [ROAS] >= 0.50 THEN "High Efficiency (Scale)"
ELSEIF [ROAS] >= 0.25 THEN "Moderate Efficiency (Optimize)"
ELSE "Low Efficiency (Reduce/Reallocate)"
END
```

---

## 2. Dashboard 1: Executive Overview

**Target Audience:** Chief Marketing Officer (CMO), VP of E-Commerce, Chief Revenue Officer (CRO).  
**Dimensions:** 1366 × 768 px (Fixed / Automatic Responsive).

### Layout & Visual Cards

```
+---------------------------------------------------------------------------------------------------------+
|  HEADER: E-COMMERCE CUSTOMER & MARKETING ANALYTICS — EXECUTIVE OVERVIEW                                 |
|  Filters: Date Range [2020-11-01 to 2021-01-31] | Channel: [All] | Customer Tier: [All]                 |
+-------------------+-------------------+-------------------+--------------------+------------------------+
| TOTAL REVENUE     | TOTAL ORDERS      | AOV               | CONVERSION RATE    | TOTAL AD SPEND         |
| $131,133.96       | 1,659             | $79.04            | 13.70%             | $308,808.42            |
| Target: Met 100%  | 1,099 buyers      | Historical Avg    | 12,108 sessions    | 8 active campaigns     |
+-------------------+-------------------+-------------------+--------------------+------------------------+
| BLENDED ROAS      | BLENDED CAC       | TOTAL CRM BASE    | REPEAT BUYER RATE  | HISTORICAL MARGIN (45%)|
| 0.424             | $186.14           | 5,000 Customers   | 34.03%             | $59,010.32             |
| $131.1K / $308.8K | 1,659 conversions | 60% web-resolved  | 374 repeat buyers  | Illustrative scenario  |
+-------------------+-------------------+-------------------+--------------------+------------------------+
| CHART 1: DAILY REVENUE & ORDER VOLUME TREND (Dual-Axis)                                                 |
| Columns: [last_order_date] (Continuous Day)                                                            |
| Rows: SUM([customer_total_revenue]) (Bars), SUM([customer_total_orders]) (Line)                         |
| Highlight: Peak holiday shopping surges during Cyber Week (Late Nov) and Holiday Sales (Dec 2020).      |
+---------------------------------------------------+-----------------------------------------------------+
| CHART 2: REVENUE MIX BY ACQUISITION CHANNEL       | CHART 3: BUYER VS NON-BUYER RETENTION FUNNEL        |
| Marks: Donut Chart                                | Marks: Horizontal Funnel Bar Chart                  |
| Dimension: [acquisition_channel]                  | • Total Visitors: 7,000 (100%)                      |
| Measure: SUM([customer_total_revenue])            | • Resolved CRM Profiles: 4,200 (60.0%)              |
| Labels: Paid Search (37%), Paid Social (27%),     | • Active Sessions Recorded: 2,631 (37.6%)           |
| Organic Search (9%), Direct (8%), Display/Video   | • Purchasing Customers: 1,099 (15.7%)               |
|                                                   | • Repeat Buyers (>=2 orders): 374 (5.3%)            |
+---------------------------------------------------+-----------------------------------------------------+
```

---

## 3. Dashboard 2: Marketing Channel Performance & Attribution Comparison

**Target Audience:** VP of Growth, Acquisition Lead, Attribution Specialist.  
**Primary Dataset:** `data/fct_attribution_multi_model.csv` (9,464 rows).

### Worksheet Specifications

#### Sheet 2.1: Multi-Model Channel Revenue Comparison (Grouped Bar Chart)
* **Columns:** `channel` (Alphabetical: Affiliate, Direct, Display, Organic Search, Paid Search, Paid Social, Video).
* **Rows:** `SUM([attributed_revenue])`.
* **Color:** `attribution_model` (First Touch = Navy Blue, Last Touch = Crimson Red, Linear = Amber, Time Decay = Forest Green).
* **Tooltip:** Model Name, Channel, Attributed Revenue ($), % of Total Revenue.
* **Key Visual Comparison:**
  * **Paid Search:** First Touch ($48,331.64) vs Last Touch ($33,530.97) vs Linear ($39,840.05) vs Time Decay ($37,727.20).
  * **Direct:** First Touch ($10,712.22) vs Last Touch ($49,682.71) vs Linear ($34,281.51) vs Time Decay ($39,210.67).
  * **Paid Social:** First Touch ($35,640.91) vs Last Touch ($22,307.15) vs Linear ($27,635.81) vs Time Decay ($25,924.94).
* **Insight Callout:** First Touch credits customer acquisition channels (Paid Search + Paid Social = $83.9K, 64% of total), whereas Last Touch over-indexes on Direct ($49.7K, 37.9%) as repeat buyers navigate straight to the URL.

#### Sheet 2.2: Channel Unit Economics Table (Cross-Tab)
* **Rows:** `channel`.
* **Measures:**
  * Attributed Revenue (Linear): `$39,840` (Search), `$27,636` (Social), `$34,282` (Direct).
  * Allocated Ad Spend: `$123,847` (Search), `$105,872` (Social), `$0` (Direct).
  * Channel ROAS: `0.32` (Search), `0.26` (Social), `0.39` (Display), `0.26` (Affiliate), `0.24` (Video).
  * Channel CAC: `$17.38` (Search), `$32.10` (Social), `$14.88` (Affiliate), `$68.28` (Display), `$103.20` (Video).

#### Sheet 2.3: Lookback Touchpoint Decay Curve (Area Chart)
* **Columns:** `touchpoint_day_offset` ($0$ to $30$ days prior to conversion).
* **Rows:** Exponential weight $w(t) = 2^{-t/7}$.
* **Annotation:** Half-life point at $t = 7.0\text{ days}$ ($w = 0.50$).

---

## 4. Dashboard 3: Campaign Performance & Unit Economics

**Target Audience:** Performance Marketing Managers, Paid Media Buyers.  
**Primary Dataset:** `data/fct_campaign_roi.csv` (8 rows).

### Worksheet Specifications

#### Sheet 3.1: Campaign Efficiency Matrix (Scatter Plot)
* **X-Axis:** `CAC` ($0 to $120).
* **Y-Axis:** `ROAS` (0.0 to 0.70).
* **Size:** `spend` (Bubble size scaled by marketing spend).
* **Color:** `recommended_action`:
  * `SCALE_BUDGET (+20%)` = Emerald Green
  * `OPTIMIZE_WATCH` = Sky Blue
  * `REDUCE_REALLOCATE (-30%)` = Coral Red
* **Reference Lines:**
  * Horizontal line at $\text{ROAS} = 0.35$ (Break-even target).
  * Vertical line at $\text{CAC} = \$50.00$ (Target acquisition cost).
* **Data Points Position:**
  1. `Brand_Search_Core`: Top Left ($CAC = \$8.02, ROAS = 0.567$, Spend = $36.7K) — **Star Performer**.
  2. `Dynamic_Remarketing_Banners`: Middle ($CAC = \$68.28, ROAS = 0.265$, Spend = $25.2K) — **Watchlist**.
  3. `Affiliate_Partner_Deals`: Low CAC but low ROAS ($CAC = \$14.88, ROAS = 0.178$, Spend = $22.1K).
  4. `Holiday_Gift_Guide_2020`: ($CAC = \$37.79, ROAS = 0.234$, Spend = $43.2K).
  5. `Generic_Apparel_Promo`: ($CAC = \$38.36, ROAS = 0.231$, Spend = $51.8K).
  6. `Brand_Awareness_Video_Q4`: High CAC ($CAC = \$103.20, ROAS = 0.201$, Spend = $31.8K).
  7. `Black_Friday_Cyber_Week`: ($CAC = \$29.08, ROAS = 0.189$, Spend = $62.6K).
  8. `Winter_Clearance_Sale`: Zero Revenue ($CAC = \$29.56, ROAS = 0.000$, Spend = $35.4K).

#### Sheet 3.2: Campaign League Table (Ranked Horizontal Bar Chart)
* **Rows:** `campaign` sorted descending by `ROAS`.
* **Measures:** Spend, Revenue, ROAS, CAC, CTR (%), CVR (%), RPC ($).

---

## 5. Dashboard 4: Customer Intelligence — RFM & CLV Segmentation

**Target Audience:** CRM Director, Retention Marketing Lead, Customer Support.  
**Primary Dataset:** `data/tableau_customer_marketing_analytics.csv` (5,000 customer rows).

### Worksheet Specifications

#### Sheet 4.1: RFM 5×5 Heatmap Grid
* **Columns:** `f_score` (1 = Infrequent to 5 = Top Frequent).
* **Rows:** `r_score` (1 = Stale to 5 = Highly Recent).
* **Color:** Average `m_score` or Total `customer_total_revenue` (Viridis / Orange-Blue sequential).
* **Labels:** Customer Count in each cell + Total Revenue.
* **Top Cells:** Cell 555 (182 top spenders), Cell 111 (612 dormant users).

#### Sheet 4.2: Strategic RFM Segments Treemap
* **Dimension:** `rfm_segment`.
* **Size:** `customer_count`.
* **Color:** Total Segment Revenue:
  * **At Risk High Value:** 1,154 customers (23.1%), $32,410 revenue.
  * **Champions:** 962 customers (19.2%), $48,150 revenue.
  * **Loyal Customers:** 884 customers (17.7%), $29,620 revenue.
  * **Hibernating / Inactive:** 846 customers (16.9%), $2,180 revenue.
  * **Recent Potential Loyalists:** 704 customers (14.1%), $12,890 revenue.
  * **Promising / General:** 450 customers (9.0%), $5,884 revenue.

#### Sheet 4.3: Customer Lifetime Value (Historical vs Predicted 12M CLV)
* **X-Axis:** `historical_clv` ($0 to $350).
* **Y-Axis:** `predicted_12m_clv` ($0 to $1,550).
* **Color:** `clv_segment`:
  * `High Value VIP` (163 customers, >$120 predicted CLV, Emerald).
  * `Medium Value Core` (388 customers, $50–$120 predicted CLV, Blue).
  * `Low Value Nurture` (1,020 customers, $20–$50 predicted CLV, Gold).
  * `Prospect / Inactive` (3,429 customers, <$20 predicted CLV, Gray).
* **Annotation:** Total Historical Realized Margin: **$59,010.32**; Total Predicted Forward Margin: **$149,065.05**.

---

## 6. Dashboard 5: Budget Optimization & Capital Reallocation Engine

**Target Audience:** CFO, CMO, Performance Marketing Director.  
**Key Deliverable:** Actionable, auditable budget moves based on empirical ROI thresholds.

### Reallocation Framework & Rules

| Category | Quantitative Rule | Budget Action | Actioned Campaigns | Spend Shift |
|---|---|---|---|---|
| **SCALE_BUDGET** | $\text{ROAS} \ge 0.50$ OR ($\text{ROAS} \ge 0.35$ & $\text{CAC} \le \$200$) | Increase daily budget by +20% | `Brand_Search_Core` | **+$7,342.88** immediate expansion (Primary target of pooled funds) |
| **MAINTAIN_EFFICIENT** | $0.35 \le \text{ROAS} < 0.50$ AND $\text{CAC} \le \$250$ | Hold current budget; creative testing | *(None qualify)* | **$0.00** |
| **OPTIMIZE_WATCH** | $0.25 \le \text{ROAS} < 0.35$ | Freeze spend; tighten exclusions | `Dynamic_Remarketing_Banners` | **$0.00** ($25,196.70 preserved) |
| **REDUCE_REALLOCATE** | $\text{ROAS} < 0.25$ OR $\text{CAC} > \$300$ | Reduce budget by -30%; sweep pool | 6 campaigns | **-$74,069.20** total capital extracted |

### Waterfall Budget Reallocation Table

```text
Campaign Name                 Channel        Initial Spend   Action                Shift ($)      Revised Spend
───────────────────────────────────────────────────────────────────────────────────────────────────────────────
Affiliate_Partner_Deals       Affiliate       $22,108.37    REDUCE_REALLOCATE     -$6,632.51       $15,475.86
Generic_Apparel_Promo         Paid Search     $51,782.54    REDUCE_REALLOCATE    -$15,534.76       $36,247.78
Winter_Clearance_Sale         Paid Search     $35,350.49    REDUCE_REALLOCATE    -$10,605.15       $24,745.34
Black_Friday_Cyber_Week       Paid Social     $62,642.72    REDUCE_REALLOCATE    -$18,792.82       $43,849.90
Holiday_Gift_Guide_2020       Paid Social     $43,228.92    REDUCE_REALLOCATE    -$12,968.68       $30,260.24
Brand_Awareness_Video_Q4      Video           $31,784.28    REDUCE_REALLOCATE     -$9,535.28       $22,249.00
Dynamic_Remarketing_Banners   Display         $25,196.70    OPTIMIZE_WATCH             $0.00       $25,196.70
Brand_Search_Core             Paid Search     $36,714.40    SCALE_BUDGET         +$74,069.20      $110,783.60
───────────────────────────────────────────────────────────────────────────────────────────────────────────────
TOTAL MARKETING BUDGET                       $308,808.42    REALLOCATION POOL          $0.00      $308,808.42
```

---

## 7. Interactive Filter Design & Dashboard Usability

### Global Filters
1. **Date Range Filter:** `signup_date` / `last_order_date` (Slider: 2020-11-01 to 2021-01-31). Applied to all sheets.
2. **Channel Filter:** `acquisition_channel` / `channel` (Multiple values dropdown with Search).
3. **Campaign Filter:** `campaign` (Multiple values dropdown).
4. **Customer Segment Filter:** `rfm_segment` (List box with single-select / multi-select).
5. **Attribution Model Parameter:** `attribution_model` (Dropdown: `FIRST_TOUCH`, `LAST_TOUCH`, `LINEAR`, `TIME_DECAY`).

### Visual Theme & Styling Best Practices
* **Palette:**
  * Executive Primary: Classic Tableau Navy (`#1F77B4`)
  * Attribution / High Efficiency: Forest Emerald (`#2CA02C`)
  * Underperforming / Reallocate: Crimson Coral (`#D62728`)
  * Neutral / Core: Charcoal Slate (`#4A5568`)
* **Typography:** Tableau Bold for KPI headlines (24pt), Tableau Medium for section headers (14pt), Tableau Book for table values and labels (10pt).
* **Number Formatting:**
  * Currency: `$#,##0.00` for revenue, spend, and CLV.
  * Percentages: `0.0%` for CTR, CVR, Repeat Purchase Rate.
  * Ratios: `0.00x` for ROAS.
