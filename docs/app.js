// Byte-Dash: data-driven renderer (no dummy)
// Loads ./data/*.json and prints into <pre id="...">

async function getJSON(relPath) {
  const url = new URL(relPath.replace(/^\/+/, ''), location.href);
  const r = await fetch(url.toString(), { cache: 'no-store' });
  if (!r.ok) throw new Error(`${url} -> ${r.status}`);
  return r.json();
}
function $(sel){ return document.querySelector(sel); }
function putJSON(target, payload){
  if (!target) return;
  if (target.tagName !== 'PRE') {
    const pre = document.createElement('pre');
    pre.className = target.className || '';
    target.replaceWith(pre);
    target = pre;
  }
  target.textContent = JSON.stringify(payload, null, 2);
}
async function loadAll(){
  const jobs = [
    { id: '#ai-note',  path: './data/ai_note.json' },
    { id: '#news',     path: './data/news.json' },
    { id: '#github',   path: './data/github.json' },
    { id: '#platform-rankings', path: './data/platform_rankings.json' }
  ];
  for (const j of jobs){
    const host = $(j.id); if (!host) continue;
    try { putJSON(host, await getJSON(j.path)); }
    catch(e){ console.error('load error', j.path, e); putJSON(host, {error:String(e), path:j.path}); }
  }
}
document.addEventListener('DOMContentLoaded', loadAll);
