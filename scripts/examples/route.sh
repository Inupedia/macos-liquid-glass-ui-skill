#!/usr/bin/env bash
# Example adapter for: python3 scripts/run_evals.py --route-cmd ./scripts/examples/route.sh
#
# The runner sends one raw user prompt on stdin and expects the name of the
# single skill this agent would load. Copy this file, point AGENT_CMD at your
# agent CLI, and keep the prompt strict — a verbose answer makes the router's
# parse unreliable.
set -euo pipefail

# Replace with your agent CLI. It must read the prompt on stdin and print the
# answer on stdout, e.g.
#   codex exec --skip-git-repo-check -
#   claude -p
#   llm -m gpt-4.1
AGENT_CMD=${AGENT_CMD:-"claude -p"}

PROMPT=$(cat)

read -r -d '' ROUTING_QUESTION <<'EOF' || true
You are routing a request to exactly one agent skill. Answer with the skill name
only, nothing else, no punctuation, no explanation.

Available skills:
- macos-liquid-glass-ui          (Web / Electron / Tauri page and component UI)
- macos-liquid-glass-native-ui   (native SwiftUI / AppKit app UI)
- macos-liquid-glass-icon        (App Icon / product icon artwork)

Request:
EOF

printf '%s\n%s\n' "$ROUTING_QUESTION" "$PROMPT" | $AGENT_CMD
