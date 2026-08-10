import streamlit as st

def render_ai_chat(context: dict = None):
    """Render the AI mentor chat interface."""
    st.markdown("### AI Assistant")
    
    mode = st.radio("Mode", ["🎓 Mentor", "🔍 Reviewer", "🎤 Interviewer"], horizontal=True)
    
    if 'ai_chat_history' not in st.session_state:
        st.session_state.ai_chat_history = []
        
    if context:
        ctx_name = context.get('problem_title') or context.get('topic_title') or 'Current Context'
        st.caption(f"Context: {ctx_name}")
        
    if st.button("Clear Chat"):
        st.session_state.ai_chat_history = []
        st.rerun()
        
    # Display chat messages
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.ai_chat_history:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            with st.chat_message(role):
                st.markdown(content)
                
    # Input
    user_input = st.chat_input("Ask your AI mentor...")
    if user_input:
        st.session_state.ai_chat_history.append({'role': 'user', 'content': user_input})
        st.rerun()
