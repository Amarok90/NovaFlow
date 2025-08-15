'use client';
import { useEffect, useState } from 'react'; import { api } from '@/lib/api';
export default function Dashboard(){
  const [products,setProducts]=useState<any[]>([]); const [loading,setLoading]=useState(false);
  async function sync(){ setLoading(true); try { await api('/sync/shopify/products', { method:'POST' }); await load(); } catch(e:any){ alert(e.message); } setLoading(false); }
  async function load(){ try{ const data = await api('/products'); setProducts(data); } catch(e:any){ alert(e.message); } }
  useEffect(()=>{ load(); },[]);
  return (<div><h2>Dashboard</h2><button onClick={sync} disabled={loading}>Sync products</button><button onClick={async ()=>{ const txt = await api('/export/products'); const blob = new Blob([txt], { type:'text/csv' }); const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url; a.download = 'products.csv'; a.click(); URL.revokeObjectURL(url);} }>Export CSV</button><table><thead><tr><th>Title</th><th>Price</th><th>SKU</th><th>Stock</th></tr></thead><tbody>{products.map((p:any)=>(<tr key={p.id}><td>{p.title}</td><td>{p.price}</td><td>{p.sku}</td><td>{p.stock}</td></tr>))}</tbody></table></div>);
}
