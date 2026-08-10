import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_client() -> Client:
    """Returns a singleton Supabase client initialized from st.secrets."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
