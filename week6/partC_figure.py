"""
Week 6 · Task C — the one figure the board sees.

    Where is supply least reliable?

Interruptions per 1,000 billed households, on an equal-area choropleth, beside
the same 24 rates as a sorted bar chart against the national pooled rate. The
map shows where; the bars show by how much, which a map cannot.

Reads only clean/, so run partA_process.py first.

    python partC_figure.py
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import geolib
import vizlib

HERE = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(HERE, "clean")
P = vizlib.PALETTE
PER = 1000                 # interruptions per 1,000 billed households
SCHEME, K = "natural", 5   # Jenks, five classes

vizlib.style_defaults()

reg = pd.read_csv(os.path.join(CLEAN, "district_grid.csv"))
feats = geolib.read_geojson(os.path.join(HERE, "data", "regions.geojson"))

# ---- the join, counted ---------------------------------------------------
codes = {f["code"] for f in feats}
matched = codes & set(reg.code)
print(f"join: {len(matched)} matched, {len(codes - set(reg.code))} geometry-only, "
      f"{len(set(reg.code) - codes)} register-only")
assert len(matched) == 24

# ---- the quantity, and the anchors ----------------------------------------
reg["rate"] = reg.outages / reg.households * PER
national = reg.outages.sum() / reg.households.sum() * PER
r_count = np.corrcoef(reg.outages, reg.households)[0, 1]
r_rate = np.corrcoef(reg.rate, reg.households)[0, 1]
r_income = np.corrcoef(reg.rate, reg.income_pc_usd)[0, 1]
top_count = reg.nlargest(3, "outages").code.tolist()
top_rate = reg.nlargest(3, "rate").code.tolist()
both = sorted(set(top_count) & set(top_rate))
print(f"r(interruptions, households)        {r_count:+.3f}")
print(f"r(rate per {PER:,} households, households) {r_rate:+.3f}")
print(f"r(rate, income per head)            {r_income:+.3f}")
print(f"top 3 by count {top_count}, by rate {top_rate}, on both {both}")
print(f"national pooled rate {national:.1f} per {PER:,} households")

edges = geolib.breaks(reg.rate, SCHEME, K)
for s in ("natural", "quantile", "equal"):
    e = geolib.breaks(reg.rate, s, K)
    print(f"   {s:<8} breaks {[round(v, 1) for v in e]}  "
          f"GVF {geolib.gvf(reg.rate, e):.3f}")

# Is any of it noise? Poisson limits around the national rate for each
# district's households. The smallest district has 76,721 households, so its
# 95% band is about ±1.5 per 1,000 — a gap of 7 per 1,000 is not chance.
fl = geolib.funnel_limits(reg.households, national, per=PER)
n_inside = int(((reg.sort_values("households").rate.to_numpy() >= fl.lo)
                & (reg.sort_values("households").rate.to_numpy() <= fl.hi)).sum())
print(f"funnel: widest band {fl.lo.iloc[0]:.1f}–{fl.hi.iloc[0]:.1f}; "
      f"{n_inside} of 24 inside it")

# the five most populous: what a choropleth does to their ink
area = {f["code"]: geolib.polygon_area_km2(f["ring"]) for f in feats}
reg["area_geo"] = reg.code.map(area)
big5 = reg.nlargest(5, "population")
land5 = big5.area_geo.sum() / reg.area_geo.sum() * 100
ppl5 = big5.population.sum() / reg.population.sum() * 100
print(f"5 most populous: {land5:.1f}% of the land, {ppl5:.1f}% of the people")

# ---- the figure ------------------------------------------------------------
cm = plt.get_cmap(P["sequential"])
shades = [cm(0.18 + 0.78 * c / (K - 1)) for c in range(K)]
cls = dict(zip(reg.code, geolib.class_of(reg.rate, edges)))

fig = plt.figure(figsize=(12, 6.6))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.05], wspace=0.32)
axm = fig.add_subplot(gs[0, 0])
axb = fig.add_subplot(gs[0, 1])

geolib.choropleth(axm, feats, dict(zip(reg.code, reg.rate)), scheme=SCHEME,
                  k=K, legend=True, fmt="{:.1f}",
                  legend_title=f"Interruptions\nper {PER:,} billed\nhouseholds,\n"
                               "12 months\n(Jenks breaks)",
                  legend_loc="upper right", legend_anchor=(-0.03, 1.0))
lat_ts = geolib._collection_lat_ts(feats)
for f in feats:
    if f["code"] not in set(top_rate) | set(top_count):
        continue
    lon, lat = geolib.representative_point(f["ring"])
    x, y = geolib.equal_area_xy(lon, lat, lat_ts=lat_ts)
    dark = cls[f["code"]] >= 3
    axm.text(float(x), float(y), f["code"], ha="center", va="center",
             fontsize=8, fontweight="bold" if f["code"] in top_rate else "normal",
             color="white" if dark else P["ink"])
axm.set_title("Where: darker = more interruptions per household",
              fontsize=10, fontweight="normal", color=P["ink_soft"])

s = reg.sort_values("rate")
y = np.arange(len(s))
axb.barh(y, s.rate, color=[shades[cls[c]] for c in s.code], height=0.72,
         edgecolor="white", linewidth=0.4)
axb.axvline(national, color=P["ink"], lw=1, ls="--", zorder=2)
axb.text(national, len(s) - 0.1, f" national {national:.1f}",
         fontsize=8, color=P["ink"], va="bottom")
axb.set_yticks(y)
axb.set_yticklabels([f"{c} {d}" for c, d in zip(s.code, s.district)],
                    fontsize=8)
for t, c in zip(axb.get_yticklabels(), s.code):
    if c in top_rate:
        t.set_fontweight("bold")
        t.set_color(P["ink"])
for yi, (c, v, n) in enumerate(zip(s.code, s.rate, s.outages)):
    label = f"{v:.1f}"
    if c in top_count:
        label += f"   ◆ #{top_count.index(c) + 1} by raw count ({n:,})"
    axb.text(v + 0.4, yi, label, va="center", fontsize=7.5, zorder=4,
             color=P["highlight"] if c in top_count else P["ink_soft"],
             bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
axb.set_xlim(0, s.rate.max() * 1.55)
axb.set_ylim(-0.7, len(s) + 0.4)
axb.set_xlabel(f"Interruptions per {PER:,} billed households, 12 months")
axb.grid(axis="y", visible=False)
axb.set_title("By how much: all 24 districts, sorted",
              fontsize=10, fontweight="normal", color=P["ink_soft"])

top = reg.set_index("code").loc[top_rate]
cnt = reg.set_index("code").loc[top_count]
names = lambda t: ", ".join(f"{d} ({c})" for c, d in zip(t.index[:-1], t.district[:-1]))     + f" and {t.district.iloc[-1]} ({t.index[-1]})"
fig.suptitle(
    f"Supply is least reliable in {names(top)}: about {top.rate.min():.0f} interruptions per {PER:,} households, "
    f"{(top.rate.min() / national - 1) * 100:.0f}% above the national "
    f"{national:.1f}.\nRanked by raw count instead, the list would be "
    f"Qilabad, Mehrabad and Zhobara — the three biggest districts.",
    x=0.06, y=1.03, ha="left", fontsize=12, fontweight="bold", color=P["ink"])
fig.text(0.06, 0.935, "For the National Grid Authority board, splitting the "
         "reliability budget across 24 districts.", fontsize=9,
         color=P["ink_soft"], style="italic")

out = vizlib.save_fig(fig, os.path.join(HERE, "partC_figure.png"), note=(
    f"Rate = feeder interruptions over 12 months ÷ billed domestic connections "
    f"× {PER:,}. National = pooled (all interruptions ÷ all households), not "
    f"the mean of 24 rates. Classes: Jenks natural breaks, {K} classes, "
    f"edges {', '.join(f'{v:.1f}' for v in edges)}.\n"
    f"Projection: Lambert cylindrical equal-area. Join: 24 of 24 districts "
    f"matched, 0 unmatched. No district suppressed: Poisson 95% limits around "
    f"the national rate are at most ±{(fl.hi - fl.lo).max() / 2:.1f} per "
    f"{PER:,}.\nD21's households repaired 182 → 182,000 (Task A); uncorrected, "
    f"its rate would read {reg.set_index('code').outages['D21'] / 182 * PER:,.0f}. ◆ = top 3 by raw count. "
    f"Synthetic data generated for CDB601220 Week 6. Boundaries: regions.geojson."))
plt.close(fig)
print(f"wrote {os.path.basename(out)}")
