# Week 5 · Multivariate Data & Geospatial Visualization

**Name:** Ali Afzal
**Roll No.:** BSAI-7B-102
**Subject:** Data Visualization

My solutions to the five parts in [TASKS.md](TASKS.md). This week's broken charts are correctly computed and
carefully drawn. What lies is **the encoding or the geography**: which channel carried which variable, or
which boundaries carved up the land.

← [Back to all weeks](../README.md)

## What's here

| File | Part | What it shows |
|---|---|---|
| [partA.ipynb](partA.ipynb) | A · Nine cases | Each chart rebuilt to its self-check, then the decoy, the lying channel or boundary with its number, and a redesign |
| [partB.ipynb](partB.ipynb) | B · Decisions | Size range, four overplotting fixes, three scalings + PCA, sphere vs degrees vs Mercator, funnel plot |
| [partC.ipynb](partC.ipynb) | C · Two maps | Count map vs rate map of 20 counties, and the reader experiment |
| [partD.ipynb](partD.ipynb) | D · Figures | Four-variable bubble chart, parallel coordinates, and the normalized choropleth with counts beside it |
| [partE_justification.md](partE_justification.md) | E · Write-up | Channels, PCP decisions, spatial decisions, and the counterfactual |

The three deliverables are [`charts/partD_bubble.png`](charts/partD_bubble.png),
[`charts/partD_pcp.png`](charts/partD_pcp.png) and [`charts/partD_choropleth.png`](charts/partD_choropleth.png),
all at 300 dpi. `geolib.py` and `vizlib.py` are the course toolkits.

## Run it

```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn jupyter ipykernel
cd week5
jupyter notebook
```

No GIS install is needed: the boundaries are plain GeoJSON, and `geolib` handles projection and drawing.

> **Toolkit note.** `geolib.corr_chain()` fails under pandas 3 with `ValueError: underlying array is
> read-only`. Copy-on-write makes `df.corr().values` read-only, so its in-place `fill_diagonal` fails. That
> also stops `python geolib.py`'s self-check partway through. I left the course file unchanged and wrote the
> same greedy rule into the notebooks using `.to_numpy(copy=True)`.

## The experiment (Part C)

The two-map activity needs **at least five real readers**. In `partC.ipynb`:

1. Set `READER = "..."` and `RUN_EXPERIMENT = True`, then run the cell with the reader at the screen. They
   see Map A (counts) and name three counties for extra police, then Map B (per 100,000), and name three
   again. Answer 1 can't be revised.
2. Repeat for each reader. Each run appends one row to `partC_reader_results.csv`.
3. Set `RUN_EXPERIMENT = False`, then **Restart & Run All**. The report cell gives each reader's overlap and
   the mean.

Then fill in the quoted block at the end of Part C and the last sentence of Part E §4.

## The nine mechanisms, in one line each

| # | Claim | What's really going on |
|---|---|---|
| 1 | Population unrelated to access | `s = pop**2` drives radius: 346,921× area instead of 589× |
| 2 | Outbreak around the capital | Count map = population map (r = +0.986). Top-3 overlap with rate: 0 |
| 3 | GDP barely varies | One $120k country flattens min–max. 58/60 below 0.10 |
| 4 | Access and cases unrelated | Axis order puts r = −0.80 three axes apart |
| 5 | Five-level gradient | Quantile classes over a 7.2% spread. 0 of 24 outside noise |
| 6 | U32 hotspot | 9 cases in 22,000 people. The only unit outside the funnel, among 40 that share one rate |
| 7 | Income weakly related | MAUP: r = −0.31 by district, −0.89 by zone |
| 8 | Rural outbreak | Land read as people: top 5 populous = 12.6% of land, 59.9% of people. r(rate, density) = 0.00 |
| 9 | Region A stronger | Radar area depends on axis order: A wins 78 of 120 orders, B wins 42 |

## Rules I kept to

- Area means area: every size channel is linear in the value, in points², with a legend in real units.
- Hue carries identity (regions) and lightness carries amount (rates), on one sequential ramp, never a rainbow.
- Every PCP states its scaling and axis order on the figure.
- Every choropleth is normalized, with the denominator in words in the legend title, the class breaks in
  the legend, an equal-area projection, the join checked (0 failures), and the boundaries, date and any
  suppression in the caption.
- Every chart uses `fig, ax` and is exported at 300 dpi through `vizlib.save_fig`.
- All data is synthetic course data for CDB601220, and every figure says so.

*Part F (bonus) isn't attempted. It needs a real dataset and boundary file that I source and cite myself.*
