# app/sync_products.py
from .shopify_client import list_products
from .db import sb
import os, math

def to_price(p):
    # берём первую цену из варианта
    try:
        return float(p["variants"][0]["price"])
    except Exception:
        return None

def to_stock(p):
    try:
        return int(p["variants"][0].get("inventory_quantity", 0))
    except Exception:
        return None

def upsert_products():
    store = os.getenv("SHOPIFY_STORE")
    items = list_products(limit=50)  # первая страница (для MVP)
    rows = []
    for p in items:
        rows.append({
            "id": str(p["id"]),
            "shop_domain": store,
            "title": p.get("title"),
            "price": to_price(p),
            "sku": p["variants"][0].get("sku") if p.get("variants") else None,
            "stock": to_stock(p),
            "raw": p
        })
    client = sb()
    # upsert по primary key
    if rows:
        client.table("products").upsert(rows).execute()
    return len(rows)