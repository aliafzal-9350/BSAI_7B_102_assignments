# Task A · Decisions table

Written by `partA_process.py`. Every count below comes from the run, not from typing.

| # | File | What | How I detected it | Rule applied | Rows affected |
|---|---|---|---|---|---|
| 1 | `district_grid` | Duplicate key: D11 appears as 'Kotla' and 'Kotla City' | `code` not unique (24 codes in 25 rows); both rows share population, households and area | Keep the row named as in `regions.geojson` ('Kotla'), drop 'Kotla City'. Dropped, not merged: the two rows disagree on outages by 3, so they cannot both be true | 1 |
| 2 | `district_grid` | `electrification_pct` stored as text, some with a trailing '%' | Column dtype is text, not float; two values end in '%' | Strip the '%' and parse as a number. All parsed values are 0–100, so none was a fraction | 2 |
| 3 | `district_grid` | `electrification_pct` blank | Null after parsing | Leave missing. Not imputed, not zero: a blank is not 0% connected. Not used by any figure | 3 |
| 4 | `district_grid` | `outage_minutes` = -1 (operator's not-available code) | Range check: a duration cannot be negative, and -1 is the only negative value | Set to missing. Mean interruption length is reported for the 22 districts that have one; the two are named on any chart that uses it | 2 |
| 5 | `district_grid` | D21 `households` = 182 for 1,081,000 people | Persons per household = 5,940; the other 23 are 5.70–7.36 | Repair ×1,000 (keyed in thousands). 182,000 gives 5.94, inside the band. Repaired, not dropped, because the true value can be stated | 1 |
| 6 | `grid_daily` | `date` is text in two formats (ISO, and dd/mm/yyyy for every November row) | Regex on the raw text; in the non-ISO rows the first field reaches 30, so it is the day | Parse each format explicitly (`%Y-%m-%d`, `%d/%m/%Y`); never let pandas guess | 174 |
| 7 | `grid_daily` | Rows arrive shuffled | `is_monotonic_increasing` is False | Sort by zone, then date, after parsing (never sort the text) | 3,061 |
| 8 | `grid_daily` | Exact duplicate rows (same zone-day, every field equal) | `duplicated()` on all columns | Drop the copy, keep one | 12 |
| 9 | `grid_daily` | Conflicting duplicates: same zone-day filed twice with different peak and minutes | `duplicated(['zone','date'])` after removing exact copies | Keep one row: the meter reading agrees, so keep it; set peak and minutes to missing because neither filing can be shown to be the true one | 3 |
| 10 | `grid_daily` | Zone-days never reported | Rebuild the full 2025-04-01 → 2026-09-11 calendar per zone and difference it against the file (`tslib.audit_index`) | Reinsert as rows with `reported = False`. Minutes and peak stay missing, never zero; the line breaks there. Energy across a gap is spread evenly (next step) | 128 |
| 11 | `grid_daily` | `peak_load_mw` = -1 (SCADA not-available code) | Range check: a load cannot be negative; -1 is the only value ≤ 0 | Set to missing. Peak is never summed; monthly figures use the median of the readings that exist | 46 |
| 12 | `grid_daily` | `cumulative_mwh` is a meter reading (a counter), not energy | Strictly rising per zone; the dictionary says so | Energy = forward difference of the reading, never `sum()`. Over a gap the change is spread evenly across the missing days and flagged `energy_interpolated` | 243 |
| 13 | `grid_daily` | Meter reading falls once: P4 on 2026-02-17 (21,444,255 → 1,180 MWh) | Sign of the day-on-day difference | Treat as a meter replacement: a new segment starts. The one day bridging the two meters gets no energy (missing), so nothing negative is ever summed | 1 |
| 14 | `grid_daily` | Final month is partial (September 2026: 11 days) | `tslib.audit_index` → `partial_tail = True` | Keep the days. Monthly totals for it are dropped from comparisons, and any chart that shows it marks it as partial | 66 |
| 15 | `generation_mix` | The ministry's 'All sources / Total' row sits beside its own parts | Exclusivity test: all rows summed = 200.0% of the total in every month | Drop it from the parts table (it is the whole, not a part); keep it only as a check, which the parts meet to within 2 MWh | 18 |

**Repaired, not dropped:** D21 households (×1,000), the `electrification_pct` text, the date formats, and the energy column (rebuilt by differencing).  
**Dropped:** 1 register row (D11 'Kotla City'), 12 exact and 3 conflicting daily duplicates, and 18 'Total' rows from the parts table.  
**Made missing, never zero:** 2 `outage_minutes`, 3 `electrification_pct`, 46 + 3 `peak_load_mw`, 3 daily `outage_minutes`, the 128 unreported zone-days, and 1 day of energy across the P4 meter change.
