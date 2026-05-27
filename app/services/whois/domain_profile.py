from datetime import UTC, datetime
from urllib.parse import urlparse

from pydantic import BaseModel, Field


class DomainProfile(BaseModel):
    domain: str | None
    domain_age_days: int | None = Field(default=None, ge=0)
    ssl_valid: bool | None = None


class WhoisService:
    async def inspect(self, raw_input: str) -> DomainProfile:
        parsed = urlparse(raw_input)
        domain = parsed.netloc.lower() if parsed.netloc else None
        if not domain:
            return DomainProfile(domain=None)

        ssl_valid = parsed.scheme == "https"
        # Live WHOIS is deferred; deterministic age hints keep Phase 3 offline-safe.
        age = 3 if any(marker in domain for marker in ("new", "promo", "verify")) else None
        return DomainProfile(domain=domain, domain_age_days=age, ssl_valid=ssl_valid)


def days_since(created_at: datetime) -> int:
    return max((datetime.now(UTC) - created_at).days, 0)

