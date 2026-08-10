from datetime import date, timedelta
from services.supabase_client import get_client

def log_activity(user_id: str, activity_type: str, reference_id: str = None, reference_type: str = None, xp_earned: int = 0, metadata: dict = {}) -> dict:
    """Logs user activity."""
    client = get_client()
    data = {
        'user_id': user_id,
        'activity_type': activity_type,
        'reference_id': reference_id,
        'reference_type': reference_type,
        'xp_earned': xp_earned,
        'metadata': metadata
    }
    res = client.table('activity_log').insert(data).execute()
    
    if xp_earned > 0:
        add_xp(user_id, xp_earned)
        
    update_streak(user_id)
    return res.data[0] if res.data else {}

def add_xp(user_id: str, amount: int):
    """Adds XP to user's profile."""
    client = get_client()
    client.rpc('add_user_xp', {'u_id': user_id, 'xp_amount': amount}).execute()

def get_heatmap_data(user_id: str, days: int = 365) -> list[dict]:
    """Gets daily activity counts for heatmap."""
    client = get_client()
    start_date = (date.today() - timedelta(days=days)).isoformat()
    # Simplified version - you might need a DB view or RPC for true daily grouping
    res = client.table('activity_log').select('created_at').eq('user_id', user_id).gte('created_at', start_date).execute()
    
    counts = {}
    for r in res.data:
        d = r['created_at'][:10]
        counts[d] = counts.get(d, 0) + 1
        
    return [{"date": k, "count": v} for k, v in counts.items()]

def get_streak_info(user_id: str) -> dict:
    """Gets user streak information."""
    client = get_client()
    res = client.table('profiles').select('current_streak, longest_streak, last_active').eq('id', user_id).single().execute()
    return res.data if res.data else {}

def get_weekly_report(user_id: str) -> dict:
    """Gets stats for the last 7 days."""
    return {} # Placeholder for actual logic

def get_user_stats(user_id: str) -> dict:
    """Gets comprehensive user stats."""
    client = get_client()
    subs = client.table('submissions').select('status').eq('user_id', user_id).execute()
    total = len(subs.data)
    acc = len([s for s in subs.data if s['status'] == 'Accepted'])
    
    return {
        "total_solved": acc,
        "acceptance_rate": (acc / total * 100) if total > 0 else 0,
        "avg_solve_time": 0,
        "topics_completed": 0,
        "strong_topics": [],
        "weak_topics": []
    }

def check_achievements(user_id: str) -> list[dict]:
    """Checks and awards new achievements."""
    return [] # Placeholder

def get_achievements(user_id: str) -> dict:
    """Gets earned and locked achievements."""
    return {"earned": [], "locked": []} # Placeholder

def update_streak(user_id: str):
    """Updates the user's streak using an RPC."""
    client = get_client()
    client.rpc('update_user_streak', {'user_id_param': user_id}).execute()
