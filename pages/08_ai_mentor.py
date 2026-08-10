"""
AI Mentor — Context-aware AI chat with Mentor, Reviewer, and Interviewer modes.
"""
import streamlit as st

def render_ai_mentor_page():
    st.markdown("""
    <h1 style="background: linear-gradient(135deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🤖 AI Mentor
    </h1>
    """, unsafe_allow_html=True)
    
    # Setup context
    context = {}
    if st.session_state.get("selected_problem"):
        context["type"] = "problem"
        context["data"] = st.session_state.selected_problem
    elif st.session_state.get("selected_topic"):
        context["type"] = "topic"
        context["data"] = st.session_state.selected_topic
        
    if context:
        title = context["data"].get("title", "")
        st.info(f"Context aware: AI knows you are working on **{title}**")
        
    try:
        from components.ai_chat import render_ai_chat
        render_ai_chat(context=context)
    except ImportError:
        st.error("AI chat component is missing.")

if __name__ == "__main__":
    render_ai_mentor_page()
