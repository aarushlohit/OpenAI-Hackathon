import argparse
import asyncio
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.container import AppContainer
from app.runtime.runtime_validator import RuntimeValidator


def get_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        try:
            result = subprocess.run(
                ["curl", "-fsS", url],
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return json.loads(result.stdout)
        except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
            return None


def live_runtime_report(base_url: str) -> dict | None:
    health = get_json(f"{base_url}/v1/runtime/health")
    bootstrap = get_json(f"{base_url}/v1/runtime/bootstrap")
    providers = get_json(f"{base_url}/v1/providers/capabilities")
    if health is None or bootstrap is None or providers is None:
        return None
    ready = bool(bootstrap.get("ready")) and health.get("status") == "ok"
    return {
        "ready": ready,
        "checks": [
            {"name": "runtime_health", "status": health.get("status", "degraded"), "detail": "live api"},
            {
                "name": "runtime_bootstrap",
                "status": "ok" if bootstrap.get("ready") else "degraded",
                "detail": "live api",
            },
            {
                "name": "provider_capabilities",
                "status": "ok" if providers else "degraded",
                "detail": ",".join(sorted(providers.keys())),
            },
        ],
        "status": {
            "postgres": "healthy" if ready else "degraded",
            "redis": "healthy" if ready else "degraded",
            "providers": "healthy" if providers else "degraded",
            "replay": "healthy" if health.get("status") == "ok" else "degraded",
            "websocket": "healthy" if health.get("status") == "ok" else "degraded",
            "graph": "healthy",
        },
    }


async def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Hermes-X final runtime readiness.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when dependencies are degraded.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Live API base URL.")
    args = parser.parse_args()

    payload = live_runtime_report(args.base_url)
    if payload is None:
        container = AppContainer()
        report = await RuntimeValidator(container).validate()
        await container.redis_runtime.close()
        payload = report.model_dump(mode="json")
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Hermes-X runtime ready: {payload['ready']}")
        for check in payload["checks"]:
            print(f"- {check['name']}: {check['status']} {check.get('detail', '')}")
    return 0 if payload["ready"] or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
