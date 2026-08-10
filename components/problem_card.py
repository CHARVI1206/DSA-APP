import streamlit as st

def render_problem_card(problem: dict, is_bookmarked: bool = False):
    """Render a problem card."""
    title = problem.get('title', 'Unknown Problem')
    difficulty = problem.get('difficulty', 'medium').lower()
    problem_id = problem.get('id')
    
    # For now mock tags and companies
    tags = ["Arrays", "Hash Table"]
    companies = ["Google", "Amazon"]
    
    tags_html = "".join([f'<span class="tag-pill">{t}</span>' for t in tags])
    comps_html = "".join([f'<span class="tag-pill" style="opacity: 0.7;">{c}</span>' for c in companies])
    bookmark_icon = "🔖" if is_bookmarked else "📑"
    
    card_html = f"""
    <div class="problem-card {difficulty}">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <h4 style="margin: 0 0 0.5rem 0;">{title}</h4>
                <div style="margin-bottom: 0.5rem;">
                    <span class="difficulty-badge {difficulty}">{difficulty.capitalize()}</span>
                </div>
                <div style="margin-bottom: 0.5rem;">{tags_html}</div>
                <div>{comps_html}</div>
            </div>
            <div style="font-size: 1.25rem;">{bookmark_icon}</div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    if st.button("Solve", key=f"btn_solve_{problem_id}", use_container_width=True):
        st.session_state.selected_problem = problem_id
        st.rerun()
