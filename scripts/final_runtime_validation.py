import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.container import AppContainer
from app.runtime.runtime_validator import RuntimeValidator


async def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Hermes-X final runtime readiness.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when dependencies are degraded.")
    args = parser.parse_args()

    container = AppContainer()
    report = await RuntimeValidator(container).validate()
    payload = report.model_dump(mode="json")
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Hermes-X runtime ready: {report.ready}")
        for check in report.checks:
            print(f"- {check.name}: {check.status} {check.detail}")
    return 0 if report.ready or not args.strict else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
