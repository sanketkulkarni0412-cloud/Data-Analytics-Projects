"""
Synthetic CRM Customer Data Generator.

Generates a realistic, fully reproducible synthetic CRM customer dataset
using Faker and NumPy with a fixed seed.
All records are explicitly tagged as synthetic simulation data with no real PII.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from faker import Faker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def generate_crm_customers(
    count: int = 5000,
    seed: int = 42,
    output_path: Path = None
) -> pd.DataFrame:
    """
    Generates a deterministic synthetic CRM customer dataset.

    Args:
        count: Number of customer records to generate.
        seed: Random seed for deterministic reproducibility.
        output_path: Optional path to save CSV output.

    Returns:
        pd.DataFrame containing the synthetic CRM customer table.
    """
    fake = Faker()
    Faker.seed(seed)
    np.random.seed(seed)

    # Date bounds: 2019-01-01 to 2021-01-31
    start_date = date(2019, 1, 1)
    end_date = date(2021, 1, 31)
    total_days = (end_date - start_date).days

    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    tier_probs = [0.50, 0.30, 0.15, 0.05]

    devices = ["Desktop", "Mobile", "Tablet"]
    device_probs = [0.55, 0.38, 0.07]

    countries = ["United States", "Canada", "United Kingdom", "Germany", "France", "Japan", "Australia", "India"]
    country_probs = [0.60, 0.10, 0.08, 0.06, 0.05, 0.04, 0.04, 0.03]

    churn_risks = ["Low", "Medium", "High"]
    churn_probs = [0.65, 0.25, 0.10]

    records = []
    for i in range(1, count + 1):
        customer_id = f"CRM-CUST-{i:06d}"
        first_name = fake.first_name()
        last_name = fake.last_name()
        # Strictly use RFC 2606 example domain to guarantee no real email collision
        clean_first = "".join(filter(str.isalnum, first_name.lower()))
        clean_last = "".join(filter(str.isalnum, last_name.lower()))
        synthetic_email = f"{clean_first}.{clean_last}.{i}@example.com"

        random_day_offset = int(np.random.randint(0, total_days + 1))
        signup_dt = start_date + timedelta(days=random_day_offset)

        customer_tier = np.random.choice(tiers, p=tier_probs)
        preferred_device = np.random.choice(devices, p=device_probs)
        country = np.random.choice(countries, p=country_probs)
        churn_risk = np.random.choice(churn_risks, p=churn_probs)
        is_loyalty = bool(np.random.choice([True, False], p=[0.40, 0.60]))
        opted_in_email = bool(np.random.choice([True, False], p=[0.75, 0.25]))

        records.append({
            "customer_id": customer_id,
            "synthetic_first_name": first_name,
            "synthetic_last_name": last_name,
            "synthetic_email": synthetic_email,
            "signup_date": signup_dt.isoformat(),
            "customer_tier": customer_tier,
            "country": country,
            "preferred_device": preferred_device,
            "is_loyalty_member": is_loyalty,
            "opted_in_email": opted_in_email,
            "churn_risk_level": churn_risk,
            "data_source": "SYNTHETIC_SIMULATION",
            "is_synthetic": True,
            "simulation_seed": seed
        })

    df = pd.DataFrame(records)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df):,} synthetic CRM records to: {output_path}")

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic CRM customer records.")
    parser.add_argument("--count", type=int, default=5000, help="Number of records to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output", type=str, default="data/synthetic_crm_customers.csv", help="Output CSV path")
    args = parser.parse_args()

    out_file = PROJECT_ROOT / args.output
    generate_crm_customers(count=args.count, seed=args.seed, output_path=out_file)


if __name__ == "__main__":
    main()
