"""
Logic Gate — Pre-coding reasoning step where users must explain their approach before coding.
"""
import streamlit as st

def render_logic_gate():
    st.markdown("""
    <h1 style="background: linear-gradient(135deg, #8B5CF6, #6366F1);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🧠 Logic Gate
    </h1>
    <p style="color: #94A3B8;">Think before you code. Explain your approach to unlock the editor.</p>
    """, unsafe_allow_html=True)

    problem = st.session_state.get("selected_problem")
    if not problem:
        st.warning("No problem selected.")
        if st.button("← Back to Practice"):
            st.switch_page("pages/03_practice.py")
        return

    # Back button
    if st.button("← Back to Problem", key="back_to_prob_from_logic"):
        st.switch_page("pages/03_practice.py")
        
    st.markdown(f"### Problem: {problem['title']}")
    
    # Check if already validated
    if st.session_state.get("logic_gate_validated", False):
        st.success("✅ Your logic has been validated for this session!")
        if st.button("⌨️ Proceed to Editor", type="primary", use_container_width=True):
            st.switch_page("pages/05_editor.py")
        return

    # Form
    with st.form("logic_gate_form"):
        st.markdown("#### 1. Understanding")
        understanding = st.text_area("Restate the problem in your own words:", height=100)
        
        st.markdown("#### 2. Input / Output")
        io_examples = st.text_area("Give an example input and the expected output:", height=100)
        
        st.markdown("#### 3. Brute Force")
        brute_force = st.text_area("Describe the simplest (brute force) way to solve it:", height=100)
        
        st.markdown("#### 4. Optimal Approach")
        optimal = st.text_area("Describe your optimal approach (data structures & algorithm):", height=150)
        
        st.markdown("#### 5. Edge Cases")
        edge_cases = st.text_area("What edge cases do you need to handle? (e.g., empty input, negative numbers)", height=100)
        
        st.markdown("#### 6. Pseudocode")
        pseudocode = st.text_area("Write a high-level pseudocode for your optimal approach:", height=200)
        
        submitted = st.form_submit_button("Submit for AI Validation", use_container_width=True)
        
        if submitted:
            if not all([understanding, io_examples, optimal, pseudocode]):
                st.error("Please fill out at least Understanding, I/O, Optimal Approach, and Pseudocode.")
            else:
                with st.spinner("AI is reviewing your logic..."):
                    try:
                        from services.ai_service import validate_logic_gate
                        from services.analytics_service import log_activity
                        user_id = st.session_state.user["id"]
                        
                        responses = {
                            "understanding": understanding,
                            "io_examples": io_examples,
                            "brute_force": brute_force,
                            "optimal": optimal,
                            "edge_cases": edge_cases,
                            "pseudocode": pseudocode
                        }
                        
                        result = validate_logic_gate(problem["title"], problem["description"], responses)
                        
                        if result.get("validated", False):
                            st.session_state.logic_gate_validated = True
                            st.success("✅ Excellent! Your reasoning is sound.")
                            st.markdown(f"**AI Feedback:** {result.get('feedback', '')}")
                            
                            # Log activity
                            log_activity(user_id, "logic_gate_completed", reference_id=problem["id"], reference_type="problem", xp_earned=15)
                            
                            # Save to DB
                            try:
                                from services.supabase_client import get_client
                                client = get_client()
                                client.table("logic_gate_responses").upsert({
                                    "user_id": user_id,
                                    "problem_id": problem["id"],
                                    "problem_understanding": understanding,
                                    "input_output": io_examples,
                                    "brute_force_approach": brute_force,
                                    "optimal_approach": optimal,
                                    "edge_cases": edge_cases,
                                    "pseudocode": pseudocode,
                                    "ai_feedback": result.get("feedback", ""),
                                    "ai_validated": True
                                }).execute()
                            except Exception as e:
                                st.warning(f"Could not save response to history: {e}")
                                
                            st.rerun()
                        else:
                            st.error("❌ Not quite there yet. Please review the feedback and try again.")
                            st.markdown(f"**AI Feedback:** {result.get('feedback', '')}")
                            if "suggestions" in result:
                                st.markdown("**Suggestions:**")
                                for sug in result["suggestions"]:
                                    st.markdown(f"- {sug}")
                    except Exception as e:
                        st.error(f"Error during validation: {e}")

if __name__ == "__main__":
    render_logic_gate()
