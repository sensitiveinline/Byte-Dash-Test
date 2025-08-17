import os, time, re, requests
from datetime import datetime, timezone
from typing import List, Dict
from scripts.utils import write_json, now_iso

# 선택 의존성
try:
    import feedparser
except Exception:
    feedparser = None
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None
try:
    from scripts.ai.searcher import ai_search_urls
except Exception:
    ai_search_urls = None

UA = {"User-Agent": "BYTE-DASH/1.0 (+https://github.com/sensitiveinline/Byte-Dash-Test)"}
GH = "https://api.github.com"
TOP_N = 10

def _uniq(items: List[Dict]) -> List[Dict]:
    seen=set(); out=[]
    for it in items:
        full = it.get("repo") or ""
        if not full: 
            # github url에서 repo 추출
            url = it.get("url","")
            m = re.search(r"github\.com/([^/]+/[^/#?]+)", url)
            if m: full = m.group(1)
            it["repo"] = full
        if not full: continue
        if full in seen: continue
        seen.add(full); out.append(it)
    return out

def _score(it: Dict) -> float:
    return float(it.get("new_stars30",0))*0.45 + float(it.get("commits30",0))*0.25 + float(it.get("contributors",0))*0.2 + float(it.get("release_recency",0))*0.1

def gh_api_search(log: list) -> List[Dict]:
    """GitHub Search API (있으면 최고), 실패 시 빈 리스트"""
    token = os.getenv("GITHUB_TOKEN")
    headers = {**UA}
    if token: headers["Authorization"] = f"token {token}"
    params = {"q":"topic:ai OR machine-learning OR deep-learning", "sort":"stars", "order":"desc", "per_page":30}
    try:
        log.append("try:github_api")
        r = requests.get(f"{GH}/search/repositories", headers=headers, params=params, timeout=20)
        if r.status_code == 403:
            log.append("api:rate_limited")
            return []
        r.raise_for_status()
        data = r.json()
        out=[]
        for rj in data.get("items",[]):
            full = rj.get("full_name","")
            out.append({
                "repo": full,
                "url": rj.get("html_url",""),
                "description": rj.get("description","") or "",
                "stars": int(rj.get("stargazers_count",0)),
                "new_stars30": 0,
                "commits30": 0,
                "contributors": 0,
                "release_recency": 0.0,
            })
            if len(out)>=TOP_N*2: break
        log.append(f"api_items={len(out)}")
        return out
    except Exception as e:
        log.append(f"api_error={type(e).__name__}")
        return []

def ai_fallback(log: list) -> List[Dict]:
    """Gemini+DDG로 '인기 AI GitHub' 검색 → repo URL 추출"""
    out=[]
    try:
        if not ai_search_urls:
            log.append("ai_search:skip(no_module)")
            return out
        log.append("try:ai_search")
        urls = ai_search_urls("popular AI Github repositories", top_n=16)
        for u in urls:
            m = re.search(r"github\.com/([^/]+/[^/#?]+)", u)
            if not m: continue
            full = m.group(1)
            out.append({
                "repo": full,
                "url": f"https://github.com/{full}",
                "description": "",
                "stars": 0, "new_stars30": 0, "commits30": 0, "contributors": 0,
                "release_recency": 0.0,
            })
            if len(out)>=TOP_N: break
        log.append(f"ai_items={len(out)}")
    except Exception as e:
        log.append(f"ai_error={type(e).__name__}")
    return out

def hn_fallback(log: list) -> List[Dict]:
    """Hacker News 최신 글에서 github 링크 추출"""
    out=[]
    try:
        if not feedparser:
            log.append("hn:skip(no_feedparser)")
            return out
        log.append("try:hn_fallback")
        hn = feedparser.parse("https://hnrss.org/newest?q=github")
        for e in hn.entries:
            link = getattr(e, "link", "")
            m = re.search(r"github\.com/([^/]+/[^/#?]+)", link)
            if not m: continue
            full = m.group(1)
            out.append({
                "repo": full,
                "url": f"https://github.com/{full}",
                "description": "",
                "stars": 0, "new_stars30": 0, "commits30": 0, "contributors": 0,
                "release_recency": 0.0,
            })
            if len(out)>=TOP_N: break
        log.append(f"hn_items={len(out)}")
    except Exception as e:
        log.append(f"hn_error={type(e).__name__}")
    return out

def trending_fallback(log: list) -> List[Dict]:
    """github.com/trending HTML 파싱"""
    out=[]
    try:
        if not BeautifulSoup:
            log.append("trending:skip(no_bs4)")
            return out
        log.append("try:trending_fallback")
        html = requests.get("https://github.com/trending?since=daily", headers=UA, timeout=20).text
        soup = BeautifulSoup(html, "lxml")
        for a in soup.select("article.Box-row h2 a"):
            full = " ".join(a.get_text(strip=True).split()).replace(" / ", "/")
            if "/" not in full: continue
            out.append({
                "repo": full,
                "url": "https://github.com/" + full,
                "description": "",
                "stars": 0, "new_stars30": 0, "commits30": 0, "contributors": 0,
                "release_recency": 0.0,
            })
            if len(out)>=TOP_N: break
        log.append(f"trending_items={len(out)}")
    except Exception as e:
        log.append(f"trending_error={type(e).__name__}")
    return out

def static_fallback(log: list) -> List[Dict]:
    base = [
        "huggingface/transformers","pytorch/pytorch","tensorflow/tensorflow","langchain-ai/langchain",
        "openai/openai-python","mistralai/mistral-src","meta-llama/llama","mlx-examples/mlx-examples",
        "Lightning-AI/pytorch-lightning","scikit-learn/scikit-learn","keras-team/keras","facebookresearch/faiss"
    ]
    log.append("use:static_fallback")
    return [{"repo":r, "url":"https://github.com/"+r, "description":"", "stars":0,
             "new_stars30":0,"commits30":0,"contributors":0,"release_recency":0.0} for r in base][:TOP_N]

def run(write_to="data/github.json"):
    log=[]
    items=[]
    # 0) AI 검색 (네트워크 허용 + 키 없어도 동작)
    items += ai_fallback(log)
    # 1) API
    if len(items) < TOP_N:
        items += gh_api_search(log)
    # 2) HN
    if len(items) < TOP_N:
        items += hn_fallback(log)
    # 3) Trending
    if len(items) < TOP_N:
        items += trending_fallback(log)
    # 4) Static
    if len(items) < TOP_N:
        items += static_fallback(log)

    items = _uniq(items)[:TOP_N]
    # 스코어 계산(간이)
    for it in items:
        it["score"] = round(_score(it), 1)

    out = {"generated_at": now_iso(), "items": items, "meta": {"log": log}}
    write_json(write_to, out)
    return out
