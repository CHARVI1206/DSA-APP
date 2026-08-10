"""
Roadmap — Full DSA topic tree with topic detail pages containing
AI-generated notes, visual explanations, worked examples, and more.
"""
import streamlit as st


def render_topic_list():
    """Render the full DSA topic tree as interactive cards."""
    st.markdown("""
    <h1 style="background: linear-gradient(135deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🗺️ Learning Roadmap
    </h1>
    <p style="color: #94A3B8;">Master DSA step by step — from arrays to system design.</p>
    """, unsafe_allow_html=True)

    # Fetch topics
    try:
        from services.topic_service import get_all_topics, get_user_progress
        topics = get_all_topics()
        user_id = st.session_state.user["id"]
        progress_list = get_user_progress(user_id)
        progress_map = {p["topic_id"]: p for p in progress_list} if progress_list else {}
    except Exception as e:
        st.error(f"Could not load topics: {e}")
        return

    if not topics:
        st.info("No topics found. Run the database seed script to populate topics.")
        return

    # Difficulty filter
    col_filter, _ = st.columns([2, 4])
    with col_filter:
        diff_filter = st.selectbox(
            "Filter by level",
            ["All", "Beginner", "Intermediate", "Advanced"],
            key="roadmap_filter"
        )

    # Group by difficulty
    difficulty_icons = {
        "beginner": "🟢",
        "intermediate": "🟡",
        "advanced": "🔴",
    }

    filtered = topics
    if diff_filter != "All":
        filtered = [t for t in topics if t.get("difficulty_level", "").lower() == diff_filter.lower()]

    # Render cards
    for i in range(0, len(filtered), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(filtered):
                break
            topic = filtered[idx]
            prog = progress_map.get(topic["id"], {})
            status = prog.get("status", "not_started")

            status_colors = {
                "not_started": "#4B5563",
                "in_progress": "#F59E0B",
                "completed": "#22C55E",
                "revision": "#8B5CF6",
            }
            status_labels = {
                "not_started": "Not Started",
                "in_progress": "In Progress",
                "completed": "✓ Completed",
                "revision": "Revision",
            }
            status_color = status_colors.get(status, "#4B5563")
            status_label = status_labels.get(status, "Not Started")

            diff_level = topic.get("difficulty_level", "beginner")
            diff_icon = difficulty_icons.get(diff_level, "⚪")
            hours = topic.get("estimated_hours", "—")

            problems_solved = prog.get("problems_solved", 0)
            problems_attempted = prog.get("problems_attempted", 0)

            with col:
                st.markdown(f"""
                <div class="topic-card" style="cursor:pointer;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                        <span style="font-size:1.8rem;">{topic.get('icon', '📘')}</span>
                        <span style="font-size:0.7rem; padding:0.2rem 0.6rem; border-radius:12px;
                            background:{status_color}22; color:{status_color}; font-weight:600;">
                            {status_label}
                        </span>
                    </div>
                    <h3 style="margin:0 0 0.25rem 0; font-size:1.1rem; color:#E2E8F0;">
                        {topic['title']}
                    </h3>
                    <p style="color:#94A3B8; font-size:0.8rem; margin:0 0 0.75rem 0; line-height:1.4;">
                        {topic.get('description', '')[:80]}{'...' if len(topic.get('description', '')) > 80 else ''}
                    </p>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#94A3B8; font-size:0.75rem;">{diff_icon} {diff_level.title()} · ~{hours}h</span>
                        <span style="color:#94A3B8; font-size:0.75rem;">
                            {problems_solved} solved
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Open →", key=f"topic_{topic['id']}", use_container_width=True):
                    st.session_state.selected_topic = topic
                    st.session_state.selected_topic_slug = topic["slug"]
                    st.rerun()


def render_topic_detail():
    """Render a single topic detail page with tabbed content sections."""
    topic = st.session_state.selected_topic
    if not topic:
        st.warning("No topic selected.")
        return

    # Back button
    if st.button("← Back to Roadmap", key="back_to_roadmap"):
        st.session_state.selected_topic = None
        st.session_state.selected_topic_slug = None
        st.rerun()

    st.markdown(f"""
    <div style="padding: 1rem 0;">
        <div style="display:flex; align-items:center; gap:0.75rem;">
            <span style="font-size:2.5rem;">{topic.get('icon', '📘')}</span>
            <div>
                <h1 style="margin:0; font-size:2rem; color:#E2E8F0;">{topic['title']}</h1>
                <p style="color:#94A3B8; margin:0;">{topic.get('description', '')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mark topic as in_progress
    try:
        from services.topic_service import update_user_progress
        user_id = st.session_state.user["id"]
        update_user_progress(user_id, topic["id"], {"status": "in_progress"})
    except Exception:
        pass

    # Content tabs
    tabs = st.tabs([
        "📖 Notes", "🎨 Visual", "📝 Examples", "💻 Code",
        "⏱️ Complexity", "📋 Cheat Sheet", "🎯 Interview Q's",
        "❌ Mistakes", "🗓️ Revision"
    ])

    section_types = [
        "detailed_notes", "visual_explanation", "worked_examples",
        "reference_code", "complexity_notes", "cheat_sheet",
        "interview_questions", "common_mistakes", "practice_questions"
    ]

    for tab, section_type in zip(tabs, section_types):
        with tab:
            _render_section(topic, section_type)


def _render_section(topic: dict, section_type: str):
    """Render a single content section, generating via AI if not cached."""
    topic_id = topic["id"]
    topic_name = topic["title"]

    # Try to load from cache
    try:
        from services.topic_service import get_topic_notes
        content = get_topic_notes(topic_id, section_type)
    except Exception:
        content = None

    if content:
        st.markdown(content, unsafe_allow_html=True)

        # Mark notes as read
        try:
            from services.topic_service import update_user_progress
            from services.analytics_service import log_activity
            user_id = st.session_state.user["id"]
            update_user_progress(user_id, topic_id, {"notes_read": True})
            log_activity(user_id, "notes_read", reference_id=topic_id, reference_type="topic")
        except Exception:
            pass
    else:
        st.info(f"📝 These notes haven't been generated yet for **{topic_name}**.")
        if st.button(f"🤖 Generate with AI", key=f"gen_{section_type}_{topic_id}"):
            with st.spinner(f"Generating {section_type.replace('_', ' ')} for {topic_name}..."):
                try:
                    from services.ai_service import generate_topic_notes
                    generated = generate_topic_notes(topic_name, section_type)
                    if generated:
                        # Save to database
                        from services.supabase_client import get_client
                        client = get_client()
                        client.table("topic_notes").upsert({
                            "topic_id": topic_id,
                            "section_type": section_type,
                            "content": generated,
                            "generated_by": "gemini-2.0-flash",
                        }).execute()
                        st.success("✅ Notes generated successfully!")
                        st.markdown(generated, unsafe_allow_html=True)
                    else:
                        st.error("Failed to generate notes. Check your Gemini API key.")
                except Exception as e:
                    st.error(f"Error generating notes: {e}")


# ─── Main ───────────────────────────────────────────────────────────────
if st.session_state.selected_topic:
    render_topic_detail()
else:
    render_topic_list()
