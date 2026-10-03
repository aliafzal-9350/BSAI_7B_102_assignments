# Week 2 · Visual Perception

**Name:** Ali Afzal
**Roll No.:** BSAI-7B-102
**Subject:** Data Visualization

My solutions to the five tasks in [TASKS.md](TASKS.md). They cover how the brain reads a chart and what that
means for chart design.

← [Back to all weeks](../README.md)

## What's here

| Notebook | Task | What it shows |
|---|---|---|
| [task1.ipynb](task1.ipynb) | Preattentive attributes | Timed visual search. A single feature is found in constant time, but a conjunction isn't. |
| [task2.ipynb](task2.ipynb) | Gestalt principles | Six grouping principles, connection vs colour, and proximity in a real bar chart |
| [task3.ipynb](task3.ipynb) | Cognitive load | An overloaded chart, a five-step strip-down, a 4-chunk version and an over-stripped version |
| [task4.ipynb](task4.ipynb) | Channel effectiveness | A 30-trial ratio experiment, then iris drawn on position vs lightness |
| [task5.ipynb](task5.ipynb) | Capstone redesign | The Gapminder spaghetti chart rebuilt around one message, with a before/after audit |

Every chart is saved to [`charts/`](charts/) at 300 DPI. The capstone is
[`charts/perception_redesign.png`](charts/perception_redesign.png).

## Run it

```bash
pip install pandas numpy matplotlib seaborn jupyter ipykernel
cd week2
jupyter notebook
```

The data is already in `data/`. If it's missing, run `python download_assignment_data.py`. Each notebook
runs top to bottom with **Restart & Run All**.

## The experiments

Tasks 1, 2 and 4 are run on a real person. Each of those notebooks has one experiment cell:

1. Set `READER = "..."` and `RUN_EXPERIMENT = True`.
2. Run that cell with the reader at the screen. They type their answers into the input box.
3. Set `RUN_EXPERIMENT = False`, then **Restart & Run All**.

| File | Task | Contents |
|---|---|---|
| `search_results.csv` | 1 | 18 trials: response, correct, `rt_ms` |
| `gestalt_results.csv` | 2 | Groups the reader saw, and why, for each panel |
| `channel_results.csv` | 4 | 30 estimates with `absolute_error` |

The titles on the result charts are written from the data, so they report what the reader actually did, even
when that disagrees with the theory. Task 5's reader test is a single sentence, typed into the notebook word
for word.

## Rules I kept to

- Every chart uses `fig, ax`. No `plt.plot` or `plt.bar`.
- Each chart has one pop-out: grey for context and a single red for the message.
- Colour never carries meaning alone. Direct labels, line style or line width back it up.
- Every deliberately bad chart has `BAD EXAMPLE` in its title.
- `n` and any excluded rows are stated on the figure.
- The palette is Paul Tol "bright", which stays readable for colour-blind readers.
