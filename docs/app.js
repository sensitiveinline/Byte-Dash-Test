// ---------- helpers ----------
function esc(s){return (s??'').toString().replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function unesc(s){try{return (s??'').replace(/&#(\d+);/g,(m,n)=>String.fromCharCode(+n))}catch(e){return s??''}}
function cut(s,n){s=s||'';return s.length>n?s.slice(0,n-1)+'…':s}
async function loadJson(path){
  try{
    const r = await fetch(path, {cache:'no-store'});
    if(!r.ok) throw new Error(path+' '+r.status);
    const j = await r.json();
    return Array.isArray(j) ? j : (j.items || []);
  }catch(e){ console.error('load fail:', path, e); return []; }
}

// ---------- render: Platforms (to #platformList <ol>) ----------
async function renderPlatforms(){
  const list = document.querySelector('#platformList'); // NEW
  if(!list) return;
  const items = await loadJson('data/platform_rankings.json');
  list.innerHTML='';
  items.slice(0,10).forEach((it, i)=>{
    const d7 = +((it.delta7??0));
    const arrow = d7>0?'up': d7<0?'down':'flat';
    const li = document.createElement('li');
    li.className = 'rank-item';
    li.innerHTML = `
      <div class="rank-left">
        <div class="rank-num">${i+1}</div>
        <div class="rank-texts">
          <div class="rank-title">${esc(it.name||it.id||'')}</div>
          <div class="rank-sub">score ${Number(it.score??0).toFixed(1)} · Δ7 ${d7.toFixed(1)}</div>
        </div>
      </div>
      <div class="change ${arrow}">
        <svg viewBox="0 0 24 24" class="trend ${arrow==='down'?'down':''}">
          <path d="M12 4 L12 20 M5 11 L12 4 L19 11" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        ${d7.toFixed(1)}
      </div>`;
    list.appendChild(li);
  });
}

// ---------- render: GitHub (to #repoList) ----------
function sortRepos(items, key){
  if(key==='commits') return items.sort((a,b)=>(b.commits30||0)-(a.commits30||0));
  if(key==='contributors') return items.sort((a,b)=>(b.contributors||0)-(a.contributors||0));
  if(key==='releases') return items.sort((a,b)=>(a.release_recency??9999)-(b.release_recency??9999));
  return items.sort((a,b)=>((b.new_stars30??b.stars??0)-(a.new_stars30??a.stars??0)));
}
async function renderRepos(){
  const el = document.querySelector('#repoList');    // NEW
  const sel = document.querySelector('#repoSort');
  if(!el) return;
  let items = await loadJson('data/github.json');
  items = items.slice(0,10);
  const apply = ()=>{
    el.innerHTML='';
    sortRepos(items, sel?.value||'stars').forEach(it=>{
      const repo = esc(it.repo||it.id||'');
      const url = esc(it.url||'#');
      const stars = it.new_stars30 ?? it.stars ?? 0;
      const c = it.commits30 ?? 0, u = it.contributors ?? 0, rel = it.release_recency ?? 0;
      const score = Number(it.score||0).toFixed(1);
      const desc = it.description ? `<div class="mut" style="font-size:12px;margin-top:2px;">${esc(it.description)}</div>` : '';
      const row = document.createElement('div'); row.className='item';
      row.innerHTML = `
        <div style="flex:1;min-width:0">
          <a href="${url}" target="_blank" class="kpi">${repo}</a>
          <div class="mut">★${stars} · c${c} · u${u} · rel ${rel}</div>
          ${desc}
        </div>
        <div class="mut">score ${score}</div>`;
      el.appendChild(row);
    });
  };
  sel && sel.addEventListener('change', apply);
  apply();
}

// ---------- render: News (to #newsListList) ----------
async function renderNews(){
  const el = document.querySelector('#newsListList');    // NEW
  if(!el) return;
  const items = await loadJson('data/news.json'); console.info('news items:', items.length);
  el.innerHTML='';
  items.slice(0,10).forEach(n=>{
    const host = esc(n.host || n.source || '');
    const title = esc(unesc(n.title||''));
    const url = esc(n.url||'#');
    const summary = n.summary ? esc(cut(unesc(n.summary), 140)) : '';
    const row = document.createElement('div'); row.className='item';
    row.innerHTML = `
      <div style="flex:1;min-width:0">
        <div class="kpi">${title}
          <a class="btn" style="margin-left:6px;padding:2px 6px;font-size:12px" target="_blank" href="${url}">바로가기</a>
        </div>
        ${summary?`<div class="mut" style="margin-top:4px;">${summary}</div>`:''}
      </div>
      <div class="mut">${host}</div>`;
    el.appendChild(row);
  });
}

// ---------- render: Note (to #noteBoxBox) ----------
async function renderNote(){
  const el = document.querySelector('#noteBoxBox');     // NEW
  const dateEl = document.querySelector('#noteBoxDate');
  if(!el) return;
  const arr = await loadJson('data/ai_note.json'); console.info('note items:', arr.length);
  el.innerHTML = '';
  if(!arr.length){ el.innerHTML = '<div class="mut">데이터 없음</div>'; return; }
  // 첫 항목에 날짜가 있다면 표시
  const first = arr[0]||{};
  if(dateEl && (first.date||first.created_at)) dateEl.textContent = (first.date||first.created_at);
  arr.forEach(x=>{
    const body = x.text || x.content || x.note || '';
    const row = document.createElement('div'); row.className='item';
    row.innerHTML = `<div class="insight" style="white-space:pre-line">${esc(body)}</div>`;
    el.appendChild(row);
  });
}

// ---------- boot ----------
window.addEventListener('DOMContentLoaded', async ()=>{
  await Promise.all([renderPlatforms(), renderRepos(), renderNews(), renderNote()]);
  document.querySelector('#refresh')?.addEventListener('click', ()=>location.reload());
});
