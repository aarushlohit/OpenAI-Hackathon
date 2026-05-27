# Provider Failover

Text priority:

1. OpenAI
2. NVIDIA NIM
3. Pollinations AI emergency fallback

Vision priority:

1. OpenAI Vision
2. NVIDIA NIM Vision
3. Pollinations Vision

Audio priority:

1. OpenAI Audio
2. NVIDIA NIM Audio

Embedding priority:

1. OpenAI
2. Pollinations

Fallback conditions:

- Rate limits.
- Timeouts.
- Quota failures.
- Temporary provider unavailability.
- Invalid provider responses.
- Open provider circuits.

Provider failures emit `provider_failed`. Successful fallback emits `provider_failover`.

Agents do not know which provider served a request. They receive validated domain responses from services above the gateway.

The gateway failover core owns retry loops, circuit breaker checks, latency traces, and provider metrics.
