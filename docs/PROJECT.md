# Project Documentation

## Architecture Decisions
* **Streamlit `st.navigation`:** Used for dynamic, role/auth-based multi-page routing introduced in 1.36.
* **Supabase for Backend:** chosen for seamless Auth + Postgres + Row Level Security (RLS) integration.
* **Piston API for Execution:** Cloud-based code execution to avoid running untrusted code locally.
* **Gemini 2.0 Flash:** Optimized for speed and cost-effectiveness in generating educational content.
* **AI Caching:** Responses from Gemini are aggressively cached in the `ai_cache` table to minimize latency and API costs.
* **SM-2 Clamped Algorithm:** Spaced repetition scheduling clamped to exactly 1, 3, 7, 14, 30, 60, and 90 days as per design specs.

## Database Schema (Key Tables)
- `profiles`: Extended user data.
- `topics`: 19-node hierarchical roadmap.
- `topic_notes`: Cached AI content.
- `problems`: Filterable problem bank.
- `logic_gate_responses`: Enforces reasoning before coding.
- `flashcards` / `user_flashcard_progress`: SM-2 system.
- `ai_cache`: Token and latency optimization.
