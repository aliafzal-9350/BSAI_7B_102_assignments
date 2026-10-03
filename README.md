# Data Visualization · Assignments

**Name:** Ali Afzal
**Roll No.:** BSAI-7B-102
**Subject:** Data Visualization

| Week | Topic | Folder |
|---|---|---|
| 1 | Why visualize, and choosing the right chart | this page (root) |
| 2 | Visual perception: preattentive attributes, Gestalt, cognitive load | [week2/](week2/) |

---

## Week 1 · Why visualize, and choosing the right chart

There are five datasets and five tasks, all from [TASKS.md](TASKS.md). The question decides the chart type,
and every chart has a note under it explaining why that type was chosen and what the chart shows.

| Notebook | Data | Charts | Finding |
|---|---|---|---|
| [task1_datasaurus.ipynb](task1_datasaurus.ipynb) | `datasaurus.csv` | Summary table, 13-panel scatter grid | The 13 datasets have the same means, spread and correlation (about −0.06). Plotted, one of them is a dinosaur. |
| [task2_gapminder.ipynb](task2_gapminder.ipynb) | `gapminder.csv` | Spaghetti chart (bad on purpose), continent lines, 3 highlighted countries, log-scale histogram, percentile band | Africa stalled after 1987. The gap between rich and poor countries **widened**, from 15× in 1952 to 38× in 2007. |
| [task3_penguins.ipynb](task3_penguins.ipynb) | `penguins.csv` | Histogram, small multiples, scatter with trend lines, grouped bar | Gentoo make up the heavy tail. Simpson's paradox: across all penguins, longer bills go with shallower ones (r = −0.24), but within every species they go with deeper ones (+0.39 to +0.65). |
| [task4_mpg.ipynb](task4_mpg.ipynb) | `mpg.csv` | Line, box plot, scatter, bar, dumbbell | Median mpg doubled from 1970 to 1982 (16 → 32). Cars got lighter, but at every weight a newer car still did 3–9 mpg more. |
| [task5_flights.ipynb](task5_flights.ipynb) | `flights.csv` | Line, seasonal overlay, heatmap, log-scale line | Passenger numbers nearly quadrupled. July or August is the peak every year. The growing summer swing is mostly the airline growing. |

### Chart choice, at a glance

| Question | Chart |
|---|---|
| How does it change over time? | Line |
| How is one number spread out? | Histogram, or small multiples per group |
| Do two numbers move together? | Scatter |
| How do groups compare across a whole distribution? | Box plot |
| How many in each category? | Bar, starting at zero |
| Is a pattern consistent across years? | Heatmap |
| Before vs after, holding something fixed? | Dumbbell |

### Run it

```bash
pip install pandas numpy matplotlib seaborn jupyter ipykernel
jupyter notebook
```

The data is already in `data/`. If it's missing, run `python download_assignment_data.py`.

### Rules I kept to

- The title states the finding, not the axis names.
- Bars start at zero, and there are never two y-axes.
- Colour means something, or it isn't used.
- Labels are selective, placed directly on the chart where possible.
- Any excluded or missing rows are stated on the chart.

---

**Week 2** is in [week2/](week2/). It has its own [README](week2/README.md).
