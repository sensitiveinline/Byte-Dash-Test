async function j(path){
  const r = await fetch(path+"?t="+Date.now(), {cache:"no-store"});
  try { return await r.json(); } catch { return {}; }
}
function arr(x){ return Array.isArray(x)?x:(x&&Array.isArray(x.items))?x.items:[]; }
function esc(s){ return (s??"").toString().replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function unesc(s){ return (s||"").replaceAll("&#8217;","'").replaceAll("&amp;","&").replaceAll("&lt;","<").replaceAll("&gt;",">"); }
function cut(s,n){ s=String(s||""); return s.length>n? s.slice(0,n)+"…" : s; }

async function render(){
  // 1) 데이터 로드
  const plats = arr(await j("./data/platform_rankings.json")).slice(0,10);
  const repos = arr(await j("./data/github.json")).slice(0,10);
  const news  = arr(await j("./data/news.json")).slice(0,10);
  const noteJ = await j("./data/ai_note.json");

  // 2) 플랫폼
  const $p = document.querySelector("#platformList");
  if($p){
    $p.innerHTML = plats.map((i,idx)=>`
      <li class="rank-item">
        <div class="rank-left">
          <div class="rank-num">${i.rank ?? (idx+1)}</div>
          <div class="rank-texts">
            <div class="rank-title">${esc(i.name||i.id)}</div>
            <div class="rank-sub">score ${i.score??"-"} · Δ7 ${i.delta7??"0.0"} ${ (i.sources||[]).slice(0,1).map(s=>{ try{ return `· <a target="_blank" href="${s.url}">${new URL(s.url).host}</a>`;}catch{return"";} }).join("")}</div>
          </div>
        </div>
        <div class="change ${i.delta7>0?'up':i.delta7<0?'down':'flat'}">
          <svg class="trend" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 17l6-6 4 4 8-8"/></svg>
          <span>${i.delta7>0?`+${i.delta7}`:(i.delta7??0)}</span>
        </div>
      </li>`).join("") || `<li class="rank-item"><div class="rank-texts">데이터 없음</div></li>`;
  }

  // 3) GitHub
  const $r = document.querySelector("#repoList");
  const $sort = document.querySelector("#repoSort");
  const applyRepo = ()=>{
    if(!$r) return;
    const key = ($sort?.value)||"stars";
    const map = {stars:"new_stars30", commits:"commits30", releases:"release_recency"};
    const m = map[key] || "new_stars30";
    const list = [...repos].sort((a,b)=> (b[m]||0)-(a[m]||0));
    $r.innerHTML = (list.length? list:[]).map(it=>`
      <div class="row" style="padding:8px 0; border-top:1px dashed var(--bd);">
        <div style="min-width:0">
          <div class="kpi"><a target="_blank" href="${esc(it.url||"#")}">${esc(it.repo||it.id||"repo")}</a></div>
          <div class="mut">★${it.new_stars30??it.stars??0} · c${it.commits30??0} · u${it.contributors??0} · rel ${it.release_recency??0}</div>
        </div>
        <div class="mut" style="font-size:12px;margin-top:2px;">${esc(it.description||""(no description)"")}</div>
        <div class="mut">score ${it.score??"-"}</div>
      </div>`).join("") || `<div class="mut">리포 데이터 없음</div>`;
  };
  applyRepo(); if($sort) $sort.onchange = applyRepo;

  // 4) 뉴스 (요약 짧게)
  const $n = document.querySelector("#newsList");
  if($n){
    $n.innerHTML = news.map(n=>`
      <div style="padding:8px 0; border-top:1px dashed var(--bd);">
        <div class="kpi"><a target="_blank" href="${esc(n.url)}">${esc(unesc(n.title||""))}</a></div>
        <div class="mut">${esc(n.host||"")} — R ${n.rank_score??"-"}</div>
        ${n.summary ? `<div class="mut" style="margin-top:4px;">${esc(cut(unesc(n.summary), 120))}</div>` : ""}
      </div>`).join("") || `<div class="mut">뉴스 없음</div>`;
  }

  // 5) AI Note (5줄 기본, 더보기)
  const $note = document.querySelector("#noteBox");
  const $date = document.querySelector("#noteDate");
  if($note){
    const text = (arr(noteJ)[0]?.text || noteJ.items?.[0]?.text || "").trim();
    if($date) $date.textContent = noteJ.date || noteJ.week_ending || "";
    if(!text){ $note.innerHTML = `<div class="mut">노트 없음</div>`; return; }
    const lines = text.split(/\r?\n/).filter(Boolean);
    const short = lines.slice(0,5).map(l=>`<div>${esc(cut(l, 90))}</div>`).join("");
    const full  = lines.map(l=>`<div>${esc(l)}</div>`).join("");
    $note.innerHTML = short + (lines.length>5? ` <button class="btn" id="moreNote" style="margin-top:8px;">더보기</button>`:"");
    const btn = document.querySelector("#moreNote");
    if(btn){
      let open=false;
      btn.onclick=()=>{ open=!open; $note.innerHTML = open? full+` <button class="btn" id="lessNote" style="margin-top:8px;">접기</button>` : short+` <button class="btn" id="moreNote" style="margin-top:8px;">더보기</button>`; if(!open) document.querySelector("#moreNote").onclick=btn.onclick; else document.querySelector("#lessNote").onclick=btn.onclick; };
    }
  }
}

document.addEventListener("DOMContentLoaded", render);
