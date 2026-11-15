"""
Synthetic Deterministic Identity Mapping Bridge.

Builds a reproducible, controlled bridge between simulated GA4 user_pseudo_id
identifiers and synthetic CRM customer_id values.
Preserves unlinked anonymous visitors as UNRESOLVED.
Explicitly labeled as synthetic/simulated with no claim of real identity linking.
"""

import sys
import argparse
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def generate_identity_mapping(
    crm_customers_path: Path = None,
    total_ga4_users: int = 7000,
    resolution_rate: float = 0.60,
    seed: int = 42,
    output_path: Path = None
) -> pd.DataFrame:
    """
    Generates a deterministic identity mapping bridge.

    Args:
        crm_customers_path: Path to synthetic_crm_customers.csv. If None or not found, generates IDs.
        total_ga4_users: Total GA4 pseudo visitor IDs in the simulated cohort.
        resolution_rate: Proportion of GA4 visitors successfully linked to CRM customers (e.g. 0.60).
        seed: Random seed for deterministic reproducibility.
        output_path: Destination path for CSV output.

    Returns:
        pd.DataFrame containing the mapping bridge.
    """
    np.random.seed(seed)

    # 1. Load or synthesize customer IDs
    if crm_customers_path and crm_customers_path.exists():
        df_crm = pd.read_csv(crm_customers_path)
        customer_ids = df_crm["customer_id"].tolist()
    else:
        # Fallback to deterministic IDs if CRM CSV is not pre-loaded
        customer_ids = [f"CRM-CUST-{i:06d}" for i in range(1, 5001)]

    # 2. Generate deterministic GA4 user_pseudo_id values
    # In GA4, user_pseudo_id is formatted as <integer>.<epoch_timestamp>
    base_epoch = 1604188800  # 2020-11-01 00:00:00 UTC
    ga4_user_pseudo_ids = [
        f"GA4-SIM-{i:07d}.{base_epoch + (i * 37) % 7862400}"
        for i in range(1, total_ga4_users + 1)
    ]

    # 3. Determine resolved vs unresolved count
    resolved_count = int(round(total_ga4_users * resolution_rate))
    unresolved_count = total_ga4_users - resolved_count

    # Shuffle deterministic indices
    indices = np.arange(total_ga4_users)
    np.random.shuffle(indices)

    resolved_indices = indices[:resolved_count]
    unresolved_indices = indices[resolved_count:]

    # Link methods & confidence scores
    link_methods = ["PURCHASE_CHECKOUT", "ACCOUNT_LOGIN", "EMAIL_NEWSLETTER_SIGNUP"]
    link_method_probs = [0.45, 0.40, 0.15]
    confidence_map = {
        "PURCHASE_CHECKOUT": 1.00,
        "ACCOUNT_LOGIN": 0.95,
        "EMAIL_NEWSLETTER_SIGNUP": 0.80,
        "NONE": 0.00
    }

    start_date = date(2020, 11, 1)
    end_date = date(2021, 1, 31)
    total_days = (end_date - start_date).days

    devices = ["Desktop", "Mobile", "Tablet"]
    device_probs = [0.55, 0.38, 0.07]

    records = []
    mapping_seq = 1

    # Map resolved visitors to CRM customers
    # Allow a small fraction (e.g. 15%) of cross-device customers (same customer_id, different user_pseudo_id)
    num_unique_cust = min(len(customer_ids), resolved_count)
    chosen_customers = list(np.random.choice(customer_ids[:num_unique_cust], size=resolved_count, replace=True))

    for idx, cust_id in zip(resolved_indices, chosen_customers):
        pseudo_id = ga4_user_pseudo_ids[idx]
        method = np.random.choice(link_methods, p=link_method_probs)
        confidence = confidence_map[method]
        link_day = start_date + timedelta(days=int(np.random.randint(0, total_days + 1)))
        device = np.random.choice(devices, p=device_probs)

        records.append({
            "mapping_id": f"MAP-{mapping_seq:07d}",
            "user_pseudo_id": pseudo_id,
            "customer_id": cust_id,
            "resolution_status": "RESOLVED",
            "link_method": method,
            "confidence_score": confidence,
            "first_identified_date": link_day.isoformat(),
            "device_category": device,
            "data_source": "SYNTHETIC_SIMULATION",
            "is_synthetic": True,
            "simulation_seed": seed
        })
        mapping_seq += 1

    # Map unresolved anonymous visitors
    for idx in unresolved_indices:
        pseudo_id = ga4_user_pseudo_ids[idx]
        device = np.random.choice(devices, p=device_probs)
        seen_day = start_date + timedelta(days=int(np.random.randint(0, total_days + 1)))

        records.append({
            "mapping_id": f"MAP-{mapping_seq:07d}",
            "user_pseudo_id": pseudo_id,
            "customer_id": "UNRESOLVED_ANONYMOUS",
            "resolution_status": "UNRESOLVED",
            "link_method": "NONE",
            "confidence_score": 0.00,
            "first_identified_date": seen_day.isoformat(),
            "device_category": device,
            "data_source": "SYNTHETIC_SIMULATION",
            "is_synthetic": True,
            "simulation_seed": seed
        })
        mapping_seq += 1

    df = pd.DataFrame(records)
    # Sort deterministically by mapping_id
    df = df.sort_values("mapping_id").reset_index(drop=True)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df):,} synthetic identity mappings to: {output_path}")

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic identity mapping bridge.")
    parser.add_argument("--total-users", type=int, default=7000, help="Total GA4 simulated visitors")
    parser.add_argument("--resolution-rate", type=float, default=0.60, help="Resolution rate (0.0 to 1.0)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output", type=str, default="data/synthetic_identity_mapping.csv", help="Output CSV path")
    args = parser.parse_args()

    crm_csv = PROJECT_ROOT / "data" / "synthetic_crm_customers.csv"
    out_file = PROJECT_ROOT / args.output

    generate_identity_mapping(
        crm_customers_path=crm_csv,
        total_ga4_users=args.total_users,
        resolution_rate=args.resolution_rate,
        seed=args.seed,
        output_path=out_file
    )


if __name__ == "__main__":
    main()
