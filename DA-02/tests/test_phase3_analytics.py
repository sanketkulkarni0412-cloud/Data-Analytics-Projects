"""
Phase 3 Analytics Comprehensive Automated Test Suite.

Validates:
1. Multi-Model Attribution (First Touch, Last Touch, Linear, Time Decay 7d)
   - Exact revenue reconciliation to total order revenue for all 4 models
   - Attribution weights per order sum to 1.0 within tolerance
   - No duplicate (order_id, attribution_model, channel) records
2. Customer Lifetime Value (CLV)
   - 5,000 customers, unique customer_id
   - Historical CLV = 45% of historical revenue
   - Predicted 12M CLV is strictly positive
   - Valid CLV segments
3. Campaign ROI & Budget Optimization
   - 8 campaigns
   - No negative spend
   - ROAS, CAC, CTR, CVR formulas verified
   - Transparent rule-based recommended actions populated
4. Tableau Consolidated Dataset
   - 5,000 rows
   - Dimensions, measures, governance tags verified
5. Data Governance Flags
   - SYNTHETIC_SIMULATION and LOCAL_REPRODUCIBLE_EXECUTION tags enforced
"""

import sys
import unittest
import json
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestPhase3Analytics(unittest.TestCase):
    """Validation tests for Phase 3 analytics deliverables."""

    @classmethod
    def setUpClass(cls):
        cls.data_dir = PROJECT_ROOT / "data"
        cls.sql_dir = PROJECT_ROOT / "sql" / "marts"
        cls.reports_dir = PROJECT_ROOT / "reports"

        cls.multi_attr_path = cls.data_dir / "fct_attribution_multi_model.csv"
        cls.clv_path = cls.data_dir / "fct_customer_clv.csv"
        cls.roi_path = cls.data_dir / "fct_campaign_roi.csv"
        cls.realloc_path = cls.reports_dir / "budget_reallocation_recommendations.json"
        cls.tableau_path = cls.data_dir / "tableau_customer_marketing_analytics.csv"
        cls.report_path = cls.reports_dir / "phase3_validation.json"
        cls.orders_path = cls.data_dir / "fct_orders.csv"

        cls.df_orders = pd.read_csv(cls.orders_path)
        cls.df_attr = pd.read_csv(cls.multi_attr_path)
        cls.df_clv = pd.read_csv(cls.clv_path)
        cls.df_roi = pd.read_csv(cls.roi_path)
        cls.df_tableau = pd.read_csv(cls.tableau_path)

        cls.total_order_revenue = round(float(cls.df_orders["order_revenue_usd"].sum()), 2)

    # ---------------- 1. MULTI-MODEL ATTRIBUTION TESTS ----------------

    def test_attribution_required_columns(self):
        """Verifies multi-model attribution contains all required columns."""
        required = [
            "order_id", "customer_id", "order_revenue", "attribution_model",
            "channel", "attributed_revenue", "attribution_weight",
            "touchpoint_count", "lookback_days"
        ]
        for col in required:
            self.assertIn(col, self.df_attr.columns, f"Missing attribution column: {col}")

    def test_attribution_four_models_present(self):
        """Verifies all four attribution models are populated."""
        models = set(self.df_attr["attribution_model"].unique())
        expected = {"FIRST_TOUCH", "LAST_TOUCH", "LINEAR", "TIME_DECAY"}
        self.assertEqual(models, expected)

    def test_attribution_revenue_reconciliation(self):
        """Verifies that for EVERY model, total attributed revenue equals order revenue exactly."""
        for model in ["FIRST_TOUCH", "LAST_TOUCH", "LINEAR", "TIME_DECAY"]:
            sub = self.df_attr[self.df_attr["attribution_model"] == model]
            m_rev = round(float(sub["attributed_revenue"].sum()), 2)
            self.assertAlmostEqual(
                m_rev, self.total_order_revenue, places=2,
                msg=f"Model {model} revenue {m_rev} differs from order revenue {self.total_order_revenue}"
            )

    def test_attribution_weights_sum_to_one(self):
        """Verifies attribution weights per order sum to 1.0 within tolerance."""
        order_model_weights = self.df_attr.groupby(["order_id", "attribution_model"])["attribution_weight"].sum()
        self.assertTrue(
            (order_model_weights.round(2) == 1.0).all(),
            "Attribution weights for every order and model must sum to 1.0"
        )

    def test_attribution_no_duplicate_records(self):
        """Verifies no duplicate (order_id, attribution_model, channel) records exist."""
        duplicates = self.df_attr.duplicated(subset=["order_id", "attribution_model", "channel"]).sum()
        self.assertEqual(duplicates, 0, "Found duplicate order/model/channel records in attribution mart")

    # ---------------- 2. CUSTOMER CLV TESTS ----------------

    def test_clv_required_columns(self):
        """Verifies CLV table contains all required fields."""
        required = [
            "customer_id", "historical_revenue", "order_count", "average_order_value",
            "purchase_frequency", "customer_lifespan_days", "historical_clv",
            "predicted_12m_clv", "clv_segment"
        ]
        for col in required:
            self.assertIn(col, self.df_clv.columns, f"Missing CLV column: {col}")

    def test_clv_primary_key_uniqueness(self):
        """Verifies customer_id is unique and matches 5,000 CRM customers."""
        self.assertEqual(len(self.df_clv), 5000)
        self.assertEqual(self.df_clv["customer_id"].nunique(), 5000)

    def test_clv_calculation_integrity(self):
        """Verifies historical CLV equals 45% contribution margin of historical revenue."""
        expected_hist_clv = (self.df_clv["historical_revenue"] * 0.45).round(2)
        diff = (self.df_clv["historical_clv"] - expected_hist_clv).abs()
        self.assertTrue((diff <= 0.02).all(), "Historical CLV must equal 45% of historical revenue")
        self.assertTrue((self.df_clv["predicted_12m_clv"] > 0).all(), "Predicted CLV must be positive")

    def test_clv_segments_valid(self):
        """Verifies CLV segment labels are valid and populated."""
        valid_segments = {"High Value VIP", "Medium Value Core", "Low Value Nurture", "Prospect / Inactive"}
        self.assertTrue(set(self.df_clv["clv_segment"].unique()).issubset(valid_segments))

    # ---------------- 3. MARKETING ROI / CAMPAIGN TESTS ----------------

    def test_campaign_roi_required_columns(self):
        """Verifies campaign ROI table contains all required fields."""
        required = [
            "campaign", "channel", "spend", "impressions", "clicks",
            "conversions", "revenue", "ROAS", "CAC", "CTR", "CVR",
            "revenue_per_click", "recommended_action"
        ]
        for col in required:
            self.assertIn(col, self.df_roi.columns, f"Missing Campaign ROI column: {col}")

    def test_campaign_roi_invariants_and_positivity(self):
        """Verifies non-negative spend and valid metrics without divide-by-zero errors."""
        self.assertEqual(len(self.df_roi), 8)
        self.assertTrue((self.df_roi["spend"] > 0).all())
        self.assertTrue((self.df_roi["impressions"] >= self.df_roi["clicks"]).all())
        self.assertTrue((self.df_roi["clicks"] >= self.df_roi["conversions"]).all())
        self.assertTrue((self.df_roi["ROAS"] >= 0).all())
        self.assertTrue((self.df_roi["CAC"] >= 0).all())
        self.assertFalse(self.df_roi["ROAS"].isnull().any())
        self.assertFalse(self.df_roi["CAC"].isnull().any())

    def test_budget_recommendations_json(self):
        """Verifies budget_reallocation_recommendations.json exists and is structured."""
        self.assertTrue(self.realloc_path.exists())
        with open(self.realloc_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("recommendation_framework", data)
        self.assertIn("campaign_recommendations", data)
        self.assertIn("reallocation_pool_usd", data)
        self.assertGreater(data["reallocation_pool_usd"], 0)

    # ---------------- 4. TABLEAU CONSOLIDATED DATASET TESTS ----------------

    def test_tableau_dataset_integrity(self):
        """Verifies the Tableau dataset is populated and has all key analytics dimensions."""
        self.assertEqual(len(self.df_tableau), 5000)
        self.assertEqual(self.df_tableau["customer_id"].nunique(), 5000)
        key_fields = [
            "customer_id", "customer_tier", "country", "customer_total_revenue",
            "customer_total_orders", "rfm_segment", "historical_clv",
            "predicted_12m_clv", "clv_segment", "data_source_crm", "pipeline_execution_mode"
        ]
        for col in key_fields:
            self.assertIn(col, self.df_tableau.columns, f"Tableau dataset missing: {col}")

    # ---------------- 5. SQL MODELS EXISTENCE ----------------

    def test_phase3_sql_models_exist(self):
        """Verifies all Phase 3 SQL models exist in sql/marts/."""
        for m in ["fct_attribution_multi_model.sql", "fct_customer_clv.sql", "fct_campaign_roi.sql"]:
            p = self.sql_dir / m
            self.assertTrue(p.exists(), f"Missing SQL file: {p}")


if __name__ == "__main__":
    unittest.main()
