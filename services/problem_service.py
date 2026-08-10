from services.supabase_client import get_client

def get_problems(topic_id: str = None, difficulty: str = None, search: str = None, bookmarked_by: str = None) -> list[dict]:
    """Fetches problems based on filters."""
    client = get_client()
    query = client.table('problems').select('*')
    
    if topic_id:
        query = query.eq('topic_id', topic_id)
    if difficulty:
        query = query.eq('difficulty', difficulty)
    if search:
        query = query.ilike('title', f'%{search}%')
        
    if bookmarked_by:
        bookmarks = get_bookmarks(bookmarked_by)
        if not bookmarks:
            return []
        query = query.in_('id', bookmarks)
        
    res = query.execute()
    return res.data

def get_problem_by_slug(slug: str) -> dict | None:
    """Fetches a problem by its slug."""
    client = get_client()
    res = client.table('problems').select('*, topics(title, slug)').eq('slug', slug).single().execute()
    return res.data if res.data else None

def create_problem(data: dict) -> dict:
    """Creates a new problem."""
    client = get_client()
    res = client.table('problems').insert(data).execute()
    return res.data[0] if res.data else {}

def toggle_bookmark(user_id: str, problem_id: str) -> bool:
    """Toggles bookmark status and returns the new state."""
    client = get_client()
    existing = client.table('bookmarks').select('*').eq('user_id', user_id).eq('problem_id', problem_id).execute()
    
    if existing.data:
        client.table('bookmarks').delete().eq('user_id', user_id).eq('problem_id', problem_id).execute()
        return False
    else:
        client.table('bookmarks').insert({'user_id': user_id, 'problem_id': problem_id}).execute()
        return True

def get_bookmarks(user_id: str) -> list[str]:
    """Returns a list of bookmarked problem IDs for a user."""
    client = get_client()
    res = client.table('bookmarks').select('problem_id').eq('user_id', user_id).execute()
    return [b['problem_id'] for b in res.data]

def get_problem_stats(problem_id: str) -> dict:
    """Gets stats for a specific problem."""
    client = get_client()
    res = client.table('submissions').select('status').eq('problem_id', problem_id).execute()
    
    total = len(res.data)
    accepted = len([s for s in res.data if s['status'] == 'Accepted'])
    
    return {
        "total_submissions": total,
        "acceptance_rate": (accepted / total * 100) if total > 0 else 0
    }
