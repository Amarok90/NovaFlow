'use client';
import { useState } from 'react';
export default function ShopifyConnect(){
  const [shop,setShop]=useState('your-store.myshopify.com');
  function connect(){ window.location.href = `${process.env.NEXT_PUBLIC_API_BASE}/shopify/install?shop=${encodeURIComponent(shop)}`; }
  return (<div><h2>Подключить Shopify</h2><input value={shop} onChange={e=>setShop(e.target.value)} placeholder='my-shop.myshopify.com'/><button onClick={connect}>Подключить</button></div>);
}
