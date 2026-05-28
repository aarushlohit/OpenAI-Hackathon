import json
import re
from typing import Any


INJECTION_PATTERNS = re.compile(
    r"ignore previous|developer message|system prompt|you are now|forget instructions",
    re.IGNORECASE,
)

SEVERITY_VALUES = {"low", "medium", "high", "critical"}
VALID_SEVERITY = SEVERITY_VALUES
SIGNAL_SOURCES = {"ai_reasoned", "deterministic", "hybrid", "heuristic_fallback"}


class ModelOutputValidationError(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class ModelOutputValidator:
    def validate_behavior_output(self, data: dict[str, Any]) -> dict[str, Any]:
        self._check_injection(json.dumps(data))
        self._reject_unknown(
            data,
            {"risk_score", "risk_level", "confidence", "signals", "summary", "recommended_action", "reasoning_type"},
        )
        self._require_keys(
            data,
            ["risk_score", "confidence", "signals", "summary", "recommended_action", "reasoning_type"],
        )
        self._validate_risk_score(data)
        self._validate_confidence(data)
        self._validate_signals(data)
        self._validate_string(data, "summary", max_length=2000)
        self._validate_string(data, "reasoning_type", max_length=100)
        return data

    def validate_osint_output(self, data: dict[str, Any]) -> dict[str, Any]:
        self._check_injection(json.dumps(data))
        self._reject_unknown(
            data,
            {"reputation_score", "confidence", "indicators", "summary", "reasoning_type", "recommended_action"},
        )
        self._require_keys(data, ["reputation_score", "confidence", "indicators", "summary", "reasoning_type"])
        self._validate_risk_score(data, key="reputation_score")
        self._validate_confidence(data)
        self._validate_indicators(data)
        self._validate_string(data, "summary", max_length=2000)
        return data

    def validate_vision_output(self, data: dict[str, Any]) -> dict[str, Any]:
        self._check_injection(json.dumps(data))
        self._reject_unknown(
            data,
            {
                "risk_score",
                "risk_level",
                "confidence",
                "ocr_text",
                "ocr_confidence",
                "artifacts",
                "suspicious_elements",
                "summary",
                "recommended_action",
                "reasoning_type",
            },
        )
        self._require_keys(data, ["risk_score", "confidence", "artifacts", "summary", "reasoning_type"])
        self._validate_risk_score(data)
        self._validate_confidence(data)
        self._validate_artifacts(data)
        self._validate_string(data, "summary", max_length=2000)
        return data

    def validate_audio_output(self, data: dict[str, Any]) -> dict[str, Any]:
        self._check_injection(json.dumps(data))
        self._reject_unknown(
            data,
            {
                "risk_score",
                "risk_level",
                "confidence",
                "signals",
                "summary",
                "recommended_action",
                "reasoning_type",
                "transcription",
                "transcription_confidence",
                "duration_seconds",
                "detected_patterns",
            },
        )
        self._require_keys(data, ["risk_score", "confidence", "signals", "summary", "reasoning_type"])
        self._validate_risk_score(data)
        self._validate_confidence(data)
        self._validate_signals(data)
        self._validate_string(data, "summary", max_length=2000)
        return data

    def validate_generic(self, data: dict[str, Any], required_keys: list[str]) -> dict[str, Any]:
        self._check_injection(json.dumps(data))
        self._require_keys(data, required_keys)
        if "confidence" in data:
            self._validate_confidence(data)
        if "risk_score" in data:
            self._validate_risk_score(data)
        if "reputation_score" in data:
            self._validate_risk_score(data, key="reputation_score")
        return data

    def _check_injection(self, raw: str) -> None:
        if INJECTION_PATTERNS.search(raw):
            raise ModelOutputValidationError("Model output contains prompt-injection language")

    def _require_keys(self, data: dict[str, Any], keys: list[str]) -> None:
        missing = [k for k in keys if k not in data]
        if missing:
            raise ModelOutputValidationError(f"Missing required keys: {', '.join(missing)}")

    def _reject_unknown(self, data: dict[str, Any], allowed: set[str]) -> None:
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise ModelOutputValidationError(f"Unexpected model output fields: {', '.join(unknown)}")

    def _validate_risk_score(self, data: dict[str, Any], key: str = "risk_score") -> None:
        value = data.get(key)
        if value is None:
            return
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise ModelOutputValidationError(f"{key} must be an integer") from exc
        if not (0 <= value <= 100):
            raise ModelOutputValidationError(f"{key} must be 0-100, got {value}")
        data[key] = value

    def _validate_confidence(self, data: dict[str, Any]) -> None:
        value = data.get("confidence")
        if value is None:
            return
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise ModelOutputValidationError("confidence must be a number") from exc
        if not (0.0 <= value <= 1.0):
            raise ModelOutputValidationError(f"confidence must be 0.0-1.0, got {value}")
        data["confidence"] = round(min(1.0, max(0.0, value)), 4)

    def _validate_signals(self, data: dict[str, Any]) -> None:
        signals = data.get("signals", [])
        if not isinstance(signals, list):
            raise ModelOutputValidationError("signals must be a list")
        for i, signal in enumerate(signals):
            if not isinstance(signal, dict):
                raise ModelOutputValidationError(f"signals[{i}] must be an object")
            for required in ("name", "severity", "confidence", "explanation", "source"):
                if required not in signal:
                    raise ModelOutputValidationError(f"signals[{i}] missing key: {required}")
            severity = signal.get("severity", "").lower()
            if severity not in SEVERITY_VALUES:
                raise ModelOutputValidationError(
                    f"signals[{i}].severity must be one of {SEVERITY_VALUES}, got '{severity}'"
                )
            signal["severity"] = severity
            conf = signal.get("confidence")
            if conf is not None:
                signal["confidence"] = round(min(1.0, max(0.0, float(conf))), 4)
            self._validate_source(signal.get("source"), f"signals[{i}].source")

    def _validate_indicators(self, data: dict[str, Any]) -> None:
        indicators = data.get("indicators", [])
        if not isinstance(indicators, list):
            raise ModelOutputValidationError("indicators must be a list")
        for i, ind in enumerate(indicators):
            if not isinstance(ind, dict):
                raise ModelOutputValidationError(f"indicators[{i}] must be an object")
            for required in ("name", "severity", "confidence", "evidence", "source"):
                if required not in ind:
                    raise ModelOutputValidationError(f"indicators[{i}] missing key: {required}")
            severity = ind.get("severity", "").lower()
            if severity not in SEVERITY_VALUES:
                raise ModelOutputValidationError(
                    f"indicators[{i}].severity must be one of {SEVERITY_VALUES}, got '{severity}'"
                )
            ind["severity"] = severity
            conf = ind.get("confidence")
            if conf is not None:
                ind["confidence"] = round(min(1.0, max(0.0, float(conf))), 4)
            self._validate_source(ind.get("source"), f"indicators[{i}].source")

    def _validate_artifacts(self, data: dict[str, Any]) -> None:
        artifacts = data.get("artifacts", [])
        if not isinstance(artifacts, list):
            raise ModelOutputValidationError("artifacts must be a list")
        for i, art in enumerate(artifacts):
            if not isinstance(art, dict):
                raise ModelOutputValidationError(f"artifacts[{i}] must be an object")
            for required in ("type", "description", "confidence", "source"):
                if required not in art:
                    raise ModelOutputValidationError(f"artifacts[{i}] missing key: {required}")
            severity = art.get("severity", "medium").lower()
            if severity not in SEVERITY_VALUES:
                raise ModelOutputValidationError(
                    f"artifacts[{i}].severity must be one of {SEVERITY_VALUES}, got '{severity}'"
                )
            art["severity"] = severity
            conf = art.get("confidence")
            if conf is not None:
                art["confidence"] = round(min(1.0, max(0.0, float(conf))), 4)
            self._validate_source(art.get("source"), f"artifacts[{i}].source")

    def _validate_source(self, value: Any, field: str) -> None:
        if value not in SIGNAL_SOURCES:
            raise ModelOutputValidationError(f"{field} must be one of {SIGNAL_SOURCES}")

    def _validate_string(self, data: dict[str, Any], key: str, max_length: int = 2000) -> None:
        value = data.get(key)
        if value is not None and isinstance(value, str):
            data[key] = value[:max_length]
