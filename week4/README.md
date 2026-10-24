# Week 4 · Time-Series, Proportions & Hierarchies

**Name:** Ali Afzal
**Roll No.:** BSAI-7B-102
**Subject:** Data Visualization

My solutions to the five parts in [TASKS.md](TASKS.md). This week's broken charts aren't broken by a drawing
decision. They're broken before anything is drawn, by a parse, a resample, a window or a denominator. So
every diagnosis here is proved with a number computed from the file.

← [Back to all weeks](../README.md)

## What's here

| File | Part | What it shows |
|---|---|---|
| [partA.ipynb](partA.ipynb) | A · Nine cases | Each published chart rebuilt to its self-check, then the decoy, the mechanism with its number, and a redesign |
| [partB.ipynb](partB.ipynb) | B · Windows | Window report, three smoothers vs Black Friday, decomposition, trailing lag, and 60 framings of one series |
| [partC.ipynb](partC.ipynb) | C · Shares | Slide-32 legality tests on three share tables, and the pie vs bars ranking experiment |
| [partD.ipynb](partD.ipynb) | D · The figure | The six faults found and fixed, the hierarchy checked, and the 2×2 review figure at 300 dpi |
| [partE_justification.md](partE_justification.md) | E · Write-up | One page: panels, time decisions, rows removed, roll-ups, and the window ethics clause |
| [sessions_clean.py](sessions_clean.py) | B + D | The cleaning rules, written once and used by both notebooks |

The main deliverable is [`charts/partD_figure.png`](charts/partD_figure.png). Every chart is saved to
[`charts/`](charts/) at 300 dpi. `tslib.py` and `vizlib.py` are the course toolkits, imported unchanged.

## Run it

```bash
pip install pandas numpy matplotlib seaborn scipy statsmodels squarify jupyter ipykernel
cd week4
jupyter notebook
```

The data is already in `data/`. Each notebook runs top to bottom with **Restart & Run All**. Run Part D
before Part B if you want to read them in the brief's order. They share `sessions_clean.py`, so either order
works.

## The experiment (Part C)

The pie-ranking test runs on a real person. In `partC.ipynb`:

1. Set `READER = "..."` and `RUN_EXPERIMENT = True`.
2. Run that cell with the reader at the screen. They see the pie, then the sorted bars, and type the letters
   A–H largest first. Each answer is timed with `time.perf_counter()`.
3. Set `RUN_EXPERIMENT = False`, then **Restart & Run All**. The responses go to `pie_ranking_results.csv`,
   and the scoring cell reports how many letters were misplaced and at which ranks.

Then fill in the two quoted blocks at the end of Part C: the reader's result, and my one-sentence pie rule.

## The nine mechanisms, in one line each

| # | Claim | What's really going on |
|---|---|---|
| 1 | Q1 peak, annual collapse | `YYYY-M` sorted as text: 22 of 24 rows out of place, and orders rose all 23 months |
| 2 | Steady +22% | Row-number axis hides a 21-day closure: flat, then a +32% step |
| 3 | +43% overnight | A level summed, and June missing 227 hours. Peak load +3.7% |
| 4 | Worked from 7 Sep | Trailing 31-day mean, 15 days late. The turn was 23 Aug |
| 5 | Six months of decline | May→Nov falls 42% every year. Year-on-year up in 24 of 24 months |
| 6 | October collapse | 11 days of October against 30 of September. Daily mean at a record 367 |
| 7 | D is erratic | B's volatility (SD 35.6) shows up on D's stacked edge. D's own SD is 3.6 |
| 8 | Search drives 43% | Non-exclusive touches. Slices sum to 131% |
| 9 | Record 38% share | Total −40%, premium −5%, everything else −51% |

## The six faults in `sessions_hourly.csv`

Two timestamp formats (`format="mixed"` silently moves 1,382 rows) · rows unsorted · six spellings of three
device labels · 287 sentinel `-1` hours · 286 duplicated hours · 312 missing hours (13 whole days). The extract
also stops 11 days into September, so the figure ends on 31 August.

## Rules I kept to

- Every chart uses `fig, ax`, with no `plt.plot` or `plt.bar`, and is saved with `fig.savefig` (through
  `vizlib.save_fig`) at 300 dpi.
- Every smoothed line names its window and keeps the raw series in grey beneath it.
- The aggregation is in the axis label ("sum of hours", "daily max"). Levels are never summed.
- Missing periods stay as gaps. Interpolation is used only inside Part B's decomposition, and it's stated
  there.
- Every share is tested for exclusivity and a meaningful whole before it's drawn.
- Negatives are named on the figure, not drawn as area. The `Other` bucket is declared, even though it's
  empty.
- The palette is `vizlib.PALETTE` (Okabe–Ito), one hue per parent category, with values printed on the
  treemap.
- All data is synthetic course data for CDB601220, and every figure says so.

*Part F (bonus) isn't attempted. It needs a real dataset that I source and cite myself.*
