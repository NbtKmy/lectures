# Handling GeoJSON

## What is GeoJSON?

> GeoJSON is an open standard format designed for representing simple geographical features, along with their non-spatial attributes. It is based on the JSON format. ...
> The coordinate reference system for all GeoJSON coordinates is a geographic coordinate reference system, using the World Geodetic System 1984 (WGS 84) [WGS84] datum, with longitude and latitude units of decimal degrees.

([Wikipedia](https://en.wikipedia.org/wiki/GeoJSON))

In short, a GeoJSON file normally uses the geographic coordinate system WGS84. WGS84 is well suited for displaying features on online maps. To calculate distances or areas, however, the data should be converted to a projected coordinate system.

Note that the current specification ([RFC 7946](https://datatracker.ietf.org/doc/html/rfc7946)) allows only WGS84. The `crs` member, which older GeoJSON files used to declare other coordinate systems, was removed from the specification because it caused interoperability problems. QGIS still reads a `crs` member, but other software (e.g. web mapping libraries) may ignore it and misplace the data. A good rule of thumb:

- For web maps and data exchange, keep the file in WGS84.
- For distance and area calculations, use a projected CRS, and save the result as GeoPackage if possible.

## Coordinate Reference System (CRS)

- **Geographic coordinate system:** A system that represents a position by latitude and longitude (degrees), modelling the Earth as an ellipsoid (e.g. WGS84, as used by GPS).
- **Projected coordinate system:** A system that represents a position by lengths (e.g. metres), obtained by projecting the curved surface of the Earth onto a plane (e.g. Web Mercator, used in web maps, and the Japan Plane Rectangular Coordinate System, used in land surveying).

The data used in this lecture (the national land numerical information "Medical Institutions" data, `P04-20_23.geojson`) is declared as EPSG:6668 (JGD2011, the Japanese geodetic datum). For practical purposes, JGD2011 and WGS84 give almost identical positions, so such a file can be treated as WGS84 on a map.

## How to change the CRS in QGIS

1. Open the GeoJSON file in QGIS (just drag the file into QGIS). The layer appears in the Layers panel.
2. Right-click the layer. A context menu opens.
3. Choose **Export ▸ Save Features As…**. The "Save Vector Layer as…" window opens.
4. In the **CRS** field, select **EPSG:6675 (JGD2011 / Japan Plane Rectangular CS VII)**, and save the file in GeoJSON or GeoPackage format.

EPSG:6675 is zone VII of the Japan Plane Rectangular Coordinate System, which covers Ishikawa, Toyama, Gifu and Aichi prefectures. For other prefectures, choose the zone that covers your area.

### Example: before and after

The file name differs because the layer was saved under a new name.

Before (`P04-20_23.geojson`):

```json
{
"type": "FeatureCollection",
"name": "P04-20_23",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::6668" } },
"features": [
{ "type": "Feature", "properties": { ... }, "geometry": { "type": "Point", "coordinates": [ 137.132363899999007, 35.1271412 ] } },
...
]
}
```

After (`aichi_medical.geojson`):

```json
{
"type": "FeatureCollection",
"name": "aichi_medical",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::6675" } },
"features": [
{ "type": "Feature", "properties": { ... }, "geometry": { "type": "Point", "coordinates": [ -3126.272796160367307, -96834.279928898147773 ] } },
...
]
}
```

The coordinates are now in metres from the origin of zone VII (latitude 36°N, longitude 137°10′E): this point lies about 3.1 km west and 96.8 km south of it.
