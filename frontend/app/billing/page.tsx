'use client';
import { loadStripe } from '@stripe/stripe-js'; import { api } from '@/lib/api'; import { supabase } from '@/lib/supabase';
export default function Billing(){
  async function start(){ const { data } = await supabase.auth.getUser(); const user_id = data.user?.id; if(!user_id){ alert('Войдите в аккаунт'); return; } const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!); const res = await api('/billing/create-checkout-session', { method:'POST', body: JSON.stringify({ user_id }) }); await stripe?.redirectToCheckout({ sessionId: res.id }); }
  return (<div><h2>Подписка</h2><button onClick={start}>Оформить подписку</button></div>);
}
