const $ = (s)=>document.querySelector(s);

async function getJSON(rel){
  const url = new URL(rel.replace(/^\/+/, ''), location.href);
  const r = await fetch(url, {cache:'no-store'});
  if(!r.ok) throw new Error(`${url} -> ${r.status}`);
  return r.json();
}
const upIcon = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 5l7 7h-4v7h-6v-7H5l7-7z"/></svg>';

function fmt(n, d=1){ if(n===undefined||n===null||isNaN(n)) return '—'; return Number(n).toFixed(d); }
function deltaClass(x){ if(x>0) return 'up'; if(x<0) return 'down'; return 'flat'; }

function renderPlatforms(items){
  const list = $('#platformList'); list.innerHTML='';
  const arr = (items||[]).slice(0,10);
  arr.forEach(p=>{
    const li = document.createElement('li'); li.className='rank-item';
    const left = document.createElement('div'); left.className='rank-left';
    left.innerHTML = `
      <div class="rank-num">${p.rank ?? ''}</div>
      <div class="rank-texts">
        <div class="rank-title">${p.name ?? p.id ?? '—'}</div>
        <div class="rank-sub">score ${fmt(p.score)} ${p.delta7 ? `· Δ7 ${fmt(p.delta7)}` : ''}</div>
      </div>`;
    const right = document.createElement('div');
    const dc = deltaClass(p.delta7||0);
    right.innerHTML = `<div class="change ${dc}">${upIcon}<span>${fmt(p.delta7)}</span></div>`;
    li.append(left, right); list.append(li);
  });
}

function renderRepos(data){
  const wrap = $('#repoList'); wrap.innerHTML='';
  const q = ($('#q')?.value||'').toLowerCase();
  let items = (data?.items||[]).filter(x=>{
    const key = `${x.repo||''} ${x.desc||''}`.toLowerCase();
    return !q || key.includes(q);
  });
  const sort = $('#repoSort').value;
  items.sort((a,b)=>(b[sort]??0)-(a[sort]??0));
  items = items.slice(0,10);

  items.forEach(g=>{
    const div = document.createElement('div'); div.className='news-card';
    const repoName = g.repo || g.name || '—';
    const href = g.url || (g.repo ? `https://github.com/${g.repo}` : '#');
    div.innerHTML = `
      <div class="row">
        <a class="news-title" href="${href}" target="_blank">${repoName}</a>
        <span class="mut">score ${fmt(g.score)} · ⭐ ${g.stars ?? g.new_stars30 ?? '—'} · commits30 ${g.commits30 ?? '—'}</span>
      </div>
      <div class="mut">${g.desc||''}</div>`;
    wrap.append(div);
  });
}

function renderNews(data){
  const wrap = $('#newsList'); wrap.innerHTML='';
  (data?.items||[]).slice(0,10).forEach(n=>{
    const div = document.createElement('div'); div.className='news-card';
    const url = n.url || '#';
    div.innerHTML = `
      <a class="news-title" href="${url}" target="_blank">${n.title||'(제목없음)'}</a>
      <div class="news-meta">${n.source||''} · score ${fmt(n.rank_score,2)}</div>
      <div>${n.summary||n.takeaway||''}</div>`;
    wrap.append(div);
  });
}

function renderNote(arr){
  const box = $('#noteBox'); const date = $('#noteDate'); box.innerHTML='';
  if(!Array.isArray(arr)||!arr.length){ box.textContent='데이터 없음'; return; }
  const note = arr[0]; date.textContent = `${note.period||''} · ${note.date||''}`;
  (note.items||[]).slice(0,10).forEach(it=>{
    const d = document.createElement('div'); d.className='note-line';
    d.innerHTML = `<div class="mut">${it.type||'note'}</div><div>${it.text||''}</div>`;
    box.append(d);
  });
}

async function boot(){
  try { renderPlatforms((await getJSON('./data/platform_rankings.json')).items); } catch(e){ console.error(e); }
  try { renderRepos(await getJSON('./data/github.json')); } catch(e){ console.error(e); }
  try { renderNews(await getJSON('./data/news.json')); } catch(e){ console.error(e); }
  try { renderNote(await getJSON('./data/ai_note.json')); } catch(e){ console.error(e); }
}
document.addEventListener('DOMContentLoaded', ()=>{
  $('#repoSort').addEventListener('change', boot);
  $('#q').addEventListener('input', boot);
  boot();
});
