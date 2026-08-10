"""
DSA Mastery Platform — Main Application Entry Point

Premium DSA learning platform with AI-powered mentoring,
spaced repetition, and comprehensive analytics.
"""
import streamlit as st
import os

# ─── Page Config (must be first Streamlit command) ───────────────────────
st.set_page_config(
    page_title="DSA Mastery",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Load Custom CSS ────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Session State Initialization ───────────────────────────────────────
defaults = {
    "user": None,
    "session": None,
    "selected_topic": None,
    "selected_topic_slug": None,
    "selected_problem": None,
    "selected_problem_slug": None,
    "ai_chat_history": [],
    "ai_chat_mode": "mentor",
    "logic_gate_validated": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ─── Authentication Gate ────────────────────────────────────────────────
if st.session_state.user is None:
    # Show login/signup page
    from components.auth_forms import render_auth_page
    render_auth_page()
else:
    # ─── Update Streak on Session Start ─────────────────────────────
    if "streak_updated_today" not in st.session_state:
        try:
            from services.analytics_service import update_streak
            update_streak(st.session_state.user["id"])
            st.session_state.streak_updated_today = True
        except Exception:
            pass  # Non-critical, don't block the app

    # ─── Sidebar ────────────────────────────────────────────────────
    from components.sidebar import render_sidebar
    render_sidebar(st.session_state.user)

    # ─── Navigation ─────────────────────────────────────────────────
    dashboard   = st.Page("pages/01_dashboard.py",   title="Dashboard",      icon="🏠", default=True)
    roadmap     = st.Page("pages/02_roadmap.py",     title="Roadmap",        icon="🗺️")
    practice    = st.Page("pages/03_practice.py",    title="Infinity Practice", icon="♾️")
    logic_gate  = st.Page("pages/04_logic_gate.py",  title="Logic Gate",     icon="🧠")
    editor      = st.Page("pages/05_editor.py",      title="Code Editor",    icon="⌨️")
    notes       = st.Page("pages/06_notes.py",       title="Notes",          icon="📝")
    flashcards  = st.Page("pages/07_flashcards.py",  title="Flashcards",     icon="🃏")
    ai_mentor   = st.Page("pages/08_ai_mentor.py",   title="AI Mentor",      icon="🤖")
    analytics   = st.Page("pages/09_analytics.py",   title="Analytics",      icon="📊")
    profile     = st.Page("pages/10_profile.py",     title="Profile",        icon="👤")
    mistakes    = st.Page("pages/11_mistakes.py",    title="Mistake Journal",icon="📓")

    nav = st.navigation({
        "Learn":    [dashboard, roadmap],
        "Practice": [practice, logic_gate, editor],
        "Review":   [notes, flashcards, mistakes],
        "AI":       [ai_mentor],
        "Track":    [analytics, profile],
    })

    nav.run()
