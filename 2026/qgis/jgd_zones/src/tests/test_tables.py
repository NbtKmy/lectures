import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import prep  # noqa: E402


def zones_by_pref(rules, pref):
    return {r["zone"] for r in rules if r["pref_code"] == pref}


class TestZones(unittest.TestCase):
    def test_zones_has_19_rows_with_epsg_formula(self):
        rows = prep.load_zones()
        self.assertEqual([r["zone"] for r in rows], list(range(1, 20)))
        for r in rows:
            self.assertEqual(r["epsg"], 6668 + r["zone"])
            self.assertEqual(r["epsg_jgd2000"], 2442 + r["zone"])

    def test_zone_vii_origin(self):
        z = prep.load_zones()[6]
        self.assertEqual(z["roman"], "VII")
        self.assertAlmostEqual(z["origin_lat"], 36.0, places=6)
        self.assertAlmostEqual(z["origin_lon"], 137 + 10 / 60, places=6)


class TestRules(unittest.TestCase):
    def setUp(self):
        self.rules = prep.load_rules()

    def test_every_prefecture_has_a_default_rule(self):
        defaults = {
            r["pref_code"]
            for r in self.rules
            if not r["muni_code"] and all(r[k] is None for k in ("lat_min", "lat_max", "lon_min", "lon_max"))
        }
        self.assertEqual(defaults, {f"{n:02d}" for n in range(1, 48)})

    def test_split_prefectures_have_specific_rows(self):
        self.assertEqual(zones_by_pref(self.rules, "01"), {11, 12, 13})
        self.assertEqual(zones_by_pref(self.rules, "13"), {9, 14, 18, 19})
        self.assertEqual(zones_by_pref(self.rules, "47"), {15, 16, 17})
        self.assertEqual(zones_by_pref(self.rules, "46"), {1, 2})

    def test_hokkaido_muni_rows_cover_both_split_zones(self):
        rows = [r for r in self.rules if r["pref_code"] == "01" and r["muni_code"]]
        by_code = {r["muni_code"]: r["zone"] for r in rows}
        self.assertEqual(by_code["01202"], 11)  # Hakodate
        self.assertEqual(by_code["01571"], 11)  # Toyoura (Iburi, named in XI)
        self.assertEqual(by_code["01207"], 13)  # Obihiro
        self.assertNotIn("01101", by_code)      # Sapporo falls to the XII default

    def test_specific_rows_come_before_prefecture_defaults(self):
        seen_default = set()
        for r in self.rules:
            specific = r["muni_code"] or any(r[k] is not None for k in ("lat_min", "lat_max", "lon_min", "lon_max"))
            if specific:
                self.assertNotIn(r["pref_code"], seen_default)
            else:
                seen_default.add(r["pref_code"])

    def test_rules_cite_source(self):
        first = prep.RULES_CSV.read_text(encoding="utf-8").splitlines()[0]
        self.assertTrue(first.startswith("# source: https://www.gsi.go.jp/"))


if __name__ == "__main__":
    unittest.main()
