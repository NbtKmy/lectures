---
marp: true
theme: default
paginate: true
footer: "Visualise the numbers & statistics on Maps / Nobutake Kamiya"
style: |
  section {
    background: #14161a;
    color: #e6e8eb;
    font-family: -apple-system, "Helvetica Neue", "Hiragino Sans", sans-serif;
    font-size: 28px;
    padding: 60px 70px;
  }
  h1, h2 { color: #ffffff; }
  h1 { font-size: 1.9em; }
  h2 { border-bottom: 2px solid #cc2936; padding-bottom: 0.15em; }
  strong { color: #ff8a65; }
  em { color: #9ecbff; }
  a { color: #7cc4ff; }
  code { background: #23272e; color: #ffd479; padding: 0 0.25em; border-radius: 4px; }
  pre { background: #23272e; border-radius: 6px; padding: 0.5em 0.8em; font-size: 0.65em; }
  pre code { background: transparent; }
  li { margin: 0.15em 0; }
  table { font-size: 0.8em; border-collapse: collapse; }
  table tr, table tr:nth-child(2n) { background: transparent; color: #e6e8eb; }
  th { background: #23272e; color: #fff; }
  th, td { border: 1px solid #3a3f47; padding: 0.3em 0.7em; }
  td { background: #14161a; color: #e6e8eb; }
  tr:nth-child(even) td { background: #1a1d22; }
  footer, section::after { color: #7b828c; font-size: 0.55em; }
  blockquote { border-left: 4px solid #cc2936; color: #b8bec6; background: #1a1d22; padding: 0.2em 1em; }
  section.lead { text-align: center; justify-content: center; }
  section.lead h1 { border: none; }
  .small { font-size: 0.75em; color: #9aa1ab; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; }
  .ph { border: 2px dashed #3a3f47; border-radius: 8px; color: #7b828c; text-align: center; padding: 2.2em 1em; font-size: 0.8em; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Visualise the numbers & statistics on Maps
## Mapping foreign residents in Aichi with QGIS

60 min · hands-on

<!--
0–5 min. Welcome. Goal: leave with one finished choropleth map and a list of things that can go wrong when you map counts.
-->

---

## Today's goal

By the end of this session you will have

1. understood **the three building blocks** of a statistical map
2. **made a map** of foreign residents in Aichi with QGIS – from raw numbers
3. learned **what can go wrong** when counts are put on a map

> No GIS knowledge is assumed. QGIS is free: [qgis.org](https://qgis.org)

---

## Schedule

| Min | Part |
|---|---|
| 0–10 | Why maps? Three building blocks. Today's data |
| 10–35 | Hands-on: from CSV to map |
| 35–52 | What can go wrong when we map counts |
| 52–60 | Your own data, wrap-up, questions |

---

## Why maps?

A table of 69 municipalities hides what a map shows at once: **where**, **how clustered**, **next to what**.

<div class="cols">
<div>

**Migration** – where do nationalities settle?
**Education** – school catchments, access to schools
**Inequality** – income or deprivation by district

</div>
<div class="ph">finished map of today's data<br>(assets/qgis_result_brazil.png)</div>
</div>

> A map is an **argument**, not a photograph. Every choice – classes, colours, denominator – changes what readers see.

---

## Three building blocks

| Block | Today |
|---|---|
| **Base map** – where are we? | GSI standard tiles (raster) |
| **Shapes** – the areas | Municipality polygons, MLIT *N03* |
| **Numbers** – what to colour | Foreign residents per municipality, e-Stat |

- Shapes and numbers meet in a **join**: a column that has the same value in both
- Today's join key: the **5-digit municipality code**
- If the key does not match, nothing is coloured

---

## Today's data

*Statistics on Foreign Residents* (在留外国人統計), Dec 2025, e-Stat – **Aichi**, one row per municipality (Nagoya: per ward)

| Column | Meaning |
|---|---|
| `city_code` | 5-digit code, join key |
| `pr_all` | foreign residents with status **permanent resident** (永住者) |
| `pr_brazil` | … of these, Brazilian nationals |
| `pr_korea` | … of these, South Korean nationals |

69 rows · 106,839 permanent residents in total · 34,357 of them Brazilian

<!--
Make clear: "permanent resident" (永住者) is ONE residence status. Special permanent residents (特別永住者, mostly Zainichi Koreans) are a separate category and NOT included.
-->

---

## The code is the same everywhere

`23201` = **23** (Aichi) + **201** (Toyohashi)

- 2 digits prefecture + 3 digits municipality (JIS X 0401 / 0402)
- Published by the Ministry of Internal Affairs and Communications (総務省)
- Nagoya's 16 wards have own codes: `23101` … `23116`
- The polygon file carries it as `N03_007`

> The same code works in statistics, boundary files and many other datasets – the key to combining them.

---

## What I cleaned before class

Raw copy from a spreadsheet:

- `4’182` – a *thousands separator* inside the number → QGIS reads **text**, not a number
- a *total row* at the bottom (`Gesamtergebnis`)
- two municipalities (東栄町, 豊根村) **missing** in the Korea table → set to `0`

> Real data often needs this step. Always check **the type of a column** (number? text?) before you map it.

<!--
Honest data prep. The decimal-comma / separator problem is the classic: a column that LOOKS numeric but is a string cannot be classified.
-->

---

## Hands-on 1: base map

Layer ▸ Add Layer ▸ Add XYZ Layer ▸ **New**

```
Name: GSI standard
URL:  https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png
Minimum zoom level: 5
```

Select the new connection ▸ **Add**.

<span class="small">Tiles: [GSI](https://maps.gsi.go.jp/development/ichiran.html) · alternatives: [OSM raster tile providers](https://wiki.openstreetmap.org/wiki/Raster_tile_providers)</span>

---

## Hands-on 2: polygons

1. [N03-2025](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html) ▸ download **Aichi (23)**, GeoJSON
2. Drag the `.geojson` into QGIS
3. Open the attribute table – find `N03_007`

- Reference date 2025-01-01 · CC BY 4.0
- More features than municipalities: islands and exclaves are separate polygons
- One feature is `23000`: **unassigned area** (所属未定地)

---

## Hands-on 3: join the numbers

1. Drag `aichi_permanent_residents_202512.csv` into QGIS
2. Polygon layer ▸ right-click ▸ **Properties ▸ Joins ▸ +**
3. Join layer = the CSV · Join field = `city_code` · Target field = `N03_007`
4. Open the attribute table: `pr_all`, `pr_brazil`, `pr_korea` are attached

<div class="ph">attribute table after the join (assets/qgis_join.png)</div>

---

## Hands-on 4: colour by number

Properties ▸ **Symbology** ▸ **Graduated**

- Value: `pr_brazil` · pick a colour ramp · classes: 5 · **Classify**
- Try the *Mode* menu: Equal Interval · Equal Count (Quantile) · Natural Breaks (Jenks) · Pretty Breaks · Standard Deviation

<div class="ph">graduated map, pr_brazil (assets/qgis_brazil_equal.png)</div>

<!--
Let the participant produce the first map with the default mode. They will see almost everything in one colour. That is the next part's first problem.
-->

---

## Hands-on 5: export

1. Project ▸ **New Print Layout**
2. Add Map · Legend · Scale bar · Title
3. Layout ▸ **Export as Image**

Check before you export:

- legend title and labels readable, not `pr_brazil`
- base map **pale**, so that data colours stand out
- source and date in the caption

---

<!-- _class: lead -->

# What can go wrong when we map counts?

---

## 1 · The classes decide the picture

Brazilians with permanent residency, 69 municipalities: median **169**, maximum **4,182** (Toyohashi)

| Mode (5 classes) | Municipalities per class |
|---|---|
| Equal Interval | 57 · 5 · 5 · **0** · 2 |
| Quantile | ≈ 14 each |

- Equal Interval → almost the whole prefecture in the lowest colour
- Quantile → always a balanced map, even if differences are small
- Natural Breaks → follows gaps in the data

> No mode is neutral. **Say which one you used.**

---

## 2 · Counts are a map of population

Top municipalities by **count** (Brazil): Toyohashi 4,182 · Toyota 3,563 · Nishio 2,491

- Big places have more of everything
- To see *concentration*, divide by a **denominator**: `pr_brazil / pr_all × 100`
- Field calculator ▸ new decimal field → colour by it

| | by count | by share of all permanent residents |
|---|---|---|
| 1 | Toyohashi 4,182 (57%) | Hekinan 64% |
| 2 | Toyota 3,563 (47%) | Shinshiro 62% |
| 3 | Nishio 2,491 (52%) | Toyone 60% (**6 of 10**) |

<!--
Brazil is a fairly robust story: Toyohashi, Toyokawa (also 60%), Nishio, Hekinan are high in both lists, so count and share agree. That check is what lets you trust it. But note Toyone: 6 of 10 people - a hint of the small-numbers problem (slide 4 of this part).
-->

---

## 3 · Which denominator?

Three different questions, three different denominators:

- Brazilians **among permanent residents** (what we have) – composition
- Brazilians **among all foreign residents** – needs a different column
- Brazilians **among all inhabitants** – needs census / resident register

> Dividing by **one constant** (e.g. the Aichi total) changes only the legend numbers, **not the pattern**.

---

## 4 · Small numbers make wild rates

South Korea, permanent residents – highest **share**:

| Municipality | Count | All | Share |
|---|---|---|---|
| Shitara | 1 | 7 | **14.3%** |
| Minamichita | 8 | 59 | 13.6% |
| Tobishima | 3 | 23 | 13.0% |
| Nagoya Chikusa-ku | 216 | 2,075 | 10.4% |

- The "top" places are **one to eight people**
- 14 municipalities have fewer than 10 Korean permanent residents
- Remedies: minimum-size threshold · hatch small cells · show the counts · note it in the caption

---

## 5 · Big areas, small people

Nagoya's 16 wards are tiny polygons – but hold **58%** of the Korean permanent residents in Aichi.

- Choropleth colour fills the **area**, not the people
- Large rural municipalities dominate the picture although they have few people
- Remedies: **proportional symbols** (circles, sized by count) for counts; colour areas only for *rates*
- QGIS: Symbology ▸ *Data-defined override* ▸ **Size assistant**

<div class="ph">Korea: choropleth vs. proportional circles (assets/qgis_korea_compare.png)</div>

---

## 6 · Missing is not zero

- The raw Korea table has no row for 東栄町 and 豊根村 → a join would give **NULL**, which is not the same as 0
- We set both to **0**: the source lists no Korean permanent residents there. That is a *decision*, not a fact of the join
- The unassigned area `23000` has no data at all → stays NULL after the join: look at how it is drawn

> Decide for every gap: **zero, not available, or suppressed?** – and say so in the legend.

---

## 7 · Know what the category means

- "Permanent resident" (永住者) ≠ "special permanent resident" (特別永住者)
- Korea total here: **3,513** – without special permanent residents the map shows recent migration, **not** the long-established Korean community
- The same word in a column header can hide different populations

> Read the statistical definitions **before** you choose title and legend.

---

## 8 · The unit and the viewer

- **Ecological fallacy** – a municipality's rate says nothing about an individual
- **MAUP** – other boundaries (wards, neighbourhoods) give another picture
- **Time** – polygons: 2025-01-01, data: 2025-12. Mergers change borders
- **Base map** – dark or busy tiles hide the data colours; use a pale one
- **Colours** – sequential ramp for counts or rates; avoid red–green; check grey-scale print

---

## A checklist for your own map

1. **Count or rate?** – if a rate, which denominator?
2. **Which classification** – and does the legend show it?
3. Are there **small numbers**? Mark or suppress.
4. **Missing = ?** – zero, unavailable, suppressed
5. What does the **category** include and exclude?
6. Pale **base map**, readable **legend**, **source and date**

---

## Your own data

- **Statistics**: national statistics offices, e-Stat (Japan), Eurostat; codes must match the boundary file
- **Boundaries**: N03 (Japan), Natural Earth, Eurostat GISCO, OpenStreetMap
- **Interview sites** as points: Add Delimited Text Layer (lon/lat) – **coarsen the location** to protect anonymity
- **Migration or life-course** as lines: possible, not today

> Check the licence of every dataset you publish a map from.

---

## References

- QGIS manual: [docs.qgis.org](https://docs.qgis.org/latest/en/docs/user_manual/) · [vector properties](https://docs.qgis.org/latest/en/docs/user_manual/working_with_vector/vector_properties.html)
- [Statistics on Foreign Residents, e-Stat (Dec 2025)](https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00250012&tstat=000001018034&cycle=1&year=20250&month=24101212&tclass1=000001060399&result_back=1&tclass2val=0)
- [Prefecture and municipality codes, MIC](https://www.soumu.go.jp/denshijiti/code.html)
- [Administrative Areas N03-2025, MLIT](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html)
- [GSI tiles](https://maps.gsi.go.jp/development/ichiran.html)

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Questions?
