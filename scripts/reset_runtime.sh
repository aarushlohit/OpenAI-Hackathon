#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ "${1:-}" = "--volumes" ]; then
  if [ "${CONFIRM_RESET:-}" != "YES" ]; then
    echo "Refusing to delete volumes without CONFIRM_RESET=YES"
    echo "Run: CONFIRM_RESET=YES ./scripts/reset_runtime.sh --volumes"
    exit 1
  fi
  docker compose down --volumes --remove-orphans
  echo "[RESET] Runtime stopped and volumes removed"
else
  docker compose down --remove-orphans
  echo "[RESET] Runtime stopped; volumes preserved"
fi

