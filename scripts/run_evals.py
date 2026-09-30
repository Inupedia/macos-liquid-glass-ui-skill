#!/usr/bin/env python3
"""Run the behaviour eval fixtures under skills/*/evals/.

Fixtures are JSONL cases:
    {"id": "...", "prompt": "...", "expected_skill": "...",
     "must_include": ["..."], "must_not": ["..."],
     "aliases": {"must_include phrase": ["alternative wording", "..."]}}

Three ways to score a case:

1. Semantic (recommended) — let a model judge the answer:
       python3 scripts/run_evals.py --agent-cmd "./run-agent.sh" --judge-cmd "./judge.sh"
   `--agent-cmd` receives the prompt on stdin and prints the final answer.
   `--judge-cmd` receives {"prompt", "response", "expected_skill",
   "must_include", "must_not"} as JSON on stdin and prints
   {"pass": bool, "missing": [...], "violations": [...], "reason": "..."}.

2. Recorded answers — score an existing run, no network needed:
       python3 scripts/run_evals.py --responses responses.jsonl --judge-cmd "./judge.sh"

3. Keyword smoke test — offline heuristic, good for catching obvious
   regressions (a missing routing handoff, a forbidden API showing up):
       python3 scripts/run_evals.py --responses responses.jsonl --keyword
   Keyword scoring is intentionally blunt: every `must_include` entry must
   appear literally (or via `aliases`), so semantic expectations need a judge.

Trigger quality has its own mode, separate from answer quality:
       python3 scripts/run_evals.py --route-cmd "./route.sh"
   `--route-cmd` receives the raw user prompt and must print the single skill
   name it would load; each result is compared with `expected_skill`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shlex
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
ROUTE_PREFIX = "route to "


def load_cases(skills: list[str] | None, ids: list[str] | None) -> list[dict]:
    cases: list[dict] = []
    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        if skills and skill_dir.name not in skills:
            continue
        for jsonl in sorted((skill_dir / "evals").glob("*.jsonl")):
            for line_no, raw in enumerate(jsonl.read_text(encoding="utf-8").splitlines(), 1):
                if not raw.strip():
                    continue
                case = json.loads(raw)
                try:
                    location = jsonl.relative_to(ROOT)
                except ValueError:
                    # The skill tree may live outside the repository root when
                    # the runner is embedded or tested against a fixture tree.
                    location = jsonl
                case["_source"] = f"{location}:{line_no}"
                case["_owner"] = skill_dir.name
                cases.append(case)
    if ids:
        wanted = set(ids)
        cases = [c for c in cases if c.get("id") in wanted]
        missing = wanted - {c.get("id") for c in cases}
        if missing:
            raise SystemExit(f"unknown eval id(s): {', '.join(sorted(missing))}")
    return cases


def run_command(cmd: str, stdin_text: str, timeout: float) -> str:
    proc = subprocess.run(
        shlex.split(cmd),
        input=stdin_text,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {cmd}\n{proc.stderr.strip()[:2000]}"
        )
    return proc.stdout


def judge_case(judge_cmd: str, case: dict, response: str, timeout: float) -> dict:
    payload = json.dumps(
        {
            "id": case.get("id"),
            "prompt": case.get("prompt"),
            "response": response,
            "expected_skill": case.get("expected_skill"),
            "must_include": case.get("must_include", []),
            "must_not": case.get("must_not", []),
        },
        ensure_ascii=False,
    )
    raw = run_command(judge_cmd, payload, timeout).strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", raw, re.S)
    if fence:
        raw = fence.group(1).strip()
    try:
        verdict = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"judge did not return JSON: {exc}\noutput: {raw[:1000]}")
    if not isinstance(verdict, dict) or "pass" not in verdict:
        raise RuntimeError(f"judge JSON must contain a `pass` boolean: {raw[:1000]}")
    verdict["pass"] = bool(verdict["pass"])
    verdict.setdefault("missing", [])
    verdict.setdefault("violations", [])
    verdict.setdefault("reason", "")
    return verdict


def alternatives(check: str, case: dict) -> list[str]:
    """All literal strings that satisfy one check in keyword mode."""
    variants = [check]
    if check.lower().startswith(ROUTE_PREFIX):
        variants.append(check[len(ROUTE_PREFIX):])
        expected = case.get("expected_skill")
        if expected:
            variants.append(expected)
            variants.append(expected.replace("macos-liquid-glass-", "").replace("-", " "))
    aliases = case.get("aliases") or {}
    for key, value in aliases.items():
        if key.lower() == check.lower() and isinstance(value, list):
            variants.extend(value)
    return [v.lower() for v in variants if v]


# A correct answer often has to *name* the thing it refuses ("不要调用外部图像
# API"). Naive substring matching would score that as a violation, so a hit that
# sits inside a negation window is not counted.
NEGATION_CUES = (
    "不要", "不得", "禁止", "避免", "不能", "不应", "无需", "别再", "不去", "不做",
    "no ", "not ", "never", "don't", "do not", "avoid", "without", "instead of",
)
NEGATION_WINDOW = 24


def is_negated(haystack: str, index: int) -> bool:
    context = haystack[max(0, index - NEGATION_WINDOW):index]
    return any(cue in context for cue in NEGATION_CUES)


def keyword_score(case: dict, response: str) -> dict:
    haystack = response.lower()
    missing = [
        check
        for check in case.get("must_include", [])
        if not any(variant in haystack for variant in alternatives(check, case))
    ]
    violations = []
    for check in case.get("must_not", []):
        for variant in alternatives(check, case):
            index = haystack.find(variant)
            if index != -1 and not is_negated(haystack, index):
                violations.append(check)
                break
    return {
        "pass": not missing and not violations,
        "missing": missing,
        "violations": violations,
        "reason": "keyword heuristic (negation-aware for must_not)",
    }


def lexical_route(prompt: str) -> str | None:
    """Deterministic sanity router over the skill frontmatter descriptions."""
    best, best_score = None, 0
    for skill_dir in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        header = text.split("---", 2)[1] if text.startswith("---") else ""
        tokens = set(re.findall(r"[a-zA-Z]{3,}", header.lower()))
        tokens |= {w for w in re.findall(r"[a-zA-Z]{3,}", skill_dir.name.lower())}
        lowered = prompt.lower()
        score = sum(1 for token in tokens if token in lowered)
        if score > best_score:
            best, best_score = skill_dir.name, score
    return best


def report(args: argparse.Namespace, cases: list[dict]) -> int:
    if args.keyword and args.judge_cmd:
        raise SystemExit("--keyword and --judge-cmd are mutually exclusive")
    if not args.keyword and not args.judge_cmd:
        raise SystemExit(
            "choose a scoring mode: --judge-cmd (semantic, recommended) or --keyword (offline smoke test)"
        )
    if not args.agent_cmd and not args.responses:
        raise SystemExit("provide --agent-cmd (generate answers) or --responses (recorded answers)")

    recorded: dict[str, str] = {}
    if args.responses:
        path = pathlib.Path(args.responses)
        for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            item = json.loads(raw)
            if "id" not in item or "response" not in item:
                raise SystemExit(f"{path}:{line_no}: expected {{\"id\", \"response\"}}")
            recorded[item["id"]] = item["response"]

    results: list[dict] = []
    out_handle = open(args.out, "w", encoding="utf-8") if args.out else None
    try:
        for case in cases:
            case_id = case.get("id")
            started = time.time()
            if case_id in recorded:
                response = recorded[case_id]
            elif args.agent_cmd:
                response = run_command(args.agent_cmd, case["prompt"], args.timeout)
            else:
                results.append(
                    {
                        "id": case_id,
                        "skill": case.get("_owner"),
                        "expected_skill": case.get("expected_skill"),
                        "status": "skipped",
                        "missing": [],
                        "violations": [],
                        "reason": "no recorded response",
                        "elapsed_ms": 0,
                    }
                )
                continue
            elapsed_ms = int((time.time() - started) * 1000)
            if out_handle:
                out_handle.write(
                    json.dumps({"id": case_id, "response": response, "elapsed_ms": elapsed_ms}, ensure_ascii=False)
                    + "\n"
                )
            try:
                verdict = (
                    keyword_score(case, response)
                    if args.keyword
                    else judge_case(args.judge_cmd, case, response, args.timeout)
                )
                status = "pass" if verdict["pass"] else "fail"
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                verdict = {"missing": [], "violations": [], "reason": str(exc)}
                status = "error"
            results.append(
                {
                    "id": case_id,
                    "skill": case.get("_owner"),
                    "expected_skill": case.get("expected_skill"),
                    "status": status,
                    "missing": verdict.get("missing", []),
                    "violations": verdict.get("violations", []),
                    "reason": verdict.get("reason", ""),
                    "elapsed_ms": elapsed_ms,
                }
            )
    finally:
        if out_handle:
            out_handle.close()

    if not args.json:
        if args.agent_cmd and not args.judge_cmd:
            print("scoring mode: keyword smoke test (heuristic; use --judge-cmd for real grading)\n")
        for item in results:
            mark = {"pass": "PASS", "fail": "FAIL", "error": "ERR ", "skipped": "SKIP"}[item["status"]]
            print(f"{mark} {item['id']}  [{item['skill']}]")
            if item["missing"]:
                print(f"     missing: {', '.join(item['missing'])}")
            if item["violations"]:
                print(f"     forbidden: {', '.join(item['violations'])}")
            if item["status"] in {"error"} or (item["status"] == "fail" and item["reason"]):
                print(f"     note: {item['reason'][:400]}")

    counts = {name: sum(1 for r in results if r["status"] == name) for name in ("pass", "fail", "error", "skipped")}
    if not args.json:
        print(
            f"\n{counts['pass']} passed, {counts['fail']} failed, {counts['error']} errored, "
            f"{counts['skipped']} skipped (of {len(results)})"
        )
    if args.json:
        print(json.dumps({"counts": counts, "results": results}, ensure_ascii=False, indent=2))
    return 1 if counts["fail"] or counts["error"] else 0


def routing_check(args: argparse.Namespace, cases: list[dict]) -> int:
    """Lexical sanity check only; kept as a smoke signal, never a real trigger test."""
    mismatches = []
    for case in cases:
        picked = lexical_route(case["prompt"])
        if picked != case.get("expected_skill"):
            mismatches.append((case["id"], case.get("expected_skill"), picked))
    total = len(cases)
    matched = total - len(mismatches)
    if not args.json:
        print(f"lexical routing agreement: {matched}/{total}")
        for case_id, expected, picked in mismatches:
            print(f"  MISMATCH {case_id}: expected {expected}, lexical router picked {picked}")
        print(
            "\nNOTE: this compares prompt wording with skill descriptions (mostly English tokens against\n"
            "Chinese prompts), so a low score is expected and proves nothing on its own. Do not gate CI on\n"
            "it. For a real trigger test use --route-cmd with an agent, or --agent-cmd for answer quality."
        )
    else:
        print(json.dumps({"matched": matched, "total": total, "mismatches": mismatches}, ensure_ascii=False, indent=2))
    return 1 if (args.gate_routing and mismatches) else 0


def route_agent_check(args: argparse.Namespace, cases: list[dict]) -> int:
    """Real trigger test: ask an agent which single skill it would load."""
    known = sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir())
    results = []
    for case in cases:
        expected = case.get("expected_skill")
        try:
            raw = run_command(args.route_cmd, case["prompt"], args.timeout)
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            results.append({"id": case["id"], "expected": expected, "picked": None, "status": "error", "reason": str(exc)})
            continue
        picked = next((name for name in known if name in raw), None)
        if picked is None:
            lowered = raw.lower()
            for name in known:
                short = name.replace("macos-liquid-glass-", "").replace("-ui", "").replace("-", " ").strip()
                if short and short in lowered:
                    picked = name
                    break
        status = "pass" if picked == expected else ("error" if picked is None else "fail")
        results.append({"id": case["id"], "expected": expected, "picked": picked, "status": status, "reason": raw.strip()[:200]})

    if not args.json:
        for item in results:
            mark = {"pass": "PASS", "fail": "FAIL", "error": "ERR "}[item["status"]]
            print(f"{mark} {item['id']}: expected {item['expected']}, picked {item['picked']}")
        counts = {n: sum(1 for r in results if r["status"] == n) for n in ("pass", "fail", "error")}
        print(f"\n{counts['pass']} correct, {counts['fail']} misrouted, {counts['error']} unparsable (of {len(results)})")
    else:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    return 1 if any(r["status"] != "pass" for r in results) else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="list fixtures and exit")
    parser.add_argument("--routing", action="store_true", help="lexical routing smoke signal only (not a gate)")
    parser.add_argument("--gate-routing", action="store_true", help="fail when the lexical router disagrees")
    parser.add_argument(
        "--route-cmd",
        help="real trigger test: command that reads a prompt and prints the single skill name it would load",
    )
    parser.add_argument("--skill", action="append", help="only cases owned by this skill (repeatable)")
    parser.add_argument("--id", action="append", help="only these eval ids (repeatable)")
    parser.add_argument("--agent-cmd", help="command that reads a prompt on stdin and prints the answer")
    parser.add_argument("--judge-cmd", help="command that reads a JSON case on stdin and prints a JSON verdict")
    parser.add_argument("--responses", help="JSONL of {id, response} recorded answers")
    parser.add_argument("--keyword", action="store_true", help="offline keyword heuristic scoring")
    parser.add_argument("--out", help="write {id, response, elapsed_ms} for every scored case")
    parser.add_argument("--timeout", type=float, default=300.0, help="per-command timeout in seconds")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    cases = load_cases(args.skill, args.id)

    if args.list:
        for case in cases:
            print(f"{case['id']:<14} {case.get('_owner'):<32} -> {case.get('expected_skill')}")
        print(f"\n{len(cases)} cases")
        return 0
    if not cases:
        print("no eval cases matched the filter", file=sys.stderr)
        return 2
    if args.routing:
        return routing_check(args, cases)
    if args.route_cmd:
        return route_agent_check(args, cases)
    return report(args, cases)


if __name__ == "__main__":
    sys.exit(main())
