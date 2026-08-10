import streamlit as st

def render_achievement(achievement: dict, earned: bool = False):
    """Render a single achievement badge."""
    icon = achievement.get('icon', '🏆')
    name = achievement.get('name', 'Achievement')
    desc = achievement.get('description', 'Description')
    
    locked_class = "" if earned else "locked"
    
    html = f"""
    <div class="achievement-badge {locked_class}">
        <div class="icon">{icon}</div>
        <div style="font-weight: bold; margin-bottom: 0.25rem;">{name}</div>
        <div style="font-size: 0.75rem; color: #94A3B8;">{desc}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_achievements_gallery(earned: list[dict], locked: list[dict]):
    """Render a gallery of achievements."""
    if not earned and not locked:
        st.info("No achievements available.")
        return
        
    st.markdown("### Earned Achievements")
    if earned:
        cols = st.columns(4)
        for i, ach in enumerate(earned):
            with cols[i % 4]:
                render_achievement(ach, earned=True)
    else:
        st.markdown("Keep learning to earn achievements!")
        
    st.markdown("### Locked Achievements")
    if locked:
        cols = st.columns(4)
        for i, ach in enumerate(locked):
            with cols[i % 4]:
                render_achievement(ach, earned=False)
