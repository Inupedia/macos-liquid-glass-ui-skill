"""Static checks for the optional component showcase (not browser interaction tests)."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "skills" / "macos-liquid-glass-ui"
NATIVE = ROOT / "skills" / "macos-liquid-glass-native-ui"


class DemoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))


class ComponentRecipesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (WEB / "assets" / "component-recipes.css").read_text(encoding="utf-8")
        cls.foundation = (WEB / "assets" / "foundation.css").read_text(encoding="utf-8")
        cls.demo = (WEB / "assets" / "component-showcase.html").read_text(encoding="utf-8")
        cls.parsed = DemoParser()
        cls.parsed.feed(cls.demo)

    def test_css_uses_only_existing_foundation_tokens(self):
        referenced = set(re.findall(r"var\(\s*(--lg-[\w-]+)", self.css))
        declared = set(re.findall(r"(--lg-[\w-]+)\s*:", self.foundation))
        self.assertTrue(referenced)
        self.assertEqual(set(), referenced - declared, "Undeclared tokens in component recipes")

    def test_example_contains_real_semantic_primitives(self):
        tags = self.parsed.tags
        self.assertTrue(any(tag == "dialog" for tag, _ in tags))
        self.assertTrue(any(tag == "select" for tag, _ in tags))
        self.assertTrue(any(tag == "table" for tag, _ in tags))
        self.assertTrue(any(tag == "th" and attr.get("scope") == "col" for tag, attr in tags))
        self.assertTrue(any(tag == "input" and attr.get("type") == "checkbox" for tag, attr in tags))
        self.assertTrue(any(tag == "input" and attr.get("type") == "radio" for tag, attr in tags))
        self.assertNotIn('role="grid"', self.demo)

    def test_behavior_wiring_is_not_a_static_picture(self):
        for key in ('showModal()', 'aria-sort', 'indeterminate', 'addEventListener("change"', 'addEventListener("click"'):
            self.assertIn(key, self.demo)

    def test_skills_route_to_component_spec_files(self):
        web_skill = (WEB / "SKILL.md").read_text(encoding="utf-8")
        native_skill = (NATIVE / "SKILL.md").read_text(encoding="utf-8")
        for filename in ("component-design-contract.md", "overlays-and-dialog-components.md",
                         "selection-and-input-components.md", "tables-and-data-components.md",
                         "component-recipes.css", "component-showcase.html"):
            self.assertIn(filename, web_skill)
        self.assertIn("native-components.md", native_skill)

    def test_material_does_not_blur_every_data_row(self):
        self.assertIn("background: var(--lg-surface)", self.css)
        self.assertNotIn("backdrop-filter", self.css)
        self.assertIn("lgc-dialog::backdrop", self.css)


if __name__ == "__main__":
    unittest.main()
