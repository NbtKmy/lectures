import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build  # noqa: E402

SRC = Path(__file__).resolve().parents[1]
DATA = {"task1": {"x": 1}, "task2": {"x": 2}, "task3": {"x": 3}}
THUMBS = {k: f'<svg data-thumb="{k}"></svg>' for k in ("task1", "task2", "task3")}


def assemble(data=None):
    return build.assemble(data or DATA, THUMBS, SRC)


def panel(html, name):
    m = re.search(rf'<section[^>]*data-panel="{name}".*?</section>', html, re.S)
    assert m, f"panel {name} missing"
    return m.group(0)


class TestAssemble(unittest.TestCase):
    def test_assemble_has_four_tabs(self):
        html = assemble()
        for tab in ("task1", "task2", "task3", "limits"):
            self.assertIn(f'data-tab="{tab}"', html)
            self.assertIn(f'data-panel="{tab}"', html)
        self.assertEqual(len(re.findall(r"<button[^>]*data-tab=", html)), 4)

    def test_landing_cards_link_to_tabs(self):
        html = assemble()
        for n in (1, 2, 3):
            self.assertIn(f'href="#task{n}"', html)
            self.assertIn(f'data-thumb="task{n}"', html)

    def test_no_unreplaced_placeholders(self):
        self.assertIsNone(re.search(r"\{\{[a-z0-9_]+\}\}", assemble()))

    def test_unknown_placeholder_raises(self):
        with self.assertRaises(ValueError):
            build.render("<p>{{nope}}</p>", {})

    def test_no_external_resources_except_tiles(self):
        html = assemble()
        self.assertIsNone(re.search(r"<script[^>]+\ssrc=", html))
        # Only inline (data:) <link> targets are allowed, e.g. the favicon.
        for href in re.findall(r'<link[^>]+href="([^"]*)"', html):
            self.assertTrue(href.startswith("data:"), href)
        self.assertIsNone(re.search(r'<link[^>]+rel=["\']?stylesheet', html))
        self.assertIsNone(re.search(r'<img[^>]+src=["\']?(https?:)?//', html))
        self.assertNotIn("@import", html)
        self.assertNotIn("<iframe", html)
        # The only remote URL fetched at runtime is the tile server.
        hosts = set(re.findall(r"https://([a-z0-9.\-]*gsi\.go\.jp)/[^'\"\s]*\{z\}", html))
        self.assertTrue(hosts, "tile URL template not found")

    def test_footer_attribution(self):
        html = assemble()
        footer = re.search(r"<footer.*?</footer>", html, re.S).group(0)
        for name in ("OpenStreetMap", "MLIT", "e-Stat"):
            self.assertIn(name, footer)

    def test_json_embedding_escapes_script_end(self):
        evil = {"task1": {"name": "</script><b>x</b>"}, "task2": {}, "task3": {}}
        html = assemble(evil)
        m = re.search(r'<script id="session-data" type="application/json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(m)
        self.assertNotIn("</", m.group(1))
        self.assertEqual(json.loads(m.group(1)), evil)

    def test_html_lang_is_en(self):
        self.assertRegex(assemble(), r'<html[^>]*\blang="en"')

    def test_viewport_meta_present(self):
        self.assertIn('name="viewport"', assemble())


class TestMapMarkup(unittest.TestCase):
    def test_task1_map_markup(self):
        html = panel(assemble(), "task1")
        self.assertIn('id="map-task1"', html)
        for mode in ("equal", "quantile", "jenks"):
            self.assertIn(f'value="{mode}"', html)
        for measure in ("count", "rate"):
            self.assertIn(f'data-measure="{measure}"', html)

    def test_task2_map_markup(self):
        html = panel(assemble(), "task2")
        self.assertIn('id="map-task2"', html)
        layers = re.findall(r'type="checkbox"[^>]*data-layer="([a-z]+)"', html)
        self.assertEqual(sorted(layers), ["boundary", "hospital", "mesh", "reach", "roads"])
        self.assertIn("different method", html)

    def test_task3_map_markup(self):
        html = panel(assemble(), "task3")
        self.assertIn('id="map-task3"', html)
        self.assertRegex(html, r'<input[^>]*type="range"[^>]*min="10"[^>]*max="30"[^>]*step="10"')
        self.assertIn("Approximate", html)


class TestContent(unittest.TestCase):
    def test_task1_content(self):
        html = panel(assemble(), "task1")
        base = "https://github.com/NbtKmy/lectures/blob/main/2026/assets/"
        for name in ("aichi_admin_fields2025.geojson", "aichi_permanent_residents_202512.csv"):
            self.assertIn(base + name, html)
        for text in ("Add XYZ Layer", "Joins", "Graduated", "N03_007", "city_code", "pr_brazil", "3.44", 'href="#limits"'):
            self.assertIn(text, html)
        self.assertGreaterEqual(html.count("<ol"), 1)

    def test_task2_task3_content(self):
        html = assemble()
        t2, t3 = panel(html, "task2"), panel(html, "task3")
        for text in ("川島病院", "different method", "5,421", "moriyama_admin_field.gpkg", 'href="#limits"'):
            self.assertIn(text, t2)
        for text in ("17.90%", "46.61%", "62.60%", "174,833.87", "Dissolve", "Clip", "potential"):
            self.assertIn(text, t3)
        self.assertNotIn("QNEAT3", t2)
        self.assertNotIn("QNEAT3", t3)

    def test_limits_and_start_content(self):
        html = assemble()
        limits = panel(html, "limits")
        for text in ("approximation", "96", "potential"):
            self.assertIn(text, limits)
        start = re.search(r'<section[^>]*id="start".*?</section>', html, re.S).group(0)
        for text in ("3.44", "MLIT", "e-Stat", "OpenStreetMap"):
            self.assertIn(text, start)


class TestScratchPages(unittest.TestCase):
    def pages(self):
        return {name: build.assemble_scratch(page, SRC) for name, page in build.SCRATCH_PAGES.items()}

    def test_two_pages_defined(self):
        self.assertEqual(sorted(build.SCRATCH_PAGES), ["qgis_task2_scratch.html", "qgis_task3_scratch.html"])

    def test_pages_are_self_contained(self):
        for name, html in self.pages().items():
            self.assertIsNone(re.search(r"\{\{[a-z0-9_]+\}\}", html), name)
            self.assertIsNone(re.search(r"<script", html), name)
            self.assertRegex(html, r'<html[^>]*\blang="en"')
            self.assertIn('name="viewport"', html)
            self.assertIsNone(re.search(r'<link[^>]+rel=["\']?stylesheet', html), name)

    def test_task2_scratch_content(self):
        html = self.pages()["qgis_task2_scratch.html"]
        for text in ("川島病院", "23113", "EPSG:6675", "666.67", '"DN" = 1', "QuickOSM", "MESH05236", "MESH05237",
                     "tblT001142Q23", "5,421", "2,745", "308", 'id="step-0"', 'id="step-5"', "qgis_task3_scratch.html"):
            self.assertIn(text, html)
        # Every file a checkpoint tells the reader to load instead ships in the repository.
        assets = SRC.parents[1] / "assets"
        shipped = re.findall(r"Repository files?: <code>([a-z0-9_]+\.gpkg)</code>", html)
        self.assertGreaterEqual(len(shipped), 6)
        for fname in shipped:
            self.assertTrue((assets / fname).exists(), fname)

    def test_task3_scratch_content(self):
        html = self.pages()["qgis_task3_scratch.html"]
        for script in ("find_roads_to_hospitals.py", "create_roads_to_hospitals_10and20min.py",
                       "line_to_30mbuffer_polygon.py", "analysis_B.py"):
            self.assertIn(script, html)
            self.assertTrue((SRC.parents[1] / "assets" / script).exists(), script)
        for text in ("moriyama_boundary", "moriyama_buffer_hospitals", "17.90%", "46.61%", "62.60%",
                     "174,833.87", "96", "qgis_task2_scratch.html#step-0", "Dissolve", "Clip"):
            self.assertIn(text, html)

    def test_layer_names_match_scripts(self):
        html = self.pages()["qgis_task3_scratch.html"]
        scripts = "".join(
            (SRC.parents[1] / "assets" / s).read_text(encoding="utf-8")
            for s in ("find_roads_to_hospitals.py", "analysis_B.py")
        )
        for name in re.findall(r'"(moriyama_[a-z0-9_]+)"', scripts):
            if name.startswith("moriyama_hospitals_") or name.startswith("moriyama_analysis") or "coverage" in name:
                continue
            self.assertIn(f"<code>{name}</code>", html)

    def test_handout_links_to_scratch_pages(self):
        html = assemble()
        self.assertIn('href="qgis_task2_scratch.html"', panel(html, "task2"))
        self.assertIn('href="qgis_task3_scratch.html"', panel(html, "task3"))
        for name, page in build.SCRATCH_PAGES.items():
            self.assertIn(f'href="qgis_session.html#{page["back_tab"]}"', build.assemble_scratch(page, SRC))


if __name__ == "__main__":
    unittest.main()
