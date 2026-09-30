#!/usr/bin/env bash
# Example adapter for:
#   python3 scripts/run_evals.py --agent-cmd ./scripts/examples/agent.sh --judge-cmd ./scripts/examples/judge.sh
#
# The runner sends one raw user prompt on stdin and expects the answer on
# stdout. Point AGENT_CMD at your agent CLI. The agent should be given the
# skill under test (the usual way is to install it and let the description
# trigger it), otherwise you are measuring the model, not the skill.
set -euo pipefail

AGENT_CMD=${AGENT_CMD:-"claude -p"}

cat | $AGENT_CMD
