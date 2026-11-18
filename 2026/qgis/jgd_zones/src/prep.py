"""N03 boundaries + GeoNames -> zone polygons and place list for the JGD2011 zone finder.

    python3 -I 2026/qgis/jgd_zones/src/prep.py
"""
from __future__ import annotations

import csv
from pathlib import Path

SRC = Path(__file__).resolve().parent
ZONES_CSV = SRC / "zones.csv"
RULES_CSV = SRC / "zone_rules.csv"
BOUNDS = ("lat_min", "lat_max", "lon_min", "lon_max")


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
