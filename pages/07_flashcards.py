"""
Flashcards — Spaced repetition flashcards interface.
"""
import streamlit as st

def render_flashcards_page():
    st.markdown("""
    <h1 style="background: linear-gradient(135deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🃏 Flashcards
    </h1>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user["id"]
    
    try:
        from services.flashcard_service import get_due_cards, get_review_stats, initialize_cards_for_user
        from services.topic_service import get_all_topics
        from components.flashcard_widget import render_review_session
        
        stats = get_review_stats(user_id)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'><div style='color:#94A3B8;'>Due Today</div><div style='font-size:1.5rem; color:#F59E0B;'>{stats.get('due_today', 0)}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><div style='color:#94A3B8;'>Total Reviewed</div><div style='font-size:1.5rem; color:#8B5CF6;'>{stats.get('total_reviewed', 0)}</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><div style='color:#94A3B8;'>Retention Rate</div><div style='font-size:1.5rem; color:#22C55E;'>{stats.get('retention_rate', 0):.0f}%</div></div>", unsafe_allow_html=True)
            
        st.markdown("---")
        
        due_cards = get_due_cards(user_id)
        
        if due_cards:
            st.markdown("### 📝 Review Session")
            render_review_session(due_cards)
        else:
            st.success("🎉 You're all caught up for today! No flashcards due.")
            
            st.markdown("### Generate More Flashcards")
            topics = get_all_topics()
            if topics:
                topic_options = {t["title"]: t["id"] for t in topics}
                selected_title = st.selectbox("Select Topic", list(topic_options.keys()))
                topic_id = topic_options[selected_title]
                
                if st.button("Generate & Add to Deck", type="primary"):
                    with st.spinner("Generating flashcards via AI..."):
                        try:
                            from services.flashcard_service import get_or_generate_flashcards
                            cards = get_or_generate_flashcards(topic_id, selected_title)
                            if cards:
                                initialize_cards_for_user(user_id, topic_id)
                                st.success(f"Added {len(cards)} flashcards to your deck!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error generating flashcards: {e}")
            else:
                st.info("No topics available.")
                
    except Exception as e:
        st.error(f"Error loading flashcards: {e}")

if __name__ == "__main__":
    render_flashcards_page()
