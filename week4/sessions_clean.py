"""
Cleaning for data/sessions_hourly.csv, shared by Part B and Part D.

Part B has to work on the same cleaned series as Part D's figure, so the rules
live here once instead of being copied into two notebooks. Every rule records
what it did in `LOG`, and Part E quotes those numbers.

The six faults, in the order they were found:

    1. two timestamp formats   ISO "2024-04-29 11:00:00" and day-first "05/10/2024 09:00"
    2. rows out of time order  the file is shuffled
    3. device labels           "Mobile", "mobile" and "MOBILE" are one device
    4. sentinel -1 sessions    a logger writing -1 for "no reading"
    5. duplicated hours        the same hour written by both loggers
    6. missing hours           whole days the collector never recorded

plus the fact the data dictionary gives away: the extract stops part-way
through September 2025.
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).parent / "data"
LAST_FULL_DAY = "2025-08-31"   # September 2025 is an incomplete month: 11 of 30 days

LOG = {}


def parse_ts(ts: pd.Series) -> pd.Series:
    """Parse each format with an explicit pattern.

    Day-first is not a guess: 59% of the slash-format rows have a first field
    above 12, so they can only be day/month, and the platform is in Pakistan,
    where day/month is the convention. format="mixed" reads them month-first
    wherever it can and moves the series to the wrong dates.
    """
    iso = ts.str.match(r"^\d{4}-\d{2}-\d{2} ")
    out = pd.Series(pd.NaT, index=ts.index, dtype="datetime64[ns]")
    out[iso] = pd.to_datetime(ts[iso], format="%Y-%m-%d %H:%M:%S")
    out[~iso] = pd.to_datetime(ts[~iso], format="%d/%m/%Y %H:%M")

    mixed = pd.to_datetime(ts, format="mixed")
    LOG["n_iso"] = int(iso.sum())
    LOG["n_dayfirst"] = int((~iso).sum())
    LOG["n_unparsed"] = int(out.isna().sum())
    LOG["mixed_rows_moved"] = int((mixed != out).sum())
    LOG["mixed_span"] = (str(mixed.min()), str(mixed.max()))
    LOG["true_span"] = (str(out.min()), str(out.max()))
    return out


def load_hourly() -> pd.DataFrame:
    """Hourly rows, parsed, sorted, de-duplicated, sentinels set to NaN."""
    raw = pd.read_csv(DATA / "sessions_hourly.csv")
    LOG["n_raw_rows"] = len(raw)

    df = raw.assign(ts=parse_ts(raw.ts))
    LOG["was_sorted"] = bool(df.ts.is_monotonic_increasing)
    df = df.sort_values("ts", kind="stable")

    LOG["device_labels_before"] = raw.device.value_counts().to_dict()
    df["device"] = df.device.str.strip().str.title()
    LOG["device_labels_after"] = df.device.value_counts().to_dict()

    # A duplicated hour is the same reading logged twice, once in each format.
    # Check that before dropping: if the copies disagreed, dropping one would be
    # choosing a value, not removing a copy.
    dup = df[df.ts.duplicated(keep=False)]
    cols = ["sessions", "orders", "revenue_pkr"]
    LOG["n_duplicate_rows"] = int(df.ts.duplicated().sum())
    LOG["duplicates_disagree"] = int((dup.groupby("ts")[cols].nunique() > 1).any(axis=1).sum())
    df = df.drop_duplicates("ts").set_index("ts")

    sentinel = df.sessions < 0
    LOG["n_sentinel"] = int(sentinel.sum())
    LOG["sentinel_values"] = sorted(df.loc[sentinel, "sessions"].unique().tolist())
    df.loc[sentinel, "sessions"] = np.nan

    full = pd.date_range(df.index.min(), df.index.max(), freq="h")
    missing = full.difference(df.index)
    LOG["n_missing_hours"] = len(missing)
    LOG["missing_days"] = sorted({str(d.date()) for d in missing})
    LOG["n_clean_hours"] = len(df)
    return df


def load_daily() -> pd.Series:
    """Daily sessions (sum of the hours), ending on the last complete month.

    Sessions are a flow, so a day is the sum of its hours. min_count=1 makes a
    day with no recorded hours NaN instead of 0, so the line breaks there.
    """
    hourly = load_hourly()
    hours_per_day = hourly.sessions.resample("D").count()
    daily = hourly.sessions.resample("D").sum(min_count=1)

    short = hours_per_day[(hours_per_day > 0) & (hours_per_day < 24)]
    LOG["n_days_short"] = len(short)
    LOG["min_hours_in_short_day"] = int(short.min())
    LOG["n_days_missing"] = int(daily.isna().sum())

    LOG["n_days_after_cut"] = int((daily.index > LAST_FULL_DAY).sum())
    daily = daily[:LAST_FULL_DAY]
    LOG["daily_span"] = (str(daily.index.min().date()), str(daily.index.max().date()))
    LOG["n_days"] = len(daily)
    daily.name = "sessions"
    return daily
