import hashlib
from datetime import datetime
from utils.constants import DIFFICULTY_COLORS

def format_xp(xp: int) -> str:
    """Formats XP with commas and suffix."""
    return f"{xp:,} XP"

def time_ago(dt: datetime) -> str:
    """Returns a string representing the time elapsed since the given datetime."""
    now = datetime.now()
    diff = now - dt
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    else:
        return f"{int(seconds // 86400)} days ago"

def slugify(text: str) -> str:
    """Converts a title to a URL slug."""
    import re
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def truncate(text: str, length: int) -> str:
    """Truncates text to the specified length."""
    if len(text) <= length:
        return text
    return text[:length-3] + '...'

def get_difficulty_badge(difficulty: str) -> str:
    """Returns a colored markdown badge for the given difficulty."""
    color = DIFFICULTY_COLORS.get(difficulty.lower(), '#808080')
    return f"<span style='background-color:{color};color:white;padding:2px 6px;border-radius:4px;font-size:12px;'>{difficulty.capitalize()}</span>"

def format_runtime(ms: int) -> str:
    """Formats runtime in milliseconds."""
    return f"{ms} ms"

def hash_prompt(prompt: str) -> str:
    """Returns SHA256 hash for cache keys."""
    return hashlib.sha256(prompt.encode()).hexdigest()
