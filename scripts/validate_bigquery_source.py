"""
Validation Script: Validates BigQuery GA4 Source Connectivity & Metrics.

Runs safe, read-only queries against bigquery-public-data.ga4_obfuscated_sample_ecommerce
and records execution results in reports/phase1_bigquery_validation.json.
"""

import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import default_config
from scripts.bigquery_runner import BigQueryRunner


def run_source_validation() -> Dict[str, Any]:
    """Validates the GA4 public dataset source and logs detailed metadata."""
    runner = BigQueryRunner(default_config)
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_file = reports_dir / "phase1_bigquery_validation.json"

    validation_result: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_dataset": f"{default_config.ga4_source_project}.{default_config.ga4_source_dataset}",
        "target_project": default_config.project_id or "NONE_CONFIGURED",
        "authentication_method": "SERVICE_ACCOUNT_KEY" if default_config.is_credentials_set else "ADC / AMBIENT",
        "checks": {}
    }

    # Query 1: Benchmark partition validation (single partition to be safe and cost-effective)
    sample_table = f"{default_config.ga4_source_project}.{default_config.ga4_source_dataset}.events_20210131"
    validation_query = f"""
        SELECT
            COUNT(*) AS total_events,
            COUNT(DISTINCT user_pseudo_id) AS distinct_users,
            MIN(PARSE_DATE('%Y%m%d', event_date)) AS min_date,
            MAX(PARSE_DATE('%Y%m%d', event_date)) AS max_date
        FROM `{sample_table}`
    """

    distribution_query = f"""
        SELECT
            event_name,
            COUNT(*) AS event_count
        FROM `{sample_table}`
        GROUP BY event_name
        ORDER BY event_count DESC
    """

    print("Running BigQuery dry run on sample partition...")
    dry_run_res = runner.dry_run(validation_query)
    validation_result["checks"]["dry_run"] = dry_run_res

    if dry_run_res["status"] == "SUCCESS":
        print(f"Dry run succeeded! Estimated data processed: {dry_run_res['mb_processed']} MB")
        try:
            print("Executing sample partition validation query...")
            df_summary = runner.query_to_dataframe(validation_query)
            row = df_summary.iloc[0].to_dict()

            print("Executing event distribution query...")
            df_dist = runner.query_to_dataframe(distribution_query)
            dist_dict = dict(zip(df_dist["event_name"], df_dist["event_count"].astype(int)))

            validation_result["status"] = "PASSED"
            validation_result["sample_partition"] = "events_20210131"
            validation_result["metrics"] = {
                "sample_partition_total_events": int(row["total_events"]),
                "sample_partition_distinct_users": int(row["distinct_users"]),
                "sample_date_range": {
                    "min_date": str(row["min_date"]),
                    "max_date": str(row["max_date"])
                },
                "event_type_distribution": dist_dict
            }
            print("Live validation succeeded!")
        except Exception as e:
            validation_result["status"] = "QUERY_EXECUTION_BLOCKED"
            validation_result["error"] = str(e)
            validation_result["error_type"] = type(e).__name__
            print(f"Query execution blocked: {e}")
    else:
        validation_result["status"] = "AUTHENTICATION_OR_PERMISSION_BLOCKED"
        validation_result["error"] = dry_run_res["error"]
        validation_result["error_type"] = dry_run_res["error_type"]
        validation_result["resolution_guidance"] = (
            "BigQuery requires an active Google Cloud Project to sponsor query compute. "
            "Configure a Google Cloud Project with the BigQuery API enabled, and ensure "
            "the identity has `roles/bigquery.jobUser` permission. "
            "A zero-cost BigQuery Sandbox project can be created without a billing account."
        )
        print(f"Validation blocked: {dry_run_res['error']}")

    # Write report
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(validation_result, f, indent=2)

    print(f"Report written to: {report_file}")
    return validation_result


if __name__ == "__main__":
    run_source_validation()
