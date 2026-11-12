# Visualise the numbers & statistics on Maps - Visualisation with QGIS

## Materials

### Base maps and map data
- [Geospatial Information Authority of Japan (GSI) tiles (国土地理院タイル)](https://maps.gsi.go.jp/development/ichiran.html)
- [OpenStreetMap raster tile providers](https://wiki.openstreetmap.org/wiki/Raster_tile_providers)
- [National Land Numerical Information: Administrative Areas, N03-2025 (国土数値情報 行政区域データ)](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html) – municipality polygons, CC BY 4.0, reference date 2025-01-01, one GeoJSON per prefecture

### Data
- [Statistics on Foreign Residents (在留外国人統計), December 2025, e-Stat](https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00250012&tstat=000001018034&cycle=1&year=20250&month=24101212&tclass1=000001060399&result_back=1&tclass2val=0)
- [Codes for prefectures and municipalities (都道府県コード及び市区町村コード), Ministry of Internal Affairs and Communications](https://www.soumu.go.jp/denshijiti/code.html) – the same 5-digit codes are used in the polygon data

The class table `./assets/aichi_permanent_residents_202512.csv` was extracted from the e-Stat table (Aichi Prefecture, one row per municipality or ward of Nagoya):

| Column | Meaning |
|---|---|
| `city_code` | 5-digit municipality code (2 digits prefecture + 3 digits municipality); join key |
| `municipality` | name |
| `pr_all` | all foreign residents with the status "permanent resident" (永住者) |
| `pr_brazil` | of these, Brazilian nationals |
| `pr_korea` | of these, South Korean nationals (without "special permanent residents", 特別永住者) |

Cleaning done before class: thousands separators (`4’182`) removed, the total row removed, and the two municipalities missing in the Korea table (東栄町, 豊根村) set to 0.

## Example walkthrough

### Adding a base map

1. Click QGIS > Layer > Add Layer > Add XYZ Layer => a pop-up window opens.
2. In the pop-up window "XYZ Connections", click "New" => a second pop-up window appears.
3. In the second pop-up window, enter the details for, e.g., the GSI standard tiles:

```
Name: any name you like
URL: https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png (as given on the website)
Minimum zoom level: 5
```

4. Save with OK. You return to the first pop-up window.
5. Select the newly added tile connection from the drop-down menu and click "Add". The layer is added.

### Adding vector data
1. Open the [N03-2025 page](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2025.html) and download the GeoJSON of Aichi Prefecture (愛知県, code 23).
2. Unzip it and drag and drop the `.geojson` file into QGIS to add it as a layer.
3. Open the attribute table. The column `N03_007` holds the 5-digit municipality code. One municipality can consist of several polygons, so the file has more features than municipalities.

### Linking statistical data to map features
1. Drag and drop `./assets/aichi_permanent_residents_202512.csv` into QGIS.
2. Right-click the polygon layer > Properties > "Joins" > "+".
3. Join layer: the CSV layer. Join field: `city_code`. Target field: `N03_007`. Click OK.
4. Open the attribute table of the polygon layer: the columns `pr_all`, `pr_brazil` and `pr_korea` are now attached. Polygons without a match (e.g. the unassigned area `23000`) stay empty (NULL).

### Visualizing the statistics
1. Right-click the layer > Properties.
2. Symbology > select "Graduated" at the top.
3. Enter `pr_brazil` as the "Value". Choose a colour ramp and the number of classes, then click "Classify".
4. Change the "Mode" (Equal Interval, Equal Count (Quantile), Natural Breaks (Jenks), ...) and compare the maps.

### Exporting the visualization for your own work
1. Select "New Print Layout".
2. Add the map, legend, labels, etc. to the canvas.
3. Export the result as an image.

## Pitfalls when visualizing counts

See the slides (`qgis_for_socialsciences_en_slides.md`): classification, counts vs. rates, small numbers, area bias, missing vs. zero, category definitions.

The earlier walkthrough with the 2026 election data (electoral districts of Aichi, decimal comma conversion) is kept in the git history (`ab61f5d`).
