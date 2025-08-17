// app.js — no-import single file (GitHub Pages/로컬 file:// 호환)

// ---- helpers ---------------------------------------------------------------
function $(s){ return document.querySelector(s); }
function esc(s){ return (s==null?"":String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;")); }

async function loadJSON(name){
  const paths = [
    `./data/${name}`, `../data/${name}`, `/data/${name}`,
    `./public/data/${name}`, `../public/data/${name}`
  ];
  for (const p of paths){
    try{ const r = await fetch(p, {cache:"no-store"}); if(r.ok) return await r.json(); }catch(e){}
  }
  return null;
}
function unwrap(payload){
  if(!payload) return {items:[], meta:{}};
  if(Array.isArray(payload)) return {items:payload, meta:{}};
  return {items: payload.items||[], meta: payload.meta||{}};
}
function fmtDelta(n){
  const v = Number(n ?? 0);
  const cls = v>0 ? "up" : v<0 ? "down" : "flat";
  const text = v>0 ? `+${v.toFixed(1)}` : v<0 ? v.toFixed(1) : "0.0";
  return `<span class="delta ${cls}">${text}</span>`;
}

// ---- 1) 플랫폼 -------------------------------------------------------------
async function mountPlatforms(){
  const raw = await loadJSON("platform_rankings.json");
  const {items, meta} = unwrap(raw);
  $("#platMeta").textContent = meta?.generatedAt ? new Date(meta.generatedAt).toLocaleString() : "";
  const el = $("#platforms");
  if(!items.length){ el.innerHTML = `<div class="empty">데이터 없음</div>`; return; }
  el.innerHTML = items
    .sort((a,b)=> (a.rank??999)-(b.rank??999))
    .map(p=>{
      const sub = `${p.score?.toFixed?.(1) ?? "-"}점 · ${p.url ? `<a href="${esc(p.url)}" target="_blank">링크</a>` : "링크 없음"}`;
      const insight = p.ai?.insight ? `<div class="insight">${esc(p.ai.insight)}</div>` : "";
      return `
      <div class="item">
        <div style="display:flex;gap:10px;align-items:flex-start;min-width:0">
          <div class="rank">${p.rank ?? "–"}</div>
          <div style="min-width:0">
            <div style="font-weight:700">${esc(p.name || p.id || "Unknown")}</div>
            <div class="hint">${sub}</div>
            ${insight}
          </div>
        </div>
        <div>${fmtDelta(p.delta7)}</div>
      </div>`;
    }).join("");
}

// ---- 2) GitHub -------------------------------------------------------------
let GH = [];
function repoScore(r, mode){
  if(mode==="stars") return r.new_stars30 ?? r.new_stars7 ?? r.delta7 ?? r.score ?? 0;
  if(mode==="commits") return r.commits30 ?? 0;
  if(mode==="contributors") return r.contributors ?? 0;
  return r.score ?? 0;
}
function renderRepos(mode="stars", q=""){
  const el = $("#repos");
  const needle = q.trim().toLowerCase();
  const rows = GH
    .filter(r => !needle || `${r.repo} ${(r.ai?.tags||[]).join(" ")}`.toLowerCase().includes(needle))
    .sort((a,b)=> repoScore(b,mode) - repoScore(a,mode))
    .map((r,i)=>`
      <div class="item">
        <div style="display:flex;gap:10px;align-items:flex-start">
          <div class="rank">${(r.rank ?? (i+1))}</div>
          <div>
            <div style="font-weight:700"><a href="${esc(r.url||"#")}" target="_blank">${esc(r.repo)}</a></div>
            <div class="hint">⭐︎ ${r.new_stars30 ?? 0} · 🍴 ${r.forks ?? 0} · 👥 ${r.contributors ?? 0}</div>
            ${r.ai?.insight ? `<div class="insight">${esc(r.ai.insight)}</div>` : ""}
          </div>
        </div>
        <div>${fmtDelta(r.delta7)}</div>
      </div>`).join("");
  el.innerHTML = rows || `<div class="empty">검색 결과 없음</div>`;
}
async function mountRepos(){
  const raw = await loadJSON("github_trends.json");
  const {items} = unwrap(raw);
  GH = items || [];
  renderRepos($("#repoSort").value, $("#q").value);
  $("#repoSort").addEventListener("change", ()=> renderRepos($("#repoSort").value, $("#q").value));
  $("#q").addEventListener("input", ()=> renderRepos($("#repoSort").value, $("#q").value));
}

// ---- 3) 뉴스 ---------------------------------------------------------------
async function mountNews(){
  const raw = await loadJSON("news.json");
  const {items, meta} = unwrap(raw);
  $("#newsMeta").textContent = meta?.generatedAt ? new Date(meta.generatedAt).toLocaleString() : "";
  const el = $("#news");
  if(!items.length){ el.innerHTML = `<div class="empty">데이터 없음</div>`; return; }
  el.innerHTML = items.slice(0,10).map(n=>`
    <div class="item">
      <div style="min-width:0">
        <div style="font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
          <a href="${esc(n.url)}" target="_blank">${esc(n.title)}</a>
        </div>
        <div class="hint">${esc(n.source)} · ${esc(n.category||"")}</div>
        ${n.summary ? `<div class="insight">${esc(n.summary)}</div>` : ""}
        ${n.takeaway ? `<div class="hint" style="margin-top:4px">· ${esc(n.takeaway)}</div>` : ""}
      </div>
    </div>`).join("");
}

// ---- 4) 노트 ---------------------------------------------------------------
let NOTE_DAILY=null, NOTE_WEEKLY=null;
function renderNote(doc){
  const el = $("#note");
  if(!doc){ el.innerHTML = `<div class="empty">노트 없음</div>`; return; }
  const H = (doc.highlights||[]).map(h=>`<li>【${esc(h.category)}】 <b>${esc(h.title)}</b> — ${esc(h.takeaway)}</li>`).join("");
  const C = (doc.cross_signals||[]).map(c=>`<li><b>${esc(c.entity)}</b> · ${esc(c.signal)} — ${esc(c.insight)}</li>`).join("");
  el.innerHTML = `
    <div class="item"><div>
      <div class="hint">기간: ${esc(doc.period)} · 날짜: ${esc(doc.date||"")}</div>
      <div style="margin-top:8px"><b>하이라이트</b><ul>${H || "<li class='empty'>없음</li>"}</ul></div>
      <div style="margin-top:8px"><b>교차 신호</b><ul>${C || "<li class='empty'>없음</li>"}</ul></div>
      <div style="margin-top:8px"><b>요약</b>
        <div class="insight">시장: ${esc(doc.summary?.market||"-")}</div>
        <div class="insight">위험: ${esc(doc.summary?.risk||"-")}</div>
        <div class="insight">다음: ${esc(doc.summary?.next||"-")}</div>
      </div>
    </div></div>`;
}
async function mountNote(){
  NOTE_DAILY = await loadJSON("ai_note.json");
  renderNote(NOTE_DAILY);
  document.querySelectorAll(".tab").forEach(t=>{
    t.addEventListener("click", async ()=>{
      document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
      t.classList.add("active");
      const p = t.dataset.period;
      if(p==="daily") return renderNote(NOTE_DAILY);
      if(!NOTE_WEEKLY){
        const w = await loadJSON("aggregates/weekly/2025-W33.json");
        NOTE_WEEKLY = w || { period:"weekly", date:"—", highlights:[], cross_signals:[], summary:{market:"—",risk:"—",next:"—"} };
      }
      renderNote(NOTE_WEEKLY);
    });
  });
}

// ---- boot ------------------------------------------------------------------
document.getElementById("refresh")?.addEv
