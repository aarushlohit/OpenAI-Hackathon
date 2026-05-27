# Provider Failover

Provider failover is centralized in `FailoverRouter`.

Failure triggers:

- rate limits.
- timeout.
- quota exhaustion.
- provider unavailable.
- circuit breaker open.
- invalid normalized response.

Routing:

- Text: OpenAI, NVIDIA Gemma 3n, Pollinations.
- Vision: OpenAI Vision, NVIDIA Gemma 3n, Pollinations.
- Audio: OpenAI Audio, NVIDIA Gemma 3n.
- Embeddings: OpenAI, Pollinations.

Provider responses are normalized into `ProviderResponse` descendants before leaving provider classes. Raw provider payloads never reach agents.

