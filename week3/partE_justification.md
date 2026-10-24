# Part E · Written justification

**Ali Afzal** · BSAI-7B-102 · Data Visualization · Week 3 · Figure: [`charts/partD_figure.png`](charts/partD_figure.png)

## 1 · The four panels

| Panel | Question it answers | Why this chart | Week 2 channel rule |
|---|---|---|---|
| 1 · Systolic histogram | Is blood pressure one population or two? | A histogram shows the *shape* of a distribution, and the two peaks are the finding. Integer data, so bins are whole mmHg | **Position along a common scale** for the value, and **length** (bar height) for the count |
| 2 · LOS box plot by ward | How long does each ward keep its patients? | A box plot compares four distributions at once, showing the median, IQR and outliers, on a log axis because stays span four orders of magnitude | **Position** on a common log scale. Wards sorted by median so the order itself shows the ranking. Grey only, since the ward names on the axis carry identity, not colour |
| 3 · Age vs cholesterol scatter | Does cholesterol rise with age? | Two continuous measures, so a scatter. A line of 5-year-band means shows the trend through 10,000 points | **Position on two axes**. One pop-out (orange) for the trend, the cloud in blue at low alpha as context |
| 4 · Correlation heatmap | Which measures move together at all? | A screen of every pair at once, which is what pointed panel 3 at age–cholesterol | **Lightness + hue** on a diverging scale pinned to −1…+1 with white at 0, because a correlation has a sign |

## 2 · Every parameter, named and defended

- **Panel 1: bin width 2 mmHg, edges on half-values (89.5, 91.5, …).** Systolic is recorded in whole mmHg, so every bin holds exactly two possible readings. That avoids both `bins=3` (which hides the second peak) and `bins=400` (296 empty bins of picket fence, Part A case 8).
- **Panel 2: log y-axis, whiskers 1.5 × IQR, wards sorted by median.** On a linear axis the 274-day stay squashes every box to a line. The log axis can't show the **2 stays of 0.00 days**, so they're omitted from this panel only, and that's stated on the figure. Data from `ward_los_wide.csv` melted to long form, and the medians match `vitals_10k.csv` exactly.
- **Panel 3: alpha = 0.12, point size 4, no subsample, 5-year age bands.** All 10,000 patients are drawn, and transparency shows density without throwing data away.
- **Panel 4: `RdBu_r`, `vmin=-1`, `vmax=1`, `center=0`, lower triangle only.** `map_mmhg` is excluded because it's computed from systolic and diastolic (its r is arithmetic), and `risk_score` is excluded because it's a ratio.
- **Colour:** the course palette's blue and orange only. The figure was checked under simulated deuteranopia ([`partD_cvd_check.png`](charts/partD_cvd_check.png)), and no meaning depends on red vs green.

## 3 · Every value removed

No row was deleted. Each bad value was set to missing **in its own column only**, so the patient still counts everywhere else.

| Rule | Count | Moved from → to |
|---|---|---|
| `bmi` of 999 or 0 is a "missing" code | 402 × 999, 84 × 0 = **486** | mean BMI **66.2 → 27.3** kg/m² |
| `heart_rate` of 0 or above 250 bpm is a device fault | 29 above 250, 8 of 0 = **37** | mean HR **78.83 → 78.05** bpm |
| `ward` spellings conformed | 12 spellings → 4 wards, 0 unmatched | groups merged, no values changed |
| `admit_date` parsed from 3 formats (slash = day/month: 59% have a first field > 12) | 3,382 + 3,253 + 3,365, 0 unparsed | text → dates, 1 Jan – 30 Apr 2026 |
| LOS of 0.00 days, off the log axis in panel 2 only | 2 | kept in every number |

**The ethics clause.** Readings above 250 bpm were removed as device faults (n = 29), along with 8 readings of 0 bpm (n = 37 in all). Mean heart rate moves from 78.83 to 78.05 bpm. The figure was also produced without the exclusion, and it's in the appendix ([`partD_appendix_no_exclusion.png`](charts/partD_appendix_no_exclusion.png)). No heart-rate correlation moves by more than 0.021, and no panel's conclusion changes.

*Symmetry test:* the cut-off sits in an empty gap, with nothing between 135 bpm (the highest real reading) and 331 bpm (the lowest fault). I'd make the same removal whichever way it pushed the result, because no human resting heart rate is 331 bpm. That's a cleaning rule, not an edit.
