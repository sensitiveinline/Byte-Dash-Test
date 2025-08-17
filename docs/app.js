(async function(){
  const el = (id)=>document.getElementById(id);
  try {
    const res = await fetch('data/ai_note.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    el('note').textContent = JSON.stringify(json, null, 2);
  } catch (e) {
    el('note').textContent = '데이터 로드 실패: ' + e.message;
  }
})();
