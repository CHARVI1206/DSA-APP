"""
Mistakes — Track and review recurring errors.
"""
import streamlit as st

def render_mistakes_page():
    st.markdown("""
    <h1 style="background: linear-gradient(135deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        📓 Mistake Journal
    </h1>
    <p style="color: #94A3B8;">Log and learn from your recurring mistakes.</p>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user["id"]
    
    try:
        from services.supabase_client import get_client
        client = get_client()
        
        tab_view, tab_add = st.tabs(["View Mistakes", "Log a Mistake"])
        
        with tab_add:
            with st.form("add_mistake_form"):
                mistake_type = st.selectbox("Mistake Type", ["logic", "syntax", "edge_case", "complexity", "approach", "other"])
                description = st.text_area("Description")
                lesson = st.text_area("Lesson Learned")
                code_snippet = st.text_area("Code Snippet (optional)")
                
                if st.form_submit_button("Log Mistake", type="primary"):
                    if description:
                        client.table("mistake_journal").insert({
                            "user_id": user_id,
                            "mistake_type": mistake_type,
                            "description": description,
                            "lesson_learned": lesson,
                            "code_snippet": code_snippet,
                            "problem_id": st.session_state.get("selected_problem", {}).get("id")
                        }).execute()
                        st.success("Mistake logged!")
                    else:
                        st.error("Description is required.")
                        
        with tab_view:
            res = client.table("mistake_journal").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            mistakes = res.data
            
            if mistakes:
                for m in mistakes:
                    with st.expander(f"[{m['mistake_type'].upper()}] {m['description'][:50]}..."):
                        st.markdown(f"**Description:** {m['description']}")
                        if m.get('lesson_learned'):
                            st.markdown(f"**Lesson:** {m['lesson_learned']}")
                        if m.get('code_snippet'):
                            st.code(m['code_snippet'])
                        
                        if st.button("Delete", key=f"del_m_{m['id']}"):
                            client.table("mistake_journal").delete().eq("id", m['id']).execute()
                            st.rerun()
            else:
                st.info("No mistakes logged yet. Good job!")
                
    except Exception as e:
        st.error(f"Error managing mistakes: {e}")

if __name__ == "__main__":
    render_mistakes_page()
