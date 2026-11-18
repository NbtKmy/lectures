import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import prep  # noqa: E402


def rule(pref, zone, muni="", lat_min=None, lat_max=None, lon_min=None, lon_max=None):
    return {"pref_code": pref, "muni_code": muni, "zone": zone,
            "lat_min": lat_min, "lat_max": lat_max, "lon_min": lon_min, "lon_max": lon_max}


RULES = [
    rule("01", 11, muni="01202"),
    rule("01", 12),
    rule("13", 14, lat_max=28, lon_min=140.5, lon_max=143),
    rule("13", 18, lat_max=28, lon_max=140.5),
    rule("13", 19, lat_max=28, lon_min=143),
    rule("13", 9),
    rule("23", 7),
]


def square(x, y, size=1.0):
    return [[x, y], [x + size, y], [x + size, y + size], [x, y + size], [x, y]]


def geonames_line(name, ascii_, lat, lon, fclass, fcode, pop):
    cols = ["1", name, ascii_, "", str(lat), str(lon), fclass, fcode, "JP", "", "", "", "", "", str(pop), "", "", "", ""]
    return "\t".join(cols)


class TestAssignZone(unittest.TestCase):
    def test_assign_zone_prefecture_default(self):
        self.assertEqual(prep.assign_zone("23", "23101", 136.9, 35.2, RULES), 7)

    def test_assign_zone_muni_override_wins(self):
        self.assertEqual(prep.assign_zone("01", "01202", 140.7, 41.8, RULES), 11)
        self.assertEqual(prep.assign_zone("01", "01101", 141.35, 43.06, RULES), 12)

    def test_assign_zone_bounds(self):
        self.assertEqual(prep.assign_zone("13", "13421", 142.19, 27.09, RULES), 14)
        self.assertEqual(prep.assign_zone("13", "13421", 136.08, 20.42, RULES), 18)
        self.assertEqual(prep.assign_zone("13", "13421", 153.98, 24.29, RULES), 19)
        self.assertEqual(prep.assign_zone("13", "13104", 139.7, 35.69, RULES), 9)

    def test_assign_zone_unknown_pref_is_none(self):
        self.assertIsNone(prep.assign_zone("99", "99999", 139.0, 35.0, RULES))

    def test_zone_features_drops_empty_geometry(self):
        n03 = {"features": [
            {"properties": {"N03_007": "23101"}, "geometry": {"type": "MultiPolygon", "coordinates": []}},
            {"properties": {"N03_007": "23101"}, "geometry": {"type": "Polygon", "coordinates": [square(136.9, 35.1, 0.1)]}},
        ]}
        out = prep.zone_features(n03, RULES)
        self.assertEqual([f["properties"]["zone"] for f in out], [7])


class TestCentroid(unittest.TestCase):
    def test_ring_centroid_square(self):
        geom = {"type": "Polygon", "coordinates": [square(10, 20)]}
        x, y = prep.ring_centroid(geom)
        self.assertAlmostEqual(x, 10.5)
        self.assertAlmostEqual(y, 20.5)

    def test_ring_centroid_multipolygon_uses_largest(self):
        geom = {"type": "MultiPolygon", "coordinates": [[square(0, 0, 0.1)], [square(5, 5, 2)]]}
        x, y = prep.ring_centroid(geom)
        self.assertAlmostEqual(x, 6.0)
        self.assertAlmostEqual(y, 6.0)

    def test_inner_point_lies_inside_a_c_shape(self):
        # C opening east: the area centroid falls in the gap
        ring = [[0, 0], [3, 0], [3, 1], [1, 1], [1, 2], [3, 2], [3, 3], [0, 3], [0, 0]]
        x, y = prep.inner_point({"type": "Polygon", "coordinates": [ring]})
        self.assertTrue(prep.point_in_ring(x, y, ring))
        self.assertFalse(prep.point_in_ring(2.0, 1.5, ring))

    def test_add_labels_puts_a_point_inside_the_largest_part(self):
        fc = {"features": [{"properties": {"zone": 7}, "geometry": {
            "type": "MultiPolygon", "coordinates": [[square(0, 0, 0.1)], [square(5, 5, 2)]]}}]}
        prep.add_labels(fc)
        self.assertEqual(fc["features"][0]["properties"]["label"], [6.0, 6.0])


class TestPlaces(unittest.TestCase):
    def test_fold(self):
        self.assertEqual(prep.fold("Ōsaka-shi"), "osaka")
        self.assertEqual(prep.fold("Chichi-jima"), "chichijima")
        self.assertEqual(prep.fold("大阪市"), "大阪市")

    def test_place_rows_filters_and_dedupes(self):
        lines = [
            geonames_line("Ōsaka", "Osaka", 34.69, 135.50, "P", "PPLA", 2_600_000),
            geonames_line("Osaka-shi", "Osaka-shi", 34.70, 135.51, "A", "ADM2", 2_600_000),
            geonames_line("Tiny", "Tiny", 35.0, 136.0, "P", "PPL", 50),
            geonames_line("Chichi-jima", "Chichi-jima", 27.09, 142.19, "T", "ISL", 0),
            geonames_line("Some Hill", "Some Hill", 35.0, 136.0, "T", "HLL", 0),
        ]
        n03 = [{"properties": {"N03_001": "大阪府", "N03_003": "", "N03_004": "大阪市", "N03_007": "27100"},
                "geometry": {"type": "Polygon", "coordinates": [square(135.4, 34.6, 0.2)]}},
               {"properties": {"N03_001": "大阪府", "N03_004": "大阪市", "N03_007": "27100"}, "geometry": None}]
        rows = prep.place_rows(lines, n03, pop_min=1000)
        keys = [r[1] for r in rows]
        self.assertEqual(keys.count("osaka"), 1)
        self.assertIn("chichijima", keys)
        self.assertNotIn("tiny", keys)
        self.assertNotIn("somehill", keys)
        self.assertIn(["大阪府大阪市", "大阪府大阪市", 34.7, 135.5], rows)


class TestPlaceZones(unittest.TestCase):
    ZONED = [
        {"properties": {"zone": 7}, "geometry": {"type": "Polygon", "coordinates": [square(136.0, 35.0, 1.0)]}},
        {"properties": {"zone": 8}, "geometry": {"type": "Polygon", "coordinates": [square(137.0, 35.0, 1.0)]}},
    ]

    def test_point_inside_gets_its_zone(self):
        rows = prep.place_zones([["A", "a", 35.5, 136.5]], self.ZONED)
        self.assertEqual(rows, [["A", "a", 35.5, 136.5, 7]])

    def test_offshore_point_gets_the_nearest_zone(self):
        # ~1 km east of the zone-8 square
        rows = prep.place_zones([["Rock", "rock", 35.5, 138.01]], self.ZONED)
        self.assertEqual(rows[0][4], 8)

    def test_far_point_is_dropped(self):
        self.assertEqual(prep.place_zones([["Sea", "sea", 30.0, 150.0]], self.ZONED), [])


if __name__ == "__main__":
    unittest.main()
