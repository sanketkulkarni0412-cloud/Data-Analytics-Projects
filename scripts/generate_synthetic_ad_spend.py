"""
Synthetic Multi-Channel Ad Spend Generator.

Generates daily advertising spend across paid channels (Search, Social, Display, Video, Affiliate)
covering the GA4 date range (2020-11-01 to 2021-01-31).
Uses realistic cost, impression, CTR, and CVR dynamics with seasonal holiday peaks.
Clearly labeled as synthetic simulation data.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


CAMPAIGN_CONFIG = [
    {
        "campaign_id": "CMP-001",
        "channel": "Paid Search",
        "campaign_name": "Brand_Search_Core",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "Brand_Search_Core",
        "base_daily_spend": 320.0,
        "cpm_range": (18.0, 24.0),
        "ctr_range": (0.045, 0.075),  # High intent brand search CTR
        "cvr_range": (0.035, 0.055),  # High CVR
    },
    {
        "campaign_id": "CMP-002",
        "channel": "Paid Search",
        "campaign_name": "Generic_Apparel_Promo",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "Generic_Apparel_Promo",
        "base_daily_spend": 450.0,
        "cpm_range": (22.0, 32.0),
        "ctr_range": (0.020, 0.038),
        "cvr_range": (0.018, 0.030),
    },
    {
        "campaign_id": "CMP-003",
        "channel": "Paid Social",
        "campaign_name": "Holiday_Gift_Guide_2020",
        "utm_source": "instagram",
        "utm_medium": "social_paid",
        "utm_campaign": "Holiday_Gift_Guide_2020",
        "base_daily_spend": 380.0,
        "cpm_range": (14.0, 20.0),
        "ctr_range": (0.015, 0.028),
        "cvr_range": (0.015, 0.025),
    },
    {
        "campaign_id": "CMP-004",
        "channel": "Paid Social",
        "campaign_name": "Black_Friday_Cyber_Week",
        "utm_source": "facebook",
        "utm_medium": "social_paid",
        "utm_campaign": "Black_Friday_Cyber_Week",
        "base_daily_spend": 550.0,
        "cpm_range": (16.0, 25.0),
        "ctr_range": (0.018, 0.032),
        "cvr_range": (0.020, 0.038),
    },
    {
        "campaign_id": "CMP-005",
        "channel": "Display",
        "campaign_name": "Dynamic_Remarketing_Banners",
        "utm_source": "google_display",
        "utm_medium": "display",
        "utm_campaign": "Dynamic_Remarketing_Banners",
        "base_daily_spend": 220.0,
        "cpm_range": (6.0, 10.0),
        "ctr_range": (0.006, 0.012),  # Display banners lower CTR
        "cvr_range": (0.008, 0.018),
    },
    {
        "campaign_id": "CMP-006",
        "channel": "Video",
        "campaign_name": "Brand_Awareness_Video_Q4",
        "utm_source": "youtube",
        "utm_medium": "video",
        "utm_campaign": "Brand_Awareness_Video_Q4",
        "base_daily_spend": 280.0,
        "cpm_range": (10.0, 16.0),
        "ctr_range": (0.008, 0.016),
        "cvr_range": (0.006, 0.014),
    },
    {
        "campaign_id": "CMP-007",
        "channel": "Paid Search",
        "campaign_name": "Winter_Clearance_Sale",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "Winter_Clearance_Sale",
        "base_daily_spend": 310.0,
        "cpm_range": (20.0, 28.0),
        "ctr_range": (0.022, 0.040),
        "cvr_range": (0.020, 0.032),
    },
    {
        "campaign_id": "CMP-008",
        "channel": "Affiliate",
        "campaign_name": "Affiliate_Partner_Deals",
        "utm_source": "rakuten",
        "utm_medium": "affiliate",
        "utm_campaign": "Affiliate_Partner_Deals",
        "base_daily_spend": 190.0,
        "cpm_range": (12.0, 18.0),
        "ctr_range": (0.025, 0.045),
        "cvr_range": (0.022, 0.035),
    }
]


def get_seasonal_multiplier(curr_date: date) -> float:
    """Simulates realistic Q4 retail seasonality (Black Friday, Cyber Week, Holiday)."""
    # Black Friday / Cyber Monday 2020: Nov 25 to Nov 30
    if date(2020, 11, 25) <= curr_date <= date(2020, 11, 30):
        return 2.4
    # Early Dec Holiday rush: Dec 1 to Dec 15
    elif date(2020, 12, 1) <= curr_date <= date(2020, 12, 18):
        return 1.6
    # Post-Christmas / New Year Clearance: Dec 26 to Jan 5
    elif date(2020, 12, 26) <= curr_date <= date(2021, 1, 5):
        return 1.3
    # Normal days
    return 1.0


def generate_ad_spend(
    start_date: date = date(2020, 11, 1),
    end_date: date = date(2021, 1, 31),
    seed: int = 42,
    output_path: Path = None
) -> pd.DataFrame:
    """
    Generates deterministic daily synthetic advertising spend across marketing campaigns.
    """
    np.random.seed(seed)

    current_dt = start_date
    rows = []
    spend_seq = 1

    while current_dt <= end_date:
        season_mult = get_seasonal_multiplier(current_dt)

        for camp in CAMPAIGN_CONFIG:
            # Daily noise +/- 15%
            daily_noise = np.random.uniform(0.85, 1.15)
            spend = round(camp["base_daily_spend"] * season_mult * daily_noise, 2)

            # CPM calculation: spend / impressions * 1000
            cpm = np.random.uniform(*camp["cpm_range"])
            impressions = int(max(100, round((spend / cpm) * 1000)))

            # CTR calculation: clicks = impressions * CTR
            ctr = np.random.uniform(*camp["ctr_range"])
            clicks = int(max(1, round(impressions * ctr)))
            # Guarantee clicks <= impressions
            clicks = min(clicks, impressions)

            # CVR calculation: conversions = clicks * CVR
            cvr = np.random.uniform(*camp["cvr_range"])
            conversions = int(round(clicks * cvr))
            # Guarantee conversions <= clicks
            conversions = min(conversions, clicks)

            spend_id = f"SPD-{spend_seq:07d}"
            spend_seq += 1

            rows.append({
                "spend_id": spend_id,
                "spend_date": current_dt.isoformat(),
                "campaign_id": camp["campaign_id"],
                "channel": camp["channel"],
                "campaign_name": camp["campaign_name"],
                "utm_source": camp["utm_source"],
                "utm_medium": camp["utm_medium"],
                "utm_campaign": camp["utm_campaign"],
                "daily_spend_usd": spend,
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "cpm": round((spend / impressions) * 1000, 2) if impressions > 0 else 0.0,
                "ctr_pct": round((clicks / impressions) * 100, 3) if impressions > 0 else 0.0,
                "cpc_usd": round(spend / clicks, 2) if clicks > 0 else 0.0,
                "cvr_pct": round((conversions / clicks) * 100, 3) if clicks > 0 else 0.0,
                "data_source": "SYNTHETIC_SIMULATION",
                "is_synthetic": True,
                "simulation_seed": seed
            })

        current_dt += timedelta(days=1)

    df = pd.DataFrame(rows)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df):,} synthetic ad spend records to: {output_path}")

    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic advertising spend.")
    parser.add_argument("--start-date", type=str, default="2020-11-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2021-01-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output", type=str, default="data/synthetic_ad_spend.csv", help="Output CSV path")
    args = parser.parse_args()

    s_dt = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    e_dt = datetime.strptime(args.end_date, "%Y-%m-%d").date()
    out_file = PROJECT_ROOT / args.output

    generate_ad_spend(start_date=s_dt, end_date=e_dt, seed=args.seed, output_path=out_file)


if __name__ == "__main__":
    main()
