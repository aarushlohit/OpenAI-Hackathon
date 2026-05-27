import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for path in [Path(".env"), Path("app/.env")]:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    values.update({key: value for key, value in os.environ.items() if key.endswith("_API_KEY")})
    return values


def post_json(url: str, payload: dict, headers: dict[str, str] | None = None) -> tuple[bool, str]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read(2048).decode("utf-8", errors="replace")
            return 200 <= response.status < 300, f"HTTP {response.status}: {body[:120]}"
    except urllib.error.HTTPError as error:
        body = error.read(512).decode("utf-8", errors="replace")
        return False, f"HTTP {error.code}: {body[:120]}"
    except Exception as error:
        return False, f"{type(error).__name__}: {error}"


def check_nvidia(env: dict[str, str]) -> tuple[bool, str]:
    key = env.get("NVIDIA_NIM_API_KEY", "")
    if not key:
        return False, "NVIDIA_NIM_API_KEY missing"
    base_url = env.get("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
    model = env.get("NVIDIA_NIM_TEXT_MODEL", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
    return post_json(
        f"{base_url}/chat/completions",
        {
            "model": model,
            "messages": [{"role": "user", "content": "Reply with HERMES_PROVIDER_OK."}],
            "max_tokens": 16,
        },
        {"Authorization": f"Bearer {key}"},
    )


def check_pollinations(env: dict[str, str]) -> tuple[bool, str]:
    url = env.get("POLLINATIONS_CHAT_URL", "https://gen.pollinations.ai/v1/chat/completions")
    model = env.get("POLLINATIONS_TEXT_MODEL", "openai")
    headers = {}
    if env.get("POLLINATIONS_API_KEY"):
        headers["Authorization"] = f"Bearer {env['POLLINATIONS_API_KEY']}"
    ok, detail = post_json(
        url,
        {
            "model": model,
            "messages": [{"role": "user", "content": "Reply with HERMES_PROVIDER_OK."}],
            "max_tokens": 16,
        },
        headers,
    )
    if ok:
        return ok, detail
    legacy_url = env.get("POLLINATIONS_BASE_URL", "https://text.pollinations.ai").rstrip("/")
    legacy_prompt = urllib.parse.quote("Reply with HERMES_PROVIDER_OK.", safe="")
    try:
        with urllib.request.urlopen(f"{legacy_url}/{legacy_prompt}", timeout=20) as response:
            body = response.read(512).decode("utf-8", errors="replace")
            return 200 <= response.status < 300, f"legacy HTTP {response.status}: {body[:120]}"
    except Exception as error:
        return False, f"chat failed ({detail}); legacy failed ({type(error).__name__}: {error})"


def main() -> int:
    env = load_env()
    checks = {"nvidia_nim": check_nvidia(env), "pollinations": check_pollinations(env)}
    failed = False
    for provider, (ok, detail) in checks.items():
        status = "ok" if ok else "failed"
        print(f"{provider}: {status} - {detail}")
        failed = failed or not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
