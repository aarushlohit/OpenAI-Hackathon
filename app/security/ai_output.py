import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.core.errors import UnsafeInputError

ModelT = TypeVar("ModelT", bound=BaseModel)


class AIOutputValidator:
    injection_terms = re.compile(r"ignore previous|developer message|system prompt", re.IGNORECASE)

    def parse_model(self, raw: str, model_type: type[ModelT]) -> ModelT:
        sanitized = self._sanitize(raw)
        try:
            payload = json.loads(sanitized)
        except json.JSONDecodeError:
            payload = self._recover_json_object(sanitized)
        try:
            return model_type.model_validate(payload)
        except ValidationError as error:
            raise UnsafeInputError("AI output failed schema validation") from error

    def _sanitize(self, raw: str) -> str:
        if self.injection_terms.search(raw):
            raise UnsafeInputError("AI output contained prompt-injection language")
        return raw.replace("\x00", "").strip()

    def _recover_json_object(self, raw: str) -> dict:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise UnsafeInputError("AI output did not contain a JSON object")
        return json.loads(raw[start : end + 1])

