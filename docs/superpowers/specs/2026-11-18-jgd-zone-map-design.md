# JGD2011 plane rectangular zone finder — design

Date: 2026-11-18
Location: `2026/qgis/jgd_zones/`

## Intent

Students and researchers who want to set up a QGIS project for a place in Japan often do not know which plane rectangular coordinate zone (系 I–XIX) or EPSG code to use, and a quick Google search does not give a map that answers it. This page answers "which zone and EPSG code does this place use?" in a few seconds, and explains how plane rectangular coordinates differ from WGS84 for beginners.

Audience: beginners in GIS (students, researchers), reading in English. Page language: English; Japanese place and zone names (e.g. 系VII, 愛知県) shown alongside where helpful.

## Goals

- Nationwide interactive map with the 19 zones drawn at municipality precision, following the official zone table (平成14年国土交通省告示第9号).
- Click on the map, or search by place name, and get: zone number (Roman and 系 form), EPSG code for JGD2011 (EPSG:6669–6687), the zone's origin (lat/lon), and the WGS84 lat/lon of the clicked point plus its X/Y in that zone.
- Short explainer section: geographic (WGS84, EPSG:4326, degrees) vs projected (JGD2011 plane rectangular, metres); why metres matter for buffers, distances and areas; X is northing and Y is easting in the Japanese convention; JGD2000 vs JGD2011 codes (EPSG:2443–2461) in one line so users recognise old data.
- "How to set it in QGIS" box: project CRS, reprojecting a layer, checking the CRS of a layer.
- "Last updated" date shown on the page (under the title and in the footer), with the data editions used (N03 edition, GeoNames download date).
- The worked example from the session: Moriyama, Nagoya → zone VII, EPSG:6675.

## Non-goals

- Not a general coordinate converter or batch tool.
- No UTM zone finder (one-line mention only).
- Not part of the QGIS session build; it does not change `qgis_session.html`.

## Anti-goals

- A zone shown wrongly for any area. The tricky places (Hokkaido's three zones, Tokyo's islands, Kagoshima and Okinawa islands) are the reason the page exists.
- A page too heavy to open on a phone or a slow connection.

## Constraints

- Zone assignment taken from the official GSI source, never from memory; source URL cited on the page.
- Boundaries from 国土数値情報 N03 (nationwide, latest year), attribution cited. Place names from GeoNames (CC BY 4.0), attribution cited.
- Hosted on GitHub Pages from this repo, like the session handout.
- Reuse the session's stack: Leaflet (vendored), GSI pale tiles, single-file HTML assembled by a Python build script. The map must still show the zones when the tiles fail to load (offline).
- Target size of embedded zone geometry: about 1–2 MB.

## Approaches

1. **Municipality-level nationwide zone map** — chosen. Accurate in exactly the confusing areas; costs a one-off data-prep step.
2. Prefecture-level with exception notes — easy, but wrong where users most need help. Rejected.
3. Origins only, no boundaries — cannot answer "which zone is this place". Rejected.

## Decided

- Approach 1, English, under `2026/qgis/jgd_zones/` with its own `src/` (build script, CSS, JS, zone table), copying, not importing, from `html_src/`.
- Output `2026/qgis/jgd_zones/index.html`.

## Left to the builder

- Data prep: download N03 nationwide, join a municipality → zone table built from the official notice (zones split by municipality in Hokkaido, Tokyo, Kagoshima, Okinawa; whole prefecture elsewhere), dissolve by zone, simplify (mapshaper or ogr2ogr), and check that nothing is left with no zone. Keep the zone table as a reviewed CSV in `src/`.
- Remote islands outside municipalities (e.g. Okinotorishima, Minamitorishima): handle via the notice's text; add point markers if polygons are too small to click.
- Place search, fully offline (no runtime API): an embedded list of named points — N03 municipality names in Japanese (representative point per municipality) plus GeoNames `JP.zip` (CC BY 4.0, attribution on the page) for romanised names: ADM1/ADM2, populated places above a population threshold, and islands. The zone for a search hit is found by point-in-polygon against the zone layer in the browser, so no name join between N03 and GeoNames is needed. Pick the filter so the list stays around 200–300 KB. Also: paste "lat, lon" and a "my location" button.
  - Rejected: GSI address search (`msearch.gsi.go.jp`) — no terms of use cover it, GSI says it may change without notice, and it is backed by an experimental CSIS service (see zenn.dev/ohsun/articles/313bfe4b976274).
- X/Y for the clicked point: proj4js (vendored) with the zone's parameters, or a small Gauss–Krüger implementation; verify against QGIS for a few points.
- Colour scheme for 19 zones, legend, mobile layout (375 px, no horizontal page scroll).
- Tests in the style of the existing ones: zone table coverage, build placeholders, sample-point lookups (e.g. Moriyama → VII, Sapporo → XII, Naha → XV, Chichijima → XIV).
