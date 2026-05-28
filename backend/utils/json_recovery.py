"""
JSON recovery — attempts to parse a JSON object from LLM output
that may contain markdown fences, preamble text, or trailing junk.
"""

import json
import re


def recover_json(text: str | None) -> dict | None:
    """
    Try hard to extract a JSON object from messy LLM output.
    Returns parsed dict or None if all attempts fail.
    """
    if not text:
        return None

    # 1. Strip markdown code fences
    text = re.sub(r"```(?:json)?", "", text).strip()

    # 2. Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 3. Find first { ... } block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # 4. Try to find last complete JSON object
    start = text.rfind("{")
    if start != -1:
        for end in range(len(text), start, -1):
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                continue

    return None
