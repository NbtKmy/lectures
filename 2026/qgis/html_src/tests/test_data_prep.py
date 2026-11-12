import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import data_prep  # noqa: E402


def iter_coords(geometry):
    """Yield every [lon, lat] pair in a GeoJSON geometry."""
    def walk(node):
        if node and isinstance(node[0], (int, float)):
            yield node
        else:
            for child in node:
                yield from walk(child)
    yield from walk(geometry["coordinates"])


class TestConverter(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def test_reprojects_to_wgs84(self):
        out = data_prep.ogr_to_geojson(
            data_prep.ASSETS / "moriyama_admin_field.gpkg", self.tmp / "a.geojson"
        )
        coords = [c for f in out["features"] for c in iter_coords(f["geometry"])]
        self.assertTrue(coords)
        for lon, lat in coords:
            self.assertTrue(136 <= lon <= 138, lon)
            self.assertTrue(34 <= lat <= 36, lat)

    def test_simplify_reduces_size(self):
        src = data_prep.ASSETS / "moriyama_admin_field.gpkg"
        data_prep.ogr_to_geojson(src, self.tmp / "raw.geojson", simplify_deg=0.0)
        data_prep.ogr_to_geojson(src, self.tmp / "simple.geojson", simplify_deg=0.001)
        self.assertLess(
            (self.tmp / "simple.geojson").stat().st_size,
            (self.tmp / "raw.geojson").stat().st_size,
        )

    def test_missing_source_raises(self):
        with self.assertRaises(FileNotFoundError):
            data_prep.ogr_to_geojson(self.tmp / "nope.gpkg", self.tmp / "x.geojson")


class TestTask1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = data_prep.build_task1()
        cls.by_code = {f["properties"]["code"]: f for f in cls.data["features"]}

    def test_feature_count_is_70(self):
        self.assertEqual(len(self.data["features"]), 70)
        self.assertEqual(len(self.by_code), 70)

    def test_unassigned_area_has_null_rate(self):
        props = self.by_code["23000"]["properties"]
        self.assertIsNone(props["rate_brazil"])
        self.assertIsNone(props["pr_all"])
        self.assertIsNone(props["pr_brazil"])
        self.assertEqual(props["name"], "所属未定地")

    def test_totals_match_csv(self):
        props = [f["properties"] for f in self.data["features"]]
        self.assertEqual(sum(p["pr_all"] for p in props if p["pr_all"] is not None), 106839)
        self.assertEqual(sum(p["pr_brazil"] for p in props if p["pr_brazil"] is not None), 34357)

    def test_rate_is_rounded_percentage(self):
        props = self.by_code["23561"]["properties"]
        self.assertEqual((props["pr_all"], props["pr_brazil"]), (7, 3))
        self.assertEqual(props["rate_brazil"], 42.86)

    def test_geometry_is_multipolygon_for_all(self):
        for f in self.data["features"]:
            self.assertEqual(f["geometry"]["type"], "MultiPolygon", f["properties"]["code"])

    def test_payload_size_under_1_5mb(self):
        self.assertLess(len(json.dumps(self.data, ensure_ascii=False)), 1_500_000)


def bbox(fc):
    pts = [c for f in fc["features"] for c in iter_coords(f["geometry"])]
    lons, lats = [p[0] for p in pts], [p[1] for p in pts]
    return min(lons), min(lats), max(lons), max(lats)


class TestTask2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = data_prep.build_task2()

    def test_mesh_has_20_cells(self):
        self.assertEqual(len(self.data["mesh"]["features"]), 20)

    def test_total_pop_est(self):
        self.assertEqual(self.data["summary"]["total_pop_est"], 5420.9)
        self.assertEqual(self.data["summary"]["mesh_count"], 20)
        self.assertEqual(self.data["summary"]["hospital_name"], "川島病院")

    def test_service_area_is_line_geometry(self):
        types = {f["geometry"]["type"] for f in self.data["service_area"]["features"]}
        self.assertTrue(types)
        self.assertLessEqual(types, {"LineString", "MultiLineString"})

    def test_reach_inside_boundary_bbox(self):
        rx0, ry0, rx1, ry1 = bbox(self.data["reach"])
        bx0, by0, bx1, by1 = bbox(self.data["boundary"])
        tol = 0.01
        self.assertGreaterEqual(rx0, bx0 - tol)
        self.assertGreaterEqual(ry0, by0 - tol)
        self.assertLessEqual(rx1, bx1 + tol)
        self.assertLessEqual(ry1, by1 + tol)

    def test_payload_size_under_600kb(self):
        self.assertLess(len(json.dumps(self.data, ensure_ascii=False)), 600_000)


class TestTask3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = data_prep.build_task3()

    def test_hospital_count_is_41(self):
        self.assertEqual(len(self.data["hospitals"]["features"]), 41)

    def test_stats_match_csv(self):
        stats = self.data["stats"]
        self.assertEqual(
            stats["30"],
            {"total": 174833.87, "accessible": 109452.93, "outside": 65380.94, "percent": 62.6},
        )
        self.assertEqual(stats["10"]["percent"], 17.9)
        self.assertEqual(stats["20"]["percent"], 46.61)

    def test_coverage_has_one_feature_per_minute(self):
        self.assertEqual(set(self.data["coverage"]), {"10", "20", "30"})
        for minutes, fc in self.data["coverage"].items():
            self.assertEqual(len(fc["features"]), 1, minutes)

    def test_percent_is_monotonic(self):
        pct = [self.data["stats"][m]["percent"] for m in ("10", "20", "30")]
        self.assertEqual(pct, sorted(pct))

    def test_payload_size_under_1mb(self):
        self.assertLess(len(json.dumps(self.data, ensure_ascii=False)), 1_000_000)


if __name__ == "__main__":
    unittest.main()
