export async function loadJson(path){
  const r = await fetch(path + "?t=" + Date.now(), {cache:"no-store"});
  try { return await r.json(); } catch { return {}; }
}
export function items(x){ return Array.isArray(x)?x:(x&&Array.isArray(x.items))?x.items:[]; }
export function esc(s){ return (s??'').toString().replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
export function fmt(n){ if(n==null||isNaN(n)) return "-"; return n.toLocaleString(); }
export function when(x){ return x?.generated_at ? new Date(x.generated_at).toLocaleString() : ""; }
