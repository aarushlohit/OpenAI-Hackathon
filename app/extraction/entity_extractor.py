import re
from urllib.parse import urlparse

from app.models.investigation_context import InvestigationEntities


class EntityExtractor:
    url_pattern = re.compile(r"https?://[^\s)>\"]+", re.IGNORECASE)
    email_pattern = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
    telegram_pattern = re.compile(r"(?:t\.me/|@)([A-Za-z0-9_]{5,32})")
    upi_pattern = re.compile(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b")

    def extract(self, text: str) -> InvestigationEntities:
        urls = self._unique(self.url_pattern.findall(text))
        domains = self._unique(self._domain(url) for url in urls if self._domain(url))
        emails = self._unique(self.email_pattern.findall(text))
        telegram_handles = self._unique(self.telegram_pattern.findall(text))
        upi_ids = [value for value in self._unique(self.upi_pattern.findall(text)) if value not in emails]
        return InvestigationEntities(
            urls=urls,
            domains=domains,
            emails=emails,
            telegram_handles=telegram_handles,
            upi_ids=upi_ids,
        )

    def _domain(self, url: str) -> str:
        return urlparse(url).netloc.lower()

    def _unique(self, values) -> list[str]:
        return sorted({value.strip().rstrip(".,") for value in values if value})

