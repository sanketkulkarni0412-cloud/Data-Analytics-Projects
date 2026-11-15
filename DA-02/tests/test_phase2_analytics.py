"""
Phase 2 End-to-End Analytics Validation Tests.

Validates the full analytics output: sessions, orders, attribution, campaign performance,
customer RFM segments, reconciliation invariants, and report schemas.
"""

import sys
import unittest
import json
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase2Analytics(unittest.TestCase):
    """Validation test suite for Phase 2 Core Analytics Deliverables."""

    @classmethod
    def setUpClass(cls):
        cls.data_dir = PROJECT_ROOT / "data"
        cls.sql_dir = PROJECT_ROOT / "sql"
        cls.reports_dir = PROJECT_ROOT / "reports"

        cls.sessions_path = cls.data_dir / "fct_sessions.csv"
        cls.orders_path = cls.data_dir / "fct_orders.csv"
        cls.attr_path = cls.data_dir / "fct_channel_attribution.csv"
        cls.campaign_path = cls.data_dir / "fct_campaign_performance.csv"
        cls.rfm_path = cls.data_dir / "fct_customer_rfm.csv"
        cls.report_path = cls.reports_dir / "phase2_validation.json"

        cls.df_sessions = pd.read_csv(cls.sessions_path)
        cls.df_orders = pd.read_csv(cls.orders_path)
        cls.df_attr = pd.read_csv(cls.attr_path)
        cls.df_campaign = pd.read_csv(cls.campaign_path)
        cls.df_rfm = pd.read_csv(cls.rfm_path)

    def test_sql_models_exist(self):
        """Verifies that all required SQL models exist in sql/."""
        expected_sql = [
            "staging/stg_ga4_events.sql",
            "staging/stg_crm_customers.sql",
            "staging/stg_identity_mapping.sql",
            "staging/stg_ad_spend.sql",
            "intermediate/int_sessions.sql",
            "intermediate/int_orders.sql",
            "marts/customer_profile.sql",
            "marts/fct_attribution.sql",
            "marts/fct_campaign_performance.sql",
            "marts/fct_customer_rfm.sql"
        ]
        for rel_path in expected_sql:
            p = self.sql_dir / rel_path
            self.assertTrue(p.exists(), f"Missing SQL model: {p}")

    def test_sessions_mart_integrity(self):
        """Verifies session mart has expected volume, uniqueness, and valid fields."""
        self.assertGreater(len(self.df_sessions), 10000)
        self.assertEqual(len(self.df_sessions), self.df_sessions["session_key"].nunique())
        self.assertTrue((self.df_sessions["session_duration_seconds"] >= 0).all())
        self.assertTrue((self.df_sessions["page_views"] >= 1).all())

    def test_orders_mart_integrity_and_deduplication(self):
        """Verifies orders mart has zero duplicates and non-negative revenue."""
        self.assertGreater(len(self.df_orders), 1000)
        self.assertEqual(len(self.df_orders), self.df_orders["order_id"].nunique(), "order_id must be strictly unique")
        self.assertTrue((self.df_orders["order_revenue_usd"] > 0).all(), "Order revenue must be positive")
        self.assertTrue((self.df_orders["total_item_quantity"] >= 1).all())

    def test_attribution_reconciliation(self):
        """Verifies 100% of orders are attributed and total revenue reconciles perfectly."""
        self.assertEqual(len(self.df_attr), len(self.df_orders), "Every order must have an attribution record")
        self.assertEqual(self.df_attr["order_id"].nunique(), len(self.df_orders))

        order_rev_sum = round(float(self.df_orders["order_revenue_usd"].sum()), 2)
        attr_rev_sum = round(float(self.df_attr["attributed_revenue_usd"].sum()), 2)
        self.assertAlmostEqual(order_rev_sum, attr_rev_sum, places=2, msg="Order revenue must reconcile with attributed revenue")

    def test_campaign_performance_metrics(self):
        """Verifies campaign performance table contains all 8 campaigns with valid unit economics."""
        self.assertEqual(len(self.df_campaign), 8)
        self.assertTrue((self.df_campaign["total_ad_spend_usd"] > 0).all())
        self.assertTrue((self.df_campaign["total_clicks"] > 0).all())
        self.assertTrue((self.df_campaign["ctr_pct"] > 0).all())
        self.assertTrue((self.df_campaign["cpc_usd"] > 0).all())

    def test_customer_rfm_mart_integrity(self):
        """Verifies customer RFM mart has 5,000 unique customers, scores 1-5, and valid segments."""
        self.assertEqual(len(self.df_rfm), 5000)
        self.assertEqual(self.df_rfm["customer_id"].nunique(), 5000)
        self.assertTrue(self.df_rfm["r_score"].isin([1, 2, 3, 4, 5]).all())
        self.assertTrue(self.df_rfm["f_score"].isin([1, 2, 3, 4, 5]).all())
        self.assertTrue(self.df_rfm["m_score"].isin([1, 2, 3, 4, 5]).all())
        self.assertTrue((self.df_rfm["composite_rfm"].between(1.0, 5.0)).all())

        valid_segments = {
            "Champions", "Loyal Customers", "Recent Potential Loyalists",
            "At Risk High Value", "At Risk Spenders", "Hibernating / Inactive",
            "Promising / General"
        }
        self.assertTrue(set(self.df_rfm["rfm_segment"].unique()).issubset(valid_segments))

    def test_phase2_report_json(self):
        """Verifies phase2_validation.json is valid and status is PASSED."""
        self.assertTrue(self.report_path.exists())
        with open(self.report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["validation_status"], "PASSED")
        self.assertIn("core_kpis", data)
        self.assertIn("marketing_performance", data["core_kpis"])
        self.assertIn("e_commerce", data["core_kpis"])


if __name__ == "__main__":
    unittest.main()
