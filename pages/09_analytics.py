"""
Analytics — User progress, achievements, and statistics.
"""
import streamlit as st

def render_analytics_page():
    st.markdown("""
    <h1 style="background: linear-gradient(135deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        📊 Analytics
    </h1>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user["id"]
    
    try:
        from services.analytics_service import get_user_stats, get_heatmap_data, get_achievements
        from components.heatmap import render_heatmap
        from components.achievement_badge import render_achievements_gallery
        
        # Stats
        stats = get_user_stats(user_id)
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown(f"<div class='metric-card'><div style='color:#94A3B8;'>Total Solved</div><div style='font-size:1.8rem; color:#22C55E;'>{stats.get('total_solved', 0)}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><div style='color:#94A3B8;'>Acceptance Rate</div><div style='font-size:1.8rem; color:#8B5CF6;'>{stats.get('acceptance_rate', 0):.0f}%</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><div style='color:#94A3B8;'>Avg Solve Time</div><div style='font-size:1.8rem; color:#F59E0B;'>{stats.get('avg_solve_time', 0):.1f}m</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='metric-card'><div style='color:#94A3B8;'>Topics Completed</div><div style='font-size:1.8rem; color:#6366F1;'>{stats.get('topics_completed', 0)}</div></div>", unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Heatmap
        st.markdown("### Activity Heatmap")
        heatmap_data = get_heatmap_data(user_id)
        if heatmap_data:
            render_heatmap(heatmap_data)
        else:
            st.info("No activity data yet.")
            
        st.markdown("---")
        
        # Achievements
        st.markdown("### Achievements")
        achievements = get_achievements(user_id)
        render_achievements_gallery(achievements.get("earned", []), achievements.get("locked", []))
        
    except Exception as e:
        st.error(f"Error loading analytics: {e}")

if __name__ == "__main__":
    render_analytics_page()
