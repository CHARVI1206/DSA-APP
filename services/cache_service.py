import hashlib
import json
from datetime import datetime, timedelta
from services.supabase_client import get_client

def generate_cache_key(*args) -> str:
    """Generates a deterministic SHA256 hash for the given arguments."""
    key_string = "_".join(str(arg) for arg in args)
    return hashlib.sha256(key_string.encode()).hexdigest()

def get_cached(cache_key: str) -> str | None:
    """Fetches a cached response from the database."""
    client = get_client()
    res = client.table('ai_cache').select('response, expires_at').eq('cache_key', cache_key).execute()
    if res.data:
        entry = res.data[0]
        if datetime.fromisoformat(entry['expires_at']) > datetime.now():
            client.rpc('increment_cache_hit', {'c_key': cache_key}).execute() # Assuming such RPC or we do a simple update
            return entry['response']
        else:
            client.table('ai_cache').delete().eq('cache_key', cache_key).execute()
    return None

def set_cached(cache_key: str, prompt_hash: str, response: str, model: str = 'gemini-2.0-flash', ttl_days: int = 30):
    """Caches an AI response."""
    client = get_client()
    expires_at = (datetime.now() + timedelta(days=ttl_days)).isoformat()
    client.table('ai_cache').upsert({
        'cache_key': cache_key,
        'prompt_hash': prompt_hash,
        'response': response,
        'model': model,
        'expires_at': expires_at,
        'hit_count': 0
    }).execute()

def clear_expired():
    """Deletes expired cache entries."""
    client = get_client()
    now = datetime.now().isoformat()
    client.table('ai_cache').delete().lt('expires_at', now).execute()
