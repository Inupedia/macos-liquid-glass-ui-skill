#!/usr/bin/env bash
# Example adapter for:
#   python3 scripts/run_evals.py --agent-cmd ./scripts/examples/agent.sh \
#     --judge-cmd ./scripts/examples/judge.sh
#
# The runner sends the eval case as JSON on stdin and expects a JSON verdict on
# stdout:
#   {"pass": bool, "missing": [...], "violations": [...], "reason": "..."}
set -euo pipefail

AGENT_CMD=${AGENT_CMD:-"claude -p"}
CASE=$(cat)

read -r -d '' RUBRIC <<'EOF' || true
You are grading one answer against a fixed rubric. Return JSON only:
{"pass": boolean, "missing": [string], "violations": [string], "reason": string}

Rules:
- "must_include" lists behaviours a correct answer cannot omit. A behaviour that
  is only implied, or contradicted later in the answer, does not count.
- "must_not" lists concrete failures. Naming a forbidden thing in order to
  refuse it is NOT a violation. Recommending it, or doing it, IS.
- Fabricated facts, invented APIs, or unverified claims presented as verified
  are violations.
- The answer may be in any language; judge meaning, not exact wording.
EOF

printf '%s\n\nCase to grade:\n%s\n' "$RUBRIC" "$CASE" | $AGENT_CMD
