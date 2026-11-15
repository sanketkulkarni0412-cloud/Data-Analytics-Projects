"""
Comprehensive Data Validation Tests for Synthetic CRM, Ad Spend, and Identity Mapping.
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, date
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_synthetic_crm import generate_crm_customers
from scripts.generate_synthetic_ad_spend import generate_ad_spend
from scripts.generate_identity_mapping import generate_identity_mapping


class TestSyntheticData(unittest.TestCase):
    """Validation test suite for synthetic datasets."""

    @classmethod
    def setUpClass(cls):
        cls.data_dir = PROJECT_ROOT / "data"
        cls.crm_csv = cls.data_dir / "synthetic_crm_customers.csv"
        cls.ad_spend_csv = cls.data_dir / "synthetic_ad_spend.csv"
        cls.id_map_csv = cls.data_dir / "synthetic_identity_mapping.csv"

        # Ensure files are generated
        if not cls.crm_csv.exists():
            generate_crm_customers(count=5000, seed=42, output_path=cls.crm_csv)
        if not cls.ad_spend_csv.exists():
            generate_ad_spend(seed=42, output_path=cls.ad_spend_csv)
        if not cls.id_map_csv.exists():
            generate_identity_mapping(crm_customers_path=cls.crm_csv, seed=42, output_path=cls.id_map_csv)

        cls.df_crm = pd.read_csv(cls.crm_csv)
        cls.df_spend = pd.read_csv(cls.ad_spend_csv)
        cls.df_map = pd.read_csv(cls.id_map_csv)

    # ---------------- CRM CUSTOMER TESTS ----------------

    def test_crm_determinism(self):
        """Verifies CRM generation is strictly deterministic for identical seeds."""
        df_run1 = generate_crm_customers(count=100, seed=999)
        df_run2 = generate_crm_customers(count=100, seed=999)
        pd.testing.assert_frame_equal(df_run1, df_run2)

    def test_crm_unique_customer_ids(self):
        """Verifies customer_id is strictly unique and non-null."""
        self.assertEqual(len(self.df_crm), 5000, "CRM row count must equal 5000")
        self.assertEqual(self.df_crm["customer_id"].nunique(), 5000, "customer_id must be strictly unique")
        self.assertFalse(self.df_crm["customer_id"].isnull().any(), "customer_id must not contain nulls")

    def test_crm_synthetic_labeling(self):
        """Verifies all records are explicitly labeled as synthetic simulation."""
        self.assertTrue((self.df_crm["data_source"] == "SYNTHETIC_SIMULATION").all())
        self.assertTrue((self.df_crm["is_synthetic"] == True).all())

    def test_crm_no_real_pii(self):
        """Verifies email addresses exclusively use RFC 2606 reserved example domain."""
        emails = self.df_crm["synthetic_email"]
        self.assertTrue(emails.str.endswith("@example.com").all(), "All emails must use @example.com")

    def test_crm_valid_dates(self):
        """Verifies signup dates fall within the planned historical window."""
        dates = pd.to_datetime(self.df_crm["signup_date"])
        min_date = pd.Timestamp("2019-01-01")
        max_date = pd.Timestamp("2021-01-31")
        self.assertTrue((dates >= min_date).all())
        self.assertTrue((dates <= max_date).all())

    # ---------------- AD SPEND TESTS ----------------

    def test_ad_spend_determinism(self):
        """Verifies ad spend generation is strictly deterministic for identical seeds."""
        df_run1 = generate_ad_spend(seed=999)
        df_run2 = generate_ad_spend(seed=999)
        pd.testing.assert_frame_equal(df_run1, df_run2)

    def test_ad_spend_hierarchy_and_positivity(self):
        """Verifies spend is positive and impressions >= clicks >= conversions >= 0."""
        self.assertTrue((self.df_spend["daily_spend_usd"] > 0).all(), "Daily spend must be strictly positive")
        self.assertTrue((self.df_spend["impressions"] >= self.df_spend["clicks"]).all(), "Impressions must be >= clicks")
        self.assertTrue((self.df_spend["clicks"] >= self.df_spend["conversions"]).all(), "Clicks must be >= conversions")
        self.assertTrue((self.df_spend["conversions"] >= 0).all(), "Conversions must be non-negative")

    def test_ad_spend_synthetic_labeling(self):
        """Verifies ad spend data is explicitly tagged as synthetic simulation."""
        self.assertTrue((self.df_spend["data_source"] == "SYNTHETIC_SIMULATION").all())
        self.assertTrue((self.df_spend["is_synthetic"] == True).all())

    def test_ad_spend_date_coverage(self):
        """Verifies ad spend spans exactly 92 days across 8 campaigns (736 rows)."""
        self.assertEqual(len(self.df_spend), 736, "Ad spend must contain 736 rows (92 days * 8 campaigns)")
        dates = pd.to_datetime(self.df_spend["spend_date"])
        self.assertEqual(dates.min(), pd.Timestamp("2020-11-01"))
        self.assertEqual(dates.max(), pd.Timestamp("2021-01-31"))

    # ---------------- IDENTITY MAPPING TESTS ----------------

    def test_identity_mapping_determinism(self):
        """Verifies identity mapping bridge is strictly deterministic."""
        df_run1 = generate_identity_mapping(total_ga4_users=200, seed=999)
        df_run2 = generate_identity_mapping(total_ga4_users=200, seed=999)
        pd.testing.assert_frame_equal(df_run1, df_run2)

    def test_identity_mapping_uniqueness_and_keys(self):
        """Verifies mapping_id and user_pseudo_id are unique."""
        self.assertEqual(len(self.df_map), 7000, "Mapping table must contain 7,000 rows")
        self.assertEqual(self.df_map["mapping_id"].nunique(), 7000, "mapping_id must be strictly unique")
        self.assertEqual(self.df_map["user_pseudo_id"].nunique(), 7000, "user_pseudo_id must be strictly unique")

    def test_identity_mapping_resolution_logic(self):
        """Verifies resolved vs unresolved split and referential logic."""
        resolved = self.df_map[self.df_map["resolution_status"] == "RESOLVED"]
        unresolved = self.df_map[self.df_map["resolution_status"] == "UNRESOLVED"]

        # 60% resolution rate
        self.assertEqual(len(resolved), 4200, "Resolved count must equal 4,200 (60%)")
        self.assertEqual(len(unresolved), 2800, "Unresolved count must equal 2,800 (40%)")

        # Resolved records must have positive confidence score and valid CRM customer format
        self.assertTrue((resolved["confidence_score"] >= 0.80).all())
        self.assertTrue(resolved["customer_id"].str.startswith("CRM-CUST-").all())

        # Unresolved records must have 0.0 confidence score and anonymous tag
        self.assertTrue((unresolved["confidence_score"] == 0.0).all())
        self.assertTrue((unresolved["customer_id"] == "UNRESOLVED_ANONYMOUS").all())
        self.assertTrue((unresolved["link_method"] == "NONE").all())

    def test_identity_mapping_synthetic_labeling(self):
        """Verifies identity mapping bridge is explicitly tagged as synthetic simulation."""
        self.assertTrue((self.df_map["data_source"] == "SYNTHETIC_SIMULATION").all())
        self.assertTrue((self.df_map["is_synthetic"] == True).all())


if __name__ == "__main__":
    unittest.main()
