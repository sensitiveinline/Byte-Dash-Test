import {loadJson, items, esc, fmt, when} from "./api.js";

async function render(){
  // 1) 데이터 로드
  const platsRaw = await loadJson("./data/platform_rankings.json");
  const reposRaw = await loadJson("./data/github.json");
  const newsRaw  = await loadJson("./data/news.json");
  const noteRaw  = await loadJson("./data/ai_note.json");

  // 2) 메타 표시
  const platMeta = document.querySelector("#platMeta");
  if(platMeta) platMeta.textContent = when(platsRaw);
  const newsMeta = document.querySelector("#newsMeta");
  if(newsMeta) newsMeta.textContent = when(newsRaw);

  // 3) 플랫폼 순위
  const plats = items(platsRaw).slice(0,10);
  const $plats = document.querySelector("#platforms");
  if($plats){
    $plats.innerHTML = plats.length ? plats.map(i => {
      const src = (i.sources||[]).slice(0,2).map(s=>{
        try{ return `<a target="_blank" href="${s.url}">${new URL(s.url).host}</a>` }catch{ return "" }
      }).join(" · ");
      const d = (i.delta7==null) ? "" : (i.delta7>0?`<span class="delta up">+${i.delta7}</span>`:i.delta7<0?`<span class="delta down">${i.delta7}</span>`:`<span class="delta flat">0.0</span>`);
      return `
        <div class="item">
          <div class="row" style="gap:8px;">
            <span class="rank">${i.rank??""}</span>
            <div style="flex:1">
              <div class="row"><div class="title">${esc(i.name||i.id)}</div><div>score ${fmt(i.score)}</div></div>
              <div class="hint">${src}</div>
            </div>
            ${d}
          </div>
        </div>`;
    }).join("") : `<div class="empty">플랫폼 데이터 없음</div>`;
  }

  // 4) GitHub 리스트 (정렬 셀렉터 대응)
  const repos = items(reposRaw).slice(0,10);
  const $repos = document.querySelector("#repos");
  const $sort  = document.querySelector("#repoSort");
  const applyRepo = ()=>{
    if(!$repos) return;
    const key = ($sort?.value)||"stars";
    const mapKey = {stars:"new_stars30", commits:"commits30", contributors:"contributors"}[key] || "new_stars30";
    const sorted = [...repos].sort((a,b)=> (b[mapKey]||0) - (a[mapKey]||0));
    $repos.innerHTML = sorted.map(r=>`
      <div class="item">
        <div style="flex:1">
          <div class="row">
            <a target="_blank" href="${esc(r.url||"#")}">${esc(r.repo||r.id||"repo")}</a>
            <span class="hint">score ${fmt(r.score)}</span>
          </div>
          <div class="hint">★${fmt(r.new_stars30??r.stars)} · c${fmt(r.commits30)} · u${fmt(r.contributors)} · rel ${r.release_recency??"-"}</div>
        </div>
      </div>`).join("") || `<div class="empty">리포 데이터 없음</div>`;
  };
  applyRepo();
  if($sort) $sort.onchange = applyRepo;

  // 5) 뉴스 (Top10)
  const news = items(newsRaw).slice(0,10);
  const $news = document.querySelector("#news");
  if($news){
    $news.innerHTML = news.length ? news.map(n=>`
      <div class="item">
        <div style="flex:1">
          <a target="_blank" href="${esc(n.url)}">${esc(n.title)}</a>
          <div class="hint">${esc(n.host||"")} · R=${n.rank_score??"-"}</div>
          ${n.summary? `<div class="insight">${esc(n.summary)}</div>` : ""}
        </div>
      </div>`).join("") : `<div class="empty">뉴스 데이터 없음</div>`;
  }

  // 6) AI Note (daily/weekly 구조 모두 지원)
  const $note = document.querySelector("#note");
  if($note){
    const arr = items(noteRaw);
    const text = arr[0]?.text || (noteRaw.items?.[0]?.text) || "";
    $note.innerHTML = text ? text.split("\n").map(l=>`<div>${esc(l)}</div>`).join("") : `<div class="empty">노트 없음</div>`;
  }
}

// 버튼/탭
document.addEventListener("DOMContentLoaded", ()=>{
  const $refresh = document.querySelector("#refresh");
  if($refresh) $refresh.onclick = ()=>render();
  // 주간 탭은 weekly json을 별도로 만들었을 때 연결 (후속 확장)
  render();
});
