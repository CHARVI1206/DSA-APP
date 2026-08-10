import streamlit as st
from streamlit_ace import st_ace

def render_code_editor(problem=None, key='main'):
    """Render the code editor with language selection and action buttons."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Code Editor")
    with col2:
        language = st.selectbox("Language", ["python", "cpp", "java"], key=f"lang_{key}")
    
    starter_code = {
        "python": "def solve():\n    # Write your code here\n    pass\n",
        "cpp": "#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your code here\n    return 0;\n}\n",
        "java": "public class Main {\n    public static void main(String[] args) {\n        // Write your code here\n    }\n}\n"
    }
    
    code = st_ace(
        value=starter_code.get(language, ""),
        language=language if language != "cpp" else "c_cpp",
        theme="monokai",
        key=f"editor_{key}",
        font_size=14,
        height=400
    )
    
    col_run, col_sub, _ = st.columns([1, 1, 3])
    
    run_clicked = col_run.button("▶ Run Code", key=f"run_{key}", use_container_width=True)
    sub_clicked = col_sub.button("✅ Submit", key=f"sub_{key}", use_container_width=True)
    
    if run_clicked or sub_clicked:
        st.session_state[f'editor_action_{key}'] = {
            'action': 'run' if run_clicked else 'submit',
            'code': code,
            'language': language
        }
    
    with st.expander("Console Output", expanded=(run_clicked or sub_clicked)):
        if f'editor_output_{key}' in st.session_state:
            output = st.session_state[f'editor_output_{key}']
            st.markdown(f'<div class="code-output">{output}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="code-output">Ready...</div>', unsafe_allow_html=True)
            
    if problem and f'editor_test_results_{key}' in st.session_state:
        results = st.session_state[f'editor_test_results_{key}']
        st.markdown("### Test Cases")
        if not results:
            st.info("No test results yet.")
        else:
            # Render test cases in a simple format
            for i, res in enumerate(results):
                status_class = "status-accepted" if res.get('passed') else "status-wrong_answer"
                st.markdown(f"**Test Case {i+1}**: <span class='{status_class}'>{'Passed' if res.get('passed') else 'Failed'}</span>", unsafe_allow_html=True)
                
    return code, language
