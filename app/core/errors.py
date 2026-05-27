class HermesError(Exception):
    """Base exception for domain-specific Hermes-X failures."""


class ProviderUnavailableError(HermesError):
    """Raised when an AI provider cannot satisfy the request."""


class UnsafeInputError(HermesError):
    """Raised when untrusted input violates intake policy."""

