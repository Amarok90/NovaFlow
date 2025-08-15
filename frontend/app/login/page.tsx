'use client';
import { supabase } from '@/lib/supabase'; import { useState } from 'react';
export default function Login(){
  const [email,setEmail]=useState(''); const [password,setPassword]=useState(''); const [mode,setMode]=useState<'login'|'signup'>('login');
  async function submit(e:any){ e.preventDefault(); const fn = mode==='login' ? supabase.auth.signInWithPassword : supabase.auth.signUp; const { error } = await fn({ email, password }); if(error) alert(error.message); else location.href='/dashboard'; }
  async function reset(){ const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo: 'http://localhost:3000/login' }); if(error) alert(error.message); else alert('Проверьте почту'); }
  return (<div><h2>{mode==='login'?'Вход':'Регистрация'}</h2><form onSubmit={submit}><input placeholder='Email' value={email} onChange={e=>setEmail(e.target.value)}/><input placeholder='Пароль' type='password' value={password} onChange={e=>setPassword(e.target.value)}/><button type='submit'>{mode==='login'?'Войти':'Зарегистрироваться'}</button></form><button onClick={()=>setMode(mode==='login'?'signup':'login')}>Переключить режим</button><button onClick={reset}>Восстановить пароль</button></div>);
}
