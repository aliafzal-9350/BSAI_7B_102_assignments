# Part E · Written justification

**Ali Afzal** · BSAI-7B-102 · Data Visualization · Week 5 · Figures: [`partD_bubble.png`](charts/partD_bubble.png),
[`partD_pcp.png`](charts/partD_pcp.png), [`partD_choropleth.png`](charts/partD_choropleth.png)

## 1 · Which variable got which channel, and why

The channels were assigned in order of how precisely the reader needs to compare each variable (slide 8):

| Rank | Variable | Channel | Reason |
|---|---|---|---|
| 1 | GDP per capita | **x position**, log scale | The explanatory variable. Read precisely along a common axis, and multiplicative, so logged |
| 2 | Healthcare access | **y position**, 0–100 | The outcome. The title's claim (r = 0.83) is read straight off the two positions |
| 3 | Population | **area**, linear, 12–1,500 pt² | Context ("is this a big country?"), where ±20% accuracy is enough. Area, never radius, with a legend in real millions |
| 4 | Region | **hue**, 6 Okabe–Ito colours | Identity, not amount. Six categories is within the ~7 the eye can keep apart |

In the choropleth, position is used up by geography, so the rate goes to **lightness** (one sequential hue, dark = more). The count goes back onto a **length** channel in the bar chart beside it, because counts need precise comparison and a map's area can't give it.

## 2 · The parallel coordinates decisions

- **Scaling:** `log10(gdp_pc)`, then min–max on all five axes. Min–max keeps the gaps between countries. Logging GDP first stops Aldonia ($120,219, 9.2× the next) crushing 58 of 60 countries below 0.10 (case 3, Part B.3). Rank scaling was rejected because it would erase the gaps the reader needs to see.
- **Axis order:** the greedy |r| chain (slide 24), **computed on the same columns that are drawn**: GDP → access → cases → urban → median age. On raw GDP the chain is the brief's access → cases → urban → age → GDP. Logging GDP makes it correlate 0.83 with access, so it moves to the front. The order was computed before drawing and is stated on the figure. `geolib.corr_chain()` crashes under pandas 3 (copy-on-write), so the same rule is reimplemented in the notebook.
- **What it showed that a SPLOM wouldn't:** a scatter matrix shows every pair separately, but it can't follow one country across all five variables. Brushing **Caldera** traces one region's *profile* across all five axes at once. Seven of its ten countries come in below the median on access, and seven leave above the median on cases. Three follow the whole low-access → high-cases → low-urbanisation path, and the other seven can be seen breaking from it at a particular axis. A scatter matrix would split that one path across ten separate panels.

## 3 · The spatial decisions

- **Denominator:** cases per **100,000 residents**. It's the population at risk, and it takes the correlation with population from +0.986 (counts) to −0.000. The words are in the legend title.
- **Classification:** Jenks natural breaks, five classes, with the breaks printed in the legend. It has the highest goodness of variance fit (0.969 vs quantile 0.908), and the rates here really do spread from 30 to 77, unlike case 5's 7% spread, where any five-class scheme would invent a pattern.
- **Projection:** Lambert cylindrical equal-area, true scale at 30.5°N, one projection shared by every layer. Colour spread over an area makes area the encoding. Mercator would draw northern districts 1.21× larger than southern ones of the same size (Part B.4), and the north is exactly where the highest rates are.

## 4 · The counterfactual

A raw-count map would have coloured **D17 (Qilabad, 11.0 M people), D13 (Mehrabad) and D09 (Ilyaspur)** darkest. They're the three most populous districts, around the capital, and their rates (50–64 per 100,000) sit in the middle of the distribution. It would have pointed extra clinics, testing and attention at the places where the most people live, and away from **D19, D20 and D21**, the small northern districts (1.1–1.8 M people) where a resident is actually most likely to be infected. It would also have attached an "outbreak district" label to the capital's neighbourhoods, a reputation the data doesn't support, and the people living there would bear the cost. Part C tested this directly: *(after running the experiment: "my N readers' picks overlapped by X of 3 on average between the count map and the rate map; on the count map, Y of them chose the three most populous counties")*.

**Suppression:** no district was suppressed or merged. The smallest has 468,000 people and 186 cases, ten times the ~43,000 floor below which a rate of 18 per 100,000 can't be told from 9 (Part B.5). Case 6's small-area file would need that rule. At district scale it doesn't bind, and aggregating up to zones would have hidden the northern cluster that this map exists to show.
