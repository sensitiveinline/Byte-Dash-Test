import time, math, feedparser
from rapidfuzz import fuzz
from scripts.utils import write_json, now_iso, host_of, allow_host, TRUST_SCORES, KR_HOSTS, dedupe, sigmoid_age_score

GOOGLE_NEWS = [
  "https://news.google.com/rss/search?q=Artificial+Intelligence",
  "https://news.google.com/rss/search?q=ChatGPT",
  "https://news.google.com/rss/search?q=Gemini+AI",
  "https://news.google.com/rss/search?q=Claude+AI",
  "https://news.google.com/rss/search?q=LLaMA+AI",
]

OFFICIAL = [
  "https://openai.com/blog/rss.xml",
  "https://ai.googleblog.com/atom.xml",
  "https://deepmind.google/discover/rss.xml",
  "https://www.anthropic.com/rss.xml",
  "https://ai.meta.com/feed/",
  "https://mistral.ai/news/feed.xml",
]

MEDIA = [
  "https://techcrunch.com/tag/artificial-intelligence/feed/",
  "https://www.technologyreview.com/feed/",
  "https://www.theverge.com/rss/artificial-intelligence/index.xml",
  "https://venturebeat.com/category/ai/feed/",
  "https://www.wired.com/feed/category/business/latest/rss",
  "https://hnrss.org/frontpage"
]

def _norm_items(feeds):
    items=[]
    for url in feeds:
        try:
            d=feedparser.parse(url)
            for e in d.entries[:30]:
                link = getattr(e,"link",None) or getattr(e,"id",None)
                if not (link and allow_host(link)): continue
                host = host_of(link)
                title = (getattr(e,"title","") or "").strip()
                summary = (getattr(e,"summary","") or getattr(e,"description","") or "").strip()
                # 시간
                ts = None
                for k in ("updated_parsed","published_parsed"):
                    if getattr(e,k,None): 
                        tm = getattr(e,k)
                        ts = int(time.mktime(tm)); break
                items.append({"title":title,"url":link,"summary":summary,"host":host,"ts":ts})
        except: pass
    return items

def _dedupe_title(items, thr=85):
    out=[]
    for it in items:
        dup=False
        for u in out:
            if fuzz.token_set_ratio(it["title"], u["title"])>=thr:
                dup=True; break
        if not dup: out.append(it)
    return out

def _rank(items):
    now=int(time.time())
    ranked=[]
    for it in items:
        host=it["host"]; ts=it["ts"] or now; hours=(now-ts)/3600.0
        freshness = sigmoid_age_score(hours)               # 0~1
        trust = TRUST_SCORES.get(host, 0.5)               # 0~1
        buzz = 1.0                                        # 간단 버즈 기본값
        locale = 1.0 if any(host.endswith(k) for k in KR_HOSTS) else 0.6
        dup_penalty = 0.0                                  # 이미 유사제거함
        score = 0.4*freshness + 0.25*trust + 0.2*buzz + 0.1*locale - 0.05*dup_penalty
        ranked.append({**it, "rank_score": round(score,3)})
    ranked.sort(key=lambda x: x["rank_score"], reverse=True)
    return ranked[:10]

def run(write_to="data/news.json"):
    items = _norm_items(GOOGLE_NEWS + OFFICIAL + MEDIA)
    items = dedupe(items, key=lambda x: x["url"])
    items = _dedupe_title(items)
    items = _rank(items)
    out={"generated_at": now_iso(), "items": items}
    write_json(write_to, out); return out

if __name__=="__main__":
    run()
