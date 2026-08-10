import streamlit as st

def render_flashcard(card: dict, index: int, total: int):
    """Render a single flashcard with flip animation and rating buttons."""
    card_id = card.get('id', 'default')
    flip_key = f"flip_{card_id}"
    
    if flip_key not in st.session_state:
        st.session_state[flip_key] = False
        
    is_flipped = st.session_state[flip_key]
    
    st.markdown(f"**Card {index} of {total}**")
    
    flip_class = "flipped" if is_flipped else ""
    
    st.markdown(f"""
    <div class="flashcard-container">
        <div class="flashcard {flip_class}">
            <div class="flashcard-front">
                <h3>{card.get('front_content', 'Question')}</h3>
            </div>
            <div class="flashcard-back">
                <h3>{card.get('back_content', 'Answer')}</h3>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not is_flipped:
        if st.button("Show Answer", key=f"btn_show_{card_id}", use_container_width=True):
            st.session_state[flip_key] = True
            st.rerun()
    else:
        st.markdown("### How well did you know this?")
        col1, col2, col3, col4 = st.columns(4)
        
        rating = None
        if col1.button("Again (0)", key=f"btn_0_{card_id}", use_container_width=True):
            rating = 0
        if col2.button("Hard (2)", key=f"btn_2_{card_id}", use_container_width=True):
            rating = 2
        if col3.button("Good (4)", key=f"btn_4_{card_id}", use_container_width=True):
            rating = 4
        if col4.button("Easy (5)", key=f"btn_5_{card_id}", use_container_width=True):
            rating = 5
            
        if rating is not None:
            st.session_state['flashcard_rating'] = {
                'card_id': card_id,
                'rating': rating
            }
            # reset flip state for next view
            st.session_state[flip_key] = False

def render_review_session(cards: list[dict]):
    """Full review flow for a list of cards."""
    if not cards:
        st.success("You're all caught up! No cards to review.")
        return
        
    if 'current_card_index' not in st.session_state:
        st.session_state.current_card_index = 0
        
    idx = st.session_state.current_card_index
    if idx < len(cards):
        render_flashcard(cards[idx], idx + 1, len(cards))
    else:
        st.success("Review session complete!")
        if st.button("Reset Session"):
            st.session_state.current_card_index = 0
            st.rerun()
