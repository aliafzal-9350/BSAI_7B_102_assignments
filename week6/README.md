# Week 6 · The Integration Checkpoint

**Name:** Ali Afzal
**Roll No.:** BSAI-7B-102
**Subject:** Data Visualization

My solution to the class task in [TASKS.md](TASKS.md). One unchecked dataset from the National Grid
Authority: audit it, clean it, and turn it into one figure the board can act on. Unlike Weeks 3–5 this is
scripts, not notebooks, laid out the way the brief's hand-in list asks.

← [Back to all weeks](../README.md)

## Run it, in this order

```bash
cd week6
pip install -r requirements.txt     # pandas, numpy, matplotlib (versions inside)
python selfcheck.py                 # optional: toolkits and data load (writes _selfcheck.png)
python partA_process.py             # data/ -> audit -> clean/, partA_audit.txt, partA_decisions.md
python partB_charts.py              # clean/ -> partB_1.png, partB_2.png, partB_3.png
python partC_figure.py              # clean/ -> partC_figure.png
```

Every path is relative to the script, so it runs from any checkout. `data/` holds the raw files exactly as
the course shipped them, and no script writes to it. `clean/` is written only by `partA_process.py`.
All figures are 300 dpi with a source note.

## What's here

| File | Task | What it is |
|---|---|---|
| [partA_process.py](partA_process.py) | A | One script: raw → printed audit → one rule per defect → `clean/` |
| [partA_audit.txt](partA_audit.txt) | A | The printed audit: dtypes, keys, duplicates, gaps, sentinels, join, denominators |
| [partA_decisions.md](partA_decisions.md) | A | 15 decisions: what, how detected, rule, rows affected. Written by the script |
| [partB_charts.py](partB_charts.py) | B | [Trend](partB_1.png) (daily energy from the meter), [composition](partB_2.png) (generation mix), [relationship](partB_3.png) (solar vs income) |
| [partC_figure.py](partC_figure.py) | C | [The board figure](partC_figure.png): rate choropleth beside the 24 rates, sorted |
| [partC_note.md](partC_note.md) | C | Reader, message, parameters with reasons, and the counterfactual |

`vizlib.py`, `tslib.py` and `geolib.py` are the Weeks 3–5 toolkits, unchanged.

## Every expected check, reproduced

| Check | Expected | Mine |
|---|---|---|
| Register rows / population / households | 24 / 57,857,000 / 8,908,512 | ✓ |
| Persons per household | 5.70 – 7.36 | ✓ (D21 repaired 182 → 182,000) |
| Electrification parsed / missing | 66.6 – 90.3 / 3 | ✓ |
| Usable `outage_minutes`, mean length | 22 of 24, 77 – 214 min | ✓ |
| Zone-days kept / never reported | 3,046 / 128 of 3,174 | ✓ |
| Unusable peak readings / meter falls | 46 / 1 | ✓ (+3 from conflicting duplicates, counted separately) |
| P1 energy, June 2026: differenced vs summed | 1,200,239 vs 574,845,315 MWh (479×) | ✓ |
| Generation rows summed | 200.0% of the total | ✓ (the "Total" row is excluded) |
| Generation / solar, 2025-04 → 2026-09 | −5.0% / +82.1%, 4.1% → 7.9% | ✓ |
| r(count, households) / r(rate, households) | +0.991 / +0.175 | ✓ |
| Top 3 by count / by rate | D17, D13, D24 / D12, D11, D13 | ✓ (D13 on both: lowest income) |
| National rate; 5 most populous | 43.7; 12.6% of land, 59.9% of people | ✓ |

## Two judgement calls worth knowing

- **Conflicting duplicates.** Three zone-days were filed twice with the same meter reading but different
  peak and minutes. The file is shuffled, so "first filed" means nothing. I kept the meter and set those two
  fields to missing instead of picking one.
- **Meter convention.** The brief's 1,200,239 MWh comes from differencing the reading *forward*
  (1 Jul − 1 Jun). Read literally, the dictionary's "end of day" gives 1,199,207 MWh (−0.09%). I use the
  convention that matches the brief, and the audit prints both.

*Task D (bonus) isn't attempted.*
