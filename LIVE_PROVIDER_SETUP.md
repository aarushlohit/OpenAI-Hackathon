# Live Provider Setup

Configure providers through environment variables only.

OpenAI:

- `OPENAI_API_KEY`
- `OPENAI_TEXT_MODEL`
- `OPENAI_VISION_MODEL`
- `OPENAI_AUDIO_MODEL`
- `OPENAI_EMBEDDING_MODEL`

NVIDIA NIM Gemma 3n:

- `NVIDIA_NIM_API_KEY`
- `NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1`
- `NVIDIA_NIM_TEXT_MODEL=google/gemma-3n-e2b-it`
- `NVIDIA_NIM_VISION_MODEL=google/gemma-3n-e2b-it`
- `NVIDIA_NIM_AUDIO_MODEL=google/gemma-3n-e2b-it`

Pollinations:

- `POLLINATIONS_CHAT_URL=https://gen.pollinations.ai/v1/chat/completions`
- `POLLINATIONS_TEXT_MODEL=openai`
- `POLLINATIONS_VISION_MODEL=openai`

Provider secrets are masked by Pydantic secret fields and never passed to agents.

