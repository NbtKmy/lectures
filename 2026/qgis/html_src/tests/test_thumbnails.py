import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from thumbnails import svg_thumbnail  # noqa: E402


def fc(*geometries, props=None):
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "properties": (props[i] if props else {}), "geometry": g}
            for i, g in enumerate(geometries)
        ],
    }


SQUARE = {"type": "Polygon", "coordinates": [[[136.9, 35.1], [137.0, 35.1], [137.0, 35.2], [136.9, 35.2], [136.9, 35.1]]]}
HOLED = {
    "type": "Polygon",
    "coordinates": [
        [[136.9, 35.1], [137.0, 35.1], [137.0, 35.2], [136.9, 35.2], [136.9, 35.1]],
        [[136.94, 35.14], [136.96, 35.14], [136.96, 35.16], [136.94, 35.16], [136.94, 35.14]],
    ],
}
LINE = {"type": "LineString", "coordinates": [[136.9, 35.1], [137.0, 35.2]]}
POINT = {"type": "Point", "coordinates": [136.95, 35.15]}
STYLE = {"fill": "#123456", "stroke": "#ffffff", "stroke_width": 1.0, "opacity": 1.0}


class TestSvgThumbnail(unittest.TestCase):
    def test_polygon_becomes_path(self):
        svg = svg_thumbnail([(fc(SQUARE), STYLE)])
        self.assertIn("<path", svg)
        self.assertIn("#123456", svg)

    def test_fill_callable_per_feature(self):
        other = {"type": "Polygon", "coordinates": [[[137.1, 35.1], [137.2, 35.1], [137.2, 35.2], [137.1, 35.1]]]}
        data = fc(SQUARE, other, props=[{"c": "#aa0000"}, {"c": "#00bb00"}])
        svg = svg_thumbnail([(data, {**STYLE, "fill": lambda f: f["properties"]["c"]})])
        self.assertIn("#aa0000", svg)
        self.assertIn("#00bb00", svg)

    def test_point_becomes_circle(self):
        svg = svg_thumbnail([(fc(POINT), STYLE)])
        self.assertIn("<circle", svg)

    def test_line_becomes_unfilled_path(self):
        svg = svg_thumbnail([(fc(LINE), {**STYLE, "fill": None})])
        self.assertIn("<path", svg)
        self.assertIn('fill="none"', svg)

    def test_empty_layers_returns_valid_svg(self):
        for layers in ([], [(fc(), STYLE)]):
            svg = svg_thumbnail(layers)
            self.assertTrue(svg.startswith("<svg"))
            self.assertTrue(svg.rstrip().endswith("</svg>"))

    def test_coordinates_stay_inside_viewbox(self):
        w, h = 480, 300
        svg = svg_thumbnail([(fc(SQUARE, LINE), STYLE), (fc(POINT), STYLE)], width=w, height=h)
        self.assertIn(f'viewBox="0 0 {w} {h}"', svg)
        for d in re.findall(r' d="([^"]+)"', svg):
            nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", d)]
            xs, ys = nums[0::2], nums[1::2]
            self.assertTrue(all(0 <= x <= w for x in xs), xs)
            self.assertTrue(all(0 <= y <= h for y in ys), ys)
        for cx, cy in re.findall(r'cx="([-\d.]+)" cy="([-\d.]+)"', svg):
            self.assertTrue(0 <= float(cx) <= w and 0 <= float(cy) <= h)

    def test_north_is_up(self):
        svg = svg_thumbnail([(fc(LINE), {**STYLE, "fill": None})])
        d = re.search(r' d="([^"]+)"', svg).group(1)
        nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", d)]
        (x0, y0), (x1, y1) = (nums[0], nums[1]), (nums[2], nums[3])
        self.assertGreater(x1, x0)  # east is right
        self.assertLess(y1, y0)     # north is up

    def test_hole_uses_evenodd(self):
        svg = svg_thumbnail([(fc(HOLED), STYLE)])
        self.assertIn('fill-rule="evenodd"', svg)


if __name__ == "__main__":
    unittest.main()
