"""Assemble the single-file JGD2011 zone finder page.

    python3 2026/qgis/jgd_zones/src/build.py
"""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

import prep

SRC = Path(__file__).resolve().parent
OUTPUT = SRC.parent / "index.html"
PLACEHOLDER = re.compile(r"\{\{([a-z0-9_]+)\}\}")


def render(template: str, values: dict[str, str]) -> str:
    """Substitute {{name}} in one pass; substituted text is never re-scanned."""
    missing = sorted({m for m in PLACEHOLDER.findall(template) if m not in values})
    if missing:
        raise ValueError(f"unreplaced placeholders: {', '.join(missing)}")
    return PLACEHOLDER.sub(lambda m: values[m.group(1)], template)


def _read(src_dir: Path, rel: str) -> str:
    return (src_dir / rel).read_text(encoding="utf-8").rstrip("\n")


def _dms(deg: float) -> str:
    d = int(deg)
    m = round((deg - d) * 60)
    return f"{d}°{m:02d}′"


def zone_table(zones: list[dict]) -> str:
    rows = []
    for z in zones:
        rows.append(
            f'<tr data-zone="{z["zone"]}"><th scope="row">{z["roman"]} <span lang="ja">({z["zone"]}系)</span></th>'
            f'<td><code>EPSG:{z["epsg"]}</code></td><td><code>EPSG:{z["epsg_jgd2000"]}</code></td>'
            f'<td>{_dms(z["origin_lat"])}N {_dms(z["origin_lon"])}E</td><td>{html.escape(z["area_en"])}</td></tr>'
        )
    return "\n".join(rows)


def source_url(src_dir: Path) -> str:
    first = (src_dir / "zone_rules.csv").read_text(encoding="utf-8").splitlines()[0]
    return re.search(r"https://\S+", first).group(0)


def assemble(src_dir: Path, updated: date) -> str:
    """Return the complete HTML page as one string."""
    src_dir = Path(src_dir)
    zones = prep.load_zones(src_dir / "zones.csv")
    meta = json.loads(_read(src_dir, "data/meta.json"))
    data = {
        "zones": json.loads(_read(src_dir, "data/zones.geojson")),
        "places": json.loads(_read(src_dir, "data/places.json")),
        "info": [{k: z[k] for k in ("zone", "roman", "epsg", "epsg_jgd2000", "origin_lat", "origin_lon", "area_en")}
                 for z in zones],
    }
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    values = {
        "style": _read(src_dir, "style.css"),
        "leaflet_css": _read(src_dir, "vendor/leaflet/leaflet.css"),
        "leaflet_js": _read(src_dir, "vendor/leaflet/leaflet.js"),
        "proj4_js": _read(src_dir, "vendor/proj4/proj4.js"),
        "lookup_js": _read(src_dir, "lookup.js"),
        "app_js": _read(src_dir, "app.js"),
        "data_json": data_json,
        "zone_rows": zone_table(zones),
        "updated": updated.isoformat(),
        "n03_edition": meta["n03_edition"],
        "geonames_downloaded": meta["geonames_downloaded"],
        "source_url": source_url(src_dir),
    }
    values["explainer"] = render(_read(src_dir, "content/explainer.html"), values)
    return render(_read(src_dir, "template.html"), values)


def main() -> None:
    page = assemble(SRC, date.today())
    OUTPUT.write_text(page + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT} ({len(page.encode('utf-8')) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
