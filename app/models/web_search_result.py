"""Data model for WebSearchAgent result."""

from typing import Any

from pydantic import BaseModel, Field


class WebSearchResult(BaseModel):
    """Result produced by the WebSearchAgent."""

    investigation_id: str
    extracted_entities: dict[str, list[str]] = Field(default_factory=dict)

    # Positive trust signals (reduce threat score)
    trust_signals: list[dict[str, Any]] = Field(default_factory=list)

    # Negative suspicion signals (raise threat score)
    suspicion_signals: list[dict[str, Any]] = Field(default_factory=list)

    # Entities confirmed legitimate via web search
    verified_entities: list[str] = Field(default_factory=list)

    # Entities that could not be verified
    unverified_entities: list[str] = Field(default_factory=list)

    # Net score adjustment (-50 to +40); negative = score reduction
    trust_delta: int = Field(default=0, ge=-50, le=40)

    # Human-readable web verification summary
    web_summary: str = ""

    # Whether OpenCode web search was actually performed
    search_performed: bool = False
