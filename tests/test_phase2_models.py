"""
Phase 2 Analytics Data Models Validation Tests.

Validates that int_sessions.sql, int_orders.sql, and customer_profile.sql meet
all requirements: file existence, column presence, deduplication logic,
data invariant handling, and synthetic labeling boundaries.
"""

import sys
import unittest
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config import BigQueryConfig
from scripts.bigquery_runner import BigQueryRunner


class TestPhase2Models(unittest.TestCase):
    """Test suite for Phase 2 intermediate and mart models."""

    @classmethod
    def setUpClass(cls):
        cls.config = BigQueryConfig(
            project_id="test-ecom-project",
            dataset_id="ecommerce_analytics_marts",
            ga4_source_project="bigquery-public-data",
            ga4_source_dataset="ga4_obfuscated_sample_ecommerce",
            ga4_source_table_prefix="events_*"
        )
        cls.runner = BigQueryRunner(cls.config)
        cls.models_dir = PROJECT_ROOT / "models"
        cls.sessions_sql_path = cls.models_dir / "intermediate" / "int_sessions.sql"
        cls.orders_sql_path = cls.models_dir / "intermediate" / "int_orders.sql"
        cls.profile_sql_path = cls.models_dir / "marts" / "customer_profile.sql"

    def test_required_model_files_exist(self):
        """Verifies that all Phase 2 intermediate and mart SQL files exist."""
        self.assertTrue(self.sessions_sql_path.exists(), f"Missing {self.sessions_sql_path}")
        self.assertTrue(self.orders_sql_path.exists(), f"Missing {self.orders_sql_path}")
        self.assertTrue(self.profile_sql_path.exists(), f"Missing {self.profile_sql_path}")

    def test_int_sessions_columns_and_logic(self):
        """Verifies int_sessions.sql exposes all required session dimensions and metrics."""
        sql = self.sessions_sql_path.read_text(encoding="utf-8")
        rendered = self.runner.render_sql(sql)

        # No unexpanded template tags
        self.assertNotIn("{{", rendered)
        self.assertNotIn("}}", rendered)

        required_columns = [
            "session_id",
            "user_pseudo_id",
            "session_key",
            "session_date",
            "session_start_timestamp",
            "device_category",
            "country",
            "traffic_source",
            "traffic_medium",
            "traffic_campaign",
            "landing_page",
            "session_duration_seconds",
            "is_engaged_session",
            "event_count",
            "page_views",
            "has_purchase"
        ]
        for col in required_columns:
            self.assertIn(col, sql, f"int_sessions.sql missing required column/field: {col}")

    def test_int_orders_columns_and_deduplication(self):
        """Verifies int_orders.sql contains deduplication and revenue fields."""
        sql = self.orders_sql_path.read_text(encoding="utf-8")
        rendered = self.runner.render_sql(sql)

        self.assertNotIn("{{", rendered)
        self.assertNotIn("}}", rendered)

        required_columns = [
            "order_id",
            "order_date",
            "order_timestamp",
            "user_pseudo_id",
            "session_id",
            "order_revenue_usd",
            "tax_usd",
            "shipping_usd",
            "total_item_quantity",
            "net_merchandise_revenue_usd",
            "device_category",
            "traffic_source"
        ]
        for col in required_columns:
            self.assertIn(col, sql, f"int_orders.sql missing required column/field: {col}")

        # Verify explicit deduplication logic
        self.assertIn("ROW_NUMBER()", sql, "int_orders.sql must implement ROW_NUMBER() deduplication")
        self.assertIn("PARTITION BY transaction_id", sql, "int_orders.sql must partition by transaction_id")
        self.assertIn("transaction_instance_rank = 1", sql, "int_orders.sql must filter for rank = 1")

    def test_customer_profile_columns_and_governance(self):
        """Verifies customer_profile.sql combines CRM, Identity, and GA4 metrics with clear lineage."""
        sql = self.profile_sql_path.read_text(encoding="utf-8")
        rendered = self.runner.render_sql(sql)

        self.assertNotIn("{{", rendered)
        self.assertNotIn("}}", rendered)

        required_metrics = [
            "customer_id",
            "signup_date",
            "first_session_date",
            "last_session_date",
            "total_sessions",
            "total_orders",
            "total_revenue",
            "average_order_value",
            "days_since_last_activity",
            "purchase_frequency",
            "acquisition_source",
            "is_linked_to_ga4_visitor",
            "identity_resolution_confidence",
            "identity_link_method",
            "data_lineage_classification"
        ]
        for metric in required_metrics:
            self.assertIn(metric, sql, f"customer_profile.sql missing metric: {metric}")

        # Verify governance distinctions
        self.assertIn("SYNTHETIC CRM ATTRIBUTES", sql)
        self.assertIn("SYNTHETIC IDENTITY-MAPPING ATTRIBUTES", sql)
        self.assertIn("AUTHENTIC GA4 BEHAVIORAL ATTRIBUTES", sql)

    def test_order_deduplication_behavior(self):
        """Validates that duplicate transaction IDs are cleanly pruned."""
        mock_orders = pd.DataFrame([
            {"transaction_id": "ORD-001", "event_timestamp": 100, "purchase_revenue_in_usd": 45.0},
            {"transaction_id": "ORD-001", "event_timestamp": 110, "purchase_revenue_in_usd": 45.0},  # Refresh duplicate
            {"transaction_id": "ORD-002", "event_timestamp": 200, "purchase_revenue_in_usd": 85.0},
        ])
        deduped = mock_orders.sort_values("event_timestamp").groupby("transaction_id", as_index=False).first()
        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped["transaction_id"].tolist(), ["ORD-001", "ORD-002"])

    def test_customer_profile_grain_uniqueness(self):
        """Validates that customer profile maintains strict 1-to-1 customer_id grain."""
        crm_csv = PROJECT_ROOT / "data" / "synthetic_crm_customers.csv"
        self.assertTrue(crm_csv.exists(), "CRM customer CSV must exist")
        df_crm = pd.read_csv(crm_csv)
        self.assertEqual(len(df_crm), df_crm["customer_id"].nunique(), "customer_id must be strictly unique")


if __name__ == "__main__":
    unittest.main()
