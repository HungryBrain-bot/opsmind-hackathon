#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export OPSMIND_ENVIRONMENT="judge-demo"
export OPSMIND_PLANNER_PROVIDER="fixture"
export OPSMIND_TOOL_TRANSPORT="local"
export OPSMIND_OPENAI_API_KEY=""
printf '\nOpsMind Offline Demo\nPlanner: deterministic fixture\nAPI key: not required\n'
exec "${ROOT_DIR}/scripts/bootstrap.sh"
