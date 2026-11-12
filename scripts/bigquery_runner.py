"""
Reusable Python BigQuery Runner.

Executes dbt-style SQL models, validates syntax and costs via dry-run,
creates datasets and views/tables in project-owned datasets, and returns structured execution metrics.
"""

import sys
import time
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import BigQueryConfig, default_config


class BigQueryRunner:
    """Executes SQL transformations and analytical queries against Google BigQuery."""

    def __init__(self, config: Optional[BigQueryConfig] = None):
        self.config = config or default_config
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = self.config.get_bigquery_client()
        return self._client

    def render_sql(self, sql: str, params: Optional[Dict[str, str]] = None) -> str:
        """
        Renders template variables inside SQL queries.
        Supports Jinja/dbt style {{ variable }} replacements.
        """
        context = {
            "source_project": self.config.ga4_source_project,
            "source_dataset": self.config.ga4_source_dataset,
            "source_table_prefix": self.config.ga4_source_table_prefix,
            "target_project": self.config.project_id or "",
            "target_dataset": self.config.dataset_id,
        }
        if params:
            context.update(params)

        rendered = sql
        for key, value in context.items():
            rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def dry_run(self, sql: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Performs a BigQuery dry-run to estimate query cost and validate syntax.
        Does not process query data or incur billing charges.
        """
        from google.cloud import bigquery

        rendered_sql = self.render_sql(sql, params)
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        start_time = time.time()
        try:
            query_job = self.client.query(rendered_sql, job_config=job_config)
            bytes_processed = query_job.total_bytes_processed
            elapsed = time.time() - start_time
            return {
                "status": "SUCCESS",
                "mode": "DRY_RUN",
                "bytes_processed": bytes_processed,
                "mb_processed": round(bytes_processed / (1024 * 1024), 2),
                "gb_processed": round(bytes_processed / (1024 * 1024 * 1024), 4),
                "duration_seconds": round(elapsed, 3),
                "error": None
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "mode": "DRY_RUN",
                "bytes_processed": 0,
                "duration_seconds": round(time.time() - start_time, 3),
                "error": str(e),
                "error_type": type(e).__name__
            }

    def execute_query(self, sql: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Executes a SQL query and returns execution metadata.
        """
        rendered_sql = self.render_sql(sql, params)
        start_time = time.time()
        try:
            query_job = self.client.query(rendered_sql)
            results = query_job.result()
            elapsed = time.time() - start_time
            return {
                "status": "SUCCESS",
                "mode": "EXECUTE",
                "job_id": query_job.job_id,
                "total_rows": results.total_rows,
                "bytes_billed": query_job.total_bytes_billed,
                "duration_seconds": round(elapsed, 3),
                "error": None
            }
        except Exception as e:
            return {
                "status": "FAILED",
                "mode": "EXECUTE",
                "duration_seconds": round(time.time() - start_time, 3),
                "error": str(e),
                "error_type": type(e).__name__
            }

    def query_to_dataframe(self, sql: str, params: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Executes a SELECT query and returns the results as a Pandas DataFrame.
        """
        rendered_sql = self.render_sql(sql, params)
        query_job = self.client.query(rendered_sql)
        return query_job.to_dataframe()

    def run_sql_file(self, file_path: Path, dry_run: bool = False, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Reads and executes or dry-runs a SQL file.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"SQL file not found at: {file_path}")

        sql_content = file_path.read_text(encoding="utf-8")
        if dry_run:
            return self.dry_run(sql_content, params)
        return self.execute_query(sql_content, params)

    def materialize_model(
        self,
        file_path: Path,
        model_name: Optional[str] = None,
        materialization: str = "view",
        dry_run: bool = False,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Renders a model SQL file and materializes it as a VIEW or TABLE
        in the project-owned target dataset.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Model file not found: {file_path}")

        name = model_name or file_path.stem
        select_sql = file_path.read_text(encoding="utf-8")
        rendered_select = self.render_sql(select_sql, params)

        target_ref = f"`{self.config.project_id}.{self.config.dataset_id}.{name}`" if self.config.project_id else f"`{self.config.dataset_id}.{name}`"

        if materialization.lower() == "table":
            ddl_sql = f"CREATE OR REPLACE TABLE {target_ref} AS\n{rendered_select}"
        else:
            ddl_sql = f"CREATE OR REPLACE VIEW {target_ref} AS\n{rendered_select}"

        if dry_run:
            return self.dry_run(ddl_sql)
        return self.execute_query(ddl_sql)

    def ensure_dataset(self, dataset_id: str, location: Optional[str] = None) -> bool:
        """
        Creates a BigQuery dataset if it does not already exist.
        """
        from google.cloud import bigquery
        from google.cloud.exceptions import Conflict

        dataset_ref = f"{self.config.project_id}.{dataset_id}"
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location or self.config.location

        try:
            self.client.create_dataset(dataset, exists_ok=True)
            print(f"Dataset verified/created: {dataset_ref}")
            return True
        except Conflict:
            return True
        except Exception as e:
            print(f"Could not create dataset {dataset_ref}: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="BigQuery Runner CLI")
    parser.add_argument("--file", type=str, help="Path to SQL file to execute")
    parser.add_argument("--materialize", choices=["view", "table"], default="view", help="Materialization type")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run only")
    args = parser.parse_args()

    runner = BigQueryRunner()
    if args.file:
        path = Path(args.file)
        result = runner.materialize_model(path, materialization=args.materialize, dry_run=args.dry_run)
        print(result)


if __name__ == "__main__":
    main()
