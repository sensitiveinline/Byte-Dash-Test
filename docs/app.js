const $ = (s)=>document.querySelector(s);
const $$ = (s)=>Array.from(document.querySelectorAll(s));

async function getJSON(rel) {
  const url = new URL(rel.replace(/^\/+/, ''), document.baseURI);
  const r = await fetch(url, {cache:'no-store'});
  if (!r.ok) throw new Error(`${url} -> ${r.status}`);
  return r.json();
}

function el(tag, cls, html){ const n=document.createElement(tag); if(cls) n.className=cls; if(html) n.innerHTML=html; return n; }

function renderNote(list, data){
  list.innerHTML = '';
  const arr = Array.isArray(data) ? data : [];
  if(!arr.length){ list.append(el('div','bd-empty','데이터 없음')); return; }
  const note = arr[0];
  const meta = el('div','bd-note-meta', `<span>${note.period}</span> · <span>${note.date}</span>`);
  list.append(meta);

  (note.items||[]).forEach(it=>{
    const li = el('div','bd-item');
    li.append(el('div','bd-item-title', it.type || 'note'));
    li.append(el('div','bd-item-desc', it.text || ''));
    list.append(li);
  });
}

function renderNews(list, data){
  list.innerHTML = '';
  const items = (data && data.items) || [];
  if(!items.length){ list.append(el('div','bd-empty','데이터 없음')); return; }
  items.forEach(n=>{
    const li = el('div','bd-item');
    const title = el('a','bd-link', n.title || '(제목 없음)');
    title.href = n.url || '#'; title.target = '_blank';
    li.append(el('div','bd-item-title').appendChild(title).parentElement);
    li.append(el('div','bd-item-sub', `${n.source || ''} · score ${n.rank_score ?? ''}`));
    li.append(el('div','bd-item-desc', n.summary || ''));
    list.append(li);
  });
}

function renderGithub(list, data){
  list.innerHTML = '';
  const items = (data && data.items) || [];
  if(!items.length){ list.append(el('div','bd-empty','데이터 없음')); return; }
  items.forEach((g,i)=>{
    const li = el('div','bd-item');
    const a = el('a','bd-link', g.repo || '(repo)');
    a.href = g.url || '#'; a.target = '_blank';
    li.append(el('div','bd-item-title').appendChild(a).parentElement);
    li.append(el('div','bd-item-sub', `score ${g.score ?? ''} · ⭐ ${g.stars ?? ''} · commits30 ${g.commits30 ?? ''}`));
    list.append(li);
  });
}

function renderPlatforms(list, data){
  list.innerHTML = '';
  const items = (data && data.items) || [];
  if(!items.length){ list.append(el('div','bd-empty','데이터 없음')); return; }
  items.forEach(p=>{
    const li = el('div','bd-item');
    li.append(el('div','bd-item-title', `${p.rank}. ${p.name}`));
    li.append(el('div','bd-item-sub', `score ${p.score} ${p.delta7 ? `(Δ7 ${p.delta7})` : ''}`));
    list.append(li);
  });
}

async function loadAll(){
  try { renderNote($('#ai-note'),  await getJSON('./data/ai_note.json')); } catch(e){ $('#ai-note').innerText = e; }
  try { renderNews($('#news'),     await getJSON('./data/news.json')); } catch(e){ $('#news').innerText = e; }
  try { renderGithub($('#github'), await getJSON('./data/github.json')); } catch(e){ $('#github').innerText = e; }
  try { renderPlatforms($('#platform-rankings'), await getJSON('./data/platform_rankings.json')); } catch(e){ $('#platform-rankings').innerText = e; }
}
document.addEventListener('DOMContentLoaded', loadAll);
