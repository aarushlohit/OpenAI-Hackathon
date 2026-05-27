# Provider Capabilities

Provider access is isolated behind gateway routers.

Text:

- OpenAI: primary reasoning provider.
- NVIDIA NIM: fallback and scale provider.
- Pollinations: emergency optional fallback.

Vision:

- OpenAI Vision: primary multimodal analysis.
- NVIDIA NIM Vision: fallback multimodal resilience.
- Pollinations Vision: optional fallback.

Audio:

- OpenAI Audio: primary transcription and audio analysis.
- NVIDIA NIM Audio: fallback transcription.

Embeddings:

- OpenAI: primary embeddings.
- Pollinations: optional embedding fallback.

Agents consume intelligence services and typed outputs. They do not consume provider clients.

