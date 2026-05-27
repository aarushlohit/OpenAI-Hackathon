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

- Text: OpenAI, NVIDIA Nemotron Omni, Pollinations.
- Vision: OpenAI Vision, NVIDIA Nemotron Omni, Pollinations.
- Audio: OpenAI Audio, NVIDIA Nemotron Omni.
- Embeddings: OpenAI, Pollinations.

Provider responses are normalized into `ProviderResponse` descendants before leaving provider classes. Raw provider payloads never reach agents.

