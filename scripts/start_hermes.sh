#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "HERMES-X OPERATIONAL BOOT"
echo "Replay Engine: STARTING"
echo "Threat Graph: STARTING"
echo "Runtime: STARTING"

./scripts/dev_bootstrap.sh

docker compose up --build -d

echo "[RUNTIME] Waiting for API liveness"
for attempt in $(seq 1 30); do
  if curl -fsS http://localhost:8000/v1/runtime/liveness >/tmp/hermes_liveness.json; then
    break
  fi
  sleep 2
  if [ "$attempt" = "30" ]; then
    echo "[RUNTIME] API liveness did not become ready"
    docker compose ps
    exit 1
  fi
done

python scripts/final_runtime_validation.py --json

echo "HERMES-X OPERATIONAL"
echo "Replay Engine: ACTIVE"
echo "Threat Graph: ACTIVE"
echo "Providers: CONFIGURED"
echo "Runtime: HEALTHY"
echo "[UI] Start Flutter with: cd frontend/flutter_app && flutter pub get && flutter run"

