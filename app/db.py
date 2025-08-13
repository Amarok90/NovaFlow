# app/db.py
import os
from supabase import create_client, Client

def sb() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Supabase env vars missing")
    return create_client(url, key)