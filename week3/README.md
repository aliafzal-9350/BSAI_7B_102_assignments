# Week 3 · Python Visualization Foundations: Matplotlib & Seaborn

**Name:** Ali Afzal
**Roll No.:** BSAI-7B-102
**Subject:** Data Visualization

My solutions to the five parts in [TASKS.md](TASKS.md). Nine published claims, each rebuilt from its
recipe and then taken apart. In most of them the first objection you'd reach for ("correlation is not
causation", "the axis is truncated", "n is too small") isn't the reason, so each diagnosis is proved with a
number computed from the file.

← [Back to all weeks](../README.md)

## What's here

| File | Part | What it shows |
|---|---|---|
| [partA.ipynb](partA.ipynb) | A · Nine cases | Each chart rebuilt to its self-check, then the decoy, the mechanism with its number, and a redesign |
| [partB.ipynb](partB.ipynb) | B · Lie Factor | Five graphics audited with `vizlib.lie_factor()`, the `ink_dimension` trap, and why the dual-axis chart has no Lie Factor |
| [partC.ipynb](partC.ipynb) | C · Palette | `tab10` vs the course palette under three kinds of colour-blindness, worst pairs in ΔE, and my rule for 4+ categories |
| [partD.ipynb](partD.ipynb) | D · The figure | Nine data problems found and handled, the wide file melted, and the 2×2 clinical figure at 300 dpi |
| [partE_justification.md](partE_justification.md) | E · Write-up | Panels, parameters, every value removed, and the heart-rate ethics clause |

The main deliverable is [`charts/partD_figure.png`](charts/partD_figure.png). The ethics-clause appendix is
[`charts/partD_appendix_no_exclusion.png`](charts/partD_appendix_no_exclusion.png). `vizlib.py` and
`starter/` are the course files, unchanged. The notebooks do what the starters' TODOs ask.

## Run it

```bash
pip install pandas numpy matplotlib seaborn scipy jupyter ipykernel
cd week3
jupyter notebook
```

The data is already in `data/`. Each notebook runs top to bottom with **Restart & Run All**.

## The nine mechanisms, in one line each

| # | Claim | What's really going on |
|---|---|---|
| 1 | Premium helmets 2.5× worse | Simpson's paradox: Premium is safer on every road type, but 85% of its trips are on motorways |
| 2 | Chai predicts failures | Enrolment tripled and drives both counts. Per student, r falls from 0.98 to 0.29 |
| 3 | AQI cut by a third | All 6 Industrial and 3 Arterial monitors went offline on day 61. The constant 13 stations didn't move |
| 4 | Departments identical | Anscombe's quartet: same five statistics, four shapes (one of them is 10 students at 16 h) |
| 5 | Cohorts identical | Statistics forced by `match_stats`: a line, two clusters, a ring, a star and an X |
| 6 | Creatinine tracks HbA1c | One participant at 1,050 µmol/L. Without them r = −0.004 |
| 7 | Loss until May | Twin axes with independent limits. Revenue beat cost every month |
| 8 | Bin width changes the shape | `bins=3` hides two peaks; `bins=400` on integer data leaves 296 bins empty |
| 9 | Density above 100% | Kernel tails crossing a physical ceiling. The maximum reading is exactly 100 |

## Where my numbers differ from the brief or the course notes

- **Case 9:** with seaborn's current default bandwidth (Scott, 0.35 points) I measure **1.6%** of the
  density above 100%, not 4.4%. A bandwidth of about 0.93 gives 4.4%. The mechanism is the same either way,
  and the notebook shows both.
- **Part C:** the course notes say `#CC79A7` falls below 3:1 contrast on white. By the WCAG 2 formula it's
  **3.06:1**, just above the minimum, though still the weakest of the four.

## Rules I kept to

- Every figure uses `fig, ax`, with no `plt.plot()`, and is saved with `fig.savefig` (through
  `vizlib.save_fig`) at 300 dpi before anything is shown.
- Titles state the finding. Every parameter that changes the picture (bins, alpha, scale, vmin/vmax) is on
  the figure.
- Every value removed is stated with its rule and count. Nothing is hidden by `showfliers=False`.
- No dual axes. Correlation heatmaps use a diverging scale pinned to −1…+1 with the upper triangle masked.
- The palette is the course's Okabe–Ito subset, checked under simulation, never colour alone for a fourth
  category.
- All data is synthetic course data for CDB601220, and every figure says so.

*The bonus (the pop-out experiment on five classmates) isn't attempted. It needs real people timed at the
screen.*
