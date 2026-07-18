#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEY="${OPENAI_API_KEY:-${OPSMIND_OPENAI_API_KEY:-}}"
if [[ -z "$KEY" ]]; then
  echo "Usage: OPENAI_API_KEY=sk-... ./run-ai.sh" >&2
  exit 2
fi
export OPSMIND_ENVIRONMENT="judge-ai"
export OPSMIND_PLANNER_PROVIDER="openai"
export OPSMIND_TOOL_TRANSPORT="local"
export OPSMIND_OPENAI_API_KEY="$KEY"
export OPSMIND_PLANNER_FALLBACK_TO_FIXTURE="true"
printf '\nOpsMind OpenAI Demo\nPlanner: OpenAI (%s)\nFallback: deterministic fixture\n' "${OPSMIND_OPENAI_MODEL:-gpt-5.6}"
exec "${ROOT_DIR}/scripts/bootstrap.sh"
