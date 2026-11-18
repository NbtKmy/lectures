# JGD2011 Zone Finder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A single-file English web page, `2026/qgis/jgd_zones/index.html`, where a beginner clicks a place in Japan (or searches for it) and gets its JGD2011 plane rectangular zone and EPSG code, plus a short explainer on plane rectangular coordinates and WGS84.

**Architecture:** A one-off Python prep step turns N03 nationwide boundaries into 19 dissolved, simplified zone polygons and builds a list of searchable named points (N03 Japanese municipality names plus GeoNames romanised names). Both are committed as small JSON files. A build script inlines them, Leaflet, proj4js and the page JS into one HTML file, like `2026/qgis/html_src/build.py`. All lookups (point-in-zone, name search, X/Y) run in the browser, with no runtime API calls.

**Tech Stack:** Python 3.11 stdlib (prep, build, `unittest`), mapshaper 0.6.102 via `npx`, Leaflet (copied from `2026/qgis/html_src/vendor/leaflet/`), proj4js 2.12.1 (vendored from cdnjs), plain ES5 browser JS in the UMD style of `html_src/classify.js`, `node:test` for the JS tests.

**Spec:** `docs/superpowers/specs/2026-11-18-jgd-zone-map-design.md`

## Global Constraints

- Page language is English. Japanese names (e.g. 系VII, 愛知県) appear alongside where helpful.
- Zone assignment comes from the official notice (平成14年国土交通省告示第9号), via the GSI page. The source URL is cited in `zone_rules.csv` and on the page. Never fill it in from memory.
- JGD2011 EPSG = 6668 + zone (6669–6687). JGD2000 EPSG = 2442 + zone (2443–2461).
- Boundaries: 国土数値情報 N03, nationwide, 2025-01-01 edition. Place names: GeoNames `JP.zip`, CC BY 4.0. Both are attributed on the page.
- No runtime API calls except the GSI pale tiles. The zones must render when the tiles fail.
- Embedded zone geometry is about 1–2 MB. The place list is about 200–300 KB. The whole page stays at or under 2.5 MB.
- The page works at 375 px width without horizontal page scroll.
- Do not touch `2026/qgis/html_src/` or `qgis_session.html`. Copy files from there, never import them.
- Downloads go to `2026/qgis/jgd_zones/src/.cache/` (gitignored), each archive in its own empty directory. Any Python that reads them runs with `python3 -I`.

## Review Focus

1. **Click on the sea or outside Japan:** the popup says "Not in a JGD2011 plane rectangular zone" and gives no zone. The test lives in Task 3 (`lookup` returns `null` for 35.0, 150.0).
2. **Pasted coordinates in lon-lat order** (`136.97, 35.19`) or with a degree sign or extra spaces: these are recognised and swapped into lat-lon. Test in Task 3 (`parseLatLon`).
3. **Search spelling:** `Ōsaka`, `osaka`, `Osaka-shi` and `大阪` all find Osaka. Test in Task 3 (`search`).
4. **Click just inside a zone boundary:** the simplification may shift the zone line. The popup carries a fixed caution line, and the sample points include two near boundaries. Test in Task 3 (sample table).
5. **Geolocation denied or tiles offline:** a visible message, the map still usable. Manual check in Task 4, step 6.

---

### Task 1: Zone tables from the official source

**Files:**
- Create: `2026/qgis/jgd_zones/src/zones.csv`
- Create: `2026/qgis/jgd_zones/src/zone_rules.csv`
- Test: `2026/qgis/jgd_zones/src/tests/test_tables.py`

**Interfaces:**
- Produces: `zones.csv` with columns `zone,roman,epsg,epsg_jgd2000,origin_lat,origin_lon,area_en`. That is 19 rows, origins in decimal degrees (converted from the notice's DMS to 6 decimals), and `area_en` as one short English line (e.g. `Aichi, Gifu, Fukui, Ishikawa, Toyama`).
- Produces: `zone_rules.csv` with columns `pref_code,muni_code,lat_min,lat_max,lon_min,lon_max,zone,note`. The first matching row wins. A blank `muni_code` means the whole prefecture. Blank bounds mean unbounded. A municipality override is a row with `muni_code` = N03_007 (5 digits). A geographic split is a row with bounds (Tokyo south of 28°N, Okinawa by longitude, Kagoshima islands per zone I's text). Put specific rows before prefecture defaults. The first line of the file is a comment `# source: <GSI URL>`.

- [ ] **Step 1: Read the official text.** Read `scriptum machinae/参照URL.md` in the Obsidian vault for a GSI URL. Otherwise use `https://www.gsi.go.jp/sokuchikijun/jpc.html` and fetch it. Record the URL. If you add a new one, update `参照URL.md`.

- [ ] **Step 2: Write the failing test** `test_tables.py` (`unittest`, the style of `html_src/tests/test_build.py`):

```python
def test_zones_has_19_rows_with_epsg_formula(self):
    rows = load_zones()
    self.assertEqual([r["zone"] for r in rows], list(range(1, 20)))
    for r in rows:
        self.assertEqual(r["epsg"], 6668 + r["zone"])
        self.assertEqual(r["epsg_jgd2000"], 2442 + r["zone"])
def test_zone_vii_origin(self):
    z = load_zones()[6]
    self.assertAlmostEqual(z["origin_lat"], 36.0, places=6)
    self.assertAlmostEqual(z["origin_lon"], 137 + 10 / 60, places=6)
def test_every_prefecture_has_a_default_rule(self):
    # pref_code 01..47 each have a row with blank muni_code and blank bounds
def test_split_prefectures_have_specific_rows(self):
    # pref 01 (Hokkaido) has muni rows for zones 11, 12, 13 only
    # pref 13 (Tokyo) has bounded rows for zones 14, 18, 19
    # pref 47 (Okinawa) has rows for zones 15, 16, 17
    # pref 46 (Kagoshima) has rows for zones 1 and 2
def test_rules_cite_source(self):
    # first line of zone_rules.csv starts with "# source: https://"
```

`load_zones()` / `load_rules()` live in `prep.py` (Task 2). For this task, put the minimal loaders there: `csv.DictReader` with int and float casts, skipping `#` lines.

- [ ] **Step 3: Run** `python3 -m unittest discover -s 2026/qgis/jgd_zones/src/tests -v`. Expected: FAIL (files missing).

- [ ] **Step 4: Fill both CSVs from the official text.** Hokkaido is split by municipality: take every Hokkaido N03_007 code from the N03 data downloaded in Task 2, step 1 (do that download now if needed), and assign each to XI, XII or XIII per the notice. Any municipality you cannot place: stop and report. Do not guess.

- [ ] **Step 5: Run the tests.** Expected: PASS.

- [ ] **Step 6: Commit** — `git add 2026/qgis/jgd_zones/src/{zones,zone_rules}.csv 2026/qgis/jgd_zones/src/prep.py 2026/qgis/jgd_zones/src/tests/test_tables.py` and commit with the message `Add JGD2011 zone tables from the official notice`.

### Task 2: Prep — zone polygons and place list

**Files:**
- Create/extend: `2026/qgis/jgd_zones/src/prep.py`
- Create: `2026/qgis/jgd_zones/src/data/zones.geojson`, `2026/qgis/jgd_zones/src/data/places.json` (generated, committed)
- Modify: `.gitignore` (add `2026/qgis/jgd_zones/src/.cache/`)
- Test: `2026/qgis/jgd_zones/src/tests/test_prep.py`

**Interfaces:**
- Consumes: `load_zones()`, `load_rules()` from Task 1.
- Produces, in `prep.py`:
  - `ring_centroid(geometry: dict) -> tuple[float, float]` — (lon, lat) of the largest outer ring's area-weighted centroid. Fall back to the first vertex for degenerate rings.
  - `assign_zone(pref_code: str, muni_code: str, lon: float, lat: float, rules: list[dict]) -> int | None` — first match wins.
  - `fold(name: str) -> str` — lower-case, NFKD with combining marks stripped (`Ōsaka` → `osaka`), drops `-shi`/`-ku`/`-machi`/`-cho`/`-mura`/`-son`/`-gun` suffixes and the characters `-` and space.
  - `place_rows(geonames_lines: Iterable[str], n03_features: list[dict]) -> list[list]` — `[display_name, folded_key, lat, lon]` with lat/lon rounded to 4 decimals and duplicates (same folded key within 0.05°) removed. GeoNames keeps feature class A with codes ADM1, ADM2; class P with population ≥ `POP_MIN`; class T with codes ISL, ISLS. N03 gives one point per N03_007, as `N03_001 + (N03_003 or '') + N03_004`, with its `ring_centroid` over that municipality's largest feature.
  - `main()` — runs the pipeline below.
- Produces, data files: `zones.geojson`, a FeatureCollection of 19 features, `properties: {"zone": int}`, coordinates at 4 decimals. `places.json`, a JSON array of `place_rows` rows.

- [ ] **Step 1: Download into `.cache/`.** N03 nationwide 2025: check the URL on the KSJ N03 page (`https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html`). GeoNames: `https://download.geonames.org/export/dump/JP.zip`. Unzip each into its own new directory.

- [ ] **Step 2: Write the failing tests** in `test_prep.py`, using a synthetic rules list (no download needed):

```python
def test_assign_zone_prefecture_default(self):       # ("23","23101",136.9,35.2) -> 7
def test_assign_zone_muni_override_wins(self):       # Hokkaido muni code row beats pref default
def test_assign_zone_bounds(self):                    # Tokyo (13): 142.19,27.09 -> 14; 136.08,20.42 -> 18; 153.98,24.29 -> 19; 139.7,35.69 -> 9
def test_assign_zone_unknown_pref_is_none(self):
def test_ring_centroid_square(self):                  # unit square at (10,20) -> (10.5, 20.5)
def test_ring_centroid_multipolygon_uses_largest(self):
def test_fold(self):                                  # "Ōsaka-shi" -> "osaka"; "大阪市" stays "大阪市"
def test_place_rows_filters_and_dedupes(self):        # PPL pop 50 dropped when POP_MIN=1000; ISL kept; same key 0.01° apart -> one row
```

- [ ] **Step 3: Run** `python3 -m unittest discover -s 2026/qgis/jgd_zones/src/tests -v`. Expected: the new tests FAIL.

- [ ] **Step 4: Implement the functions.** Then implement `main()`. It writes stage files to `.cache/`:
  1. `npx -y mapshaper@0.6.102 <N03 shp> -simplify 5% keep-shapes -o .cache/n03_simpl.json format=geojson precision=0.0001`. This shrinks the data before Python reads it.
  2. Python: for each feature, take `ring_centroid`, then `assign_zone(N03_007[:2], N03_007, …)`. Raise `ValueError` listing every feature with `None` (sea-only features with empty N03_007 are dropped first, counted, and printed). Write `.cache/n03_zoned.json` with a `zone` property only.
  3. `mapshaper .cache/n03_zoned.json -dissolve zone -simplify <PCT> keep-shapes -o data/zones.geojson format=geojson precision=0.0001`. Start with `PCT=1%`. Raise it while the file stays ≤ 1.5 MB. Choose by eye at zoom 10 around Hokkaido's zone lines.
  4. `place_rows(...)` → `data/places.json` (compact separators). Pick `POP_MIN` so the file is 200–300 KB. Print the row count and size.
  5. Write `data/meta.json`: `{"n03_edition": "2025-01-01", "geonames_downloaded": "<mtime date of JP.zip>"}`.

- [ ] **Step 5: Run the tests.** Expected: PASS. Run `python3 -I 2026/qgis/jgd_zones/src/prep.py`. Expected: it prints no unzoned features, 19 zones, and file sizes inside the limits.

- [ ] **Step 6: Commit** `prep.py`, `test_prep.py`, `data/`, `.gitignore` with the message `Prepare nationwide JGD2011 zone polygons and place list`.

### Task 3: Browser lookup logic

**Files:**
- Create: `2026/qgis/jgd_zones/src/lookup.js` (UMD like `html_src/classify.js`: `module.exports` under Node, `window.Lookup` in the browser)
- Create: `2026/qgis/jgd_zones/src/vendor/proj4/proj4.js` (proj4js 2.12.1 from cdnjs, unmodified)
- Test: `2026/qgis/jgd_zones/src/tests/lookup.test.mjs`

**Interfaces:**
- Consumes: `data/zones.geojson`, `data/places.json`, `zones.csv` (passed in as plain objects by the caller).
- Produces:
  - `zoneAt(lat: number, lon: number, zonesGeo: FeatureCollection) -> number | null` — ray-casting point-in-polygon with holes. Bbox prefilter per feature.
  - `parseLatLon(text: string) -> [lat, lon] | null` — accepts `35.19, 136.97`, `35.19 136.97`, `35.19°N 136.97°E`, and the swapped order. A pair is valid when lat ∈ [20, 46] and lon ∈ [122, 154]. If only the swapped order is valid, swap it.
  - `search(places: Array, query: string, limit = 8) -> Array<{name, lat, lon}>` — folds the query with the same rules as `prep.fold` (port it). Prefix matches rank before substring matches, then shorter names first.
  - `toPlane(lat, lon, zone: {zone, origin_lat, origin_lon}) -> {x: number, y: number}` — metres via proj4: `+proj=tmerc +lat_0=<origin_lat> +lon_0=<origin_lon> +k=0.9999 +x_0=0 +y_0=0 +ellps=GRS80 +units=m`. Return `x` = northing and `y` = easting (the Japanese convention).

- [ ] **Step 1: Write the failing tests**, including real-data samples that read `../data/zones.geojson`:

```js
const SAMPLES = [ // [label, lat, lon, zone] — confirm each against the official text before relying on it
  ["Moriyama, Nagoya", 35.203, 136.977, 7], ["Sapporo", 43.062, 141.354, 12],
  ["Hakodate", 41.769, 140.729, 11], ["Kushiro", 42.985, 144.381, 13],
  ["Shinjuku", 35.690, 139.700, 9], ["Hachijojima", 33.110, 139.790, 9],
  ["Chichijima", 27.094, 142.191, 14], ["Okinotorishima", 20.425, 136.081, 18],
  ["Minamitorishima", 24.287, 153.981, 19], ["Naha", 26.212, 127.681, 15],
  ["Ishigaki", 24.340, 124.156, 16], ["Minamidaito", 25.846, 131.247, 17],
  ["Nagasaki", 32.750, 129.878, 1], ["Kagoshima city", 31.596, 130.557, 2],
  ["Niigata", 37.916, 139.036, 8],
];
test("sample points land in the expected zone", ...);   // zoneAt for each
test("open sea is no zone", ...);                       // zoneAt(35.0, 150.0) === null
test("parseLatLon handles order and symbols", ...);     // "136.97, 35.19" -> [35.19,136.97]; "35.19°N, 136.97°E"; "abc" -> null; "0, 0" -> null
test("search finds Osaka in four spellings", ...);      // "Ōsaka","osaka","Osaka-shi","大阪" each return a row whose name contains Osaka or 大阪
test("toPlane at the origin is 0,0", ...);              // zone VII origin -> |x|,|y| < 0.001
test("toPlane matches PROJ for Nagoya Station", ...);   // EPSG:6675 for 35.170915,136.881537: x,y within 0.01 m of the values from
                                                        // /Applications/QGIS.app/Contents/MacOS/cs2cs EPSG:6668 EPSG:6675 (run once, paste the numbers)
```

Also add two near-boundary samples. Pick one point about 2 km inside each side of the Gifu/Nagano border (zone VII / VIII) and check they still land correctly. If they fail, raise the simplify percentage in Task 2.

- [ ] **Step 2: Run** `node --test 2026/qgis/jgd_zones/src/tests/`. Expected: FAIL.

- [ ] **Step 3: Implement `lookup.js` and vendor proj4.**

- [ ] **Step 4: Run** `node --test 2026/qgis/jgd_zones/src/tests/`. Expected: PASS. If a sample fails, check the official text first, then the rules. Never adjust a sample to match the output.

- [ ] **Step 5: Commit** with the message `Add browser zone lookup, coordinate parsing, search and X/Y`.

### Task 4: Page, build and explainer

**Files:**
- Create: `2026/qgis/jgd_zones/src/build.py`, `template.html`, `style.css` (start from `html_src/style.css`, trimmed), `app.js`, `content/explainer.html`
- Copy: `html_src/vendor/leaflet/` → `2026/qgis/jgd_zones/src/vendor/leaflet/`
- Output: `2026/qgis/jgd_zones/index.html`
- Test: `2026/qgis/jgd_zones/src/tests/test_build.py`

**Interfaces:**
- Consumes: `lookup.js` (`window.Lookup`), `data/*.json`, `zones.csv`.
- Produces: `build.assemble(src_dir: Path, updated: datetime.date) -> str` and `main()`, which writes `../index.html` with `updated = date.today()`. The page shows "Last updated: YYYY-MM-DD" under the title and in the footer, next to the data editions (N03 2025-01-01, GeoNames download date recorded by `prep.py` in `data/places.json`'s sibling `data/meta.json` as `{"geonames_downloaded": "YYYY-MM-DD"}`). The `render()` placeholder pattern is copied from `html_src/build.py`: unreplaced placeholders raise. Data is inlined as `<script type="application/json" id="zone-data">` with `</` escaped.

Page layout, top to bottom:
1. Title "Which coordinate system for my area? — Japan's plane rectangular zones (JGD2011)".
2. Search box, coordinate box and "My location" button.
3. Map (Leaflet, GSI pale tiles, 19 zones in distinguishable colours with Roman-numeral labels at a point inside each zone).
4. Result card: zone `VII (系VII)`, `EPSG:6675`, origin, clicked lat/lon, X/Y, a "Copy EPSG" button, and the caution line "Zone lines are simplified; within a few hundred metres of a line, check the municipality in the table below."
5. A zone table listing all 19 zones (zone, EPSG, JGD2000 EPSG, origin, area).
6. Explainer.
7. Sources and licences.

The explainer (`content/explainer.html`) covers:
- geographic (WGS84 / JGD2011 lat-lon, EPSG:4326 / 6668, degrees) vs projected (metres)
- why metres matter for buffer, distance and area in QGIS
- X = north, Y = east in Japan, and the opposite of the usual x/y
- JGD2000 codes, so old data is recognisable
- when UTM (EPSG:6688–6692) is the better choice: areas spanning several zones; one line only
- "Set it in QGIS": Project → Properties → CRS; Export → Save Features As… with a CRS; checking a layer's CRS in Layer Properties → Information
- the worked example: Moriyama → zone VII, EPSG:6675

- [ ] **Step 1: Write the failing tests** in `test_build.py`: `test_no_placeholders_left`, `test_inlines_zone_data_and_scripts` (contains `id="zone-data"`, `L.map`, `proj4`), `test_lists_all_19_epsg_codes` (each 6669–6687 appears), `test_attribution_present` (contains `国土数値情報`, `GeoNames`, `CC BY 4.0`, and the GSI source URL from `zone_rules.csv`), `test_size_limit` (output ≤ 2.5 MB), `test_last_updated_shown` (`assemble(SRC, date(2026, 11, 18))` contains `Last updated: 2026-11-18` and `2025-01-01`), `test_no_external_scripts` (no `<script src=`).

- [ ] **Step 2: Run** `python3 -m unittest discover -s 2026/qgis/jgd_zones/src/tests -v`. Expected: the build tests FAIL.

- [ ] **Step 3: Implement** `build.py`, `template.html`, `style.css`, `app.js` and the explainer. `app.js` wires the UI to `Lookup`. A geolocation error shows "Location not available — click the map or type a place instead." A tile error leaves the zones drawn on the plain background (as `html_src/app.js` does).

- [ ] **Step 4: Run** the Python and Node suites. Expected: all PASS. Run `python3 2026/qgis/jgd_zones/src/build.py`.

- [ ] **Step 5: Check it in a browser** over local HTTP (`python3 -m http.server` from the repo root, `/2026/qgis/jgd_zones/`). Check that:
  - clicking Moriyama shows VII / EPSG:6675
  - searching "Chichijima" flies there and shows XIV
  - pasting `136.97, 35.19` works
  - the result card's X/Y matches the cs2cs value from Task 3

- [ ] **Step 6: Manual Review Focus checks:**
  - at 375 px, no horizontal page scroll
  - with tiles blocked (offline devtools), the zones still render
  - with geolocation denied, the message shows
  - a click on the sea says no zone

- [ ] **Step 7: Commit** `src/` and `index.html` with the message `Add JGD2011 zone finder page`. Ask the user before pushing.
