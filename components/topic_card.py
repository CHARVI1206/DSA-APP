import streamlit as st

def render_topic_card(topic: dict, progress: dict = None):
    """Render a topic card."""
    title = topic.get('title', 'Unknown Topic')
    icon = topic.get('icon', '📚')
    difficulty = topic.get('difficulty', 'medium').lower()
    est_hours = topic.get('estimated_hours', 0)
    topic_id = topic.get('id')
    
    # Progress
    prog_val = progress.get('progress_percentage', 0) if progress else 0
    status = "Not Started"
    if prog_val == 100:
        status = "Completed"
    elif prog_val > 0:
        status = "In Progress"
        
    card_html = f"""
    <div class="topic-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <div style="font-size: 2rem;">{icon}</div>
            <div class="difficulty-badge {difficulty}">{difficulty.capitalize()}</div>
        </div>
        <h3 style="margin-top: 0.5rem; margin-bottom: 0.5rem;">{title}</h3>
        <p style="color: #94A3B8; font-size: 0.8rem;">{est_hours} hours • {status}</p>
        <div class="xp-bar-container">
            <div class="xp-bar" style="width: {prog_val}%;"></div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    if st.button("View Topic", key=f"btn_topic_{topic_id}", use_container_width=True):
        st.session_state.selected_topic = topic_id
        st.rerun()
