from datetime import date
from services.supabase_client import get_client
from services.ai_service import generate_flashcards
from utils.spaced_repetition import calculate_next_review, get_due_date

def get_or_generate_flashcards(topic_id: str, topic_name: str) -> list[dict]:
    """Fetches existing flashcards or generates them via AI."""
    client = get_client()
    res = client.table('flashcards').select('*').eq('topic_id', topic_id).execute()
    
    if res.data:
        return res.data
        
    # Generate new ones
    generated = generate_flashcards(topic_name)
    cards_data = []
    for c in generated:
        cards_data.append({
            'topic_id': topic_id,
            'front_content': c.get('front', ''),
            'back_content': c.get('back', '')
        })
        
    if cards_data:
        insert_res = client.table('flashcards').insert(cards_data).execute()
        return insert_res.data
    return []

def get_due_cards(user_id: str) -> list[dict]:
    """Gets all due flashcards for a user."""
    client = get_client()
    today = date.today().isoformat()
    # Assuming user_flashcard_progress joins with flashcards
    res = client.table('user_flashcard_progress').select('*, flashcards(*)').eq('user_id', user_id).lte('next_review_date', today).execute()
    return res.data

def get_due_cards_by_topic(user_id: str, topic_id: str) -> list[dict]:
    """Gets due flashcards filtered by topic."""
    cards = get_due_cards(user_id)
    return [c for c in cards if c['flashcards']['topic_id'] == topic_id]

def review_card(user_id: str, flashcard_id: str, quality: int) -> dict:
    """Processes a card review and updates SR progress."""
    client = get_client()
    progress = client.table('user_flashcard_progress').select('*').eq('user_id', user_id).eq('flashcard_id', flashcard_id).execute()
    
    if not progress.data:
        # Should normally exist if initialized
        ease_factor, interval, repetitions = 2.5, 0, 0
    else:
        p = progress.data[0]
        ease_factor, interval, repetitions = p['ease_factor'], p['interval_days'], p['repetitions']
        
    new_interval, new_ease, new_reps = calculate_next_review(quality, repetitions, ease_factor, interval)
    new_date = get_due_date(new_interval)
    
    data = {
        'user_id': user_id,
        'flashcard_id': flashcard_id,
        'ease_factor': new_ease,
        'interval_days': new_interval,
        'repetitions': new_reps,
        'next_review_date': new_date.isoformat(),
        'last_reviewed_at': 'now()'
    }
    
    res = client.table('user_flashcard_progress').upsert(data).execute()
    return res.data[0] if res.data else {}

def get_review_stats(user_id: str) -> dict:
    """Gets SR stats."""
    client = get_client()
    today = date.today().isoformat()
    
    due_today_res = client.table('user_flashcard_progress').select('id', count='exact').eq('user_id', user_id).lte('next_review_date', today).execute()
    
    return {
        "due_today": due_today_res.count if due_today_res else 0,
        "due_week": 0, # Could do a date range query
        "total_reviewed": 0,
        "retention_rate": 0.0
    }

def initialize_cards_for_user(user_id: str, topic_id: str):
    """Initializes progress for new cards for a user."""
    client = get_client()
    cards = client.table('flashcards').select('id').eq('topic_id', topic_id).execute()
    
    progress_data = [{
        'user_id': user_id,
        'flashcard_id': c['id'],
        'next_review_date': date.today().isoformat(),
        'ease_factor': 2.5,
        'interval_days': 0,
        'repetitions': 0
    } for c in cards.data]
    
    if progress_data:
        # Upsert in case some exist
        client.table('user_flashcard_progress').upsert(progress_data).execute()
