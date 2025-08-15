import os, requests
from tenacity import retry, stop_after_attempt, wait_exponential

SB_URL = os.getenv('SUPABASE_URL','').rstrip('/')
ANON = os.getenv('SUPABASE_ANON_KEY','')
SERVICE = os.getenv('SUPABASE_SERVICE_ROLE', ANON)

def _headers(admin=False):
    key = SERVICE if admin else ANON
    return {'apikey': key, 'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(0.5, 0.5, 4))
def sb_select(table: str, limit: int=200, order: str | None=None, eq: dict|None=None):
    url = f"{SB_URL}/rest/v1/{table}?select=*"
    if order: url += f"&order={order}"
    if eq:
        for k,v in eq.items():
            url += f"&{k}=eq.{v}"
    url += f"&limit={limit}"
    r = requests.get(url, headers=_headers(), timeout=15); r.raise_for_status()
    return r.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(0.5, 0.5, 4))
def sb_upsert(table: str, rows: list[dict], on: str='id'):
    url = f"{SB_URL}/rest/v1/{table}?on_conflict={on}"
    r = requests.post(url, headers=_headers(admin=True), json=rows, timeout=20); r.raise_for_status()
    return True
