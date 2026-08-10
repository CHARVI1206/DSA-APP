# DSA Mastery Platform

A comprehensive platform for mastering Data Structures and Algorithms with AI assistance, a logic-first problem-solving framework, and spaced repetition.

## Tech Stack
* **Frontend:** Streamlit 1.36+ (multi-page app)
* **Database/Auth:** Supabase (PostgreSQL)
* **AI:** Google Gemini (2.0 Flash)
* **Code Execution:** Piston API
* **Charts:** Plotly

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a Supabase project and execute `database/schema.sql` in the SQL editor to create all tables, policies, and seed data.
3. Obtain a Gemini API key from Google AI Studio.
4. Add your secrets to `.streamlit/secrets.toml`:
   ```toml
   SUPABASE_URL = "your-project-url"
   SUPABASE_KEY = "your-anon-key"
   GEMINI_API_KEY = "your-gemini-key"
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## Features
* **Roadmap:** Structured learning path across 19 DSA topics.
* **AI Notes:** On-demand generation of explanations, complexity analysis, and cheat sheets.
* **Logic Gate:** Structured pre-coding reasoning validated by AI.
* **Code Editor:** In-browser coding with Python, C++, and Java execution.
* **Flashcards:** Spaced repetition (SM-2 variant) for long-term retention.
* **Mistakes Journal:** Track and categorize recurring errors.
* **Analytics:** XP, streaks, heatmaps, and achievements.
