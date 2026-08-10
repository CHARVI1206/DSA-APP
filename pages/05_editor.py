"""
Code Editor — Code execution environment with problem description, tests, and submission.
"""
import streamlit as st

def render_editor_page():
    problem = st.session_state.get("selected_problem")
    if not problem:
        st.warning("No problem selected.")
        if st.button("← Back to Practice"):
            st.switch_page("pages/03_practice.py")
        return

    # Check logic gate
    if not st.session_state.get("logic_gate_validated", False):
        st.warning("🔒 You must pass the Logic Gate before accessing the editor for this session.")
        if st.button("Go to Logic Gate", type="primary"):
            st.switch_page("pages/04_logic_gate.py")
        return

    col_desc, col_edit = st.columns([1, 1.5])
    
    with col_desc:
        if st.button("← Back"):
            st.switch_page("pages/03_practice.py")
            
        st.markdown(f"## {problem['title']}")
        diff_colors = {"easy": "#22C55E", "medium": "#F59E0B", "hard": "#EF4444"}
        diff_color = diff_colors.get(problem.get("difficulty", "medium"), "#F59E0B")
        st.markdown(f'<span style="color:{diff_color}; font-weight:bold; text-transform:uppercase;">{problem.get("difficulty", "medium")}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(problem.get("description", ""))
        
        # Display test cases
        st.markdown("### Example Test Cases")
        test_cases = problem.get("test_cases", [])
        visible_cases = [tc for tc in test_cases if not tc.get("is_hidden", False)]
        for i, tc in enumerate(visible_cases):
            with st.expander(f"Example {i+1}", expanded=False):
                st.code(f"Input: {tc.get('input', '')}\nOutput: {tc.get('expected_output', '')}")
                
        # Submissions history
        st.markdown("### Previous Submissions")
        try:
            from services.submission_service import get_submission_history
            user_id = st.session_state.user["id"]
            history = get_submission_history(user_id, problem["id"])
            if history:
                for sub in history[:5]:
                    status_color = "#22C55E" if sub['status'] == 'accepted' else "#EF4444"
                    with st.expander(f"{sub['submitted_at'].split('T')[0]} - {sub['language']} - {sub['status']}"):
                        st.markdown(f"**Status:** <span style='color:{status_color}'>{sub['status']}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Runtime:** {sub.get('runtime_ms', '-')} ms | **Memory:** {sub.get('memory_kb', '-')} KB")
                        st.code(sub['code'], language=sub['language'])
            else:
                st.info("No previous submissions.")
        except Exception:
            st.info("Could not load submission history.")
            
    with col_edit:
        try:
            from components.code_editor import render_code_editor
            render_code_editor(problem=problem, key=f"editor_{problem['id']}")
        except ImportError:
            st.error("Code editor component is missing or has errors.")
            st.code("def solution():\n    pass", language="python")

if __name__ == "__main__":
    render_editor_page()
