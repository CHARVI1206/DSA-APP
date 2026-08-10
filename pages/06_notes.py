"""
Notes — Access AI-generated notes and manage personal annotations.
"""
import streamlit as st

def render_notes_page():
    st.markdown("""
    <h1 style="background: linear-gradient(135deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        📝 Notes Hub
    </h1>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user["id"]
    
    tab_ai, tab_personal = st.tabs(["🤖 AI Notes (By Topic)", "📓 My Personal Notes"])
    
    with tab_ai:
        st.markdown("### AI-Generated Topic Notes")
        try:
            from services.topic_service import get_all_topics, get_topic_notes
            topics = get_all_topics()
            if topics:
                topic_options = {t["title"]: t["id"] for t in topics}
                selected_title = st.selectbox("Select Topic", list(topic_options.keys()), key="ai_notes_topic")
                topic_id = topic_options[selected_title]
                
                section = st.selectbox("Select Section", [
                    "detailed_notes", "visual_explanation", "worked_examples", 
                    "reference_code", "complexity_notes", "cheat_sheet", 
                    "interview_questions", "common_mistakes"
                ], format_func=lambda x: x.replace("_", " ").title())
                
                notes_content = get_topic_notes(topic_id, section)
                if notes_content:
                    st.markdown(f"""
                    <div style="background: rgba(26,26,46,0.5); padding: 2rem; border-radius: 12px; border: 1px solid rgba(139,92,246,0.2);">
                        {notes_content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info(f"Notes for '{section.replace('_', ' ')}' have not been generated yet. Go to the Roadmap to generate them.")
                    if st.button("Go to Roadmap"):
                        st.session_state.selected_topic = next((t for t in topics if t["id"] == topic_id), None)
                        if st.session_state.selected_topic:
                            st.session_state.selected_topic_slug = st.session_state.selected_topic["slug"]
                        st.switch_page("pages/02_roadmap.py")
            else:
                st.info("No topics available.")
        except Exception as e:
            st.error(f"Error loading AI notes: {e}")
            
    with tab_personal:
        st.markdown("### My Personal Notes")
        
        col_search, col_new = st.columns([3, 1])
        with col_search:
            search_query = st.text_input("🔍 Search Notes", placeholder="Search in title or content...")
        with col_new:
            st.markdown("<br>", unsafe_allow_html=True) # alignment
            if st.button("➕ New Note", use_container_width=True):
                st.session_state.editing_note = "new"
                
        try:
            from services.notes_service import get_user_notes, create_user_note, update_user_note, delete_user_note, search_notes
            
            if search_query:
                notes = search_notes(user_id, search_query)
            else:
                notes = get_user_notes(user_id)
                
            # Editor form
            if st.session_state.get("editing_note"):
                is_new = st.session_state.editing_note == "new"
                note_to_edit = {} if is_new else st.session_state.editing_note
                
                with st.form("note_editor"):
                    st.markdown(f"#### {'Create Note' if is_new else 'Edit Note'}")
                    title = st.text_input("Title", value=note_to_edit.get("title", ""))
                    content = st.text_area("Content (Markdown)", value=note_to_edit.get("content", ""), height=300)
                    tags_str = st.text_input("Tags (comma separated)", value=",".join(note_to_edit.get("tags", [])))
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.form_submit_button("Save Note", type="primary"):
                            tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                            if is_new:
                                create_user_note(user_id, title, content, tags=tags)
                                from services.analytics_service import log_activity
                                log_activity(user_id, "note_created", xp_earned=5)
                                st.success("Note created!")
                            else:
                                update_user_note(note_to_edit["id"], {"title": title, "content": content, "tags": tags})
                                st.success("Note updated!")
                            st.session_state.editing_note = None
                            st.rerun()
                    with c2:
                        if st.form_submit_button("Cancel"):
                            st.session_state.editing_note = None
                            st.rerun()
                            
            # Display notes
            if not st.session_state.get("editing_note"):
                if notes:
                    for note in notes:
                        with st.expander(f"📄 {note['title']} - {note['created_at'].split('T')[0]}"):
                            if note.get('tags'):
                                tags_html = " ".join([f'<span style="background:#1E1B4B; color:#A78BFA; padding:0.1rem 0.4rem; border-radius:10px; font-size:0.7rem;">{tag}</span>' for tag in note['tags']])
                                st.markdown(tags_html, unsafe_allow_html=True)
                            
                            st.markdown(f"<div style='margin-top: 1rem;'>{note['content']}</div>", unsafe_allow_html=True)
                            
                            st.markdown("---")
                            c1, c2, c3 = st.columns([1, 1, 4])
                            with c1:
                                if st.button("Edit", key=f"edit_{note['id']}", use_container_width=True):
                                    st.session_state.editing_note = note
                                    st.rerun()
                            with c2:
                                if st.button("Delete", key=f"del_{note['id']}", use_container_width=True):
                                    delete_user_note(note['id'])
                                    st.success("Deleted!")
                                    st.rerun()
                else:
                    st.info("No personal notes found.")
                    
        except Exception as e:
            st.error(f"Error managing notes: {e}")

if __name__ == "__main__":
    render_notes_page()
