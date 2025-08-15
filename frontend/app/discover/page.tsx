'use client';
import { useState } from 'react'; import { api } from '@/lib/api';
export default function Discover(){
  const [country,setCountry]=useState('US'); const [niche,setNiche]=useState('fitness'); const [q,setQ]=useState(''); const [items,setItems]=useState<any[]>([]);
  async function search(){ const res = await api('/discover/suggest', { method:'POST', body: JSON.stringify({ country, niche, q }) }); setItems(res.items); }
  return (<div><h2>Discover</h2><input value={country} onChange={e=>setCountry(e.target.value)} /><input value={niche} onChange={e=>setNiche(e.target.value)} /><input value={q} onChange={e=>setQ(e.target.value)} /><button onClick={search}>Найти товары</button><ul>{items.map((i:any)=>(<li key={i.id}>{i.title} • {i.country} • {i.niche} • {i.price}$ • {i.probability}%</li>))}</ul></div>);
}
