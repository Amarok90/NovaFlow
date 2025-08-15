import os, requests
from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from cachetools import TTLCache

API_KEY = os.getenv('API_KEY','changeme_api_key')
bearer = HTTPBearer(auto_error=False)
JWKS_URL = os.getenv('SUPABASE_JWKS_URL','')
_jwks_cache = TTLCache(maxsize=1, ttl=3600)

def require_api_key(x_api_key: str | None = Header(None, alias='x-api-key')):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail='Invalid or missing x-api-key')

def _get_jwks():
    if 'jwks' in _jwks_cache:
        return _jwks_cache['jwks']
    if not JWKS_URL:
        raise HTTPException(status_code=500, detail='JWKS URL not configured')
    r = requests.get(JWKS_URL, timeout=10); r.raise_for_status()
    jwks = r.json(); _jwks_cache['jwks'] = jwks; return jwks

def verify_jwt(token: str):
    jwks = _get_jwks()
    try:
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get('kid')
        key = next((k for k in jwks['keys'] if k['kid']==kid), None)
        if not key: raise Exception('No matching JWK')
        payload = jwt.decode(token, key, algorithms=[key.get('alg','RS256')], audience=None, options={'verify_aud': False})
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f'Invalid JWT: {e}')

def require_bearer_token(creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=401, detail='Missing bearer token')
    return verify_jwt(creds.credentials)
