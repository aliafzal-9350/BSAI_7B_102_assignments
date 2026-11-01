"""
Week 6 · Task D1 (bonus) — Task B's trend chart, made interactive.

partB_1.png shows one line: national energy delivered per day. This rebuilds
it in Plotly with the six zones behind it, so a reader can hover any day for
the exact value, click zones on and off in the legend, and zoom to a date
range with the slider or the buttons.

Reads only clean/, so run partA_process.py first.

    python partD_interactive.py      -> partD_interactive.html (self-contained)
"""
from __future__ import annotations

import os

import pandas as pd
import plotly.graph_objects as go

import vizlib

HERE = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(HERE, "clean")
P = vizlib.PALETTE
WINDOW = 28
# Okabe–Ito. Six hues is past what colour alone can separate (vizlib allows
# four), so every trace is also named in the hover label and the legend.
ZONE_COLOURS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]

cal = pd.read_csv(os.path.join(CLEAN, "grid_daily_calendar.csv"),
                  parse_dates=["date"])
by_zone = cal.pivot(index="date", columns="zone", values="delivered_mwh") / 1000
spread = cal.pivot(index="date", columns="zone", values="energy_interpolated")
# Same rule as partB_1: a day with any zone unknown is a gap, not a 5-zone sum.
nat = by_zone.sum(axis=1, min_count=by_zone.shape[1])
smooth = nat.rolling(WINDOW, center=True, min_periods=WINDOW // 2).mean()
n_spread = int(cal.energy_interpolated.sum())

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=nat.index, y=nat.values, name="All six zones, daily",
    mode="lines", line=dict(color=P["muted"], width=1),
    hovertemplate="%{y:,.1f} GWh<extra>all zones</extra>"))
fig.add_trace(go.Scatter(
    x=smooth.index, y=smooth.values, name=f"All six zones, {WINDOW}-day centred mean",
    mode="lines", line=dict(color=P["ink"], width=2.5),
    hovertemplate="%{y:,.1f} GWh<extra>" + f"{WINDOW}-day mean</extra>"))
for z, colour in zip(by_zone.columns, ZONE_COLOURS):
    flag = spread[z].map({True: "spread over an unreported day",
                          False: "reported"}).fillna("unknown")
    fig.add_trace(go.Scatter(
        x=by_zone.index, y=by_zone[z], name=f"Zone {z}, daily",
        mode="lines", line=dict(color=colour, width=1.2),
        customdata=flag,
        hovertemplate="%{y:,.1f} GWh · %{customdata}<extra>" + z + "</extra>"))

fig.update_layout(
    template="plotly_white",
    title=dict(
        text="<b>The grid delivered 7% more energy in July 2026 than in July 2025</b>"
             "<br><span style='font-size:13px;color:#5B6573'>Click a zone in the "
             "legend to hide or show it · double-click to isolate one · drag the "
             "slider to zoom</span>",
        x=0.01, xanchor="left"),
    font=dict(family="DejaVu Sans, Arial, sans-serif", size=12, color=P["ink"]),
    hovermode="x unified",
    legend=dict(orientation="h", x=0, y=-0.3, yanchor="top",
                title_text="Click to filter:"),
    yaxis=dict(title="Energy delivered, GWh per day", rangemode="tozero",
               gridcolor=P["grid"]),
    xaxis=dict(
        gridcolor=P["grid"],
        rangeslider=dict(visible=True, thickness=0.07),
        rangeselector=dict(x=0, y=1.02, yanchor="bottom", buttons=[
            dict(count=1, label="1 month", step="month", stepmode="backward"),
            dict(count=3, label="3 months", step="month", stepmode="backward"),
            dict(count=6, label="6 months", step="month", stepmode="backward"),
            dict(step="all", label="All")])),
    margin=dict(l=70, r=30, t=130, b=290),
    height=820,
)
fig.add_annotation(
    xref="paper", yref="paper", x=0, y=-0.66, xanchor="left", yanchor="top",
    align="left", showarrow=False, font=dict(size=10, color=P["ink_soft"]),
    text=(f"Energy = forward difference of each zone's meter reading, never a sum of "
          f"readings.<br>Period 2025-04-01 → 2026-09-11, daily, no resampling. Mean: "
          f"{WINDOW} days centred, min {WINDOW // 2}.<br>{n_spread} zone-days are "
          f"spread evenly across unreported days (shown in the hover).<br>Gaps: P4 on "
          f"2026-02-16 (meter change) and the last day (no next reading); the "
          f"all-zone line breaks there.<br>Synthetic data generated for CDB601220 "
          f"Week 6 (National Grid Authority case).<br>Cleaned by partA_process.py."))

out = os.path.join(HERE, "partD_interactive.html")
fig.write_html(out, include_plotlyjs=True, full_html=True,
               config={"displaylogo": False})
print(f"wrote {os.path.basename(out)} ({os.path.getsize(out) / 1e6:.1f} MB, "
      f"opens offline)")
