# Google Analytics 4 (GA4) Source Dataset Documentation

**Source Table Reference:** `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`  
**Dataset Provider:** Google Cloud Public Datasets / Google Merchandise Store  
**Data Nature:** Authentic, anonymized real-world behavioral event telemetry.

---

## 1. Overview & Lineage

The Google Analytics 4 sample e-commerce dataset contains actual event data collected from the Google Merchandise Store. The dataset covers daily event activity from **November 1, 2020 through January 31, 2021** across multiple daily sharded tables (`events_YYYYMMDD`).

All identifiers (`user_pseudo_id`, `user_id`) and values in this dataset are obfuscated by Google to preserve visitor privacy while maintaining true relational structure, user journeys, and funnel behavior.

---

## 2. Table Schema & Column Specifications

| Column Name | BigQuery Data Type | Mode | Description |
|---|---|---|---|
| `event_date` | `STRING` | NULLABLE | Date of event occurrence in `YYYYMMDD` format. |
| `event_timestamp` | `INTEGER` | NULLABLE | Microseconds since Unix epoch (`1970-01-01 00:00:00 UTC`). |
| `event_name` | `STRING` | NULLABLE | Name of the telemetry action (e.g., `session_start`, `page_view`, `purchase`). |
| `event_params` | `RECORD` (Repeated) | REPEATED | Array of structs with schema `{key: STRING, value: {string_value: STRING, int_value: INT64, float_value: FLOAT64, double_value: FLOAT64}}`. |
| `event_previous_timestamp` | `INTEGER` | NULLABLE | Microseconds timestamp of previous event for the user. |
| `event_value_in_usd` | `FLOAT` | NULLABLE | Event-level monetary value in USD. |
| `user_id` | `STRING` | NULLABLE | Logged-in authenticated user ID (often null for anonymous traffic). |
| `user_pseudo_id` | `STRING` | NULLABLE | Unique pseudonymous identifier assigned to the web browser instance (cookie). |
| `privacy_info` | `RECORD` | NULLABLE | Consent status indicators (`analytics_storage`, `ads_storage`). |
| `user_properties` | `RECORD` (Repeated) | REPEATED | User-level custom dimensions. |
| `user_first_touch_timestamp`| `INTEGER` | NULLABLE | Timestamp when the user first interacted with the property. |
| `device` | `RECORD` | NULLABLE | Struct containing `category`, `mobile_brand_name`, `operating_system`, `web_info.browser`. |
| `geo` | `RECORD` | NULLABLE | Struct containing `continent`, `sub_continent`, `country`, `region`, `city`, `metro`. |
| `app_info` | `RECORD` | NULLABLE | Application metadata (version, ID). |
| `traffic_source` | `RECORD` | NULLABLE | User-level initial acquisition: `name`, `medium`, `source`. |
| `stream_id` | `STRING` | NULLABLE | Data stream identifier. |
| `platform` | `STRING` | NULLABLE | Platform identifier (`WEB`). |
| `event_dimensions` | `RECORD` | NULLABLE | Extra event dimensions. |
| `ecommerce` | `RECORD` | NULLABLE | Struct containing `total_item_quantity`, `purchase_revenue_in_usd`, `purchase_revenue`, `refund_value_in_usd`, `shipping_value_in_usd`, `tax_value_in_usd`, `transaction_id`. |
| `items` | `RECORD` (Repeated) | REPEATED | Array of item-level details (item_id, item_name, item_category, price, quantity). |

---

## 3. Critical Event Types in the Funnel

| Event Name | Funnel Stage | Purpose in Customer & Marketing Analysis |
|---|---|---|
| `session_start` | Acquisition / Visit | Marks start of a user browsing session; carries `ga_session_id`. |
| `page_view` | Engagement | Measures browsing depth, visited pages, content consumption. |
| `view_item` | Consideration | User views a specific product detail page. |
| `add_to_cart` | Intent | User adds an item to their shopping cart. |
| `begin_checkout`| High Intent | User enters checkout flow. |
| `purchase` | Conversion | Order completed; contains `transaction_id` and `purchase_revenue_in_usd`. |

---

## 4. Parameter Unnesting Strategy

Because GA4 stores event-level dimensions and metrics inside repeated key-value structs (`event_params`), the staging layer must unnest frequently queried parameters.

Example SQL pattern used in `stg_ga4_events.sql`:

```sql
(SELECT value.int_value FROM UNNEST(event_params) WHERE key = 'ga_session_id') AS ga_session_id,
(SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'page_location') AS page_location,
(SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'source') AS traffic_source_source,
(SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'medium') AS traffic_source_medium,
(SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'campaign') AS traffic_source_campaign
```

---

## 5. Query Optimization & Partition Pruning

The GA4 dataset spans over 90 daily partitioned tables. Querying the full wildcard `events_*` processes significant amounts of data.
For development, validation, and cost control:
- Filter on `_TABLE_SUFFIX` (e.g. `_TABLE_SUFFIX BETWEEN '20201101' AND '20210131'`).
- Always run dry-runs using `BigQueryRunner.dry_run()` prior to execution.
