#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
HOST="${OPSMIND_HOST:-127.0.0.1}"
PORT="${OPSMIND_PORT:-8000}"

log() { printf '\n[OpsMind] %s\n' "$1"; }
fail() { printf '\n[OpsMind] ERROR: %s\n' "$1" >&2; exit 1; }

command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "python3 is required."

if [[ ! -d "$VENV_DIR" ]]; then
  log "Creating virtual environment..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

log "Installing or verifying dependencies..."
python -m pip install --disable-pip-version-check -q -e "${ROOT_DIR}[dev]"

cd "$ROOT_DIR"
log "Starting OpsMind at http://${HOST}:${PORT}"
python -m uvicorn app.main:app --app-dir backend --host "$HOST" --port "$PORT" &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

for _ in {1..40}; do
  if python - "$HOST" "$PORT" <<'PY' >/dev/null 2>&1
import sys
import urllib.request
host, port = sys.argv[1], sys.argv[2]
with urllib.request.urlopen(f"http://{host}:{port}/api/v1/health", timeout=1) as response:
    raise SystemExit(0 if response.status == 200 else 1)
PY
  then
    log "Ready. Open http://${HOST}:${PORT}"
    wait "$SERVER_PID"
    exit $?
  fi
  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    wait "$SERVER_PID"
    fail "Server stopped before becoming healthy."
  fi
  sleep 0.25
done

fail "Health check timed out."
