# Current State

- Agent can run in stub mode or LLM-backed mode (OpenAI-compatible).
- API websocket chat can route either to stub or to the agent.

# How To Use

- For stub mode (no LLM): keep `CHAT_BACKEND=stub`.
- For LLM mode:
	- set `CHAT_BACKEND=http`
	- set `LLM_BACKEND=openai_compatible`
	- set `OPENAI_API_KEY` + `OPENAI_MODEL`

# What Changed

- Added OpenAI-compatible LLM calling code to the agent service.
- Added env vars + compose wiring to enable LLM-backed chat.
