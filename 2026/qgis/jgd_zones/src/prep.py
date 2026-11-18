"""N03 boundaries + GeoNames -> zone polygons and place list for the JGD2011 zone finder.

    python3 -I 2026/qgis/jgd_zones/src/prep.py
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import unicodedata
from collections.abc import Iterable
from datetime import date
from pathlib import Path

SRC = Path(__file__).resolve().parent
ZONES_CSV = SRC / "zones.csv"
RULES_CSV = SRC / "zone_rules.csv"
BOUNDS = ("lat_min", "lat_max", "lon_min", "lon_max")
POP_MIN = 10000
SUFFIX = re.compile(r"[-\s](shi|ku|machi|cho|mura|son|gun)$")


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


def load_zones(path: Path = ZONES_CSV) -> list[dict]:
    rows = _rows(path)
    for r in rows:
        for k in ("zone", "epsg", "epsg_jgd2000"):
            r[k] = int(r[k])
        for k in ("origin_lat", "origin_lon"):
            r[k] = float(r[k])
    return rows


def load_rules(path: Path = RULES_CSV) -> list[dict]:
    """Zone rules in file order; the first matching row wins."""
    rows = _rows(path)
    for r in rows:
        r["zone"] = int(r["zone"])
        for k in BOUNDS:
            r[k] = float(r[k]) if r[k] else None
    return rows


def assign_zone(pref_code: str, muni_code: str, lon: float, lat: float, rules: list[dict]) -> int | None:
    """Zone of a point in a municipality; bounds are inclusive, the first matching rule wins."""
    for r in rules:
        if r["pref_code"] != pref_code or (r["muni_code"] and r["muni_code"] != muni_code):
            continue
        if r["lat_min"] is not None and lat < r["lat_min"]:
            continue
        if r["lat_max"] is not None and lat > r["lat_max"]:
            continue
        if r["lon_min"] is not None and lon < r["lon_min"]:
            continue
        if r["lon_max"] is not None and lon > r["lon_max"]:
            continue
        return r["zone"]
    return None


def _ring_area_centroid(ring: list) -> tuple[float, float, float]:
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a /= 2
    if abs(a) < 1e-15:
        return 0.0, ring[0][0], ring[0][1]
    return abs(a), cx / (6 * a), cy / (6 * a)


def ring_centroid(geometry: dict) -> tuple[float, float]:
    """(lon, lat) of the area centroid of the largest outer ring."""
    polys = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    best = max((_ring_area_centroid(p[0]) for p in polys), key=lambda t: t[0])
    return best[1], best[2]


def point_in_ring(x: float, y: float, ring: list) -> bool:
    inside = False
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def inner_point(geometry: dict) -> tuple[float, float]:
    """(lon, lat) inside the largest outer ring: its centroid, or else the middle of the
    widest inside stretch of the horizontal line through the centroid."""
    polys = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    ring = max((p[0] for p in polys), key=lambda r: _ring_area_centroid(r)[0])
    _, cx, cy = _ring_area_centroid(ring)
    if point_in_ring(cx, cy, ring):
        return cx, cy
    xs = sorted(
        x0 + (cy - y0) * (x1 - x0) / (y1 - y0)
        for (x0, y0), (x1, y1) in zip(ring, ring[1:])
        if (y0 > cy) != (y1 > cy)
    )
    pairs = list(zip(xs[::2], xs[1::2]))
    if not pairs:
        return ring[0][0], ring[0][1]
    a, b = max(pairs, key=lambda ab: ab[1] - ab[0])
    return (a + b) / 2, cy


def geometry_area(geometry: dict) -> float:
    polys = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    return sum(_ring_area_centroid(p[0])[0] for p in polys)


def fold(name: str) -> str:
    """Search key: lower case, macrons dropped, municipal suffix and separators removed."""
    s = unicodedata.normalize("NFKD", name.strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = SUFFIX.sub("", s)
    return re.sub(r"[-\s']", "", s)


GEONAMES_KEEP = {("A", "ADM1"), ("A", "ADM2"), ("T", "ISL"), ("T", "ISLS")}


def place_rows(geonames_lines: Iterable[str], n03_features: list[dict], pop_min: int = POP_MIN) -> list[list]:
    """[display_name, key, lat, lon] rows: N03 municipalities first, then GeoNames names."""
    largest: dict[str, dict] = {}
    for f in n03_features:
        code = f["properties"].get("N03_007")
        if not code or not f["geometry"] or not f["geometry"]["coordinates"]:
            continue
        area = geometry_area(f["geometry"])
        if code not in largest or area > largest[code][0]:
            largest[code] = (area, f)
    candidates = []
    for _, f in largest.values():
        p = f["properties"]
        name = "".join(p.get(k) or "" for k in ("N03_001", "N03_003", "N03_004", "N03_005"))
        lon, lat = inner_point(f["geometry"])
        candidates.append((name, lat, lon))
    for line in geonames_lines:
        c = line.rstrip("\n").split("\t")
        if len(c) < 15:
            continue
        fclass, fcode = c[6], c[7]
        keep = (fclass, fcode) in GEONAMES_KEEP or (fclass == "P" and int(c[14] or 0) >= pop_min)
        if keep:
            candidates.append((c[1], float(c[4]), float(c[5])))
    rows: list[list] = []
    seen: dict[str, list[tuple[float, float]]] = {}
    for name, lat, lon in candidates:
        key = fold(name)
        lat, lon = round(lat, 4), round(lon, 4)
        if any(abs(lat - a) < 0.05 and abs(lon - b) < 0.05 for a, b in seen.get(key, [])):
            continue
        seen.setdefault(key, []).append((lat, lon))
        rows.append([name, key, lat, lon])
    return rows


NEAREST_DEG = 0.05  # about 5 km: offshore GeoNames points for islets and capes


def _seg_dist2(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx, dy = bx - ax, by - ay
    s = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return (ax + s * dx - px) ** 2 + (ay + s * dy - py) ** 2


def place_zones(rows: list[list], zoned_features: list[dict], cell: float = 0.1) -> list[list]:
    """Append each place's zone, from the detailed (undissolved) zoned pieces.

    A point inside a piece takes its zone; otherwise the zone of the nearest edge within
    NEAREST_DEG. Places with neither are dropped. The browser's simplified polygons miss
    small islands, so search hits rely on this zone instead.
    """
    pieces: dict[tuple[int, int], list] = {}
    edges: dict[tuple[int, int], list] = {}
    key = lambda x, y: (int(x // cell), int(y // cell))  # noqa: E731
    for f in zoned_features:
        zone, g = f["properties"]["zone"], f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            ring = poly[0]
            xs, ys = [v[0] for v in ring], [v[1] for v in ring]
            item = (min(xs), min(ys), max(xs), max(ys), ring, zone)
            for i in range(int(item[0] // cell), int(item[2] // cell) + 1):
                for j in range(int(item[1] // cell), int(item[3] // cell) + 1):
                    pieces.setdefault((i, j), []).append(item)
            for (ax, ay), (bx, by) in zip(ring, ring[1:]):
                for cellkey in {key(ax, ay), key(bx, by), key((ax + bx) / 2, (ay + by) / 2)}:
                    edges.setdefault(cellkey, []).append((ax, ay, bx, by, zone))
    out = []
    for name, k, lat, lon in rows:
        zone = next((z for x0, y0, x1, y1, ring, z in pieces.get(key(lon, lat), [])
                     if x0 <= lon <= x1 and y0 <= lat <= y1 and point_in_ring(lon, lat, ring)), None)
        if zone is None:
            ci, cj = key(lon, lat)
            near = [e for i in (ci - 1, ci, ci + 1) for j in (cj - 1, cj, cj + 1) for e in edges.get((i, j), [])]
            best = min(((_seg_dist2(lon, lat, *e[:4]), e[4]) for e in near), default=None)
            if best and best[0] <= NEAREST_DEG ** 2:
                zone = best[1]
        if zone is not None:
            out.append([name, k, lat, lon, zone])
    return out


CACHE = SRC / ".cache"
DATA = SRC / "data"
N03_SHP = CACHE / "n03" / "N03-20250101.shp"
N03_EDITION = "2025-01-01"
GEONAMES_TXT = CACHE / "geonames" / "JP.txt"
GEONAMES_ZIP = CACHE / "geonames" / "JP.zip"
MAPSHAPER = ["npx", "-y", "mapshaper@0.6.102"]
ZONE_SIMPLIFY = "15%"


def _mapshaper(*args: str) -> None:
    subprocess.run([*MAPSHAPER, *args], check=True)


def zone_features(n03: dict, rules: list[dict]) -> list[dict]:
    """N03 features with only a `zone` property; raises if any municipality gets no zone."""
    out, missing, dropped = [], [], 0
    for f in n03["features"]:
        code = f["properties"].get("N03_007")
        if not code or not f["geometry"] or not f["geometry"]["coordinates"]:
            dropped += 1
            continue
        lon, lat = inner_point(f["geometry"])
        zone = assign_zone(code[:2], code, lon, lat, rules)
        if zone is None:
            missing.append(code)
        out.append({"type": "Feature", "properties": {"zone": zone}, "geometry": f["geometry"]})
    if missing:
        raise ValueError(f"no zone for {len(missing)} features: {sorted(set(missing))[:20]}")
    print(f"zoned {len(out)} features, dropped {dropped} without a municipality code")
    return out


def add_labels(zones_fc: dict) -> None:
    """Give each zone a `label` [lat, lon] inside its largest part, for map labels and markers."""
    for f in zones_fc["features"]:
        lon, lat = inner_point(f["geometry"])
        f["properties"]["label"] = [round(lat, 4), round(lon, 4)]


def main() -> None:
    for src in (N03_SHP, GEONAMES_TXT):
        if not src.exists():
            raise FileNotFoundError(f"{src} (download step: see the plan, Task 2 step 1)")
    simpl = CACHE / "n03_simpl.json"
    _mapshaper(str(N03_SHP), "-simplify", "5%", "keep-shapes",
               "-o", str(simpl), "format=geojson", "precision=0.000001")
    n03 = json.loads(simpl.read_text(encoding="utf-8"))

    zoned = CACHE / "n03_zoned.json"
    zoned.write_text(json.dumps({"type": "FeatureCollection",
                                 "features": zone_features(n03, load_rules())}), encoding="utf-8")
    DATA.mkdir(exist_ok=True)
    zones_out = DATA / "zones.geojson"
    _mapshaper(str(zoned), "-dissolve", "zone", "-simplify", ZONE_SIMPLIFY, "keep-shapes",
               "-o", str(zones_out), "format=geojson", "precision=0.0001", "force")
    zones_geo = json.loads(zones_out.read_text(encoding="utf-8"))
    add_labels(zones_geo)
    zones_geo["features"].sort(key=lambda f: f["properties"]["zone"])
    zones_out.write_text(json.dumps(zones_geo, separators=(",", ":")), encoding="utf-8")
    print(f"zones.geojson: {len(zones_geo['features'])} zones, {zones_out.stat().st_size / 1e6:.2f} MB")

    with GEONAMES_TXT.open(encoding="utf-8") as f:
        rows = place_rows(f, n03["features"])
    zoned_fc = json.loads(zoned.read_text(encoding="utf-8"))
    placed = place_zones(rows, zoned_fc["features"])
    print(f"places: {len(rows) - len(placed)} dropped with no zone within {NEAREST_DEG}°")
    rows = placed
    places_out = DATA / "places.json"
    places_out.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"places.json: {len(rows)} rows, {places_out.stat().st_size / 1e3:.0f} KB")

    downloaded = date.fromtimestamp(GEONAMES_ZIP.stat().st_mtime).isoformat()
    (DATA / "meta.json").write_text(json.dumps({"n03_edition": N03_EDITION, "geonames_downloaded": downloaded}) + "\n",
                                    encoding="utf-8")


if __name__ == "__main__":
    main()
