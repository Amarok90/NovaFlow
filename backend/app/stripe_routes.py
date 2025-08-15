import os, stripe
from fastapi import APIRouter, HTTPException, Request
from .supabase_client import sb_upsert

router = APIRouter()
stripe.api_key = os.getenv('STRIPE_SECRET_KEY','')
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET','')
PRICE_ID = os.getenv('STRIPE_PRICE_ID','')

@router.post('/create-checkout-session')
async def create_checkout_session(body: dict):
    user_id = body.get('user_id')
    if not user_id: raise HTTPException(status_code=400, detail='user_id required')
    session = stripe.checkout.Session.create(
        mode='subscription', line_items=[{'price': PRICE_ID, 'quantity': 1}],
        success_url=body.get('success_url','http://localhost:3000/dashboard?success=1'),
        cancel_url=body.get('cancel_url','http://localhost:3000/billing?canceled=1'),
        client_reference_id=user_id
    )
    return {'id': session.id}

@router.post('/webhook')
async def stripe_webhook(request: Request):
    payload = await request.body(); sig = request.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    et = event['type']; obj = event['data']['object']
    if et in ('checkout.session.completed','customer.subscription.updated','invoice.paid'):
        user_id = obj.get('client_reference_id') or (obj.get('metadata',{}) or {}).get('user_id')
        sub_id = obj.get('subscription') or obj.get('id'); status = obj.get('status','active')
        if user_id:
            sb_upsert('subscriptions', [{ 'user_id': user_id, 'stripe_subscription_id': sub_id, 'status': status }], on='user_id')
    return {'received': True}
