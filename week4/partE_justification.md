# Part E · Written justification

**Ali Afzal** · BSAI-7B-102 · Data Visualization · Week 4 · Figure: [`charts/partD_figure.png`](charts/partD_figure.png)

## 1 · The four panels

| Panel | Question it answers | Why this chart | Week 2 channel rule |
|---|---|---|---|
| 1 · Daily sessions | Is traffic growing, and when did it turn? | A line over a calendar axis, because equal distance means equal time. The raw series stays in light grey and the signal is the one coloured line. | **Position** on a common scale. One pop-out: grey for context, blue for the 7-day mean |
| 2 · Weekday × hour heatmap | *When* in the week does traffic happen? | Two cyclic positions (weekday, hour) plus one amount. A grid holds 168 cells that seven lines would turn into spaghetti | **Lightness** for amount on a one-hue sequential ramp (`Blues`, dark = more, zero at white), since there's no midpoint |
| 3 · Treemap | *Where is the mass* in the catalogue, and how does it nest? | Containment shows the category → sub-category tree directly, because each block sits inside its parent | **Area** is the 4th-best channel, so every block has its value and share printed on it. **Hue** carries the parent category (identity, four hues) |
| 4 · Sorted bars | *By how much* does each sub-category differ? | The same eight numbers on a common baseline, sorted | **Length** from zero beats area: Phones vs Laptops (424 vs 312) is easy to read here and hard to read in panel 3 |

Panels 3 and 4 show the same numbers on purpose. The treemap answers "where", and the bars answer "how much".

## 2 · Every time decision

- **Parse.** There are two formats, and each one is parsed with an explicit pattern. Slash dates are **day-first**: 59% of them have a first field above 12, and Pakistan writes dates day-first. I rejected `format="mixed"` because it parses every row but silently moves 1,382 of them, pushing the start date to 4 Jan 2024.
- **Resolution.** Daily for the trend, because hourly is mostly the daily cycle, and hourly is kept for the heatmap.
- **Aggregation.** Sessions are a **flow**, so a day is the `sum()` of its hours, with `min_count=1` so an unrecorded day becomes NaN, not 0. The axis label says "sum of hours".
- **Window.** 7 days, **centred**. The cycle being removed is weekly (weekends are about 35% busier), and a 7-day window holds exactly one of each weekday (Part B.1). Centred, because this is a review of past data, and a trailing mean would report turns 3 days late (15 days late for a 31-day window, Part B.4). The mean is drawn only where all 7 days exist.

**The ethics clause.** The window was fixed at 7 days before plotting, because the cycle being removed is weekly (Part B.1). The series is shown from its first recorded day, 1 April 2024, and no start date was selected. It ends on 31 August 2025 only because September is incomplete. A 28-day version is in the appendix of `partD.ipynb` and doesn't change the direction of anything: it gives the same rise (+96% vs +90% from April to November), the same spring dip and the same summer climb (+20% vs +22%), although it moves the peak month from November to December. Part B.5 shows 28 of 60 framings of this series would have produced a *falling* trend. That's why the start is the first recorded day and not a choice.

*Symmetry test:* the 7-day window comes from the weekly cycle, not from the result, so it would stay the same if the trend had pointed down.

## 3 · Every row removed

| Rule | Count | Moved from → to |
|---|---|---|
| Duplicate hours (identical copies) dropped | 286 rows | 12,670 → 12,384 hourly rows |
| Sentinel `sessions = -1` set to NaN | 287 hours | 222 days summed from 21-23 hours, up to 3/24 under |
| Never-recorded hours, left missing | 312 hours = 13 days | 13 gaps in the line, not interpolated in the figure |
| Partial September 2025 cut | 11 days | 529 → 518 days |
| Duplicate `SKU-0127` (copied into Wearables) dropped | 1 row | Wearables share 10.1% → 9.4% |
| Negative net revenue left out of area | 7 SKUs, −1.07 PKR m | Named on the figure, by sub-category |

The device labels (6 → 3) and the sort order don't remove any rows.

## 4 · Every level rolled up

The depth is cut at **sub-category**, so the 336 positive SKUs underneath aren't drawn. **`Other` is empty:** with a 1% threshold, no sub-category qualifies (the smallest is Drones, 2.4%), so all 8 are shown and the figure says so. The four categories are the parents, with one hue each, and their blocks are outlined in the treemap.
