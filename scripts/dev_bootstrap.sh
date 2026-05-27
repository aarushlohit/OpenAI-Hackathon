#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[BOOT] Hermes-X development bootstrap"

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "[ENV] Created .env from .env.example"
else
  echo "[ENV] .env present"
fi

python -m compileall -q app tests hermes.py main.py scripts/final_runtime_validation.py
echo "[PYTHON] Compile check passed"

if command -v docker >/dev/null 2>&1; then
  docker compose config >/tmp/hermes_compose_config.txt
  echo "[DOCKER] Compose configuration valid"
else
  echo "[DOCKER] Docker CLI not found; install Docker for full runtime boot"
fi

if grep -q "^OPENAI_API_KEY=$" .env; then
  echo "[PROVIDER] OPENAI_API_KEY missing"
fi

if grep -q "^NVIDIA_NIM_API_KEY=$" .env; then
  echo "[PROVIDER] NVIDIA_NIM_API_KEY missing"
fi

echo "[BOOT] Development bootstrap complete"

