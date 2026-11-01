"""
Week 6 · Task B — three charts, three kinds of question.

    B1  trend         grid_daily       energy delivered per day, all zones
    B2  composition   generation_mix   what the energy was generated from
    B3  relationship  district_grid    rooftop solar against income

Reads only clean/, so run partA_process.py first.

    python partB_charts.py
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import tslib
import vizlib

HERE = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(HERE, "clean")
P = vizlib.PALETTE
SOURCE = ("Synthetic data generated for CDB601220 Week 6 (National Grid "
          "Authority case). Cleaned by partA_process.py.")

vizlib.style_defaults()


# ============================================================== B1 · trend
cal = pd.read_csv(os.path.join(CLEAN, "grid_daily_calendar.csv"),
                  parse_dates=["date"])
by_zone = cal.pivot(index="date", columns="zone", values="delivered_mwh")
# National = all six zones. A day where any zone's energy is unknown is left
# out rather than summed over five zones, so the line breaks instead of dipping.
nat = by_zone.sum(axis=1, min_count=by_zone.shape[1]) / 1000      # GWh/day
WINDOW = 28
smooth = nat.rolling(WINDOW, center=True, min_periods=WINDOW // 2).mean()
wr = tslib.window_report(nat.dropna(), windows=(7, WINDOW, 91))
print("B1 window report (GWh/day)\n", wr.to_string(index=False))

jul = nat.groupby(nat.index.to_period("M")).mean()
jul25, jul26 = jul[pd.Period("2025-07")], jul[pd.Period("2026-07")]
yoy = (jul26 / jul25 - 1) * 100
n_interp = int(cal.energy_interpolated.sum())
share_interp = (cal.loc[cal.energy_interpolated, "delivered_mwh"].sum()
                / cal.delivered_mwh.sum() * 100)
n_gap_days = int(nat.isna().sum())

fig, ax = plt.subplots(figsize=(9.5, 4.6))
ax.plot(nat.index, nat.values, color=P["muted"], lw=0.7, alpha=0.8,
        label="daily")
ax.plot(smooth.index, smooth.values, color=P["series"][0], lw=2.2,
        label=f"{WINDOW}-day centred mean")
for per, val, ha in [("2025-07", jul25, "center"), ("2026-07", jul26, "center")]:
    mid = pd.Period(per).to_timestamp() + pd.Timedelta(days=15)
    ax.annotate(f"July mean\n{val:,.0f} GWh/day", (mid, val),
                xytext=(0, 34), textcoords="offset points", ha=ha,
                fontsize=8.5, color=P["ink"],
                arrowprops=dict(arrowstyle="-", color=P["ink_soft"], lw=0.7))
ax.set_ylim(0, nat.max() * 1.22)
ax.set_ylabel("Energy delivered, GWh per day (all six zones)")
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.set_xlim(nat.index.min(), nat.index.max())
ax.legend(loc="upper left", ncols=2)
ax.set_title(f"The grid delivered {yoy:.0f}% more energy in July 2026 than in "
             "July 2025 — plan the 2027 summer reserve on that growth, not on "
             "last year's peak", fontsize=11, wrap=True)
fig.text(0.01, 0.005,
         "Supports: sizing the summer-2027 reserve margin.",
         fontsize=8.5, color=P["ink"], style="italic")
vizlib.save_fig(fig, os.path.join(HERE, "partB_1.png"), note=(
    f"Energy = forward difference of each zone's meter reading, never a sum "
    f"of readings. Period 2025-04-01 → 2026-09-11, daily, no resampling.\n"
    f"Window {WINDOW} days centred, min {WINDOW // 2} days "
    f"(removes {wr.set_index('window').loc[WINDOW, 'variation_removed_pct']}% "
    f"of the variation; the seasonal swing is the signal).\n"
    f"{n_interp} zone-days ({share_interp:.1f}% of energy) are spread evenly "
    f"across unreported days.\n{n_gap_days} days are left out because one "
    f"zone's energy is unknown (P4 meter change 2026-02-16; the last day has "
    f"no next reading).\n{SOURCE}"))
plt.close(fig)


# ======================================================== B2 · composition
gen = pd.read_csv(os.path.join(CLEAN, "generation_mix.csv"))
gen["month"] = pd.PeriodIndex(gen.month, freq="M")
# Five groups: the ministry's four sources, with Renewable split so solar
# can be read on its own. Fossil = gas + coal + furnace oil; Hydro = dam +
# run-of-river. Every MWh is in exactly one group (checked in Task A).
gen["group"] = np.where(gen.source == "Renewable", gen.subsource, gen.source)
wide = gen.pivot_table(index="month", columns="group", values="mwh",
                       aggfunc="sum") / 1e6                       # TWh
order = ["Solar", "Wind", "Hydro", "Imported", "Fossil"]          # bottom up
wide = wide[order]
total = wide.sum(axis=1)
assert len(gen.groupby(["month", "source", "subsource"])) == len(gen)

g_chg = (total.iloc[-1] / total.iloc[0] - 1) * 100
s_chg = (wide.Solar.iloc[-1] / wide.Solar.iloc[0] - 1) * 100
s0 = wide.Solar.iloc[0] / total.iloc[0] * 100
s1 = wide.Solar.iloc[-1] / total.iloc[-1] * 100

# Solar is the only hue; the rest step down in lightness so the stack still
# reads in order, and every block is direct-labelled at the right edge.
colours = {"Solar": P["highlight"], "Wind": "#4F5D6B", "Hydro": "#8794A2",
           "Imported": "#B5C0CB", "Fossil": "#E0E6EC"}
print("\nB2 palette")
vizlib.cvd_report(list(colours.values()))
for kind in ("normal", "deutan", "protan", "tritan"):
    wp = vizlib.worst_pair(list(colours.values()), kind)
    print(f"   worst pair {kind:<7} dE {wp[-1]:.1f}  {vizlib.verdict(wp[-1])}")

fig, ax = plt.subplots(figsize=(9.5, 4.8))
x = np.arange(len(wide))
base = np.zeros(len(wide))
for grp in order:
    ax.bar(x, wide[grp].values, bottom=base, width=0.78, color=colours[grp],
           edgecolor="white", linewidth=0.5, label=grp)
    base += wide[grp].values
for i in (0, len(wide) - 1):
    sh = wide.Solar.iloc[i] / total.iloc[i] * 100
    # Above every bar, with a leader down to the one it describes.
    ax.annotate(f"{wide.index[i].strftime('%b %Y')}: {total.iloc[i]:.2f} TWh, "
                f"solar {wide.Solar.iloc[i] * 1000:,.0f} GWh = {sh:.1f}%",
                (x[i], total.iloc[i]), xytext=(x[i], total.max() * 1.1),
                textcoords="data", ha="right" if i else "left", va="bottom",
                fontsize=8, color=P["ink"],
                arrowprops=dict(arrowstyle="-", color=P["ink_soft"], lw=0.7,
                                shrinkA=0, shrinkB=2))
# direct labels at the right edge, so the greys never need a legend lookup
cum = wide.iloc[-1].cumsum()
for grp in order:
    mid = cum[grp] - wide[grp].iloc[-1] / 2
    ax.text(x[-1] + 0.55, mid, grp, va="center", fontsize=8.5,
            color=P["highlight"] if grp == "Solar" else P["ink_soft"],
            fontweight="bold" if grp == "Solar" else "normal")
ax.set_xticks(x)
ax.set_xticklabels([p.strftime("%b\n%Y") if p.month in (4, 1)
                    else p.strftime("%b") for p in wide.index],
                   fontsize=8)
ax.set_xlim(-0.6, len(wide) + 0.6)
ax.set_ylim(0, total.max() * 1.2)
ax.set_ylabel("Energy generated, TWh per month")
ax.grid(axis="x", visible=False)
ax.set_title(f"Solar output rose {s_chg:.0f}% while total generation fell "
             f"{-g_chg:.0f}% — so solar's share of the mix went from "
             f"{s0:.1f}% to {s1:.1f}%", fontsize=11)
fig.text(0.01, 0.005, "Supports: the communications office's rooftop-solar "
         "line — quote the MWh growth and the falling total together.",
         fontsize=8.5, color=P["ink"], style="italic")
vizlib.save_fig(fig, os.path.join(HERE, "partB_2.png"), note=(
    "Monthly totals, 2025-04 → 2026-09, all 18 months complete. Fossil = gas + "
    "coal + furnace oil; Hydro = dam + run-of-river;\nWind and Solar split out "
    "of Renewable. No 'Other' bucket. The ministry's 'All sources / Total' "
    "row is excluded —\nit is the whole, not a part; the eight parts match it "
    f"within 2 MWh every month.\n{SOURCE}"))
plt.close(fig)


# ======================================================= B3 · relationship
reg = pd.read_csv(os.path.join(CLEAN, "district_grid.csv"))
reg["solar_w_hh"] = reg.solar_kw_installed / reg.households * 1000
r = np.corrcoef(reg.income_pc_usd, reg.solar_w_hh)[0, 1]
lo = reg.nsmallest(3, "income_pc_usd")
hi = reg.nlargest(3, "income_pc_usd")
ratio = hi.solar_w_hh.mean() / lo.solar_w_hh.mean()

fig, ax = plt.subplots(figsize=(8.2, 5.2))
ax.scatter(reg.income_pc_usd, reg.solar_w_hh, s=46, color=P["series"][0],
           edgecolor="white", linewidth=0.7, zorder=3)
ax.text(0.98, 0.04, f"Pearson r = {r:+.2f} across the 24 districts",
        transform=ax.transAxes, ha="right", fontsize=8, color=P["ink_soft"])
label = set(lo.code) | set(hi.code)
for _, row in reg[reg.code.isin(label)].iterrows():
    rich = row.income_pc_usd > 8000
    ax.annotate(f"{row.code} {row.district}", (row.income_pc_usd, row.solar_w_hh),
                xytext=(8, -3) if rich else (-8, -3), ha="left" if rich else "right",
                textcoords="offset points", fontsize=8, color=P["ink"])
ax.set_xlim(0, reg.income_pc_usd.max() * 1.2)
ax.set_ylim(0, reg.solar_w_hh.max() * 1.12)
ax.set_xlabel("Income per head, USD per person per year")
ax.set_ylabel("Rooftop solar installed, watts per billed household")
ax.set_title(f"Rooftop solar follows income: the three richest districts "
             f"have {ratio:.1f}× the solar per household of the three poorest",
             fontsize=11)
fig.text(0.01, 0.005, "Supports: who the rooftop-solar line is about — and "
         "where a solar subsidy would change most.",
         fontsize=8.5, color=P["ink"], style="italic")
vizlib.save_fig(fig, os.path.join(HERE, "partB_3.png"), note=(
    "All 24 districts, one point each. Solar = registered rooftop capacity; "
    "households = billed domestic connections\n(D21 repaired from 182 to "
    "182,000, Task A). Labelled: the three lowest- and three highest-income "
    f"districts.\nr is Pearson on the 24 points. Correlation, not cause.\n{SOURCE}"))
plt.close(fig)

print(f"\nB1 July {jul25:.1f} -> {jul26:.1f} GWh/day ({yoy:+.1f}%)")
print(f"B2 generation {g_chg:+.1f}%, solar {s_chg:+.1f}% MWh, "
      f"{s0:.1f}% -> {s1:.1f}% share")
print(f"B3 r = {r:+.3f}, top-3/bottom-3 income ratio {ratio:.2f}x")
print("wrote partB_1.png partB_2.png partB_3.png")
