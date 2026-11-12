# Data for the QGIS session

**Participants only need two files** for the hands-on part (Task 1):

- `aichi_admin_fields2025.geojson`
- `aichi_permanent_residents_202512.csv`

Everything else listed here is for the Task 2 tour and the Task 3 slides, or for rebuilding the HTML handout (`2026/qgis/html_src/build.py`). Other files in this folder are working files; they are excluded from git by `.gitignore` and are not needed.

## Task 1: foreign permanent residents in Aichi

| File | What it is | Source, licence, date |
|---|---|---|
| `aichi_admin_fields2025.geojson` | Municipality boundaries of Aichi (1,033 polygons; key `N03_007`) | MLIT National Land Numerical Information, Administrative Areas (N03-2025), CC BY 4.0, reference date 1 Jan 2025 |
| `aichi_permanent_residents_202512.csv` | Permanent residents per municipality: `city_code`, `municipality`, `pr_all`, `pr_brazil`, `pr_korea` (69 rows) | Statistics on Foreign Residents (在留外国人統計), e-Stat, December 2025. Municipality codes: Ministry of Internal Affairs and Communications (総務省) |

## Task 2: a 10-minute walk from Kawashima Hospital (川島病院)

| File | What it is |
|---|---|
| `moriyama_admin_field.gpkg` | Moriyama Ward boundary (from N03) |
| `moriyama_hospital_test.gpkg` | The test hospital, one point (from MLIT P04) |
| `moriyama_service_area_lines.gpkg` | Roads reachable on foot within 10 minutes (OpenStreetMap network, 4 km/h) |
| `moriyama_test_10min_polygon_clean.gpkg` | The 10-minute reach as an area |
| `moriyama_test_10min_intersection_with_population_clean.gpkg` | The 20 population-grid pieces inside the reach, with the estimated population `pop_est` |
| `moriyama_mesh_3km.gpkg` | 250 m population grid around the ward (2,745 cells) |

## Task 3: walking access in Moriyama Ward

| File | What it is |
|---|---|
| `moriyama_buffer_hospitals.gpkg` | The 41 hospitals in or within 3 km of the ward |
| `moriyama_hospitals.gpkg` | The 8 hospitals inside the ward |
| `moriyama_analysis_B_10min_coverage.gpkg`, `..._20min_...`, `..._30min_...` | Merged walking coverage per time, clipped to the ward |
| `moriyama_analysis_B_accessibility.csv` | Shares of residents within reach: 17.90% / 46.61% / 62.60% |
| `moriyama_hospital_distance_30min_coverage.png` | Static map of the 30-minute coverage |

The Task 2 and Task 3 numbers come from different methods and must not be compared.

## Sources and licences

- **MLIT National Land Numerical Information** (国土数値情報): administrative areas N03-2025 (CC BY 4.0) and medical institutions P04 (https://nlftp.mlit.go.jp/ksj/).
- **e-Stat**: 2020 Census 250 m population grid, and Statistics on Foreign Residents (https://www.e-stat.go.jp/).
- **OpenStreetMap contributors**: road network and walking reach, ODbL (https://www.openstreetmap.org/copyright).
- **GSI Japan** (国土地理院): base map tiles in the HTML handout and the Task 1 instructions (https://maps.gsi.go.jp/development/ichiran.html).
- Population values and walking reach are **estimates** (area apportioning, 30 m road buffer). They have not been independently validated.
