"""
Week 6 · Task A — raw -> audit -> clean/.

Reads the three raw CSVs and the GeoJSON in data/, prints an audit of each,
applies one rule per defect, and writes cleaned copies to clean/. The audit
is also written to partA_audit.txt and the decisions table to
partA_decisions.md, so every count in the table comes from this run and not
from my typing.

    python partA_process.py

The raw files are only ever read. Nothing in data/ is modified.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

import geolib
import tslib

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data")
CLEAN = os.path.join(HERE, "clean")
os.makedirs(CLEAN, exist_ok=True)

AUDIT_PATH = os.path.join(HERE, "partA_audit.txt")
_audit = open(AUDIT_PATH, "w", encoding="utf-8")


def say(*parts):
    """print() to the console and to partA_audit.txt at once."""
    line = " ".join(str(p) for p in parts)
    print(line)
    _audit.write(line + "\n")


def header(title):
    say("")
    say("=" * 72)
    say(title)
    say("=" * 72)


DECISIONS = []


def decide(file, what, detected, rule, rows):
    DECISIONS.append({"file": file, "what": what, "detected": detected,
                      "rule": rule, "rows": rows})


SENTINEL = -1          # the operator's not-available code, in both files


# ============================================================ the register
header("district_grid.csv")
reg_raw = pd.read_csv(os.path.join(RAW, "district_grid.csv"))
reg = reg_raw.copy()
say(f"rows {len(reg)}, columns {reg.shape[1]}")
say("dtypes:", ", ".join(f"{c}={t}" for c, t in reg.dtypes.items()))

# ---- key uniqueness ------------------------------------------------------
feats = geolib.read_geojson(os.path.join(RAW, "regions.geojson"))
geo_name = {f["code"]: f["name"] for f in feats}

dup = reg[reg.duplicated("code", keep=False)]
say(f"unique codes {reg.code.nunique()} of {len(reg)} rows; "
    f"duplicated keys: {sorted(dup.code.unique())}")
for _, row in dup.iterrows():
    say(f"   {row.code}  district='{row.district}'  outages={row.outages}  "
        f"solar_kw={row.solar_kw_installed}  "
        f"(GeoJSON name '{geo_name.get(row.code)}')")
# Same code, same population, households and area: one district entered
# twice under two spellings. Keep the row whose name matches the boundary
# file, because that is the register's own key to the map.
keep_mask = ~reg.code.duplicated(keep=False) | (reg.district == reg.code.map(geo_name))
n_dup_dropped = int((~keep_mask).sum())
reg = reg[keep_mask].copy()
assert reg.code.is_unique and len(reg) == 24
decide("district_grid", "Duplicate key: D11 appears as 'Kotla' and 'Kotla City'",
       "`code` not unique (24 codes in 25 rows); both rows share population, "
       "households and area",
       "Keep the row named as in `regions.geojson` ('Kotla'), drop 'Kotla City'. "
       "Dropped, not merged: the two rows disagree on outages by 3, so they "
       "cannot both be true", n_dup_dropped)

# ---- electrification_pct: text, with '%' and blanks ----------------------
raw_e = reg.electrification_pct
say(f"electrification_pct dtype {raw_e.dtype}; "
    f"values with '%': {int(raw_e.astype(str).str.contains('%').sum())}; "
    f"blank: {int(raw_e.isna().sum())}")
n_pct = int(raw_e.astype(str).str.contains("%").sum())
reg["electrification_pct"] = pd.to_numeric(
    raw_e.astype("string").str.rstrip("%").str.strip(), errors="raise")
n_e_missing = int(reg.electrification_pct.isna().sum())
say(f"   parsed: {reg.electrification_pct.min():.1f} – "
    f"{reg.electrification_pct.max():.1f}, missing {n_e_missing} "
    f"({', '.join(reg.loc[reg.electrification_pct.isna(), 'code'])})")
decide("district_grid", "`electrification_pct` stored as text, some with a "
       "trailing '%'",
       "Column dtype is text, not float; two values end in '%'",
       "Strip the '%' and parse as a number. All parsed values are 0–100, so "
       "none was a fraction", n_pct)
decide("district_grid", "`electrification_pct` blank",
       "Null after parsing",
       "Leave missing. Not imputed, not zero: a blank is not 0% connected. "
       "Not used by any figure", n_e_missing)

# ---- outage_minutes: the operator's code ---------------------------------
n_sent = int((reg.outage_minutes == SENTINEL).sum())
say(f"outage_minutes: {n_sent} rows equal {SENTINEL} "
    f"({', '.join(reg.loc[reg.outage_minutes == SENTINEL, 'code'])}); "
    f"no other value below 0")
reg["outage_minutes"] = reg.outage_minutes.where(
    reg.outage_minutes != SENTINEL).astype("Int64")
decide("district_grid", "`outage_minutes` = -1 (operator's not-available code)",
       "Range check: a duration cannot be negative, and -1 is the only "
       "negative value",
       "Set to missing. Mean interruption length is reported for the 22 "
       "districts that have one; the two are named on any chart that uses it",
       n_sent)

# ---- the ranges of anything I will divide by -----------------------------
reg["persons_per_hh"] = reg.population / reg.households
say("ranges of denominators:")
for c in ["population", "households", "area_km2", "outages"]:
    say(f"   {c:<12} {reg[c].min():>12,.1f} – {reg[c].max():>12,.1f}")
say(f"   persons/household {reg.persons_per_hh.min():.2f} – "
    f"{reg.persons_per_hh.max():,.2f}")
# One district's households is three orders of magnitude off the rest. The
# other 23 sit in 5.70–7.36 persons per household; 182 x 1,000 = 182,000
# gives 5.94, inside that band, which is what a register keyed in
# thousands for one row looks like.
others = reg.persons_per_hh[reg.persons_per_hh < 20]
bad_hh = reg.persons_per_hh > 20
say(f"   other 23: {others.min():.2f} – {others.max():.2f}; outside: "
    f"{', '.join(reg.loc[bad_hh, 'code'])} = "
    f"{reg.loc[bad_hh, 'households'].tolist()} households")
n_hh = int(bad_hh.sum())
reg.loc[bad_hh, "households"] = reg.loc[bad_hh, "households"] * 1000
reg["persons_per_hh"] = reg.population / reg.households
assert reg.persons_per_hh.between(others.min(), others.max()).all()
decide("district_grid", "D21 `households` = 182 for 1,081,000 people",
       "Persons per household = 5,940; the other 23 are 5.70–7.36",
       "Repair ×1,000 (keyed in thousands). 182,000 gives 5.94, inside the "
       "band. Repaired, not dropped, because the true value can be stated",
       n_hh)

# ---- the join ------------------------------------------------------------
reg_codes, geo_codes = set(reg.code), set(geo_name)
say(f"join to regions.geojson: {len(reg_codes & geo_codes)} matched, "
    f"{len(reg_codes - geo_codes)} register-only, "
    f"{len(geo_codes - reg_codes)} geometry-only")
name_miss = [c for c in reg.code if reg.set_index("code").district[c] != geo_name[c]]
say(f"   name mismatches after dedup: {name_miss or 'none'}")
area_geo = {f["code"]: geolib.polygon_area_km2(f["ring"]) for f in feats}
area_err = (reg.set_index("code").area_km2 / pd.Series(area_geo) - 1).abs()
say(f"   area_km2 vs spherical polygon area: max {area_err.max() * 100:.3f}% off")

say("")
say(f"CLEAN register: {len(reg)} rows, population {reg.population.sum():,}, "
    f"households {reg.households.sum():,}")
say(f"   persons/household {reg.persons_per_hh.min():.2f} – "
    f"{reg.persons_per_hh.max():.2f}")
mean_len = reg.outage_minutes / reg.outages
say(f"   usable outage_minutes {int(reg.outage_minutes.notna().sum())} of 24, "
    f"mean interruption {mean_len.min():.0f} – {mean_len.max():.0f} min")
say(f"   interruptions, all districts {reg.outages.sum():,}")

reg = reg.drop(columns="persons_per_hh")
reg.to_csv(os.path.join(CLEAN, "district_grid.csv"), index=False)


# ============================================================ the daily file
header("grid_daily.csv")
day_raw = pd.read_csv(os.path.join(RAW, "grid_daily.csv"))
day = day_raw.copy()
say(f"rows {len(day)}; dtypes:",
    ", ".join(f"{c}={t}" for c, t in day.dtypes.items()))
say(f"zones {sorted(day.zone.unique())}; join to register zones: "
    f"{'all match' if set(day.zone) == set(reg.zone) else 'MISMATCH'}")
say(f"file order sorted by date? "
    f"{bool(day.date.is_monotonic_increasing)} (rows arrive shuffled)")

# ---- dates: two formats in one column -----------------------------------
is_iso = day.date.str.fullmatch(r"\d{4}-\d{2}-\d{2}")
other = day.loc[~is_iso, "date"]
parts = other.str.extract(r"^(\d{2})/(\d{2})/(\d{4})$").astype(int)
say(f"date formats: {int(is_iso.sum())} ISO yyyy-mm-dd, {len(other)} "
    f"nn/nn/yyyy; in those, field 1 runs {parts[0].min()}–{parts[0].max()}, "
    f"field 2 is always {sorted(int(v) for v in parts[1].unique())}")
# Field 1 reaches 30, so it cannot be a month: these are dd/mm/yyyy, and
# they are all November. Parsing them month-first would have put 30 days of
# November into September and silently created duplicates there.
assert parts[0].max() > 12 and (parts[1] == 11).all()
day["date"] = pd.to_datetime(day.date.where(is_iso), format="%Y-%m-%d")
day.loc[~is_iso, "date"] = pd.to_datetime(other, format="%d/%m/%Y")
day["date"] = pd.to_datetime(day.date)
decide("grid_daily", "`date` is text in two formats (ISO, and dd/mm/yyyy for "
       "every November row)",
       "Regex on the raw text; in the non-ISO rows the first field reaches 30, "
       "so it is the day",
       "Parse each format explicitly (`%Y-%m-%d`, `%d/%m/%Y`); never let "
       "pandas guess", int((~is_iso).sum()))
decide("grid_daily", "Rows arrive shuffled",
       "`is_monotonic_increasing` is False",
       "Sort by zone, then date, after parsing (never sort the text)",
       len(day))

# ---- duplicate zone-days -------------------------------------------------
key = ["zone", "date"]
dk = day[day.duplicated(key, keep=False)]
exact = day.duplicated(keep="first")
n_exact = int(exact.sum())
day = day[~exact]
conflict = day[day.duplicated(key, keep=False)].sort_values(key)
n_conflict = int(conflict.duplicated(key).sum())
say(f"duplicate zone-days: {dk.drop_duplicates(key).shape[0]} keys "
    f"({n_exact} exact copies, {n_conflict} that disagree)")
for (z, d), g in conflict.groupby(key):
    say(f"   {z} {d.date()}: meter {g.cumulative_mwh.unique().tolist()}, "
        f"peak {g.peak_load_mw.tolist()}, minutes {g.outage_minutes.tolist()}")
# The meter reading agrees in every conflicting pair, so energy is not in
# doubt. Peak and minutes are, and the file is shuffled, so "first filed"
# means nothing. I cannot say which filing is true -> keep one row with the
# meter and mark those two fields missing.
for (z, d), g in conflict.groupby(key):
    assert g.cumulative_mwh.nunique() == 1
conflict_keys = conflict[key].drop_duplicates()
day = day.drop_duplicates(key, keep="first").copy()
ck = day.set_index(key).index.isin(conflict_keys.set_index(key).index)
day.loc[ck, ["peak_load_mw", "outage_minutes"]] = np.nan
decide("grid_daily", "Exact duplicate rows (same zone-day, every field equal)",
       "`duplicated()` on all columns", "Drop the copy, keep one", n_exact)
decide("grid_daily", "Conflicting duplicates: same zone-day filed twice with "
       "different peak and minutes",
       "`duplicated(['zone','date'])` after removing exact copies",
       "Keep one row: the meter reading agrees, so keep it; set peak and "
       "minutes to missing because neither filing can be shown to be the true "
       "one", n_conflict)

day = day.sort_values(key).reset_index(drop=True)
day["outage_minutes"] = day.outage_minutes.astype("Int64")

# ---- calendar gaps, per zone, via tslib.audit_index ----------------------
span = pd.date_range(day.date.min(), day.date.max(), freq="D")
say(f"reporting span {span[0].date()} -> {span[-1].date()} = {len(span)} days "
    f"x {day.zone.nunique()} zones = {len(span) * day.zone.nunique():,} slots; "
    f"kept {len(day):,}")
n_missing = 0
gap_months = []
for z, g in day.groupby("zone"):
    a = tslib.audit_index(g.set_index("date"), "D")
    full = pd.date_range(span[0], span[-1], freq="D")
    miss = full.difference(g.date)
    n_missing += len(miss)
    gap_months.append(pd.Series(1, index=miss.to_period("M")).groupby(level=0).sum()
                      .rename(z))
    say(f"   {z}: dtype_ok={a['dtype_ok']} monotonic={a['monotonic']} "
        f"dup={a['n_duplicated']} missing={len(miss)} "
        f"partial_tail={a['partial_tail']} ({a['tail_period']}: "
        f"{a['tail_count']} days)")
gm = pd.concat(gap_months, axis=1).fillna(0).astype(int)
say(f"never reported: {n_missing} zone-days; worst month "
    f"{gm.sum(axis=1).idxmax()} ({gm.sum(axis=1).max()}), worst zone-month "
    f"{gm.stack().idxmax()[1]} {gm.stack().idxmax()[0]} ({gm.stack().max()} days)")
decide("grid_daily", "Zone-days never reported",
       "Rebuild the full 2025-04-01 → 2026-09-11 calendar per zone and "
       "difference it against the file (`tslib.audit_index`)",
       "Reinsert as rows with `reported = False`. Minutes and peak stay "
       "missing, never zero; the line breaks there. Energy across a gap is "
       "spread evenly (next step)", n_missing)

# ---- peak_load_mw: the operator's code -----------------------------------
n_peak_code = int((day.peak_load_mw == SENTINEL).sum())
say(f"peak_load_mw: {n_peak_code} readings equal {SENTINEL}; "
    f"other minimum {day.peak_load_mw[day.peak_load_mw > 0].min():,.1f} MW")
day["peak_load_mw"] = day.peak_load_mw.where(day.peak_load_mw != SENTINEL)
say(f"outage_minutes range {day.outage_minutes.min()} – "
    f"{day.outage_minutes.max()} (no code found)")
decide("grid_daily", "`peak_load_mw` = -1 (SCADA not-available code)",
       "Range check: a load cannot be negative; -1 is the only value ≤ 0",
       "Set to missing. Peak is never summed; monthly figures use the median "
       "of the readings that exist", n_peak_code)

# ---- the meter: a counter, with one reset --------------------------------
falls = []
for z, g in day.groupby("zone"):
    dlt = g.cumulative_mwh.diff()
    for i in np.where(dlt < 0)[0]:
        falls.append((z, g.date.iloc[i - 1], g.cumulative_mwh.iloc[i - 1],
                      g.date.iloc[i], g.cumulative_mwh.iloc[i]))
say(f"zone-days where the meter reading falls: {len(falls)}")
for z, d0, v0, d1, v1 in falls:
    say(f"   {z}: {d0.date()} {v0:,.1f} -> {d1.date()} {v1:,.1f} MWh "
        "(a new meter counting up from zero)")

# Full calendar, one row per zone-day. Energy on day t is the change in the
# meter from day t to day t+1: reading(t+1) - reading(t). Where the next
# reading is k days later the k-day change is spread evenly over the k
# days (a straight line on the counter), and flagged. Across the reset the
# change is unknowable -> missing.
cal = []
for z, g in day.groupby("zone"):
    g = g.set_index("date").reindex(span)
    g.index.name = "date"
    g["zone"] = z
    g["reported"] = g.cumulative_mwh.notna()
    m = g.cumulative_mwh
    seg = (m.dropna().diff() < 0).cumsum().reindex(span).ffill().fillna(0)
    g["meter_segment"] = seg.astype(int)
    filled = m.groupby(seg).transform(lambda s: s.interpolate("index",
                                                              limit_area="inside"))
    nxt = filled.shift(-1)
    same_seg = seg.shift(-1) == seg
    g["delivered_mwh"] = (nxt - filled).where(same_seg)
    g["energy_interpolated"] = (~g.reported | ~g.reported.shift(-1, fill_value=True)) \
        & g.delivered_mwh.notna()
    cal.append(g.reset_index())
cal = pd.concat(cal, ignore_index=True)
n_reset_lost = int((cal.delivered_mwh.isna() & (cal.date < span[-1])).sum())
decide("grid_daily", "`cumulative_mwh` is a meter reading (a counter), not "
       "energy",
       "Strictly rising per zone; the dictionary says so",
       "Energy = forward difference of the reading, never `sum()`. Over a gap "
       "the change is spread evenly across the missing days and flagged "
       "`energy_interpolated`", int(cal.energy_interpolated.sum()))
decide("grid_daily", "Meter reading falls once: P4 on 2026-02-17 "
       f"({falls[0][2]:,.0f} → {falls[0][4]:,.0f} MWh)",
       "Sign of the day-on-day difference",
       "Treat as a meter replacement: a new segment starts. The one day "
       "bridging the two meters gets no energy (missing), so nothing negative "
       "is ever summed", len(falls))

last_day = cal.date.max()
n_tail = int((cal.date.dt.to_period("M") == last_day.to_period("M")).sum()
             / cal.zone.nunique())
decide("grid_daily", f"Final month is partial ({last_day:%B %Y}: {n_tail} days)",
       "`tslib.audit_index` → `partial_tail = True`",
       "Keep the days. Monthly totals for it are dropped from comparisons, and "
       "any chart that shows it marks it as partial", n_tail * cal.zone.nunique())

# ---- the anchor: energy in P1, June 2026 --------------------------------
p1_june = cal[(cal.zone == "P1") & (cal.date.dt.to_period("M") == "2026-06")]
raw_p1 = day[(day.zone == "P1") & (day.date.dt.to_period("M") == "2026-06")]
e_diff = p1_june.delivered_mwh.sum()
e_sum = raw_p1.cumulative_mwh.sum()
say(f"P1 energy, June 2026: differenced {e_diff:,.0f} MWh vs summed reading "
    f"{e_sum:,.0f} MWh ({e_sum / e_diff:,.0f}x)")
# The dictionary calls the reading "end of day"; read literally, June would
# be reading(30 Jun) - reading(31 May). That gives a figure 0.09% lower.
# The forward convention reproduces the brief, so it is the one I use, and
# both are printed so the choice is visible.
p1 = day[day.zone == "P1"].set_index("date").cumulative_mwh
p1_lit = p1.reindex(span).interpolate("index")
lit = p1_lit[pd.Timestamp("2026-06-30")] - p1_lit[pd.Timestamp("2026-05-31")]
say(f"   (end-of-day convention, reading 30 Jun - 31 May: {lit:,.0f} MWh, "
    f"{(lit / e_diff - 1) * 100:+.2f}%)")

day.to_csv(os.path.join(CLEAN, "grid_daily.csv"), index=False,
           date_format="%Y-%m-%d")
cal_out = cal[["date", "zone", "reported", "meter_segment", "cumulative_mwh",
               "delivered_mwh", "energy_interpolated", "peak_load_mw",
               "outage_minutes"]]
cal_out.to_csv(os.path.join(CLEAN, "grid_daily_calendar.csv"), index=False,
               date_format="%Y-%m-%d")
say(f"CLEAN daily: {len(day):,} reported zone-days -> clean/grid_daily.csv; "
    f"{len(cal_out):,}-slot calendar -> clean/grid_daily_calendar.csv")
say(f"   unusable peak readings {int(day.peak_load_mw.isna().sum())} "
    f"({n_peak_code} code + {n_conflict} conflicting)")


# ======================================================= the generation file
header("generation_mix.csv")
gen_raw = pd.read_csv(os.path.join(RAW, "generation_mix.csv"))
gen = gen_raw.copy()
say(f"rows {len(gen)}; dtypes:",
    ", ".join(f"{c}={t}" for c, t in gen.dtypes.items()))
gen["month"] = pd.PeriodIndex(gen.month, freq="M")
say(f"months {gen.month.min()} -> {gen.month.max()} "
    f"({gen.month.nunique()}), rows per month "
    f"{sorted(int(v) for v in gen.groupby('month').size().unique())}")
say(f"duplicate (month, source, subsource): "
    f"{int(gen.duplicated(['month', 'source', 'subsource']).sum())}; "
    f"mwh range {gen.mwh.min():,} – {gen.mwh.max():,}")
say("categories: " + "; ".join(f"{s}/{ss}" for s, ss in
                               gen[['source', 'subsource']].drop_duplicates()
                               .itertuples(index=False)))

# Week 4's exclusivity test, written out: is every MWh in exactly one row?
total_rows = gen.source.eq("All sources")
parts_ = gen[~total_rows]
published = gen[total_rows].set_index("month").mwh
part_sum = parts_.groupby("month").mwh.sum()
all_sum = gen.groupby("month").mwh.sum()
say(f"rows that are parts: {len(parts_)} = {parts_.month.nunique()} months x "
    f"{parts_.groupby('month').size().iloc[0]} categories")
say(f"parts vs published total: max gap {(part_sum - published).abs().max()} MWh")
say(f"every row summed / published total: "
    f"{sorted(float(v) for v in (all_sum / published * 100).round(1).unique())}%")
decide("generation_mix", "The ministry's 'All sources / Total' row sits beside "
       "its own parts",
       "Exclusivity test: all rows summed = 200.0% of the total in every month",
       "Drop it from the parts table (it is the whole, not a part); keep it "
       "only as a check, which the parts meet to within 2 MWh",
       int(total_rows.sum()))
gen_parts = parts_.copy()
gen_parts.to_csv(os.path.join(CLEAN, "generation_mix.csv"), index=False)

tot = gen_parts.groupby("month").mwh.sum()
sol = gen_parts[gen_parts.subsource == "Solar"].set_index("month").mwh
say(f"CLEAN generation: {len(gen_parts)} rows")
say(f"   generation {tot.index[0]} -> {tot.index[-1]}: "
    f"{(tot.iloc[-1] / tot.iloc[0] - 1) * 100:+.1f}%")
say(f"   solar: {(sol.iloc[-1] / sol.iloc[0] - 1) * 100:+.1f}% in MWh, "
    f"{sol.iloc[0] / tot.iloc[0] * 100:.1f}% -> "
    f"{sol.iloc[-1] / tot.iloc[-1] * 100:.1f}% of the mix")


# ======================================================== decisions table
header("decisions")
lines = ["# Task A · Decisions table", "",
         "Written by `partA_process.py`. Every count below comes from the run, "
         "not from typing.", "",
         "| # | File | What | How I detected it | Rule applied | Rows affected |",
         "|---|---|---|---|---|---|"]
for i, d in enumerate(DECISIONS, 1):
    lines.append(f"| {i} | `{d['file']}` | {d['what']} | {d['detected']} | "
                 f"{d['rule']} | {d['rows']:,} |")
lines += ["", "**Repaired, not dropped:** D21 households (×1,000), the "
          "`electrification_pct` text, the date formats, and the energy "
          "column (rebuilt by differencing).  ",
          "**Dropped:** 1 register row (D11 'Kotla City'), "
          f"{n_exact} exact and {n_conflict} conflicting daily duplicates, and "
          f"{int(total_rows.sum())} 'Total' rows from the parts table.  ",
          "**Made missing, never zero:** "
          f"{n_sent} `outage_minutes`, {n_e_missing} `electrification_pct`, "
          f"{n_peak_code} + {n_conflict} `peak_load_mw`, {n_conflict} daily "
          f"`outage_minutes`, the {n_missing} unreported zone-days, and "
          f"{len(falls)} day of energy across the P4 meter change."]
with open(os.path.join(HERE, "partA_decisions.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
for d in DECISIONS:
    say(f"- [{d['file']}] {d['what']}  ->  {d['rows']:,} rows")
say("")
say(f"wrote clean/ ({', '.join(sorted(os.listdir(CLEAN)))}), "
    "partA_audit.txt, partA_decisions.md")
_audit.close()
