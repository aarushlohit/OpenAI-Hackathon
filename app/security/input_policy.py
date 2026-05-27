from urllib.parse import urlparse

from app.core.errors import UnsafeInputError
from app.schemas.investigation import InvestigationInputKind, InvestigationRequest


class IntakePolicy:
    blocked_url_schemes = {"file", "ftp", "gopher", "javascript", "data"}

    def validate(self, request: InvestigationRequest) -> None:
        if "\x00" in request.raw_input:
            raise UnsafeInputError("Input contains null bytes")
        if request.kind == InvestigationInputKind.URL:
            self._validate_url(request.raw_input)

    def _validate_url(self, value: str) -> None:
        parsed = urlparse(value)
        if parsed.scheme.lower() in self.blocked_url_schemes:
            raise UnsafeInputError(f"Blocked URL scheme: {parsed.scheme}")
        if parsed.scheme.lower() not in {"http", "https"}:
            raise UnsafeInputError("Only HTTP and HTTPS URLs are accepted")
        if not parsed.netloc:
            raise UnsafeInputError("URL must include a hostname")

