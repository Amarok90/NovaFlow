
import os
import requests

def _base_url():
    store = os.getenv("SHOPIFY_STORE", "").strip()
    version = os.getenv("SHOPIFY_API_VERSION", "2025-07")
    if not store:
        raise RuntimeError("SHOPIFY_STORE is not set in .env")
    return f"https://{store}/admin/api/{version}"

def _headers():
    token = os.getenv("SHOPIFY_ACCESS_TOKEN", "").strip()
    if not token:
        raise RuntimeError("SHOPIFY_ACCESS_TOKEN is not set in .env")
    return {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }

def list_products(limit: int = 50) -> list[dict]:
    """Возвращает список продуктов из Shopify (только первая страница)."""
    url = f"{_base_url()}/products.json?limit={limit}"
    r = requests.get(url, headers=_headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("products", [])
