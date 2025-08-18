import re, math
from collections import defaultdict
from scripts.utils import read_json, write_json, now_iso, host_of, minmax
from scripts.ai.extractors import ai_extract_metrics_from_page
import requests

PLATFORM_KEYS = {
  "ChatGPT":["openai","chatgpt"],
  "Gemini":["google","gemini","deepmind"],
  "Claude":["anthropic","claude"],
  "Llama":["meta","llama"],
  "Mistral":["mistral"],
  "Perplexity":["perplexity"],
  "Cohere":["cohere"],
  "Stability":["stability","stable diffusion","stability ai"],
  "Baidu":["baidu","wenxin","ernie"],
}

def detect_platform(title,url):
    t=(title or "").lower()+" "+(url or "").lower()
    for name,keys in PLATFORM_KEYS.items():
        if any(k in t for k in keys): return name
    return None

def run(write_to="data/platform_rankings.json", snapshots_path="data/snapshots_platforms.json"):
    news = (read_json("data/news.json", {"items":[]}) or {}).get("items",[])
    # 후보 → 플랫폼별 관련 URL 모으기(official/news 혼합)
    bucket = defaultdict(list)
    for n in news:
        name = detect_platform(n.get("title"), n.get("url"))
        if not name: continue
        bucket[name].append(n["url"])

    # AI 추출 수행(최대 플랫폼당 4개 URL)
    rows=[]
    for name, urls in bucket.items():
        urls = urls[:4]
        users_vals, traffic_vals, growth_vals = [], [], []
        sources=[]
        for u in urls:
            ex = ai_extract_metrics_from_page(u)
            sources.append({"type":"official" if "openai.com" in u or "google" in u or "anthropic.com" in u or "ai.meta.com" in u or "mistral.ai" in u else "news","url":u})
            # 수치 파싱(텍스트 포함 가능 → 숫자 추출)
            def num_or_none(x):
                if x is None: return None
                m = re.search(r"([0-9][0-9\.,]*)(\s*[KkMmBb])?", str(x))
                if not m: return None
                v = float(m.group(1).replace(",",""))
                suf = (m.group(2) or "").strip().lower()
                mult = {"k":1e3,"m":1e6,"b":1e9}.get(suf,1.0)
                return v*mult
            users = num_or_none(ex.get("users"))
            traffic = num_or_none(ex.get("traffic"))
            growth = None
            if ex.get("growth"):
                g = re.search(r"([+-]?\d+(\.\d+)?)\s*%", str(ex.get("growth")))
                if g: growth=float(g.group(1))
            if users: users_vals.append(users)
            if traffic: traffic_vals.append(traffic)
            if growth is not None: growth_vals.append(growth)

        # 정규화 준비(없으면 0)
        rows.append({"name":name,
                     "users": max(users_vals) if users_vals else 0.0,
                     "traffic": max(traffic_vals) if traffic_vals else 0.0,
                     "growth": sum(growth_vals)/len(growth_vals) if growth_vals else 0.0,
                     "sources": sources})

    if not rows:
        write_json(write_to, {"generated_at": now_iso(), "items":[]}); return {"items":[]}

    # 0~100 정규화
    users_scaled = minmax([r["users"] for r in rows])
    traff_scaled = minmax([r["traffic"] for r in rows])
    grow_scaled  = minmax([max(-50.0, min(100.0, r["growth"])) for r in rows])  # -50~100% 클리핑 → minmax

    out_items=[]
    for i,r in enumerate(rows):
        score = 0.5*users_scaled[i] + 0.3*traff_scaled[i] + 0.2*grow_scaled[i]
        out_items.append({"id": r["name"].lower().replace(" ","-"),
                          "name": r["name"],
                          "score": round(score,1),
                          "metrics":{"users":r["users"],"traffic":r["traffic"],"growth":round(r["growth"],2)},
                          "sources": r["sources"]})

    # 랭크/델타 계산
    out_items.sort(key=lambda x: x["score"], reverse=True)
    for idx,it in enumerate(out_items): it["rank"]=idx+1

    # delta7/30: snapshots 저장/비교
    snap = read_json(snapshots_path, {"history":[]})
    hist = snap["history"][-30:] if snap and snap.get("history") else []
    def delta_for(days):
        # days전 snapshot의 score 찾기(플랫폼별 id)
        if len(hist)<days: return 0.0
        prev = hist[-days]
        pmap = {i["id"]: i["score"] for i in prev["items"]}
        return round(it["score"] - pmap.get(it["id"], it["score"]), 1)

    # 오늘 기록 추가
    today_record = {"ts": now_iso(), "items": [{"id":i["id"],"score":i["score"]} for i in out_items]}
    write_json(snapshots_path, {"history": hist + [today_record]})

    # delta 적용
    final=[]
    for it in out_items:
        # delta 계산 위해 it를 클로저 바깥으로 잠깐 노출
        globals()["it"]=it
        d7 = delta_for(7); d30 = delta_for(30)
        final.append({**it, "delta7": d7, "delta30": d30})

    out={"generated_at": now_iso(), "items": final[:10]}
    write_json(write_to, out); return out

if __name__=="__main__":
    run()

def unwrap_google_news(url: str) -> str:
    # news.google.com/rss/articles/* → 원문 URL로 리다이렉트 추적
    try:
        if "news.google.com" not in url:
            return url
        import requests
        r = requests.get(
            url,
            timeout=15,
            allow_redirects=True,
            headers={"User-Agent": "BYTE-DASH/1.0"}
        )
        return r.url or url
    except Exception:
        return url
