"""
Profile — Manage user settings and profile info.
"""
import streamlit as st

def render_profile_page():
    st.markdown("""
    <h1 style="background: linear-gradient(135deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        👤 Profile & Settings
    </h1>
    """, unsafe_allow_html=True)
    
    user = st.session_state.user
    
    try:
        from services.auth_service import logout, get_profile, update_profile
        
        profile = get_profile(user["id"])
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Avatar")
            avatar_url = profile.get("avatar_url")
            if avatar_url:
                st.image(avatar_url, width=150)
            else:
                st.markdown("<div style='font-size: 5rem;'>🧑‍💻</div>", unsafe_allow_html=True)
                
            # Avatar upload could be added here
            
        with col2:
            st.markdown("### Settings")
            with st.form("profile_form"):
                display_name = st.text_input("Display Name", value=profile.get("display_name", ""))
                theme = st.selectbox("Theme", ["dark", "light", "system"], index=["dark", "light", "system"].index(profile.get("theme", "dark")))
                notifications = st.checkbox("Enable Notifications", value=profile.get("notifications_enabled", True))
                
                if st.form_submit_button("Save Changes", type="primary"):
                    update_profile(user["id"], {
                        "display_name": display_name,
                        "theme": theme,
                        "notifications_enabled": notifications
                    })
                    st.success("Profile updated!")
                    st.session_state.user = get_profile(user["id"])
                    st.rerun()
                    
        st.markdown("---")
        if st.button("Logout", type="secondary"):
            logout()
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading profile: {e}")

if __name__ == "__main__":
    render_profile_page()
