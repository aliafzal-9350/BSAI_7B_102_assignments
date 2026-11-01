"""
Week 3 · Bonus — Week 1's count-the-3s activity, rebuilt in code and timed.

Three commands, run from week3/:

    python popout_experiment.py panels          the four panels, as one figure
    python popout_experiment.py run "Ayesha"    time one reader (do this 5 times)
    python popout_experiment.py report          chart + three sentences, from the CSV

`run` needs a real person at the screen. It opens one panel at a time in its
own window, starts the clock when the panel is drawn, and stops it when the
reader presses SPACE. You then type the number they said. Each reader adds
four rows to popout_results.csv. Nothing in that file is ever generated.

Two design decisions, both stated on the results chart:

- Order: each reader sees the four panels in a fresh random order
  (random.SystemRandom), so learning and fatigue spread across panels
  instead of piling onto whichever panel always comes last.
- Grids: the starter draws the same 9 targets in all four panels, which is
  right for the comparison figure. For timing it is not, because after the
  first trial the reader already knows the answer is 9. Each timed trial
  gets a new grid with 7–11 targets, and the seed and the true count are
  recorded for every trial.
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import sys
import time
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "starter"))
import popout as starter                      # noqa: E402  (unchanged course file)
from vizlib import PALETTE, save_fig, style_defaults   # noqa: E402

RESULTS = os.path.join(HERE, "popout_results.csv")
CHARTS = os.path.join(HERE, "charts")
FIELDS = ["reader", "position", "panel", "channel", "seconds", "said",
          "true_count", "correct", "grid_seed", "order", "timestamp"]
N_READERS = 5
TARGET_RANGE = (7, 11)

# panel number -> (channel name, draw() keyword arguments)
PANELS = {
    1: ("No channel", {}),
    2: ("Colour", {"colour": True}),
    3: ("Size only", {"size": True}),
    4: ("Colour + shape", {"colour": True, "shape": True}),
}


def make_grid(n_targets, seed):
    """starter.make_grid(), with the number of targets as an argument."""
    rng = np.random.default_rng(seed)
    others = [d for d in "0123456789" if d != starter.TARGET]
    grid = np.array([[rng.choice(others) for _ in range(starter.COLS)]
                     for _ in range(starter.ROWS)], dtype=object)
    for k in rng.choice(starter.ROWS * starter.COLS, size=n_targets,
                        replace=False):
        grid[k // starter.COLS, k % starter.COLS] = starter.TARGET
    return grid


# ================================================================== panels
def cmd_panels(_args):
    """The four-panel comparison figure: TODO 1 and TODO 2 of the starter."""
    style_defaults()
    grid = starter.make_grid()
    titles = {
        1: "1. No channel — you have to read every cell",
        2: "2. Colour — the targets appear before you look",
        3: "3. Size only — larger and bold, no colour",
        4: "4. Colour and shape — survives greyscale and colour-blindness",
    }
    fig, ax = plt.subplots(2, 2, figsize=(13.0, 8.0))
    for p, a in zip(PANELS, ax.flat):
        starter.draw(a, grid, titles[p], **PANELS[p][1])
    fig.suptitle(f"Count the {starter.TARGET}s. Same {starter.N_TARGETS} "
                 "targets in all four panels, same positions.",
                 x=0.006, ha="left", fontsize=13.5, fontweight="bold",
                 color=PALETTE["ink"])
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out = save_fig(fig, os.path.join(CHARTS, "popout_panels.png"),
                   f"{starter.ROWS}x{starter.COLS} grid, {starter.N_TARGETS} "
                   f"targets, seed {starter.SEED}. Week 1 activity, rebuilt in "
                   "Matplotlib. Panel 3 uses size only; panel 4 uses colour and "
                   "a ring (redundant coding).")
    plt.close(fig)
    print("wrote", os.path.relpath(out, HERE))


# ===================================================================== run
def time_one_panel(grid, panel):
    """Show one panel in its own window. Seconds from first draw to SPACE."""
    fig, ax = plt.subplots(figsize=(12, 8))
    starter.draw(ax, grid, f"Count the {starter.TARGET}s. Press SPACE the "
                 "moment you have the number, then say it aloud.",
                 **PANELS[panel][1])
    clock = {}

    def on_draw(_event):
        clock.setdefault("start", time.perf_counter())

    def on_key(event):
        if event.key in (" ", "space", "enter") and "start" in clock:
            clock["stop"] = time.perf_counter()
            plt.close(fig)

    fig.canvas.mpl_connect("draw_event", on_draw)
    fig.canvas.mpl_connect("key_press_event", on_key)
    try:
        fig.canvas.manager.window.state("zoomed")      # TkAgg: fill the screen
    except Exception:
        pass
    plt.show()
    if "stop" not in clock:
        return None                                    # window closed early
    return clock["stop"] - clock["start"]


def ask_int(prompt):
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            return int(raw)
        print("   a whole number, please")


def cmd_run(args):
    reader = args.reader.strip()
    rows = read_results()
    if any(r["reader"].lower() == reader.lower() for r in rows):
        sys.exit(f"'{reader}' already has results in popout_results.csv. "
                 "Use a different name; one reader, one sitting.")
    if plt.get_backend().lower() == "agg":
        sys.exit("No interactive window available (backend is Agg). Run this "
                 "from a normal terminal, not a notebook or a headless shell.")

    rng = random.SystemRandom()
    order = list(PANELS)
    rng.shuffle(order)
    print(f"\nReader: {reader}. Panel order (random): {order}")
    print("Tell them: 'Count the 3s. Press SPACE the moment you have the "
          "number, then say it out loud.'\n")

    input("Practice round first (not recorded). Press Enter when ready... ")
    time_one_panel(make_grid(8, rng.randrange(10**6)), 1)

    new = []
    for pos, panel in enumerate(order, 1):
        n_true = rng.randint(*TARGET_RANGE)
        seed = rng.randrange(10**6)
        input(f"Trial {pos} of 4. Press Enter when {reader} is ready... ")
        secs = time_one_panel(make_grid(n_true, seed), panel)
        if secs is None:
            sys.exit("Window closed without SPACE. Nothing was saved; run "
                     "this reader again.")
        said = ask_int("   How many did they say? ")
        new.append({
            "reader": reader, "position": pos, "panel": panel,
            "channel": PANELS[panel][0], "seconds": f"{secs:.2f}",
            "said": said, "true_count": n_true,
            "correct": int(said == n_true), "grid_seed": seed,
            "order": "-".join(map(str, order)),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })
        print(f"   {secs:.2f} s, said {said}, true {n_true}")

    write_header = not os.path.exists(RESULTS)
    with open(RESULTS, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        w.writerows(new)
    n = len({r["reader"] for r in rows} | {reader})
    print(f"\nSaved 4 rows for {reader}. Readers so far: {n} of {N_READERS}.")


# ================================================================== report
def read_results(path=None):
    path = path or RESULTS
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def cmd_report(args):
    rows = read_results(args.results)
    readers = sorted({r["reader"] for r in rows})
    if not rows:
        sys.exit("No results yet. Run `python popout_experiment.py run NAME` "
                 f"for each of your {N_READERS} readers first.")
    if len(readers) < N_READERS:
        print(f"WARNING: {len(readers)} reader(s), the brief asks for "
              f"{N_READERS}. Charting what there is.")

    secs = {p: np.array([float(r["seconds"]) for r in rows
                         if int(r["panel"]) == p]) for p in PANELS}
    correct = {p: sum(int(r["correct"]) for r in rows if int(r["panel"]) == p)
               for p in PANELS}
    mean = {p: secs[p].mean() for p in PANELS}
    fastest = min(PANELS, key=mean.get)
    slowest = max(PANELS, key=mean.get)
    gap_42 = mean[4] - mean[2]
    name = {p: f"panel {p} ({PANELS[p][0].lower()})" for p in PANELS}

    style_defaults()
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    x = np.arange(len(PANELS))
    ax.bar(x, [mean[p] for p in PANELS], width=0.62,
           color=PALETTE["series"][0], alpha=0.25, zorder=1)
    jit = np.random.default_rng(0)             # jitter only, not data
    for i, p in enumerate(PANELS):
        xs = i + jit.uniform(-0.12, 0.12, len(secs[p]))
        ax.scatter(xs, secs[p], s=36, color=PALETTE["series"][0],
                   edgecolor="white", linewidth=0.7, zorder=3)
        ax.annotate(f"mean {mean[p]:.1f} s\n{correct[p]}/{len(secs[p])} correct",
                    (i, 0), xytext=(0, 5), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8, color=PALETTE["ink"])
    ax.set_xticks(x)
    ax.set_xticklabels([f"{p}. {PANELS[p][0]}" for p in PANELS])
    ax.set_ylim(0, max(s.max() for s in secs.values()) * 1.25)
    ax.set_ylabel("Seconds to count the 3s")
    ax.grid(axis="x", visible=False)
    ax.set_title(f"{PANELS[fastest][0]} was fastest ({mean[fastest]:.1f} s) and "
                 f"{PANELS[slowest][0].lower()} slowest ({mean[slowest]:.1f} s); "
                 f"adding shape to colour changed it by {gap_42:+.1f} s",
                 fontsize=11)
    out = save_fig(fig, os.path.join(CHARTS, "popout_results.png"), (
        f"n = {len(readers)} readers, 4 timed trials each, plus one unrecorded "
        "practice trial. Bars = mean; dots = each reader.\nPanel order shuffled "
        "per reader with random.SystemRandom. Each trial used a fresh "
        f"{starter.ROWS}x{starter.COLS} grid with {TARGET_RANGE[0]}–"
        f"{TARGET_RANGE[1]} targets, so no reader could carry the answer over.\n"
        "Clock: first draw of the panel to the reader's SPACE press, so it "
        "includes the key press. Week 1 activity, rebuilt in Matplotlib."))
    plt.close(fig)
    print("wrote", os.path.relpath(out, HERE))

    sentences = (
        f"The fastest channel was {name[fastest]}, at {mean[fastest]:.1f} s on "
        f"average across {len(readers)} readers, and the slowest was "
        f"{name[slowest]}, at {mean[slowest]:.1f} s.",
        f"Colour alone took {mean[2]:.1f} s and size alone {mean[3]:.1f} s, so "
        f"size was {'slower' if mean[3] > mean[2] else 'not slower'} than colour "
        f"by {abs(mean[3] - mean[2]):.1f} s.",
        f"Adding shape to colour (panel 4) changed the mean by {gap_42:+.1f} s "
        f"against colour alone (panel 2), so redundant coding "
        f"{'cost almost nothing' if abs(gap_42) < 1 else 'had a visible cost'} "
        "in speed while keeping the targets findable without colour.",
    )
    out_md = os.path.join(HERE, "popout_findings.md")
    with open(out_md, "w", encoding="utf-8") as fh:
        fh.write("# Bonus · Pop-out experiment: findings\n\n"
                 f"Chart: [`charts/popout_results.png`](charts/popout_results.png)"
                 f" · data: [`popout_results.csv`](popout_results.csv) · "
                 f"n = {len(readers)}\n\n" + "\n\n".join(sentences) + "\n")
    print("wrote popout_findings.md\n")
    print("\n".join(sentences))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("panels").set_defaults(fn=cmd_panels)
    r = sub.add_parser("run")
    r.add_argument("reader", help="the reader's first name")
    r.set_defaults(fn=cmd_run)
    rep = sub.add_parser("report")
    rep.add_argument("--results", default=None,
                     help="results CSV (default: popout_results.csv)")
    rep.set_defaults(fn=cmd_report)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
