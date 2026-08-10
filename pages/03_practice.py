"""
Practice — Problem bank with filters, problem detail view, and bookmarks.
"""
import streamlit as st


def render_problem_list():
    """Render the filterable problem bank."""
    st.markdown("""
    <h1 style="background: linear-gradient(135deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        ♾️ Infinity Practice
    </h1>
    <p style="color: #94A3B8;">An endless repository of DSA problems. Solve existing ones or generate new ones on the fly.</p>
    """, unsafe_allow_html=True)

    user_id = st.session_state.user["id"]

    # ─── Filters ────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        search = st.text_input("🔍 Search problems", placeholder="Search by title or tag...", key="prob_search")

    with col2:
        try:
            from services.topic_service import get_all_topics
            topics = get_all_topics()
            topic_options = ["All Topics"] + [t["title"] for t in topics]
            topic_map = {t["title"]: t["id"] for t in topics}
        except Exception:
            topic_options = ["All Topics"]
            topic_map = {}
        selected_topic = st.selectbox("Topic", topic_options, key="prob_topic_filter")

    with col3:
        difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"], key="prob_diff_filter")

    with col4:
        show_bookmarked = st.checkbox("⭐ Bookmarked only", key="prob_bookmarked")

    # ─── Fetch Problems ─────────────────────────────────────────────
    try:
        from services.problem_service import get_problems, get_bookmarks
        topic_id = topic_map.get(selected_topic) if selected_topic != "All Topics" else None
        diff = difficulty.lower() if difficulty != "All" else None
        bookmarked_by = user_id if show_bookmarked else None
        problems = get_problems(topic_id=topic_id, difficulty=diff, search=search or None, bookmarked_by=bookmarked_by)
        bookmarks = get_bookmarks(user_id)
    except Exception as e:
        st.info(f"No problems found. Add problems from the roadmap or create custom ones below.")
        problems = []
        bookmarks = []

    # ─── Problem Count ──────────────────────────────────────────────
    if problems:
        easy_count = sum(1 for p in problems if p.get("difficulty") == "easy")
        med_count = sum(1 for p in problems if p.get("difficulty") == "medium")
        hard_count = sum(1 for p in problems if p.get("difficulty") == "hard")
        st.markdown(f"""
        <div style="display:flex; gap:1rem; margin:0.5rem 0 1rem 0;">
            <span style="color:#22C55E; font-size:0.85rem;">🟢 {easy_count} Easy</span>
            <span style="color:#F59E0B; font-size:0.85rem;">🟡 {med_count} Medium</span>
            <span style="color:#EF4444; font-size:0.85rem;">🔴 {hard_count} Hard</span>
            <span style="color:#94A3B8; font-size:0.85rem;">📊 {len(problems)} total</span>
        </div>
        """, unsafe_allow_html=True)

    # ─── Problem Cards ──────────────────────────────────────────────
    if not problems:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
            <h3 style="color:#E2E8F0;">No problems yet</h3>
            <p style="color:#94A3B8;">Create custom problems or generate them from the roadmap topics.</p>
        </div>
        """, unsafe_allow_html=True)

    for problem in problems:
        diff_colors = {"easy": "#22C55E", "medium": "#F59E0B", "hard": "#EF4444"}
        diff_color = diff_colors.get(problem.get("difficulty", ""), "#94A3B8")
        is_bookmarked = problem["id"] in bookmarks if bookmarks else False
        bookmark_icon = "⭐" if is_bookmarked else "☆"
        tags_html = " ".join([
            f'<span style="background:#1E1B4B; color:#A78BFA; padding:0.15rem 0.5rem; '
            f'border-radius:10px; font-size:0.7rem; margin-right:0.25rem;">{tag}</span>'
            for tag in (problem.get("tags") or [])[:5]
        ])
        companies_html = " ".join([
            f'<span style="background:#1F2937; color:#9CA3AF; padding:0.15rem 0.5rem; '
            f'border-radius:10px; font-size:0.65rem;">{c}</span>'
            for c in (problem.get("companies") or [])[:3]
        ])

        st.markdown(f"""
        <div class="problem-card" style="border-left: 3px solid {diff_color};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <h3 style="margin:0 0 0.25rem 0; font-size:1.05rem; color:#E2E8F0;">
                        {problem['title']}
                    </h3>
                    <div style="display:flex; gap:0.5rem; align-items:center; margin-bottom:0.5rem;">
                        <span style="color:{diff_color}; font-weight:600; font-size:0.8rem; text-transform:uppercase;">
                            {problem.get('difficulty', 'medium')}
                        </span>
                        {tags_html}
                    </div>
                    {f'<div style="margin-top:0.25rem;">{companies_html}</div>' if companies_html else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_solve, col_bm, _ = st.columns([1, 1, 4])
        with col_solve:
            if st.button("🚀 Solve", key=f"solve_{problem['id']}", use_container_width=True):
                st.session_state.selected_problem = problem
                st.session_state.selected_problem_slug = problem.get("slug")
                st.rerun()
        with col_bm:
            if st.button(f"{bookmark_icon} Bookmark", key=f"bm_{problem['id']}", use_container_width=True):
                try:
                    from services.problem_service import toggle_bookmark
                    toggle_bookmark(user_id, problem["id"])
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ─── Create Custom Problem ──────────────────────────────────────
    st.markdown("---")
    with st.expander("➕ Create Custom Problem"):
        with st.form("new_problem_form"):
            title = st.text_input("Problem Title")
            description = st.text_area("Description (Markdown)", height=200)
            c1, c2 = st.columns(2)
            with c1:
                diff = st.selectbox("Difficulty", ["easy", "medium", "hard"])
            with c2:
                if topic_map:
                    topic_name = st.selectbox("Topic", list(topic_map.keys()))
                    p_topic_id = topic_map[topic_name]
                else:
                    p_topic_id = st.text_input("Topic ID")

            tags_str = st.text_input("Tags (comma-separated)", placeholder="array, two-pointer, sorting")
            companies_str = st.text_input("Companies (comma-separated)", placeholder="Google, Amazon, Meta")

            tc_input = st.text_area(
                "Test Cases (JSON array)",
                value='[{"input": "example_input", "expected_output": "example_output", "is_hidden": false}]',
                height=100
            )

            time_comp = st.text_input("Time Complexity", placeholder="O(n)")
            space_comp = st.text_input("Space Complexity", placeholder="O(1)")

            submitted = st.form_submit_button("Create Problem", use_container_width=True)

            if submitted and title and description:
                import json
                try:
                    from services.problem_service import create_problem
                    from utils.helpers import slugify
                    test_cases = json.loads(tc_input) if tc_input else []
                    tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
                    companies = [c.strip() for c in companies_str.split(",") if c.strip()] if companies_str else []

                    create_problem({
                        "title": title,
                        "slug": slugify(title),
                        "description": description,
                        "difficulty": diff,
                        "topic_id": p_topic_id,
                        "tags": tags,
                        "companies": companies,
                        "test_cases": test_cases,
                        "time_complexity": time_comp,
                        "space_complexity": space_comp,
                        "is_custom": True,
                        "created_by": user_id,
                    })
                    st.success("✅ Problem created!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating problem: {e}")

    # ─── Generate AI Problem ────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🤖 Infinite Generation")
    col_ai1, col_ai2 = st.columns([2, 1])
    with col_ai1:
        st.markdown("Generate a brand new, unique problem for any topic on the fly. The AI will create the description, test cases, and hints.")
    with col_ai2:
        if st.button("✨ Generate AI Problem", use_container_width=True, type="primary"):
            st.session_state.show_ai_generator = True
            
    if st.session_state.get("show_ai_generator"):
        with st.container():
            st.markdown("#### Configure Problem Generator")
            ai_c1, ai_c2 = st.columns(2)
            with ai_c1:
                ai_topic = st.selectbox("Topic for new problem", list(topic_map.keys()) if 'topic_map' in locals() and topic_map else ["Arrays & Strings"], key="ai_gen_topic")
            with ai_c2:
                ai_diff = st.selectbox("Difficulty", ["easy", "medium", "hard"], key="ai_gen_diff")
                
            if st.button("Generate Now", use_container_width=True):
                with st.spinner(f"Generating a new {ai_diff} {ai_topic} problem..."):
                    try:
                        from services.ai_service import generate_new_problem
                        from services.problem_service import create_problem
                        from utils.helpers import slugify
                        import uuid
                        
                        # Generate problem using AI
                        topic_id = topic_map.get(ai_topic) if 'topic_map' in locals() and topic_map else None
                        new_problem_data = generate_new_problem(ai_topic, ai_diff)
                        
                        if new_problem_data:
                            # Add internal fields
                            base_slug = slugify(new_problem_data["title"])
                            new_problem_data["slug"] = f"{base_slug}-{str(uuid.uuid4())[:6]}"
                            new_problem_data["topic_id"] = topic_id
                            new_problem_data["is_custom"] = True
                            new_problem_data["created_by"] = user_id
                            
                            created = create_problem(new_problem_data)
                            st.session_state.show_ai_generator = False
                            st.success(f"✅ Generated new problem: {new_problem_data['title']}")
                            
                            # Auto-select the newly created problem
                            st.session_state.selected_problem = created
                            st.session_state.selected_problem_slug = created.get("slug")
                            st.rerun()
                        else:
                            st.error("Failed to generate problem. Please try again.")
                    except Exception as e:
                        st.error(f"Error during generation: {e}")


def render_problem_detail():
    """Render a single problem's details."""
    problem = st.session_state.selected_problem
    if not problem:
        st.warning("No problem selected.")
        return

    if st.button("← Back to Problems", key="back_to_problems"):
        st.session_state.selected_problem = None
        st.session_state.selected_problem_slug = None
        st.rerun()

    diff_colors = {"easy": "#22C55E", "medium": "#F59E0B", "hard": "#EF4444"}
    diff_color = diff_colors.get(problem.get("difficulty", ""), "#94A3B8")

    st.markdown(f"""
    <div style="padding:0.5rem 0 1rem 0;">
        <div style="display:flex; align-items:center; gap:1rem;">
            <h1 style="margin:0; color:#E2E8F0;">{problem['title']}</h1>
            <span style="color:{diff_color}; font-weight:700; font-size:0.9rem; text-transform:uppercase;
                padding:0.25rem 0.75rem; background:{diff_color}22; border-radius:12px;">
                {problem.get('difficulty', 'medium')}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Problem description
    st.markdown(problem.get("description", "No description available."))

    # Complexity
    if problem.get("time_complexity") or problem.get("space_complexity"):
        col1, col2 = st.columns(2)
        with col1:
            if problem.get("time_complexity"):
                st.markdown(f"**⏱️ Time Complexity:** `{problem['time_complexity']}`")
        with col2:
            if problem.get("space_complexity"):
                st.markdown(f"**💾 Space Complexity:** `{problem['space_complexity']}`")

    # Hints (progressive reveal)
    hints = problem.get("hints", [])
    if hints and isinstance(hints, list) and len(hints) > 0:
        st.markdown("---")
        st.markdown("#### 💡 Hints")
        for i, hint in enumerate(hints):
            with st.expander(f"Hint {i + 1}", expanded=False):
                st.markdown(hint if isinstance(hint, str) else str(hint))

    # Test cases (visible ones only)
    test_cases = problem.get("test_cases", [])
    if test_cases:
        visible = [tc for tc in test_cases if not tc.get("is_hidden", False)]
        if visible:
            st.markdown("---")
            st.markdown("#### 🧪 Example Test Cases")
            for i, tc in enumerate(visible):
                with st.expander(f"Test Case {i + 1}", expanded=(i == 0)):
                    st.code(f"Input:  {tc.get('input', '')}", language="text")
                    st.code(f"Output: {tc.get('expected_output', '')}", language="text")

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧠 Logic Gate First", use_container_width=True, type="primary"):
            st.session_state.logic_gate_validated = False
            st.switch_page("pages/04_logic_gate.py")
    with col2:
        if st.button("⌨️ Go to Editor", use_container_width=True):
            st.switch_page("pages/05_editor.py")
    with col3:
        if st.button("🤖 Ask AI Mentor", use_container_width=True):
            st.switch_page("pages/08_ai_mentor.py")


# ─── Main ───────────────────────────────────────────────────────────────
if st.session_state.selected_problem:
    render_problem_detail()
else:
    render_problem_list()
