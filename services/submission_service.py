from services.supabase_client import get_client

def create_submission(user_id: str, problem_id: str, code: str, language: str, status: str, test_results: list, runtime_ms: int = None, memory_kb: int = None, console_output: str = None) -> dict:
    """Creates a new submission record."""
    client = get_client()
    data = {
        'user_id': user_id,
        'problem_id': problem_id,
        'code': code,
        'language': language,
        'status': status,
        'test_results': test_results,
        'runtime_ms': runtime_ms,
        'memory_kb': memory_kb,
        'console_output': console_output
    }
    res = client.table('submissions').insert(data).execute()
    return res.data[0] if res.data else {}

def get_submission_history(user_id: str, problem_id: str) -> list[dict]:
    """Fetches submission history for a specific problem and user."""
    client = get_client()
    res = client.table('submissions').select('*').eq('user_id', user_id).eq('problem_id', problem_id).order('submitted_at', desc=True).execute()
    return res.data

def get_user_submissions(user_id: str, limit: int = 50) -> list[dict]:
    """Fetches recent submissions for a user."""
    client = get_client()
    res = client.table('submissions').select('*, problems(title, slug)').eq('user_id', user_id).order('submitted_at', desc=True).limit(limit).execute()
    return res.data
