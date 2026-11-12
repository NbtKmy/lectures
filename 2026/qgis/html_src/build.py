"""Assemble the single-file QGIS session page.

    python3 2026/qgis/html_src/build.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUTPUT = SRC.parent / "qgis_session.html"
PLACEHOLDER = re.compile(r"\{\{([a-z0-9_]+)\}\}")


def render(template: str, values: dict[str, str]) -> str:
    """Substitute {{name}} in one pass; substituted text is never re-scanned."""
    missing = sorted({m for m in PLACEHOLDER.findall(template) if m not in values})
    if missing:
        raise ValueError(f"unreplaced placeholders: {', '.join(missing)}")
    return PLACEHOLDER.sub(lambda m: values[m.group(1)], template)


def _read(src_dir: Path, rel: str) -> str:
    return (src_dir / rel).read_text(encoding="utf-8").rstrip("\n")


def assemble(data: dict, thumbs: dict[str, str], src_dir: Path = SRC) -> str:
    """Return the complete HTML page as one string."""
    src_dir = Path(src_dir)
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    values = {
        "style": _read(src_dir, "style.css"),
        "leaflet_css": _read(src_dir, "vendor/leaflet/leaflet.css"),
        "leaflet_js": _read(src_dir, "vendor/leaflet/leaflet.js"),
        "data_json": data_json,
        "classify_js": _read(src_dir, "classify.js"),
        "app_js": _read(src_dir, "app.js"),
    }
    for n in (1, 2, 3):
        values[f"map_task{n}_js"] = _read(src_dir, f"map_task{n}.js")
        values[f"thumb_task{n}"] = thumbs[f"task{n}"]
    # Content fragments may embed the interactive map blocks via {{map_taskN}}.
    maps = {
        f"map_task{n}": _read(src_dir, f"content/map_task{n}.html")
        for n in (1, 2, 3)
        if (src_dir / f"content/map_task{n}.html").exists()
    }
    for name in ("start", "task1", "task2", "task3", "limits"):
        values[f"content_{name}"] = render(_read(src_dir, f"content/{name}.html"), maps)
    return render(_read(src_dir, "template.html"), values)


def make_thumbnails(data: dict) -> dict[str, str]:
    from thumbnails import svg_thumbnail

    task1_fill = lambda f: _rate_color(f["properties"]["rate_brazil"])
    t2, t3 = data["task2"], data["task3"]
    return {
        "task1": svg_thumbnail([
            (data["task1"], {"fill": task1_fill, "stroke": "#10151f", "stroke_width": 0.4}),
        ]),
        "task2": svg_thumbnail([
            (t2["reach"], {"fill": "#2a78d6", "stroke": "#9ec5f4", "stroke_width": 0.8, "opacity": 0.4}),
            (t2["mesh"], {"fill": None, "stroke": "#3a4666", "stroke_width": 0.6}),
            (t2["service_area"], {"fill": "#f2b84b", "stroke": "#f2b84b", "stroke_width": 0.9}),
            ({"features": [t2["hospital"]]}, {"fill": "#ffffff", "stroke": "#10151f", "radius": 4}),
        ]),
        "task3": svg_thumbnail([
            (t3["boundary"], {"fill": "#1b2438", "stroke": "#3a4666", "stroke_width": 0.8}),
            (t3["coverage"]["30"], {"fill": "#3987e5", "stroke": "#9ec5f4", "stroke_width": 0.5, "opacity": 0.55}),
            (t3["hospitals"], {"fill": "#f2b84b", "stroke": None, "radius": 2.2}),
        ]),
    }


_RAMP = ["#184f95", "#256abf", "#3987e5", "#6da7ec", "#b7d3f6"]


def _rate_color(rate) -> str:
    if rate is None:
        return "#4a4d55"
    return _RAMP[min(int(rate // 4), len(_RAMP) - 1)]


def main() -> Path:
    import data_prep

    data = {"task1": data_prep.build_task1(), "task2": data_prep.build_task2(), "task3": data_prep.build_task3()}
    html = assemble(data, make_thumbnails(data))
    OUTPUT.write_text(html, encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    out = main()
    print(f"wrote {out} ({out.stat().st_size / 1e6:.2f} MB)")
