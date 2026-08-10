import streamlit as st
from services.supabase_client import get_client
from services.ai_service import generate_topic_notes

@st.cache_data(ttl=300)
def get_all_topics() -> list[dict]:
    """Fetches all topics ordered by sort_order."""
    client = get_client()
    res = client.table('topics').select('*').order('sort_order').execute()
    return res.data

def get_topic_by_slug(slug: str) -> dict | None:
    """Fetches a topic by its slug."""
    client = get_client()
    res = client.table('topics').select('*').eq('slug', slug).single().execute()
    return res.data if res.data else None

def get_topic_notes(topic_id: str, section_type: str) -> str:
    """Fetches topic notes from DB, generating them via AI if not present."""
    client = get_client()
    res = client.table('topic_notes').select('content').eq('topic_id', topic_id).eq('section_type', section_type).execute()
    
    if res.data:
        return res.data[0]['content']
        
    # Not found, generate via AI
    topic = client.table('topics').select('title').eq('id', topic_id).single().execute()
    if not topic.data:
        return "Topic not found."
        
    content = generate_topic_notes(topic.data['title'], section_type)
    
    # Save to DB
    client.table('topic_notes').insert({
        'topic_id': topic_id,
        'section_type': section_type,
        'content': content
    }).execute()
    
    return content

def get_user_progress(user_id: str) -> list[dict]:
    """Fetches all topic progress for a user."""
    client = get_client()
    res = client.table('user_topic_progress').select('*').eq('user_id', user_id).execute()
    return res.data

def update_user_progress(user_id: str, topic_id: str, data: dict) -> dict:
    """Updates user's topic progress."""
    client = get_client()
    res = client.table('user_topic_progress').upsert({
        'user_id': user_id,
        'topic_id': topic_id,
        **data
    }).execute()
    return res.data[0] if res.data else {}
