# Multimodal Routing

Hermes-X treats providers as capability-bearing cognition engines.

Provider matrix:

- OpenAI: text, vision, audio, embeddings.
- NVIDIA NIM Gemma 3n: text, image understanding, audio understanding.
- Pollinations: emergency text and vision fallback, future embedding fallback.

Routing is governed by:

- `ProviderCapabilityRegistry`
- `ProviderPriorityResolver`
- existing modality routers
- `MultimodalRouter`

Environment priority:

- `PRIMARY_TEXT_PROVIDER`
- `FALLBACK_TEXT_PROVIDER`
- `LAST_RESORT_TEXT_PROVIDER`
- `PRIMARY_VISION_PROVIDER`
- `FALLBACK_VISION_PROVIDER`
- `LAST_RESORT_VISION_PROVIDER`
- `PRIMARY_AUDIO_PROVIDER`
- `FALLBACK_AUDIO_PROVIDER`
- `PRIMARY_EMBEDDING_PROVIDER`
- `FALLBACK_EMBEDDING_PROVIDER`

Agents still call gateway routers only. They do not know provider names, credentials, failover state, or model details.

