import streamlit as st

def render_auth_page():
    """Render the login and signup forms."""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem; background: -webkit-linear-gradient(45deg, #8B5CF6, #6366F1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">DSA Mastery</h1>
        <p style="color: #94A3B8; font-size: 1.2rem;">Master Data Structures & Algorithms with AI</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Log In", use_container_width=True)
                
                if submit:
                    if email and password:
                        st.session_state['auth_submit'] = ('login', email, password)
                    else:
                        st.toast("Please fill in all fields.", icon="❌")
                        
        with tab2:
            with st.form("signup_form"):
                display_name = st.text_input("Display Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submit:
                    if not (display_name and email and password and confirm_password):
                        st.toast("Please fill in all fields.", icon="❌")
                    elif password != confirm_password:
                        st.toast("Passwords do not match.", icon="❌")
                    else:
                        st.session_state['auth_submit'] = ('signup', email, password, display_name)
