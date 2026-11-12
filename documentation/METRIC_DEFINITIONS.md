# Comprehensive Metric Definitions & Analytical Framework

**Project:** Ecommerce Customer & Marketing Analytics  
**Document:** `documentation/METRIC_DEFINITIONS.md`  
**Execution Environment:** Python 3.13 / BigQuery Modular SQL Pattern + LOCAL_REPRODUCIBLE_EXECUTION Engine

---

## 1. Core Digital Analytics & E-Commerce KPIs

> [!IMPORTANT]
> **Data Governance & Benchmark Lineage Notice:**
> The baseline values referenced below ($12,108$ sessions, $1,659$ orders, $\$131,133.96$ revenue, $7,000$ visitors) represent **LOCAL_REPRODUCIBLE_EXECUTION validation outputs** generated deterministically by the Python analytics engine adhering to the **Public GA4 dataset source/design** (`bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`). Because live Google Cloud credentials are not configured, they are not claimed to be results directly queried live from BigQuery.

### Users & Identity Resolution
* **Total GA4 Visitors ($U_{\text{total}}$):** Total distinct simulated GA4 visitor instances (`user_pseudo_id`) in the observation cohort ($7,000$).
* **Resolved Users ($U_{\text{resolved}}$):** Count of visitor cookies linked via deterministic identity bridge to synthetic CRM customer records ($4,200$).
* **Anonymous / Unresolved Users ($U_{\text{anon}}$):** Count of visitor cookies that browsed without authenticating ($2,800$).
* **Resolution Rate:**
  $$\text{Resolution Rate} = \frac{U_{\text{resolved}}}{U_{\text{total}}} \times 100\% = \frac{4,200}{7,000} \times 100\% = 60.0\%$$

### Sessions & Engagement
* **Total Sessions ($S$):** Total aggregated browsing sessions (`session_key` = `user_pseudo_id` + `session_id`) ($12,108$ in validation cohort).
* **Engaged Session:** A session is classified as engaged if:
  $$\text{Duration} \ge 10\text{ seconds} \quad \text{OR} \quad \text{Page Views} \ge 2 \quad \text{OR} \quad \text{reported\_engagement\_flag} = 1$$
* **Engagement Rate:**
  $$\text{Engagement Rate} = \frac{\text{Engaged Sessions}}{\text{Total Sessions}} \times 100\%$$
* **Average Session Duration:**
  $$\overline{D} = \frac{1}{S} \sum_{i=1}^S (\text{session\_end\_timestamp}_i - \text{session\_start\_timestamp}_i)$$

### E-Commerce Conversions & Revenue
* **Total Orders ($O$):** Deduplicated count of completed e-commerce transactions (`order_id`) ($1,659$ in validation cohort).
* **Total Revenue ($R$):** Net gross merchandise revenue before discounts/refunds ($\$131,133.96$).
* **Average Order Value (AOV):**
  $$\text{AOV} = \frac{\text{Total Revenue}}{\text{Total Orders}} = \frac{\$131,133.96}{1,659} = \$79.04$$
* **E-Commerce Conversion Rate (CVR):**
  $$\text{Session CVR} = \frac{\text{Total Orders}}{\text{Total Sessions}} \times 100\% = \frac{1,659}{12,108} \times 100\% = 13.70\%$$

### Customer Lifecycle
* **Purchasing Customers:** Distinct CRM customers who completed $\ge 1$ purchase ($1,099$).
* **Repeat Purchasing Customers:** Distinct CRM customers who completed $\ge 2$ purchases ($374$).
* **Repeat Purchase Rate:**
  $$\text{Repeat Rate} = \frac{\text{Repeat Purchasing Customers}}{\text{Total Purchasing Customers}} \times 100\% = \frac{374}{1,099} \times 100\% = 34.03\%$$

---

## 2. Multi-Touch Attribution Models

Evaluated across a **30-day lookback window** preceding each transaction:

### A. First Touch Model
* **Philosophy:** Attributes 100% of conversion credit and order revenue to the very first touchpoint in the customer's lookback path.
* **Use Case:** Top-of-funnel customer acquisition analysis. Emphasizes brand discovery channels.
  $$w_i = \begin{cases} 1.0 & \text{if } i = 1 \text{ (earliest)} \\ 0.0 & \text{otherwise} \end{cases}$$

### B. Last Touch Model
* **Philosophy:** Attributes 100% of conversion credit and order revenue to the final marketing touchpoint immediately prior to the order.
* **Use Case:** Closing channel analysis. Highlights bottom-of-funnel channels and direct navigation.
  $$w_i = \begin{cases} 1.0 & \text{if } i = N \text{ (latest)} \\ 0.0 & \text{otherwise} \end{cases}$$

### C. Linear Attribution Model
* **Philosophy:** Distributes credit uniformly across all $N$ touchpoints in the lookback window.
* **Use Case:** Full-funnel holistic view; prevents single-touch bias.
  $$w_i = \frac{1}{N} \quad \forall i \in \{1, \dots, N\}$$

### D. Time Decay Attribution Model ($\lambda = 7$ Days)
* **Philosophy:** Exponentially weights touchpoints closer to the conversion moment with a 7-day half-life parameter.
* **Formula:**
  $$w_i^{\text{raw}} = 2^{-\frac{\Delta t_i}{7.0}}$$
  where $\Delta t_i = (\text{order\_date} - \text{touchpoint\_date}) \text{ in days}$.
  Normalized weight:
  $$w_i = \frac{w_i^{\text{raw}}}{\sum_{j=1}^N w_j^{\text{raw}}}$$
* **Direct Fallback Rule:** Direct navigation is filtered out if non-direct marketing touchpoints exist in the lookback path; if only direct sessions occurred, Direct is credited.
* **Revenue Reconciliation Invariant:** For every model:
  $$\sum \text{Attributed Revenue} = \text{Order Revenue} = \$131,133.96 \quad (\text{Variance} = \$0.00)$$

---

## 3. Customer Lifetime Value (CLV) Framework

### Governance Notice: Illustrative Scenario Assumption
The **45% contribution margin** used below is an **explicitly labeled illustrative scenario assumption** representative of typical e-commerce retail unit economics.

### A. Historical CLV (Realized Margin)
$$\text{Historical CLV}_c = \text{Historical Revenue}_c \times 0.45$$

### B. Predicted 12-Month Forward CLV
For active purchasing customers:
$$\text{Predicted 12M CLV}_c = \left(\text{Annualized Orders}_c \times \text{AOV}_c \times \text{Retention Rate}\right) \times 0.45$$
where:
* $\text{Annualized Orders}_c = \max\left(1.0, \text{Orders}_c \times \frac{365}{\max(30, \text{Lifespan Days}_c)}\right)$
* $\text{Retention Rate} = 0.75 \text{ (repeat buyers)} \quad \text{or} \quad 0.60 \text{ (first-time buyers)}$
For prospect/non-purchasing customers: expected lead value calibrated by CRM tier ($\$6-\$65$).

### C. CLV Tiers
* **High Value VIP:** Predicted 12M CLV $\ge \$120$ ($163$ customers)
* **Medium Value Core:** $\$50 \le \text{Predicted CLV} < \$120$ ($388$ customers)
* **Low Value Nurture:** $\$20 \le \text{Predicted CLV} < \$50$ ($1,020$ customers)
* **Prospect / Inactive:** Predicted CLV $< \$20$ ($3,429$ customers)

---

## 4. RFM Quintile Scoring & Customer Segmentation

Scores are ranked into 5 equal quintiles ($1 = \text{Lowest / Stale}, 5 = \text{Top Performer}$):
* **Recency ($R$):** Days since last activity (evaluated against 2021-01-31). Fewer days = higher score.
* **Frequency ($F$):** Total orders completed. More orders = higher score.
* **Monetary ($M$):** Total customer revenue. Higher spend = higher score.

### Strategic Segment Definitions
| Segment Name | Scoring Logic | Customer Count | Marketing Strategy |
|---|---|---|---|
| **Champions** | $R \ge 4, F \ge 4, M \ge 4$ | 962 | VIP rewards, early product access, brand advocates |
| **Loyal Customers** | $R \ge 3, F \ge 3, M \ge 3$ | 884 | Cross-sell, up-sell, loyalty club engagement |
| **Recent Potential Loyalists** | $R \ge 4, F \le 2$ | 704 | Welcome series, onboarding discounts, second-purchase incentives |
| **At Risk High Value** | $R \le 2, F \ge 3, M \ge 3$ | 1,154 | Win-back campaigns, personalized reactivation offers |
| **At Risk Spenders** | $R \le 2, F \le 2, M \ge 3$ | — | High-value re-engagement, price-drop alerts |
| **Hibernating / Inactive** | $R \le 2, F \le 2$ | 846 | Automated sunsetting, low-cost newsletter re-opt-in |
| **Promising / General** | All remaining cells | 450 | Standard seasonal merchandising |

---

## 5. Marketing ROI & Rule-Based Budget Optimization

### Formula Definitions
* **Click-Through Rate (CTR):** $\text{CTR} = \frac{\text{Clicks}}{\text{Impressions}} \times 100\%$
* **Cost Per Click (CPC):** $\text{CPC} = \frac{\text{Spend}}{\text{Clicks}}$
* **Cost Per Acquisition (CAC):** $\text{CAC} = \frac{\text{Spend}}{\text{Conversions}}$
* **Return on Ad Spend (ROAS):** $\text{ROAS} = \frac{\text{Attributed Revenue}}{\text{Spend}}$
* **Revenue Per Click (RPC):** $\text{RPC} = \frac{\text{Revenue}}{\text{Clicks}}$

### Transparent Rule-Based Recommendation Framework
| Action Category | Quantitative Thresholds | Strategic Execution |
|---|---|---|
| **SCALE_BUDGET (+20%)** | $\text{ROAS} \ge 0.50$ OR ($\text{ROAS} \ge 0.35$ AND $\text{CAC} \le \$200$) | Increase daily ad spend by 20%; high efficiency warrants expansion. |
| **MAINTAIN_EFFICIENT** | $0.35 \le \text{ROAS} < 0.50$ AND $\text{CAC} \le \$250$ | Preserve current budget; refresh ad creatives and test landing pages. |
| **OPTIMIZE_WATCH** | $0.25 \le \text{ROAS} < 0.35$ | Freeze budget; refine audience exclusions, negative keywords, and dayparting. |
| **REDUCE_REALLOCATE (-30%)**| $\text{ROAS} < 0.25$ OR $\text{CAC} > \$300$ | Cut budget by 30%; shift capital into top-performing campaigns. |
