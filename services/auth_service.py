import streamlit as st
from services.supabase_client import get_client

def signup(email: str, password: str, display_name: str) -> dict:
    """Signs up a new user with Supabase."""
    client = get_client()
    res = client.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "display_name": display_name
            }
        }
    })
    return res.model_dump() if res else {}

def login(email: str, password: str) -> dict:
    """Logs in an existing user."""
    client = get_client()
    res = client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    if res and res.user:
        st.session_state['user'] = res.user.model_dump()
    return res.model_dump() if res else {}

def logout():
    """Logs out the current user and clears session state."""
    client = get_client()
    client.auth.sign_out()
    if 'user' in st.session_state:
        del st.session_state['user']

def get_current_user() -> dict | None:
    """Returns the currently authenticated user from session state."""
    return st.session_state.get('user')

def is_authenticated() -> bool:
    """Checks if a user is currently authenticated."""
    return get_current_user() is not None

def require_auth():
    """Stops execution if the user is not authenticated."""
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        st.stop()

def get_profile(user_id: str) -> dict:
    """Fetches the user profile from the database."""
    client = get_client()
    res = client.table('profiles').select('*').eq('id', user_id).single().execute()
    return res.data

def update_profile(user_id: str, data: dict) -> dict:
    """Updates the user profile."""
    client = get_client()
    res = client.table('profiles').update(data).eq('id', user_id).execute()
    return res.data[0] if res.data else {}
