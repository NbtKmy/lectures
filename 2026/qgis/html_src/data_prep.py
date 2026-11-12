"""GIS assets -> web-ready GeoJSON and stats for the QGIS session page."""
from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path

HTML_SRC = Path(__file__).resolve().parent
ASSETS = HTML_SRC.parents[1] / "assets"
CACHE = HTML_SRC / ".cache"

DEFAULT_OGR2OGR = "/Applications/QGIS.app/Contents/MacOS/ogr2ogr"
# The bundled ogr2ogr cannot find its PROJ/GDAL data outside of QGIS itself.
QGIS_RESOURCES = Path("/Applications/QGIS.app/Contents/Resources/qgis")


def _ogr_env() -> dict:
    env = dict(os.environ)
    for var, sub in (("PROJ_DATA", "proj"), ("PROJ_LIB", "proj"), ("GDAL_DATA", "gdal")):
        if var not in env and (QGIS_RESOURCES / sub).is_dir():
            env[var] = str(QGIS_RESOURCES / sub)
    return env


def ogr_to_geojson(
    src: Path,
    dest: Path,
    *,
    layer: str | None = None,
    simplify_deg: float = 0.0,
    precision: int = 5,
) -> dict:
    """Convert `src` to WGS84 GeoJSON at `dest` and return the parsed result."""
    src, dest = Path(src), Path(dest)
    if not src.exists():
        raise FileNotFoundError(src)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()  # ogr2ogr refuses to overwrite a GeoJSON

    cmd = [
        os.environ.get("OGR2OGR", DEFAULT_OGR2OGR),
        "-f", "GeoJSON",
        "-t_srs", "EPSG:4326",
        "-lco", f"COORDINATE_PRECISION={precision}",
    ]
    if simplify_deg:
        cmd += ["-simplify", str(simplify_deg)]
    cmd += [str(dest), str(src)]
    if layer:
        cmd.append(layer)

    result = subprocess.run(cmd, capture_output=True, text=True, env=_ogr_env())
    if result.returncode:
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"ogr2ogr failed ({result.returncode}): {result.stderr.strip()}")
    return json.loads(dest.read_text(encoding="utf-8"))


def _to_int(text: str | None) -> int | None:
    """Parse a CSV count such as "1,234"; blank means missing."""
    text = (text or "").replace(",", "").strip()
    return int(text) if text else None


def _feature_collection(features: list[dict]) -> dict:
    return {"type": "FeatureCollection", "features": features}


def build_task1(simplify_deg: float = 0.0001) -> dict:
    """Aichi municipalities joined with permanent-resident counts (Task 1 map)."""
    geo = ogr_to_geojson(
        ASSETS / "aichi_admin_fields2025.geojson",
        CACHE / "task1_aichi.geojson",
        simplify_deg=simplify_deg,
    )

    polygons: dict[str, list] = {}
    for feat in geo["features"]:
        code = feat["properties"]["N03_007"]
        geom = feat["geometry"]
        parts = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        polygons.setdefault(code, []).extend(parts)

    with open(ASSETS / "aichi_permanent_residents_202512.csv", encoding="utf-8-sig", newline="") as fh:
        rows = {r["city_code"]: r for r in csv.DictReader(fh)}

    features = []
    for code in sorted(polygons):
        row = rows.get(code)
        pr_all = _to_int(row["pr_all"]) if row else None
        pr_brazil = _to_int(row["pr_brazil"]) if row else None
        rate = round(pr_brazil / pr_all * 100, 2) if pr_all and pr_brazil is not None else None
        features.append({
            "type": "Feature",
            "properties": {
                "code": code,
                "name": row["municipality"] if row else "所属未定地",
                "pr_all": pr_all,
                "pr_brazil": pr_brazil,
                "rate_brazil": rate,
            },
            "geometry": {"type": "MultiPolygon", "coordinates": polygons[code]},
        })
    return _feature_collection(features)


def _keep(fc: dict, properties: dict | None = None) -> dict:
    """Return `fc` with each feature's properties replaced by `properties(feature)`."""
    feats = []
    for feat in fc["features"]:
        props = properties(feat["properties"]) if properties else {}
        feats.append({"type": "Feature", "properties": props, "geometry": feat["geometry"]})
    return _feature_collection(feats)


def build_task2() -> dict:
    """Kawashima Hospital 10-minute walking reach (Task 2 map)."""
    def load(name: str) -> dict:
        return ogr_to_geojson(ASSETS / f"{name}.gpkg", CACHE / f"task2_{name}.geojson")

    boundary = _keep(load("moriyama_admin_field"))
    hospital_src = load("moriyama_hospital_test")["features"][0]
    hospital = {
        "type": "Feature",
        "properties": {"name": "川島病院", "full_name": hospital_src["properties"]["P04_002"]},
        "geometry": hospital_src["geometry"],
    }
    service_area = _keep(load("moriyama_service_area_lines"))
    reach = _keep(load("moriyama_test_10min_polygon_clean"))
    mesh = _keep(
        load("moriyama_test_10min_intersection_with_population_clean"),
        lambda p: {"pop_est": round(float(p["pop_est"]), 2)},
    )
    total = round(sum(f["properties"]["pop_est"] for f in mesh["features"]), 1)
    return {
        "hospital": hospital,
        "boundary": boundary,
        "service_area": service_area,
        "reach": reach,
        "mesh": mesh,
        "summary": {
            "hospital_name": "川島病院",
            "total_pop_est": total,
            "mesh_count": len(mesh["features"]),
        },
    }


def build_task3(simplify_deg: float = 0.0002) -> dict:
    """Walking-access coverage at 10/20/30 minutes across 41 hospitals (Task 3 map)."""
    def load(name: str, **kw) -> dict:
        return ogr_to_geojson(ASSETS / f"{name}.gpkg", CACHE / f"task3_{name}.geojson", **kw)

    boundary = _keep(load("moriyama_admin_field"))
    hospitals = _keep(
        load("moriyama_buffer_hospitals"),
        lambda p: {"name": p["P04_002"]},
    )
    coverage = {
        m: _keep(load(f"moriyama_analysis_B_{m}min_coverage", simplify_deg=simplify_deg))
        for m in ("10", "20", "30")
    }

    stats = {}
    with open(ASSETS / "moriyama_analysis_B_accessibility.csv", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            stats[row["minutes"]] = {
                "total": float(row["total_population_est"]),
                "accessible": float(row["accessible_population_est"]),
                "outside": float(row["outside_population_est"]),
                "percent": float(row["accessibility_percent"]),
            }
    return {"boundary": boundary, "hospitals": hospitals, "coverage": coverage, "stats": stats}
