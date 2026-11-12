"""Static SVG thumbnails of GeoJSON layers (no dependencies)."""
from __future__ import annotations

import math
from html import escape
from typing import Callable

PADDING = 12


def _coords(geometry: dict):
    def walk(node):
        if node and isinstance(node[0], (int, float)):
            yield node
        else:
            for child in node:
                yield from walk(child)
    yield from walk(geometry["coordinates"])


def _paint(value, feature: dict) -> str | None:
    return value(feature) if callable(value) else value


def svg_thumbnail(layers: list[tuple[dict, dict]], width: int = 480, height: int = 300) -> str:
    """Draw `(FeatureCollection, style)` layers into one SVG string.

    style: fill (str | callable(feature) | None), stroke, stroke_width, opacity, radius.
    Longitude is scaled by cos(mid-latitude) so shapes keep their proportions.
    """
    points = [c for fc, _ in layers for f in fc["features"] for c in _coords(f["geometry"])]
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet">'
    if not points:
        return head + "</svg>"

    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    lon0, lat0, lat1 = min(lons), min(lats), max(lats)
    kx = math.cos(math.radians((lat0 + lat1) / 2))
    span_x = (max(lons) - lon0) * kx
    span_y = lat1 - lat0
    avail_w, avail_h = width - 2 * PADDING, height - 2 * PADDING
    scale = min(avail_w / span_x if span_x else math.inf, avail_h / span_y if span_y else math.inf)
    if not math.isfinite(scale):
        scale = 1.0
    off_x = (width - span_x * scale) / 2
    off_y = (height - span_y * scale) / 2

    def project(c) -> tuple[float, float]:
        return off_x + (c[0] - lon0) * kx * scale, off_y + (lat1 - c[1]) * scale

    def ring_d(ring, close: bool) -> str:
        pts = " L".join("{:.1f} {:.1f}".format(*project(c)) for c in ring)
        return f"M{pts}" + (" Z" if close else "")

    out = [head]
    for fc, style in layers:
        stroke = style.get("stroke")
        sw = style.get("stroke_width", 1.0)
        opacity = style.get("opacity", 1.0)
        for feat in fc["features"]:
            geom = feat["geometry"]
            kind = geom["type"]
            fill = _paint(style.get("fill"), feat)
            common = (
                f'stroke="{escape(stroke)}" stroke-width="{sw}"' if stroke else 'stroke="none"'
            ) + f' opacity="{opacity}"'
            if kind in ("Polygon", "MultiPolygon"):
                polys = [geom["coordinates"]] if kind == "Polygon" else geom["coordinates"]
                d = " ".join(ring_d(r, True) for poly in polys for r in poly)
                out.append(
                    f'<path d="{d}" fill="{escape(fill) if fill else "none"}" '
                    f'fill-rule="evenodd" {common}/>'
                )
            elif kind in ("LineString", "MultiLineString"):
                lines = [geom["coordinates"]] if kind == "LineString" else geom["coordinates"]
                d = " ".join(ring_d(line, False) for line in lines)
                line_stroke = escape(stroke or "#ffffff")
                out.append(
                    f'<path d="{d}" fill="none" stroke="{line_stroke}" stroke-width="{sw}" '
                    f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"/>'
                )
            elif kind in ("Point", "MultiPoint"):
                pts = [geom["coordinates"]] if kind == "Point" else geom["coordinates"]
                for p in pts:
                    x, y = project(p)
                    out.append(
                        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{style.get("radius", 3)}" '
                        f'fill="{escape(fill) if fill else "none"}" {common}/>'
                    )
    out.append("</svg>")
    return "".join(out)
