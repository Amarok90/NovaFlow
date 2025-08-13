from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from .shopify_client import list_products
from .sync_products import upsert_products

load_dotenv()
app = FastAPI(title="NovaFlow API")

def require_api_key(x_api_key: str | None = Header(None, alias="x-api-key")):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid or missing x-api-key")

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/sync/shopify/products")
def sync_shopify_products(_: None = require_api_key):
    items = list_products(limit=50)
    return {"count": len(items)}

@app.post("/sync/shopify/products/save")
def sync_and_save(_: None = require_api_key):
    count = upsert_products()
    return {"saved": count}


