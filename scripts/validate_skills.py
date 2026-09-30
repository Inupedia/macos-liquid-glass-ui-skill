#!/usr/bin/env python3
"""Validate the structure, references and eval fixtures of every Skill in this repo.

Usage:
    python3 scripts/validate_skills.py            # errors fail, warnings reported
    python3 scripts/validate_skills.py --strict   # warnings also fail
    python3 scripts/validate_skills.py --json     # machine-readable report

Exit code 0 when no blocking problem was found, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
# Backticked paths: `references/foo.md`, `assets/bar.css`
BACKTICK_REF_RE = re.compile(r"`((?:references|assets|evals|scripts)/[^`\s]+)`")
# Markdown links: [label](references/foo.md) — local, relative only
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
NAME_MENTION_RE = re.compile(r"\bmacos-liquid-glass-[a-z-]+")
FENCE_RE = re.compile(r"^```")
EVAL_REQUIRED_FIELDS = ("id", "prompt", "expected_skill", "must_include", "must_not")
EVAL_OPTIONAL_FIELDS = ("aliases", "notes", "severity", "tags", "kind")
MIN_EVAL_CASES_PER_SKILL = 3
MAX_DESCRIPTION_CHARS = 1024
MAX_NAME_CHARS = 64

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def strip_code_fences(text: str) -> str:
    """Remove fenced code blocks so example snippets are not read as real links."""
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def local_refs(text: str) -> set[str]:
    """Every relative resource path referenced by a document, in any link style.

    Backticked paths are skill-root relative (the convention used across
    SKILL.md and references/); markdown links are file relative (standard
    markdown). Both sets are returned together and each is accepted if it
    resolves against either base, so a document can mix the two styles safely.
    """
    refs: set[str] = set()
    for match in BACKTICK_REF_RE.finditer(text):
        refs.add(match.group(1))
    for match in MD_LINK_RE.finditer(text):
        target = match.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        refs.add(target.rstrip("/"))
    return refs


def resolves(ref: str, skill_dir: pathlib.Path, doc_dir: pathlib.Path) -> bool:
    return (skill_dir / ref).exists() or (doc_dir / ref).exists()


def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key_match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if key_match:
            fields[key_match.group(1)] = key_match.group(2).strip().strip("\"'")
    return fields


def check_openai_metadata(skill_name: str, path: pathlib.Path) -> None:
    if not path.exists():
        error(f"{skill_name}: missing agents/openai.yaml")
        return
    text = path.read_text(encoding="utf-8")
    for key in ("display_name", "short_description", "default_prompt"):
        match = re.search(rf"^\s*{key}:\s*(.+)$", text, re.M)
        if not match or len(match.group(1).strip().strip("\"'")) < 8:
            error(f"{path.relative_to(ROOT)}: missing or too short `{key}`")
    if "interface:" not in text:
        error(f"{path.relative_to(ROOT)}: missing top-level `interface:` key")
    if f"${skill_name}" not in text:
        warn(f"{path.relative_to(ROOT)}: default_prompt does not mention ${skill_name}")


def collect_eval_cases(skill_dir: pathlib.Path, skill_name: str) -> list[dict]:
    eval_dir = skill_dir / "evals"
    if not eval_dir.exists():
        error(f"{skill_name}: missing evals/ directory")
        return []
    files = sorted(eval_dir.glob("*.jsonl"))
    if not files:
        error(f"{skill_name}: evals/ contains no .jsonl fixture")
        return []

    cases: list[dict] = []
    for jsonl in files:
        for line_no, raw in enumerate(jsonl.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            where = f"{jsonl.relative_to(ROOT)}:{line_no}"
            try:
                item = json.loads(raw)
            except json.JSONDecodeError as exc:
                error(f"{where}: invalid JSON: {exc}")
                continue
            if not isinstance(item, dict):
                error(f"{where}: fixture must be a JSON object")
                continue
            for field in EVAL_REQUIRED_FIELDS:
                if field not in item:
                    error(f"{where}: missing required field `{field}`")
            unknown = sorted(set(item) - set(EVAL_REQUIRED_FIELDS) - set(EVAL_OPTIONAL_FIELDS))
            if unknown:
                warn(f"{where}: unknown field(s) {', '.join(unknown)}")
            for field in ("must_include", "must_not"):
                value = item.get(field)
                if not isinstance(value, list) or not value:
                    error(f"{where}: `{field}` must be a non-empty list")
                elif not all(isinstance(v, str) and len(v.strip()) >= 2 for v in value):
                    error(f"{where}: `{field}` entries must be strings of >= 2 chars")
            prompt = item.get("prompt")
            if not isinstance(prompt, str) or len(prompt.strip()) < 8:
                error(f"{where}: `prompt` missing or too short")
            item["_where"] = where
            item["_skill"] = skill_name
            cases.append(item)
    return cases


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args()

    # Repeated programmatic calls (tests, embedding) must not inherit the
    # previous run's findings.
    errors.clear()
    warnings.clear()

    if not SKILLS_DIR.is_dir():
        print("error: missing skills/ directory", file=sys.stderr)
        return 1

    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not skill_dirs:
        print("error: no skill directories found", file=sys.stderr)
        return 1
    skill_names = {p.name for p in skill_dirs}

    all_cases: list[dict] = []
    referenced_paths: dict[str, set[str]] = {}

    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            error(f"{skill_name}: missing SKILL.md")
            continue

        text = skill_file.read_text(encoding="utf-8")
        body = strip_code_fences(text)
        frontmatter = parse_frontmatter(text)
        if frontmatter is None:
            error(f"{skill_file.relative_to(ROOT)}: missing YAML frontmatter")
        else:
            extra = sorted(set(frontmatter) - {"name", "description"})
            if extra:
                warn(f"{skill_file.relative_to(ROOT)}: unexpected frontmatter key(s) {', '.join(extra)}")
            name = frontmatter.get("name", "")
            if name != skill_name:
                error(f"{skill_file.relative_to(ROOT)}: frontmatter name must match directory ({skill_name})")
            if not NAME_RE.match(skill_name) or len(skill_name) > MAX_NAME_CHARS:
                error(f"{skill_name}: directory name must be lowercase-hyphen and <= {MAX_NAME_CHARS} chars")
            description = frontmatter.get("description", "")
            if len(description) < 20:
                error(f"{skill_file.relative_to(ROOT)}: description missing or too short")
            elif len(description) > MAX_DESCRIPTION_CHARS:
                error(
                    f"{skill_file.relative_to(ROOT)}: description is {len(description)} chars "
                    f"(limit {MAX_DESCRIPTION_CHARS})"
                )

        check_openai_metadata(skill_name, skill_dir / "agents" / "openai.yaml")

        references_dir = skill_dir / "references"
        if not references_dir.is_dir() or not any(references_dir.glob("*.md")):
            error(f"{skill_name}: missing references/ (deep knowledge must live outside SKILL.md)")

        refs = local_refs(body)
        referenced_paths[skill_name] = refs
        for ref in sorted(refs):
            if not (skill_dir / ref).exists():
                error(f"{skill_file.relative_to(ROOT)}: referenced file not found: {ref}")

        # Orphans: shipped resources that SKILL.md never routes to.
        for folder in ("references", "assets"):
            directory = skill_dir / folder
            if not directory.is_dir():
                continue
            for path in sorted(directory.rglob("*")):
                if path.is_file() and str(path.relative_to(skill_dir)) not in refs:
                    warn(f"{path.relative_to(ROOT)}: not referenced from SKILL.md")

        # References may link to each other and to sibling references.
        for path in sorted(references_dir.glob("*.md")) if references_dir.is_dir() else []:
            for ref in sorted(local_refs(strip_code_fences(path.read_text(encoding="utf-8")))):
                if not resolves(ref, skill_dir, path.parent):
                    error(f"{path.relative_to(ROOT)}: referenced file not found: {ref}")

        # Token consistency: a skill that ships a token stylesheet must not have
        # docs referencing tokens that stylesheet never defines. Prefix notation
        # such as `--lg-chart-*` or `--lg-space-*` is allowed.
        css_path = skill_dir / "assets" / "foundation.css"
        if css_path.exists():
            css_text = css_path.read_text(encoding="utf-8")
            defined = set(re.findall(r"(--lg-[a-z0-9-]+)\s*:", css_text))
            docs = [skill_file] + sorted(references_dir.glob("*.md")) if references_dir.is_dir() else [skill_file]
            for path in docs:
                text = path.read_text(encoding="utf-8")
                for match in re.finditer(r"--lg-[a-z0-9-]+", text):
                    token = match.group(0)
                    if token.endswith("-") or text[match.end():match.end() + 1] == "*":
                        continue
                    if token not in defined:
                        error(
                            f"{path.relative_to(ROOT)}: undefined token {token} "
                            f"(not declared in {css_path.relative_to(ROOT)})"
                        )

        cases = collect_eval_cases(skill_dir, skill_name)
        if cases and len(cases) < MIN_EVAL_CASES_PER_SKILL:
            error(f"{skill_name}: needs at least {MIN_EVAL_CASES_PER_SKILL} eval cases, found {len(cases)}")
        own = [c for c in cases if c.get("expected_skill") == skill_name]
        if cases and len(own) < MIN_EVAL_CASES_PER_SKILL:
            warn(
                f"{skill_name}: only {len(own)} eval case(s) expect this skill; "
                f"add coverage for its own failure modes"
            )
        all_cases.extend(cases)

    # Eval-level cross checks.
    seen_ids: dict[str, str] = {}
    for case in all_cases:
        where = case["_where"]
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            error(f"{where}: `id` must be a non-empty string")
            continue
        if case_id in seen_ids:
            error(f"{where}: duplicate id {case_id} (also in {seen_ids[case_id]})")
        else:
            seen_ids[case_id] = where
        expected = case.get("expected_skill")
        if expected is not None:
            if not isinstance(expected, str) or expected not in skill_names:
                error(f"{where}: expected_skill references unknown skill {expected!r}")
        include = {s.lower() for s in case.get("must_include", []) if isinstance(s, str)}
        exclude = {s.lower() for s in case.get("must_not", []) if isinstance(s, str)}
        overlap = sorted(include & exclude)
        if overlap:
            error(f"{where}: must_include and must_not overlap on {overlap}")
        aliases = case.get("aliases")
        if aliases is not None:
            if not isinstance(aliases, dict):
                error(f"{where}: `aliases` must be an object mapping a check to alternative strings")
            else:
                for key, value in aliases.items():
                    if key.lower() not in include:
                        warn(f"{where}: aliases key {key!r} is not one of must_include")
                    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                        error(f"{where}: aliases[{key!r}] must be a list of strings")

    # Every macos-liquid-glass-* mention anywhere in the shipped docs must resolve.
    for path in sorted(ROOT.glob("**/*.md")):
        if any(part in {".git", "node_modules"} for part in path.parts):
            continue
        for mention in set(NAME_MENTION_RE.findall(strip_code_fences(path.read_text(encoding="utf-8")))):
            if mention not in skill_names:
                error(f"{path.relative_to(ROOT)}: mentions unknown skill {mention}")

    # Every other skill must be explicitly routed away from in each SKILL.md.
    for skill_dir in skill_dirs:
        text = strip_code_fences((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
        for other in sorted(skill_names - {skill_dir.name}):
            if other not in text:
                warn(f"{skill_dir.name}/SKILL.md: does not state when to hand off to {other}")

    report = {
        "skills": [p.name for p in skill_dirs],
        "eval_cases": len(all_cases),
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for message in errors:
            print(f"error: {message}")
        for message in warnings:
            print(f"warning: {message}")
        status = "OK" if not errors and not (args.strict and warnings) else "FAILED"
        print(
            f"\n{status}: {len(skill_names)} skills, {len(all_cases)} eval cases, "
            f"{len(errors)} error(s), {len(warnings)} warning(s)"
        )

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
