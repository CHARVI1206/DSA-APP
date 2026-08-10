import requests
from utils.constants import LANGUAGES

PISTON_URL = 'https://emkc.org/api/v2/piston/execute'

def execute_code(code: str, language_key: str, stdin: str = '') -> dict:
    """Executes code using the Piston API."""
    if language_key not in LANGUAGES:
        return {"error": "Unsupported language"}
    
    config = LANGUAGES[language_key]
    payload = {
        "language": config['language'],
        "version": config['version'],
        "files": [
            {
                "name": config['filename'],
                "content": code
            }
        ],
        "stdin": stdin
    }
    
    try:
        response = requests.post(PISTON_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        run_data = data.get('run', {})
        return {
            "stdout": run_data.get('stdout', ''),
            "stderr": run_data.get('stderr', ''),
            "exit_code": run_data.get('code', 1),
            "error": None
        }
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": -1, "error": str(e)}

def run_test_cases(code: str, language_key: str, test_cases: list[dict]) -> list[dict]:
    """Runs a list of test cases against the code."""
    results = []
    for tc in test_cases:
        stdin = tc.get('input', '')
        expected = tc.get('expected', '')
        
        exec_res = execute_code(code, language_key, stdin)
        
        actual = exec_res['stdout'].strip()
        passed = (actual == str(expected).strip()) and (exec_res['exit_code'] == 0)
        
        results.append({
            "input": stdin,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "error": exec_res['stderr'] if exec_res['exit_code'] != 0 else None
        })
        
    return results
