from services.supabase_client import get_client
from services.topic_service import get_topic_notes

def get_ai_notes(topic_id: str, section_type: str) -> str:
    """Gets or generates AI notes for a topic section (wrapper for topic_service)."""
    return get_topic_notes(topic_id, section_type)

def create_user_note(user_id: str, title: str, content: str, topic_id: str = None, problem_id: str = None, tags: list = []) -> dict:
    """Creates a new user note."""
    client = get_client()
    data = {
        'user_id': user_id,
        'title': title,
        'content': content,
        'topic_id': topic_id,
        'problem_id': problem_id,
        'tags': tags
    }
    res = client.table('user_notes').insert(data).execute()
    return res.data[0] if res.data else {}

def update_user_note(note_id: str, data: dict) -> dict:
    """Updates an existing user note."""
    client = get_client()
    res = client.table('user_notes').update(data).eq('id', note_id).execute()
    return res.data[0] if res.data else {}

def delete_user_note(note_id: str):
    """Deletes a user note."""
    client = get_client()
    client.table('user_notes').delete().eq('id', note_id).execute()

def get_user_notes(user_id: str, topic_id: str = None, search: str = None) -> list[dict]:
    """Fetches user notes with optional filters."""
    client = get_client()
    query = client.table('user_notes').select('*, topics(title), problems(title)').eq('user_id', user_id)
    
    if topic_id:
        query = query.eq('topic_id', topic_id)
    if search:
        query = query.ilike('title', f'%{search}%')
        
    res = query.order('updated_at', desc=True).execute()
    return res.data

def search_notes(user_id: str, query: str) -> list[dict]:
    """Full-text search across user notes."""
    # Assuming ILIKE on content or title for now
    client = get_client()
    res = client.table('user_notes').select('*, topics(title), problems(title)').eq('user_id', user_id).or_(f"title.ilike.%{query}%,content.ilike.%{query}%").execute()
    return res.data
