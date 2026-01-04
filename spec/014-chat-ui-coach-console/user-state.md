# Current State

- Web homepage is a chat-first coach console with a dark, sleek UI.
- It uses the existing WebSocket protocol (`chat.send` → `chat.message`).
- No A2UI actions or side-panel context is included.
- Chat responses default to a built-in stub coach (no agent/LLM required).

# How To Use

- Run `make run`.
- Open http://localhost:3000 and chat with the coach.

# What Changed

- Added Tailwind CSS + minimal styling baseline to the web app.
- Replaced the previous debug UI with a chat-first coach console.
- Updated the roadmap to prioritize chat UI first.
