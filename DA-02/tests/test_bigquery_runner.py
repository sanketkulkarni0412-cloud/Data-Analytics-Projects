"""
Unit and Integration Tests for BigQuery Runner and Staging SQL Configuration.
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml
from scripts.config import BigQueryConfig
from scripts.bigquery_runner import BigQueryRunner


class TestBigQueryRunnerAndConfig(unittest.TestCase):
    """Verifies the runner, configuration, and SQL models."""

    def setUp(self):
        self.config = BigQueryConfig(
            project_id="test-ecom-project",
            dataset_id="test_dataset",
            location="US",
            ga4_source_project="bigquery-public-data",
            ga4_source_dataset="ga4_obfuscated_sample_ecommerce",
            ga4_source_table_prefix="events_*"
        )
        self.runner = BigQueryRunner(self.config)

    def test_sql_rendering(self):
        """Verifies template parameters are correctly rendered."""
        raw_sql = "SELECT * FROM `{{ source_project }}.{{ source_dataset }}.{{ source_table_prefix }}`"
        rendered = self.runner.render_sql(raw_sql)
        expected = "SELECT * FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`"
        self.assertEqual(rendered, expected)

    def test_custom_param_rendering(self):
        """Verifies custom parameters are substituted."""
        raw_sql = "SELECT count(*) FROM `{{ target_dataset }}.{{ custom_table }}`"
        rendered = self.runner.render_sql(raw_sql, params={"custom_table": "my_test_table"})
        expected = "SELECT count(*) FROM `test_dataset.my_test_table`"
        self.assertEqual(rendered, expected)

    def test_stg_ga4_events_file_exists_and_valid(self):
        """Verifies staging SQL model file exists and includes essential dimensions."""
        model_path = PROJECT_ROOT / "models" / "staging" / "stg_ga4_events.sql"
        self.assertTrue(model_path.exists(), f"Missing SQL file: {model_path}")

        sql_text = model_path.read_text(encoding="utf-8")
        essential_tokens = [
            "user_pseudo_id",
            "ga_session_id",
            "event_name",
            "event_date",
            "event_timestamp",
            "purchase_revenue_in_usd",
            "transaction_id",
            "session_key"
        ]
        for token in essential_tokens:
            self.assertIn(token, sql_text, f"stg_ga4_events.sql missing required token: {token}")

    def test_sources_yaml_validity(self):
        """Verifies sources.yml is valid YAML and references the GA4 dataset."""
        sources_path = PROJECT_ROOT / "models" / "staging" / "sources.yml"
        self.assertTrue(sources_path.exists(), f"Missing sources.yml: {sources_path}")

        content = yaml.safe_load(sources_path.read_text(encoding="utf-8"))
        self.assertIn("sources", content)
        source_entry = content["sources"][0]
        self.assertEqual(source_entry["database"], "bigquery-public-data")
        self.assertEqual(source_entry["schema"], "ga4_obfuscated_sample_ecommerce")

    def test_reports_directory_structure(self):
        """Verifies required directories exist."""
        for d in ["models/staging", "models/intermediate", "models/marts", "scripts", "documentation", "reports"]:
            target_path = PROJECT_ROOT / d
            self.assertTrue(target_path.exists(), f"Directory missing: {target_path}")


if __name__ == "__main__":
    unittest.main()
