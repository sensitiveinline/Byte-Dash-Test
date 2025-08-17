import os, re, time, html, json, urllib.parse, requests
from bs4 import BeautifulSoup

ALLOW = {
  "openai.com","blog.google","ai.googleblog.com","deepmind.google","anthropic.com",
  "ai.meta.com","mistral.ai","perplexity.ai","cohere.com","stability.ai","baidu.com",
  "theverge.com","techcrunch.com","venturebeat.com","wired.com","mit.edu",
  "bloomberg.com","arxiv.org","news.ycombinator.com","reddit.com","github.com"
}

UA = {"User-Agent":"BYTE-DASH/1.0 (+https://github.com/sensitiveinline/Byte-Dash-Test)"}

def _host(u:str)->str:
    try:
        h = urllib.parse.urlparse(u).netloc.lower()
        return h[4:] if h.startswith("www.") else h
    except: return ""

def _allow(u:str)->bool:
    h = _host(u)
    return any(h==d or h.endswith("."+d) for d in ALLOW)

def ddg_search(query:str, top_n:int=10):
    """DuckDuckGo HTML 결과 파싱(무키, 간단 폴백)"""
    q = urllib.parse.quote(query)
    url = f"https://duckduckgo.com/html/?q={q}"
    r = requests.get(url, headers=UA, timeout=15)
    soup = BeautifulSoup(r.text, "lxml")
    out=[]
    for a in soup.select("a.result__a, a.result__url"):
        href = a.get("href","")
        if href.startswith("//"): href = "https:"+href
        if not href.startswith("http"): continue
        if _allow(href):
            out.append(href)
        if len(out)>=top_n: break
    # 중복 제거(호스트+경로)
    seen=set(); uniq=[]
    for u in out:
        k = urllib.parse.urlparse(u).netloc + urllib.parse.urlparse(u).path
        if k in seen: continue
        seen.add(k); uniq.append(u)
    return uniq[:top_n]

def ai_expand_queries(topic:str)->list:
    """Gemini가 있으면 관련 쿼리 생성, 없으면 기본 후보 반환"""
    base = [
        f"{topic} official site",
        f"{topic} latest announcement",
        f"{topic} blog update",
        f"{topic} site:techcrunch.com OR site:theverge.com OR site:venturebeat.com",
    ]
    try:
        from google import genai
        key = os.getenv("GOOGLE_API_KEY")
        if not key: return base
        client = genai.Client(api_key=key)
        sys = ("주어진 주제에 대해 최신 정보를 찾기 위한 웹 검색 쿼리 6개를 한국어/영문 혼합으로 짧게 만들어줘. "
               "공식/블로그/보도자료/깃허브/연구 포함. 줄바꿈으로 구분.")
        text = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL","gemini-2.5-flash"),
            contents=f"{sys}\n주제: {topic}"
        ).text
        qs = [q.strip("-• \n") for q in text.splitlines() if q.strip()]
        return (qs + base)[:8]
    except Exception:
        return base

def ai_search_urls(topic:str, top_n:int=10):
    """AI가 만든 쿼리로 검색 → 허용 도메인 필터/중복 제거"""
    urls=[]
    for q in ai_expand_queries(topic):
        urls += ddg_search(q, top_n=top_n//2 or 5)
        if len(urls)>=top_n: break
    # 최종 중복 제거
    seen=set(); uniq=[]
    for u in urls:
        if not _allow(u): continue
        k = urllib.parse.urlparse(u).netloc + urllib.parse.urlparse(u).path
        if k in seen: continue
        seen.add(k); uniq.append(u)
    return uniq[:top_n]
