import os, json, hashlib, pathlib, urllib.parse, http.client, ssl, re, math
from datetime import datetime, timezone
from bs4 import BeautifulSoup

TOP_N = int(os.getenv("RUN_TOP_N") or 10)

TRUST_SCORES = {  # 뉴스 출처 신뢰(0~1) — 필요시 확장
  "openai.com":1.0, "ai.googleblog.com":1.0, "deepmind.google":1.0, "blog.google":1.0,
  "anthropic.com":1.0, "ai.meta.com":1.0, "mistral.ai":0.9, "perplexity.ai":0.8,
  "techcrunch.com":0.8, "theverge.com":0.7, "venturebeat.com":0.7, "technologyreview.com":0.9,
  "wired.com":0.8, "bloomberg.com":0.95, "news.ycombinator.com":0.6, "arxiv.org":0.9
}
KR_HOSTS = {"co.kr","kr","chosun.com","joongang.co.kr","hani.co.kr","yonhapnews.co.kr"}

def now_iso(): return datetime.now(timezone.utc).isoformat()

def write_json(path, data):
    p = pathlib.Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def read_json(path, fallback=None):
    p = pathlib.Path(path)
    if p.exists():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except: return fallback
    return fallback

def host_of(url:str)->str:
    try:
        h = urllib.parse.urlparse(url).netloc.lower().replace("www.","")
        return h
    except: return ""

def allow_host(url:str)->bool:
    try:
        u = urllib.parse.urlparse(url)
        return u.scheme in ("http","https") and bool(u.netloc)
    except: return False

def dedupe(items, key=lambda x: x.get("url") or x.get("id")):
    seen, out = set(), []
    for it in (items or []):
        k = key(it); 
        if not k: continue
        h = hashlib.md5(str(k).encode("utf-8")).hexdigest()
        if h in seen: continue
        seen.add(h); out.append(it)
    return out

def text_from_html(html):
    try:
        soup = BeautifulSoup(html, "lxml")
        for t in soup(["script","style","noscript"]): t.extract()
        return re.sub(r"\s+"," ", soup.get_text(" ", strip=True))
    except:
        return ""

def minmax(values):
    if not values: return []
    mn, mx = min(values), max(values)
    if mx - mn < 1e-9: return [50.0 for _ in values]
    return [ (v - mn) * 100.0 / (mx - mn) for v in values ]

def sigmoid_age_score(hours):
    # 신선도(0~1): 0시간=1.0 → 240h(10d)≈0.2로 감소
    x = max(0.0, float(hours))
    return 1.0/(1.0+math.exp((x-72)/18))  # 3일을 중심으로 감소
