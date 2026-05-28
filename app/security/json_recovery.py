from __future__ import annotations

import json
import re
from typing import Any


class JsonRecoveryError(ValueError):
    pass


_TRAILING_COMMA = re.compile(r",\s*([}\]])")


def recover_json_object(content: str) -> dict[str, Any]:
    """Recover a JSON object from provider text or fail closed.

    This accepts common wrapper mistakes, but does not invent missing values.
    Truncated strings/objects remain invalid and raise JsonRecoveryError.
    """

    if not isinstance(content, str) or not content.strip():
        raise JsonRecoveryError("empty JSON content")

    candidates = _candidates(content)
    last_error = "no JSON candidate found"
    for candidate in candidates:
        candidate = _TRAILING_COMMA.sub(r"\1", candidate.strip())
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = str(exc)
            continue
        if not isinstance(parsed, dict):
            raise JsonRecoveryError("provider JSON is not an object")
        return parsed
    raise JsonRecoveryError(last_error)


def _candidates(content: str) -> list[str]:
    stripped = content.strip()
    cleaned = stripped.replace("```json", "```").strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned[3:-3].strip()

    candidates = [cleaned]
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        candidates.append(cleaned[start : end + 1])
    return candidates
