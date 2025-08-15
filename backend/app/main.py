from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse
from dotenv import load_dotenv
from .security import require_bearer_token
from .shopify_client import list_products, oauth_install_url, oauth_exchange_token
from .supabase_client import sb_select, sb_upsert
from .stripe_routes import router as stripe_router
from .utils import csv_stream

load_dotenv()
app = FastAPI(title='NovaFlow Backend PRO')

@app.get('/')
def root():
    return RedirectResponse(url='/docs')

@app.get('/health')
def health():
    return {'ok': True}

@app.get('/shopify/install')
def shopify_install(shop: str):
    return RedirectResponse(oauth_install_url(shop))

@app.get('/shopify/callback')
def shopify_callback(shop: str, code: str):
    token = oauth_exchange_token(shop, code)
    sb_upsert('shops', [{ 'platform': 'shopify', 'shop_domain': shop, 'access_token': token, 'user_id': 'demo-user' }], on='shop_domain')
    return JSONResponse({'ok': True, 'shop': shop})

@app.post('/sync/shopify/products', dependencies=[Depends(require_bearer_token)])
def sync_shopify_products(claims: dict = Depends(require_bearer_token)):
    user_id = claims.get('sub') or 'demo-user'
    shops = sb_select('shops', limit=1, eq={'user_id': user_id, 'platform': 'shopify'})
    if not shops:
        raise HTTPException(status_code=400, detail='No connected Shopify shop')
    shop = shops[0]
    items = list_products(shop['shop_domain'], shop['access_token'], limit=50)
    rows = []
    for p in items:
        price = None
        try: price = float(p['variants'][0]['price'])
        except Exception: pass
        sku = p['variants'][0].get('sku') if p.get('variants') else None
        stock = p['variants'][0].get('inventory_quantity') if p.get('variants') else None
        rows.append({ 'id': str(p['id']), 'user_id': user_id, 'shop_domain': shop['shop_domain'], 'title': p.get('title'), 'price': price, 'sku': sku, 'stock': stock, 'stats': p })
    if rows:
        sb_upsert('products', rows, on='id')
    return {'saved': len(rows)}

@app.get('/products', dependencies=[Depends(require_bearer_token)])
def list_products_for_ui(limit: int = 200, claims: dict = Depends(require_bearer_token)):
    user_id = claims.get('sub') or 'demo-user'
    data = sb_select('products', limit=limit, order='updated_at.desc', eq={'user_id': user_id})
    return data

@app.post('/discover/suggest', dependencies=[Depends(require_bearer_token)])
async def discover(body: dict, claims: dict = Depends(require_bearer_token)):
    niche = body.get('niche','general'); country = body.get('country','US'); q = body.get('q','')
    items = []
    for i in range(10):
        items.append({ 'id': f'suggest-{i}', 'title': f"{niche.title()} Product {i} {q}".strip(), 'country': country, 'niche': niche, 'price': round(9.99 + i*2.5, 2), 'probability': 62 + i, 'stats': {'trend':'up','search_volume':1000+i*150} })
    return {'items': items}

@app.get('/export/products', dependencies=[Depends(require_bearer_token)])
def export_products(claims: dict = Depends(require_bearer_token)):
    user_id = claims.get('sub') or 'demo-user'
    data = sb_select('products', limit=1000, order='updated_at.desc', eq={'user_id': user_id})
    headers = ['id','title','price','sku','stock','shop_domain']
    def rows():
        yield ','.join(headers) + '\n'
        for r in data:
            vals = [str(r.get(k,'')) for k in headers]
            yield ','.join(vals) + '\n'
    return StreamingResponse(csv_stream(rows()), media_type='text/csv', headers={'Content-Disposition': 'attachment; filename=products.csv'})

app.include_router(stripe_router, prefix='/billing', tags=['billing'])
