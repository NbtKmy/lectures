import re
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build  # noqa: E402

SRC = Path(__file__).resolve().parents[1]
HTML = build.assemble(SRC, date(2026, 11, 18))


class TestAssemble(unittest.TestCase):
    def test_no_placeholders_left(self):
        self.assertIsNone(re.search(r"\{\{[a-z0-9_]+\}\}", HTML))

    def test_render_rejects_unknown_placeholder(self):
        with self.assertRaises(ValueError):
            build.render("{{nope}}", {})

    def test_inlines_zone_data_and_scripts(self):
        self.assertIn('id="zone-data"', HTML)
        self.assertIn("L.map", HTML)
        self.assertIn("proj4", HTML)
        self.assertIn("window.Lookup", HTML.replace("root.Lookup", "window.Lookup"))

    def test_data_cannot_close_its_script_tag(self):
        m = re.search(r'<script type="application/json" id="zone-data">(.*?)</script>', HTML, re.S)
        self.assertIsNotNone(m)
        self.assertNotIn("</", m.group(1))
        for ch in "<>&":
            self.assertNotIn(ch, m.group(1))

    def test_explainer_facts(self):
        self.assertNotIn("rotated by 90", HTML)
        self.assertNotIn("all of Japan, one UTM", HTML)
        self.assertNotIn("as most of Kyushu or all of Japan does, one UTM zone", HTML)

    def test_utm_is_spelled_out(self):
        self.assertIn("UTM (Universal Transverse Mercator)", HTML)

    def test_lists_all_19_epsg_codes(self):
        for code in range(6669, 6688):
            self.assertIn(f"EPSG:{code}", HTML)
        for code in (2443, 2461):
            self.assertIn(f"EPSG:{code}", HTML)

    def test_attribution_present(self):
        for s in ("国土数値情報", "GeoNames", "CC BY 4.0", "https://www.gsi.go.jp/LAW/heimencho.html", "地理院タイル"):
            self.assertIn(s, HTML)

    def test_last_updated_shown(self):
        self.assertEqual(HTML.count("Last updated: 2026-11-18"), 2)
        self.assertIn("2025-01-01", HTML)

    def test_worked_example_moriyama(self):
        self.assertIn("Moriyama", HTML)
        self.assertIn("EPSG:6675", HTML)

    def test_size_limit(self):
        self.assertLessEqual(len(HTML.encode("utf-8")), 2_500_000)

    def test_no_external_scripts(self):
        self.assertNotIn("<script src=", HTML)


if __name__ == "__main__":
    unittest.main()
