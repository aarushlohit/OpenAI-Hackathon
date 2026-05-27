# Threat Scoring

The `ThreatScoringEngine` is the only component that converts agent findings into final severity.

Agents provide:

- Evidence.
- Indicators.
- Confidence.
- Explanations.

Threat engine provides:

- `final_score`
- `severity`
- `explanation`
- `contributing_factors`

Severity bands:

- `low`: 0-34
- `medium`: 35-64
- `high`: 65-84
- `critical`: 85-100

Current factors:

- Payment coercion.
- Telegram-only onboarding.
- Interview bypass claims.
- Refundable deposits.
- Newly registered domains.
- Suspicious TLDs.
- Offer-letter anomalies.
- Payment screenshots.

UI rule:

The frontend may display `final_score`, `severity`, and contributing factors. It must not recompute scores or alter severity bands.
