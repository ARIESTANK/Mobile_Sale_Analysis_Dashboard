"""
Myanmar Mobile Money Transaction Data Generator
================================================
Generates realistic synthetic transaction data for portfolio EDA projects.
Uses Faker for base randomness + Myanmar-specific data pools.

Usage:
    python generate_myanmar_transactions.py
    python generate_myanmar_transactions.py --rows 5000 --output my_data.csv

Output: CSV file with 1000 rows (default), ready for Pandas EDA.
"""

import argparse
import random
import uuid
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker()
random.seed(42)  # reproducible output

# ─── MYANMAR-SPECIFIC DATA POOLS ──────────────────────────────────────────────

CITIES = [
    'Yangon', 'Mandalay', 'Naypyitaw', 'Bago', 'Mawlamyine',
    'Pathein', 'Taunggyi', 'Sittwe', 'Myitkyina', 'Dawei'
]
CITY_WEIGHTS = [40, 20, 8, 5, 5, 4, 4, 3, 3, 3]  # Yangon is dominant

TOWNSHIPS = {
    'Yangon':     ['Hlaing', 'Kamayut', 'Bahan', 'Thingangyun', 'Tamwe',
                   'Sanchaung', 'Mayangon', 'Insein', 'Mingaladon', 'Dagon'],
    'Mandalay':   ['Aungmyaythazan', 'Chanayethazan', 'Maha Aungmye',
                   'Amarapura', 'Patheingyi'],
    'Naypyitaw':  ['Zabuthiri', 'Ottarathiri', 'Pobbathiri', 'Dekkhina'],
    'Bago':       ['Bago Township', 'Tanatpin', 'Waw'],
    'Mawlamyine': ['Mawlamyine Township', 'Mudon', 'Kyaikmaraw'],
    'Pathein':    ['Pathein Township', 'Yegyi', 'Maubin'],
    'Taunggyi':   ['Taunggyi Township', 'Hopong', 'Lawksawk'],
    'Sittwe':     ['Sittwe Township', 'Myebon', 'Ponnagyun'],
    'Myitkyina':  ['Myitkyina Township', 'Waingmaw'],
    'Dawei':      ['Dawei Township', 'Yebyu', 'Longlon'],
}

PLATFORMS = ['Wave Money', 'KBZPay', 'AYAPay', 'CB Pay', 'OK Dollar']
PLATFORM_WEIGHTS = [30, 28, 22, 12, 8]

TX_TYPES = [
    'P2P Transfer', 'Bill Payment', 'Mobile Top-up',
    'Merchant Payment', 'Cash In', 'Cash Out', 'Salary Credit'
]
TX_WEIGHTS = [35, 20, 15, 15, 8, 5, 2]

TX_STATUS = ['Completed', 'Completed', 'Completed', 'Failed', 'Pending']
# 60% completed, 20% completed, 20% completed, Failed, Pending

MERCHANTS = [
    'City Mart Supermarket', 'Junction City Mall', 'Myanmar Plaza',
    'MPRL Fuel Station', 'KFC Myanmar', 'Grab Myanmar', 'Foodpanda Myanmar',
    'Shwe War Myay Market', 'Ooredoo Myanmar', 'Mytel', 'MPT',
    'Bangkok Airways', 'Cathay Life Insurance', 'AIA Myanmar',
    'Pun Hlaing Hospital', 'City Express Courier',
    'AGD Bank', 'KBZ Bank', 'AYA Bank', 'CB Bank', 'MAB Bank',
    'DKSH Myanmar', 'Total Energies', 'Myanmar Brewery',
    'TMH Hospital', 'Grand Hantha Hotel',
]

BILL_CATEGORIES = [
    'Electricity (YESC)', 'Water (YCDC)', 'Internet (Fiber)',
    'Cable TV', 'Insurance Premium', 'School Fees', 'Government Fee'
]

TOP_UP_OPS = ['Ooredoo', 'Mytel', 'MPT', 'Atom (Telenor)']

NAMES_FIRST = [
    'Aung', 'Kyaw', 'Myo', 'Zaw', 'Min', 'Htet', 'Thura', 'Naing', 'Pyae', 'Soe',
    'Aye', 'Khin', 'Thida', 'Myat', 'Phyu', 'Su', 'Ei', 'Wai', 'Nge', 'Nan',
    'Mg', 'Ko', 'Ma', 'Daw', 'Thu', 'Phyo', 'Thet', 'Yee', 'Nyein', 'Shwe',
]
NAMES_LAST = [
    'Htun', 'Win', 'Naing', 'Lwin', 'Oo', 'Hlaing', 'Zin', 'Moe', 'Thu', 'Tun',
    'Kyaw', 'Aung', 'Myint', 'Phyo', 'Soe', 'Zaw', 'Thant', 'Nyi', 'Lin', 'Min',
    'Htay', 'Khaing', 'Wai', 'Lay', 'Shwe', 'Mon', 'Nge', 'San', 'Aye', 'Maung',
]

AGE_GROUPS = ['18-24', '25-34', '35-44', '45-54', '55+']
AGE_WEIGHTS = [25, 35, 22, 12, 6]

GENDERS = ['Male', 'Female']
GENDER_WEIGHTS = [52, 48]

OCCUPATIONS = [
    'Government Employee', 'Private Sector Employee', 'Business Owner',
    'Trader / Merchant', 'Student', 'Freelancer', 'Factory Worker',
    'Farmer', 'Healthcare Worker', 'Teacher',
]
OCC_WEIGHTS = [18, 25, 15, 12, 10, 8, 5, 4, 2, 1]

DEVICE_TYPES = ['Android', 'Android', 'Android', 'iOS', 'Feature Phone']


# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def myanmar_phone(has_formatting_issue: bool = False) -> str:
    """
    Generate a Myanmar mobile number.
    Myanmar format: 09XXXXXXXXX (10-11 digits depending on operator prefix)
    Optionally introduces formatting issues for dirty data generation.
    """
    operator_prefixes = [
        '5', '7', '8', '9',           # old format
        '43', '25', '26', '31', '32', # Ooredoo
        '33', '42', '44', '45', '49', # Mytel
        '73', '76', '95', '96', '97', '98',  # MPT
    ]
    prefix = random.choice(operator_prefixes)
    remaining_digits = 7  # makes total 9+ digits after 09
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(remaining_digits)])
    number = f"09{prefix}{suffix}"

    if has_formatting_issue:
        fmt = random.choice(['international', 'spaces', 'dashes'])
        if fmt == 'international':
            return number.replace('09', '+959', 1)
        elif fmt == 'spaces':
            return f"09 {prefix} {suffix[:3]} {suffix[3:]}"
        elif fmt == 'dashes':
            return f"09-{prefix}-{suffix}"

    return number


def mmk_amount(tx_type: str) -> int:
    """
    Generate a realistic MMK amount based on transaction type.
    All amounts rounded to nearest 500 MMK (realistic for Myanmar).
    """
    ranges = {
        'P2P Transfer':     (5_000,   500_000),
        'Bill Payment':     (3_000,   200_000),
        'Mobile Top-up':    (1_000,    20_000),
        'Merchant Payment': (2_000,   150_000),
        'Cash In':         (10_000, 1_000_000),
        'Cash Out':        (10_000,   500_000),
        'Salary Credit':  (200_000, 3_000_000),
    }
    lo, hi = ranges.get(tx_type, (1_000, 100_000))
    # Use log-normal distribution so small amounts are more common
    import numpy as np
    mean = (lo + hi) / 2
    raw = int(np.clip(np.random.lognormal(
        mean=np.log(mean * 0.6),
        sigma=0.8
    ), lo, hi))
    return round(raw / 500) * 500


def transaction_description(tx_type: str, platform: str) -> str:
    """Generate a realistic transaction description/note."""
    templates = {
        'P2P Transfer':     [
            f"Transfer to {random.choice(NAMES_FIRST)} {random.choice(NAMES_LAST)}",
            "Money sent to family",
            "Rent payment",
            "Personal transfer",
            f"Payment for goods",
        ],
        'Bill Payment':     [f"Pay {random.choice(BILL_CATEGORIES)}"],
        'Mobile Top-up':    [f"{random.choice(TOP_UP_OPS)} top-up {random.choice([1000,2000,3000,5000,10000])} MMK"],
        'Merchant Payment': [f"Purchase at {random.choice(MERCHANTS)}"],
        'Cash In':          ["Cash deposit at agent", "Bank transfer in", "ATM cash in"],
        'Cash Out':         ["Cash withdrawal at agent", "ATM withdrawal"],
        'Salary Credit':    ["Monthly salary", "Weekly wage", "Bonus payment"],
    }
    return random.choice(templates.get(tx_type, ["Transaction"]))


def random_timestamp(start: datetime, end: datetime) -> datetime:
    """
    Generate a realistic timestamp — weighted toward business hours
    and weekdays, with a small spike on weekends (market days).
    """
    delta = (end - start).total_seconds()
    ts = start + timedelta(seconds=random.random() * delta)

    # Bias toward business hours (8am-9pm) — 80% of transactions
    if random.random() < 0.80:
        ts = ts.replace(hour=random.randint(8, 21),
                        minute=random.randint(0, 59))
    return ts


# ─── MAIN GENERATOR ──────────────────────────────────────────────────────────

def generate_transactions(
    n_rows: int = 1000,
    start_date: str = '2024-01-01',
    end_date: str = '2024-12-31',
    dirty: bool = False,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate n_rows of realistic Myanmar mobile money transactions.

    Parameters
    ----------
    n_rows     : Number of transaction rows to generate
    start_date : Start of date range (YYYY-MM-DD)
    end_date   : End of date range (YYYY-MM-DD)
    dirty      : If True, intentionally introduces data quality issues
                 (missing values, formatting errors, duplicates)
                 — useful for data cleaning exercises
    seed       : Random seed for reproducibility

    Returns
    -------
    pd.DataFrame with all transaction columns
    """
    random.seed(seed)

    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt   = datetime.strptime(end_date,   '%Y-%m-%d')

    rows = []

    for i in range(n_rows):
        # ── Geography
        city     = random.choices(CITIES, weights=CITY_WEIGHTS)[0]
        township = random.choice(TOWNSHIPS.get(city, ['Central']))

        # ── User demographics
        name       = f"{random.choice(NAMES_FIRST)} {random.choice(NAMES_LAST)}"
        age_group  = random.choices(AGE_GROUPS, weights=AGE_WEIGHTS)[0]
        gender     = random.choices(GENDERS, weights=GENDER_WEIGHTS)[0]
        occupation = random.choices(OCCUPATIONS, weights=OCC_WEIGHTS)[0]

        # Phone — introduce formatting issues if dirty=True
        phone_dirty = dirty and random.random() < 0.05  # 5% malformed
        phone = myanmar_phone(has_formatting_issue=phone_dirty)

        # ── Transaction
        tx_type   = random.choices(TX_TYPES, weights=TX_WEIGHTS)[0]
        platform  = random.choices(PLATFORMS, weights=PLATFORM_WEIGHTS)[0]
        amount    = mmk_amount(tx_type)
        status    = random.choices(
            ['Completed', 'Failed', 'Pending'],
            weights=[88, 8, 4]
        )[0]
        description = transaction_description(tx_type, platform)
        device    = random.choice(DEVICE_TYPES)
        tx_id     = f"TXN-{fake.bothify('????-########').upper()}"
        timestamp = random_timestamp(start_dt, end_dt)

        # Fee logic — Cash Out and P2P have fees, others are free
        fee = 0
        if tx_type == 'Cash Out':
            fee = round(amount * random.uniform(0.005, 0.02) / 500) * 500
        elif tx_type == 'P2P Transfer' and platform in ['CB Pay', 'OK Dollar']:
            fee = random.choice([0, 500, 1000])

        row = {
            'transaction_id':   tx_id,
            'timestamp':        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'date':             timestamp.strftime('%Y-%m-%d'),
            'month':            timestamp.strftime('%Y-%m'),
            'hour':             timestamp.hour,
            'day_of_week':      timestamp.strftime('%A'),
            'customer_name':    name,
            'age_group':        age_group,
            'gender':           gender,
            'occupation':       occupation,
            'phone_number':     phone,
            'city':             city,
            'township':         township,
            'platform':         platform,
            'device_type':      device,
            'transaction_type': tx_type,
            'amount_mmk':       amount,
            'fee_mmk':          fee,
            'net_amount_mmk':   amount - fee,
            'status':           status,
            'description':      description,
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # ── Introduce dirty data issues if requested
    if dirty:
        n = len(df)

        # 1. Missing values (~3% of key columns)
        for col in ['phone_number', 'occupation', 'description']:
            missing_idx = random.sample(range(n), k=int(n * 0.03))
            df.loc[missing_idx, col] = None

        # 2. Duplicate rows (~1%)
        dup_idx = random.sample(range(n), k=max(1, int(n * 0.01)))
        df = pd.concat([df, df.iloc[dup_idx]], ignore_index=True)

        # 3. Mixed date formats in 2% of rows
        date_idx = random.sample(range(len(df)), k=int(len(df) * 0.02))
        for idx in date_idx:
            d = datetime.strptime(df.at[idx, 'date'], '%Y-%m-%d')
            df.at[idx, 'date'] = d.strftime('%d/%m/%Y')

        # 4. Casing inconsistencies in platform column (2%)
        case_idx = random.sample(range(len(df)), k=int(len(df) * 0.02))
        for idx in case_idx:
            df.at[idx, 'platform'] = df.at[idx, 'platform'].lower()

        # Shuffle
        df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    return df


# ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Myanmar mobile money data')
    parser.add_argument('--rows',   type=int, default=1000,               help='Number of rows (default: 1000)')
    parser.add_argument('--start',  type=str, default='2024-01-01',       help='Start date YYYY-MM-DD')
    parser.add_argument('--end',    type=str, default='2024-12-31',       help='End date YYYY-MM-DD')
    parser.add_argument('--dirty',  action='store_true',                  help='Introduce data quality issues')
    parser.add_argument('--output', type=str, default='myanmar_mobile_money_transactions.csv',
                                                                          help='Output CSV filename')
    parser.add_argument('--seed',   type=int, default=42,                 help='Random seed')
    args = parser.parse_args()

    print(f"\n🇲🇲  Myanmar Mobile Money Data Generator")
    print(f"{'─'*45}")
    print(f"  Rows     : {args.rows:,}")
    print(f"  Period   : {args.start} → {args.end}")
    print(f"  Dirty    : {'Yes — data quality issues included' if args.dirty else 'No — clean data'}")
    print(f"  Output   : {args.output}")
    print(f"  Seed     : {args.seed}")
    print(f"{'─'*45}\n")

    df = generate_transactions(
        n_rows=args.rows,
        start_date=args.start,
        end_date=args.end,
        dirty=args.dirty,
        seed=args.seed,
    )

    df.to_csv(args.output, index=False, encoding='utf-8-sig')

    print(f"✅  Generated {len(df):,} rows → {args.output}")
    print(f"\n📊  Quick summary:")
    print(f"  Total volume   : {df['amount_mmk'].sum():>15,.0f} MMK")
    print(f"  Avg transaction: {df['amount_mmk'].mean():>15,.0f} MMK")
    print(f"  Platforms      : {', '.join(df['platform'].unique())}")
    print(f"  Top city       : {df['city'].value_counts().index[0]}")
    print(f"  Date range     : {df['date'].min()} → {df['date'].max()}")
    print(f"\n🔍  First 3 rows:")
    print(df.head(3).to_string(index=False))
    print(f"\n📁  Columns ({len(df.columns)}):")
    print(f"  {', '.join(df.columns.tolist())}")