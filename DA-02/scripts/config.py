"""
BigQuery Configuration Module for Ecommerce Customer Marketing Analytics.

Loads configuration from environment variables and local .env file.
Adheres to strict security guidelines: no secrets are hardcoded or printed.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()


@dataclass
class BigQueryConfig:
    project_id: Optional[str] = None
    dataset_id: str = "ecommerce_analytics_staging"
    credentials_path: Optional[str] = None
    location: str = "US"
    ga4_source_project: str = "bigquery-public-data"
    ga4_source_dataset: str = "ga4_obfuscated_sample_ecommerce"
    ga4_source_table_prefix: str = "events_*"

    @classmethod
    def from_env(cls) -> "BigQueryConfig":
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
        dataset_id = os.getenv("BIGQUERY_DATASET", "ecommerce_analytics_staging")
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        location = os.getenv("BIGQUERY_LOCATION", "US")

        # Resolve credentials path relative to project root if not absolute
        if credentials_path and not os.path.isabs(credentials_path):
            resolved = PROJECT_ROOT / credentials_path
            if resolved.exists():
                credentials_path = str(resolved)

        return cls(
            project_id=project_id,
            dataset_id=dataset_id,
            credentials_path=credentials_path,
            location=location,
        )

    @property
    def is_credentials_set(self) -> bool:
        if self.credentials_path and os.path.exists(self.credentials_path):
            return True
        return False

    @property
    def has_project(self) -> bool:
        return bool(self.project_id)

    def get_bigquery_client(self):
        """
        Creates and returns a google.cloud.bigquery.Client instance.
        Raises RuntimeError if authentication prerequisites are not met.
        """
        from google.cloud import bigquery
        from google.auth.exceptions import DefaultCredentialsError

        if self.credentials_path and os.path.exists(self.credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            return bigquery.Client.from_service_account_json(
                self.credentials_path,
                project=self.project_id,
                location=self.location
            )
        try:
            return bigquery.Client(project=self.project_id, location=self.location)
        except DefaultCredentialsError as e:
            raise RuntimeError(
                "Google Cloud Application Default Credentials not found. "
                "Set GOOGLE_APPLICATION_CREDENTIALS in .env or run `gcloud auth application-default login`."
            ) from e


default_config = BigQueryConfig.from_env()
