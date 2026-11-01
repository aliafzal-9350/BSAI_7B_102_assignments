# Task D1 (bonus) · Making it interactive

**Ali Afzal** · SU92-BSAIM-F23-102 · BSAI · Section 7B · Chart: [`partD_interactive.html`](partD_interactive.html), from `partD_interactive.py`

I rebuilt **Task B's trend chart** ([`partB_1.png`](partB_1.png), national energy delivered per day) in Plotly,
with the six supply zones drawn behind the national line. Open the HTML in any browser. It's self-contained
and works offline.

| Interaction | How |
|---|---|
| **Hover a value** | Exact GWh for every zone on that day, and whether each zone-day was *reported* or *spread over an unreported day* |
| **Filter a category** | Click a zone in the legend to hide or show it; double-click to see that zone alone |
| **Zoom a date range** | Drag the range slider, or use the 1 / 3 / 6-month buttons |

**What it lets a reader do that the static chart can't.** A planner can isolate one zone, say P6, which
carries over a third of the grid's energy (35.6%), and read its exact daily figure on the day they care about, instead
of seeing only the national total.

**What it lets them do that I'd rather they didn't.** They can zoom into a single week, where the 28-day
mean is almost flat and day-to-day noise looks like a trend, or read an evenly-spread gap day as a real
reading. The hover label flags those days, but a reader zoomed into one week has already lost the seasonal
picture that the static chart's title is about.

Declared on the chart, the same as Task B: energy is the forward difference of the meter reading, never a sum
of readings. The period is 2025-04-01 → 2026-09-11, daily, with no resampling, and the mean is 28 days
centred. There are 243 spread zone-days and two gap days (the P4 meter change, and the last day).
