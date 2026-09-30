# Evals

Skill quality rots quietly: a `SKILL.md` grows, a reference gets renamed, and the
agent still answers confidently — just worse. The fixtures in `skills/*/evals/`
plus the two scripts in `scripts/` exist to catch that.

## What each script does

| Script | Purpose | Blocking |
| --- | --- | --- |
| `scripts/validate_skills.py` | Structure, frontmatter, reference integrity, token consistency, eval schema, routing coverage | Yes (CI, `--strict`) |
| `scripts/run_evals.py` | Actually scores agent answers against the fixtures | Run manually / in your own harness |
| `tests/` | Unit tests for both scripts (validator findings, negation-aware scoring, skip handling) | Yes (CI) |

```bash
python3 -m unittest discover -s tests       # tests for the two scripts
python3 scripts/validate_skills.py --strict # fails on errors and warnings
python3 scripts/run_evals.py --list         # what is covered
python3 scripts/run_evals.py --route-cmd ./route.sh    # trigger test
python3 scripts/run_evals.py --agent-cmd ./agent.sh --judge-cmd ./judge.sh
```

`validate_skills.py` is deterministic and offline, so it gates every pull request.
`run_evals.py` needs a model, so it is not wired into CI — bring your own agent.

## Fixture schema

One JSON object per line, in any `*.jsonl` under a skill's `evals/` directory.
A fixture lives with the skill that owns the scenario, but `expected_skill` may
point at a different skill — that is how routing handoffs get covered.

```json
{"id": "web-003",
 "prompt": "给地图应用设计 Liquid Glass 控制层。",
 "expected_skill": "macos-liquid-glass-ui",
 "must_include": ["glass-clear", "floating controls", "rich background contrast"],
 "must_not": ["glass map canvas"],
 "aliases": {"glass-clear": ["clear glass", "clear 材质"]},
 "notes": "optional free text",
 "kind": "optional tag, e.g. routing / anti-pattern"}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Unique across the whole repo. Prefix by area (`web-`, `native-`, `icon-`, `inspira-`, `route-`). |
| `prompt` | yes | A realistic user request, in the user's own words. |
| `expected_skill` | yes | The skill that should handle it. Must be a real skill directory. |
| `must_include` | yes | Behaviours a correct answer cannot omit. |
| `must_not` | yes | Concrete failures: forbidden APIs, anti-patterns, misroutes. |
| `aliases` | no | Alternative wordings that satisfy a `must_include` entry in keyword mode. |
| `notes` / `kind` / `severity` / `tags` | no | Metadata; ignored by scoring. |

Writing rules that matter more than the schema:

- A check must be **decidable by reading the answer**. "Mentions accessibility"
  is decidable; "is accessible" is not.
- `must_not` should name a **specific observable mistake** ("glass every row"),
  not a general quality ("bad design").
- Add a fixture **every time a real failure is found**. A bug that produced a new
  fixture is a bug that cannot silently return.

## Scoring modes

Keyword mode (`--keyword`) is a blunt offline smoke test: every `must_include`
must appear literally or via `aliases`. Useful for routing handoffs and forbidden
API strings, hopeless for semantics — expect false failures on cases like
`["single core metaphor"]`.

One deliberate refinement: a hit on `must_not` that sits inside a negation window
(within ~24 characters of 不要 / 禁止 / 避免 / never / do not / instead of) is
**not** counted as a violation, because a correct answer often has to *name* the
thing it refuses. Plain mentions still fail:

```text
禁止 call a remote image API，只使用宿主能力   -> pass
我会 call a remote image API 来生成            -> violation
```

This cuts most mechanical false positives but not all of them. `must_include`
entries phrased as English semantics ("single core metaphor") remain
undecidable by substring — **do not treat keyword mode as a regression baseline
for semantic cases; use `--judge-cmd` there.** Keyword mode is only trustworthy
for cases whose checks are literal strings (skill names, API names, forbidden
options) or that carry `aliases`.

Judge mode (`--judge-cmd`) is the real grader. The judge receives JSON on stdin:

```json
{"id": "...", "prompt": "...", "response": "...", "expected_skill": "...",
 "must_include": ["..."], "must_not": ["..."]}
```

and must print JSON on stdout:

```json
{"pass": false, "missing": ["frozen palette"], "violations": ["glass every row"],
 "reason": "one sentence"}
```

The judge prompt itself is your call, but keep it strict about `must_not`:
a fabricated feature or a forbidden API must fail the case even if everything
else is well written. Using a different model family for the judge than for the
answer catches more than self-grading does.

`--agent-cmd` reads the prompt on stdin and prints the final answer on stdout;
combine it with `--out responses.jsonl` to freeze a run and turn it into an
offline regression baseline:

```bash
python3 scripts/run_evals.py --agent-cmd ./agent.sh --out /tmp/run.jsonl --keyword
python3 scripts/run_evals.py --responses /tmp/run.jsonl --keyword   # no network
```

Copy-paste starting points for the three adapters live in `scripts/examples/`:
`agent.sh` (answer the prompt), `judge.sh` (grade a case, with the rubric
inlined) and `route.sh` (trigger test). Each defaults to `AGENT_CMD="claude -p"`
and takes `AGENT_CMD` from the environment, so they work with any CLI that reads
stdin and prints stdout:

```bash
AGENT_CMD="codex exec --skip-git-repo-check -" \
  python3 scripts/run_evals.py --route-cmd ./scripts/examples/route.sh
```

For `--agent-cmd`, install the skill under test first — otherwise you measure
the model, not the skill.

## Trigger tests are separate

Answer quality and trigger quality fail differently. A skill can answer a
scenario perfectly while never being selected for it, because selection is driven
by the frontmatter `description` alone.

- `--route-cmd ./route.sh` is the real trigger test: the command receives the raw
  user prompt and prints the single skill name it would load. Mismatches are
  routing bugs — fix the description, not the fixture.
- `--routing` is a lexical smoke signal that compares prompt wording with the
  descriptions. Chinese prompts against English tokens score poorly and this is
  **not** a gate; use it only to spot a description that stopped mentioning a
  term entirely.

## Coverage expectations enforced by CI

- Every skill ships `SKILL.md`, `agents/openai.yaml`, a non-empty `references/`
  directory and at least three eval cases expecting that skill's own failure modes.
- Every local reference exists (backticked paths are skill-root relative,
  markdown links are file relative) and every shipped reference is reachable
  from `SKILL.md`.
- Every `macos-liquid-glass-*` name mentioned anywhere resolves to a real skill,
  and every `SKILL.md` says when to hand off to the other two.
- Every `--lg-*` token mentioned in the Web skill's docs is declared in
  `assets/foundation.css` — this is what stops an adapter example from quietly
  referencing a variable that no longer exists.
