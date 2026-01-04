# 015 — Plan

1. Add minimal HTTP client dependency to the agent for LLM calls.
2. Implement OpenAI-compatible chat completions integration (base URL + key + model).
3. Keep a stub fallback when LLM isn’t configured.
4. Add `.env.example` variables and document how to enable `CHAT_BACKEND=http`.
5. Rebuild containers and verify:
   - stub mode works without keys
   - LLM mode works when keys are provided
