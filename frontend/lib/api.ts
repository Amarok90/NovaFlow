import { supabase } from './supabase';
export async function api(path: string, init: RequestInit = {}){
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token ?? '';
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}${path}`, {
    ...init, headers: {'Authorization': `Bearer ${token}`, 'Content-Type':'application/json', ...(init.headers||{})}
  });
  if(!res.ok) throw new Error(await res.text());
  const ct = res.headers.get('content-type')||'';
  return ct.includes('text/csv') ? await res.text() : await res.json();
}
