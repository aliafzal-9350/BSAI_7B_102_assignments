# Task C · Note on the board figure

**Ali Afzal** · SU92-BSAIM-F23-102 · BSAI · Section 7B · Figure: [`partC_figure.png`](partC_figure.png), from `partC_figure.py`

**Reader.** The National Grid Authority board, splitting the reliability budget across 24 districts.

**Message.** Supply is least reliable in **Lashkar (D12), Kotla (D11) and Mehrabad (D13)**: about 50–51
interruptions per 1,000 billed households a year, 15% above the national 43.7. A ranking by raw count
would have picked a different list.

## Parameters, and why

| Parameter | Choice | Reason |
|---|---|---|
| Denominator | **Billed households** (domestic connections), per 1,000, over 12 months | An interruption hits a connection, not a person. Using population would mix household size (5.70–7.36 persons) into the rate. The words are in the legend and axis titles |
| National line | **Pooled**: all 388,879 interruptions ÷ all 8,908,512 households = 43.7 | The mean of 24 rates would weight a 77,000-household district the same as a 1.57 M one |
| Classes | **Jenks**, 5 classes, edges 30.4 · 33.5 · 36.2 · 42.7 · 45.8 · 50.9, printed in the legend and the caption | GVF 0.959, against 0.899 for quantiles. Quantiles would split the 40–43 cluster into three shades of noise |
| Scheme | `Blues`, one hue, dark = worse. Bars use the same five shades | A rate is an amount, so lightness carries it. Matching shades make the bar chart a key to the map |
| Projection | Lambert cylindrical equal-area, one reference latitude for every polygon | Colour over an area makes area the channel. Areas are computed on the sphere, not in degrees |
| Bars | Sorted by rate, zero baseline, values printed | The map shows *where*. Only the bars show that the top three are 7 per 1,000 above the line and D05 is 13 below |
| Suppression | **None.** 0 districts merged or hidden | The smallest district has 76,721 households, so Poisson 95% limits around 43.7 are ±1.5 at most. Only 2 of 24 districts fall inside them: the spread is real, not chance |

## The counterfactual

A raw-count map would have been a population map. r(interruptions, households) = **+0.991**; for the rate it
is **+0.175**. That map would have sent the budget to **Qilabad (D17), Mehrabad (D13) and Zhobara (D24)**.
But Qilabad's rate is 40.4, 19th of 24 and *below* the national rate, and Zhobara's 42.5 is 12th. Both are on
the list only because they are the largest districts. The money would have been taken **away from Lashkar
(D12, 50.9) and Kotla (D11, 50.8)**, where a household loses supply most often.

Only **Mehrabad (D13)** is on both lists. It isn't there because it is big. Its households earn the least in
the federation ($2,600 per head), and across the 24 districts r(rate, income) = **−0.71**. It is on the rate
list for what it earns, and the count list happens to agree because it is also big.

Two more ways the figure could have lied, both closed: a choropleth gives the five most populous districts
**12.6% of the ink for 59.9% of the people**, which is why the bars sit beside it. And the uncorrected register
(D21 households = 182) would have put Ushkan at **47,907** per 1,000, painting one district dark and every
other district the same light shade.
