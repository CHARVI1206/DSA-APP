import streamlit as st

def render_sidebar(user: dict = None):
    """Render the sidebar with user profile and stats."""
    if not user:
        st.sidebar.markdown("Please log in to view your profile.")
        return

    display_name = user.get('display_name', 'User')
    xp = user.get('xp', 0)
    level = xp // 100
    streak = user.get('streak', 0)
    
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🧑‍💻</div>
        <h3 style="margin: 0; color: #E2E8F0;">{display_name}</h3>
        <p style="color: #8B5CF6; font-weight: 600; margin-top: 0.25rem;">Level {level}</p>
    </div>
    """, unsafe_allow_html=True)

    # XP Bar
    xp_progress = (xp % 100)
    st.sidebar.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #94A3B8;">
            <span>XP: {xp}</span>
            <span>Next: {(level + 1) * 100}</span>
        </div>
        <div class="xp-bar-container">
            <div class="xp-bar" style="width: {xp_progress}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats Grid
    st.sidebar.markdown(f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
        <div class="metric-card" style="padding: 1rem; text-align: center;">
            <div class="streak-fire" style="font-size: 1.5rem;">🔥</div>
            <div style="font-size: 1.25rem; font-weight: bold; color: #E2E8F0;">{streak}</div>
            <div style="font-size: 0.75rem; color: #94A3B8;">Day Streak</div>
        </div>
        <div class="metric-card" style="padding: 1rem; text-align: center;">
            <div style="font-size: 1.5rem;">📝</div>
            <div style="font-size: 1.25rem; font-weight: bold; color: #E2E8F0;">{user.get('problems_solved', 0)}</div>
            <div style="font-size: 0.75rem; color: #94A3B8;">Solved</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.divider()
    
    # Navigation hints or extra links can go here
    st.sidebar.markdown("### Quick Links")
    # Wrap in try/except in case pages don't exist yet
    try:
        st.sidebar.page_link("pages/2_Dashboard.py", label="Dashboard", icon="📊")
        st.sidebar.page_link("pages/3_Problems.py", label="Problems", icon="💻")
        st.sidebar.page_link("pages/4_Learn.py", label="Learn", icon="📚")
    except Exception:
        pass
