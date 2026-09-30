"""Tests for scripts/validate_skills.py.

Each test builds a throwaway skill tree, points the validator at it, and checks
the report. Run with:  python3 -m unittest discover -s tests
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import tempfile
import textwrap
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("validate_skills", ROOT / "scripts" / "validate_skills.py")
validate_skills = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_skills)


def skill_md(name: str, body: str, description: str | None = None) -> str:
    description = description or f"{name} 用于测试：这是一段足够长的描述，用来通过长度校验。"
    return f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n\n{body}\n"


def eval_case(case_id: str, expected: str) -> str:
    return json.dumps(
        {
            "id": case_id,
            "prompt": "一个足够长的测试请求，用来通过 prompt 长度校验。",
            "expected_skill": expected,
            "must_include": ["something required"],
            "must_not": ["something forbidden"],
        },
        ensure_ascii=False,
    )


class ValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.skills_dir = self.root / "skills"
        self.skills_dir.mkdir(parents=True)
        self._orig = (validate_skills.ROOT, validate_skills.SKILLS_DIR)
        validate_skills.ROOT = self.root
        validate_skills.SKILLS_DIR = self.skills_dir
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        validate_skills.ROOT, validate_skills.SKILLS_DIR = self._orig
        self._tmp.cleanup()

    def make_skill(
        self,
        name: str = "demo-skill",
        body: str | None = None,
        refs: dict[str, str] | None = None,
        css: str | None = None,
        cases: list[str] | None = None,
        eval_files: dict[str, list[str]] | None = None,
        metadata: str | None = None,
    ) -> pathlib.Path:
        skill = self.skills_dir / name
        (skill / "agents").mkdir(parents=True)
        (skill / "references").mkdir(parents=True)
        (skill / "evals").mkdir(parents=True)

        body = body if body is not None else "读取 `references/note.md`。"
        (skill / "SKILL.md").write_text(skill_md(name, body), encoding="utf-8")
        (skill / "references" / "note.md").write_text("# note\n", encoding="utf-8")
        for filename, content in (refs or {}).items():
            target = skill / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        if css is not None:
            (skill / "assets").mkdir(parents=True, exist_ok=True)
            (skill / "assets" / "foundation.css").write_text(css, encoding="utf-8")
        (skill / "agents" / "openai.yaml").write_text(
            metadata
            or textwrap.dedent(
                f"""\
                interface:
                  display_name: "Demo Skill"
                  short_description: "一个足够长的简短描述"
                  default_prompt: "使用 ${name} 完成任务。"
                """
            ),
            encoding="utf-8",
        )
        if eval_files:
            for filename, lines in eval_files.items():
                (skill / "evals" / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            (skill / "evals" / "core.jsonl").write_text(
                "\n".join(cases or [eval_case(f"{name}-00{i}", name) for i in (1, 2, 3)]) + "\n",
                encoding="utf-8",
            )
        return skill

    def run_validator(self, *argv: str) -> tuple[int, str]:
        buffer = io.StringIO()
        original_argv = sys.argv
        sys.argv = ["validate_skills.py", *argv]
        try:
            with contextlib.redirect_stdout(buffer):
                code = validate_skills.main()
        finally:
            sys.argv = original_argv
        return code, buffer.getvalue()

    def test_minimal_repo_passes_strict(self) -> None:
        self.make_skill()
        code, output = self.run_validator("--strict")
        self.assertEqual(code, 0, output)
        self.assertIn("0 error(s), 0 warning(s)", output)

    def test_missing_referenced_file_is_an_error(self) -> None:
        self.make_skill(body="读取 `references/does-not-exist.md`。")
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("referenced file not found: references/does-not-exist.md", output)

    def test_orphan_reference_is_a_warning_that_strict_rejects(self) -> None:
        self.make_skill(refs={"references/never-routed.md": "# orphan\n"})
        code, output = self.run_validator()
        self.assertEqual(code, 0)
        self.assertIn("not referenced from SKILL.md", output)

        strict_code, strict_output = self.run_validator("--strict")
        self.assertEqual(strict_code, 1)
        self.assertIn("not referenced from SKILL.md", strict_output)

    def test_undefined_token_is_an_error(self) -> None:
        self.make_skill(
            css=".lg-theme { --lg-text: #111; }\n",
            body="读取 `references/note.md`。使用 `--lg-text` 与 `--lg-nope`。",
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("undefined token --lg-nope", output)
        self.assertNotIn("undefined token --lg-text", output)

    def test_token_prefix_notation_is_allowed(self) -> None:
        self.make_skill(
            css=".lg-theme { --lg-chart-1: #0a63b0; --lg-space-1: 4px; }\n",
            body="读取 `references/note.md`。系列色用 `--lg-chart-*`，间距 `--lg-space-*`。",
        )
        code, output = self.run_validator()
        self.assertEqual(code, 0, output)

    def test_duplicate_eval_id_across_files_is_an_error(self) -> None:
        self.make_skill(
            eval_files={
                "core.jsonl": [eval_case("demo-skill-001", "demo-skill"), eval_case("demo-skill-002", "demo-skill"), eval_case("dupe", "demo-skill")],
                "extra.jsonl": [eval_case("dupe", "demo-skill")],
            }
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("duplicate id dupe", output)

    def test_overlapping_must_include_and_must_not_is_an_error(self) -> None:
        case = json.dumps(
            {
                "id": "demo-skill-001",
                "prompt": "一个足够长的测试请求，用来通过 prompt 长度校验。",
                "expected_skill": "demo-skill",
                "must_include": ["glass everywhere", "unique requirement"],
                "must_not": ["Glass Everywhere"],
            },
            ensure_ascii=False,
        )
        self.make_skill(eval_files={"core.jsonl": [case, eval_case("demo-skill-002", "demo-skill"), eval_case("demo-skill-003", "demo-skill")]})
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("must_include and must_not overlap", output)

    def test_missing_evals_directory_is_an_error(self) -> None:
        skill = self.make_skill()
        for path in (skill / "evals").iterdir():
            path.unlink()
        (skill / "evals").rmdir()
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("missing evals/ directory", output)

    def test_missing_references_directory_is_an_error(self) -> None:
        skill = self.make_skill()
        (skill / "references" / "note.md").unlink()
        (skill / "references").rmdir()
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("missing references/", output)

    def test_unknown_skill_mention_is_an_error(self) -> None:
        self.make_skill(body="读取 `references/note.md`。原生请求转用 macos-liquid-glass-native-ui。")
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("mentions unknown skill macos-liquid-glass-native-ui", output)

    def test_expected_skill_must_exist(self) -> None:
        self.make_skill(
            eval_files={
                "core.jsonl": [
                    eval_case("demo-skill-001", "not-a-skill"),
                    eval_case("demo-skill-002", "demo-skill"),
                    eval_case("demo-skill-003", "demo-skill"),
                ]
            }
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("expected_skill references unknown skill", output)

    def test_frontmatter_name_must_match_directory(self) -> None:
        skill = self.make_skill()
        (skill / "SKILL.md").write_text(
            skill_md("other-name", "读取 `references/note.md`。"), encoding="utf-8"
        )
        code, output = self.run_validator()
        self.assertEqual(code, 1)
        self.assertIn("frontmatter name must match directory", output)


if __name__ == "__main__":
    unittest.main()
