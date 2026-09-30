"""Tests for scripts/run_evals.py scoring, routing aliases and skip handling.

Run with:  python3 -m unittest discover -s tests
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("run_evals", ROOT / "scripts" / "run_evals.py")
run_evals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_evals)


def case(**overrides):
    base = {
        "id": "demo-001",
        "prompt": "一个足够长的测试请求。",
        "expected_skill": "macos-liquid-glass-native-ui",
        "must_include": [],
        "must_not": [],
    }
    base.update(overrides)
    return base


class KeywordScoringTest(unittest.TestCase):
    def test_plain_mention_of_must_not_is_a_violation(self) -> None:
        verdict = run_evals.keyword_score(
            case(must_not=["call a remote image API"]), "我会 call a remote image API 来生成。"
        )
        self.assertFalse(verdict["pass"])
        self.assertEqual(verdict["violations"], ["call a remote image API"])

    def test_negated_mention_of_must_not_is_not_a_violation(self) -> None:
        for text in (
            "禁止 call a remote image API，只使用宿主能力。",
            "不要 call a remote image API。",
            "do not call a remote image API",
            "avoid call a remote image API",
        ):
            with self.subTest(text=text):
                verdict = run_evals.keyword_score(case(must_not=["call a remote image API"]), text)
                self.assertEqual(verdict["violations"], [], text)

    def test_missing_must_include_is_reported(self) -> None:
        verdict = run_evals.keyword_score(case(must_include=["stable action area"]), "其他内容")
        self.assertEqual(verdict["missing"], ["stable action area"])

    def test_aliases_satisfy_must_include(self) -> None:
        verdict = run_evals.keyword_score(
            case(must_include=["stable action area"], aliases={"stable action area": ["稳定底栏"]}),
            "保存按钮放在稳定底栏里。",
        )
        self.assertTrue(verdict["pass"], verdict)


class RoutingAliasTest(unittest.TestCase):
    def test_route_check_accepts_the_resolved_skill_name(self) -> None:
        variants = run_evals.alternatives("route to native skill", case())
        self.assertIn("macos-liquid-glass-native-ui", variants)
        verdict = run_evals.keyword_score(
            case(must_include=["route to native skill"]), "这属于 macos-liquid-glass-native-ui。"
        )
        self.assertTrue(verdict["pass"], verdict)

    def test_route_check_accepts_the_short_form(self) -> None:
        verdict = run_evals.keyword_score(case(must_include=["route to native skill"]), "改用 native skill。")
        self.assertTrue(verdict["pass"], verdict)


class ReportSkipTest(unittest.TestCase):
    """A missing recorded response must be reported as skipped, never crash."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        skill = self.root / "skills" / "demo-skill"
        (skill / "evals").mkdir(parents=True)
        cases = [
            case(id="demo-001", expected_skill="demo-skill", must_include=["present behaviour"]),
            case(id="demo-002", expected_skill="demo-skill"),
        ]
        (skill / "evals" / "core.jsonl").write_text(
            "\n".join(json.dumps(c, ensure_ascii=False) for c in cases) + "\n", encoding="utf-8"
        )
        self.responses = self.root / "responses.jsonl"
        self.responses.write_text(
            json.dumps({"id": "demo-001", "response": "we do present behaviour here"}, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        self._orig = run_evals.SKILLS_DIR
        run_evals.SKILLS_DIR = self.root / "skills"
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        run_evals.SKILLS_DIR = self._orig
        self._tmp.cleanup()

    def _args(self, **overrides):
        base = {
            "keyword": True,
            "judge_cmd": None,
            "agent_cmd": None,
            "responses": str(self.responses),
            "out": None,
            "timeout": 5.0,
            "json": False,
        }
        base.update(overrides)
        return type("Args", (), base)

    def test_partial_responses_are_scored_and_the_rest_skipped(self) -> None:
        cases = run_evals.load_cases(None, None)
        self.assertEqual(len(cases), 2)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = run_evals.report(self._args(), cases)
        output = buffer.getvalue()
        self.assertEqual(code, 0, output)
        self.assertIn("1 passed", output)
        self.assertIn("1 skipped", output)
        self.assertIn("SKIP demo-002", output)

    def test_json_mode_includes_skill_for_skipped_cases(self) -> None:
        cases = run_evals.load_cases(None, None)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            run_evals.report(self._args(json=True), cases)
        payload = json.loads(buffer.getvalue())
        skipped = [r for r in payload["results"] if r["status"] == "skipped"]
        self.assertEqual(skipped[0]["skill"], "demo-skill")
        self.assertEqual(skipped[0]["expected_skill"], "demo-skill")


class FilterTest(unittest.TestCase):
    def test_unknown_id_raises(self) -> None:
        with self.assertRaises(SystemExit):
            run_evals.load_cases(None, ["does-not-exist"])


if __name__ == "__main__":
    unittest.main()
