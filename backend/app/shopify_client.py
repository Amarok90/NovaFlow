import os, requests
from tenacity import retry, stop_after_attempt, wait_exponential

def shopify_base(store: str, version: str | None = None):
    version = version or os.getenv('SHOPIFY_API_VERSION','2024-10')
    return f"https://{store}/admin/api/{version}"

def auth_headers(access_token: str):
    return {'X-Shopify-Access-Token': access_token, 'Content-Type': 'application/json'}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(0.5, 0.5, 4))
def list_products(store: str, access_token: str, limit: int = 50) -> list[dict]:
    url = f"{shopify_base(store)}/products.json?limit={limit}"
    r = requests.get(url, headers=auth_headers(access_token), timeout=20); r.raise_for_status()
    return r.json().get('products', [])

def oauth_install_url(shop_domain: str):
    client_id = os.getenv('SHOPIFY_CLIENT_ID','')
    scopes = os.getenv('SHOPIFY_SCOPES','read_products')
    redirect = os.getenv('SHOPIFY_REDIRECT_URI','')
    return f"https://{shop_domain}/admin/oauth/authorize?client_id={client_id}&scope={scopes}&redirect_uri={redirect}"

def oauth_exchange_token(shop_domain: str, code: str) -> str:
    client_id = os.getenv('SHOPIFY_CLIENT_ID','')
    client_secret = os.getenv('SHOPIFY_CLIENT_SECRET','')
    url = f"https://{shop_domain}/admin/oauth/access_token"
    r = requests.post(url, json={'client_id': client_id, 'client_secret': client_secret, 'code': code}, timeout=20)
    r.raise_for_status()
    return r.json()['access_token']
