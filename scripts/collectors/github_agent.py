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
            full = " ".join(a.get_text(strip=True).split())
            full = re.sub(r"\s*/\s*", "/", full).strip()
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


def enrich_metrics(items, log):
    """가벼운 메트릭 보강: stars, updated → release_recency 근사. 토큰 없어도 일부는 성공."""
    import requests, datetime
    from datetime import timezone
    token = os.getenv("GITHUB_TOKEN")
    headers = dict(UA)
    if token: headers["Authorization"] = f"token {token}"
    ok = 0
    for it in items:
        full = it.get("repo","")
        if "/" not in full: continue
        try:
            r = requests.get(f"{GH}/repos/{full}", headers=headers, timeout=8)
            if r.status_code == 403:  # rate limit
                log.append("enrich:rate_limited")
                break
            if r.status_code >= 400:
                continue
            data = r.json()
            it["stars"] = int(data.get("stargazers_count", it.get("stars",0)) or 0)
            # updated_at → 일수로 근사하여 release_recency 대체
            upd = data.get("updated_at")
            if upd:
                from datetime import datetime as dt
                try:
                    t = dt.fromisoformat(upd.replace('Z','+00:00'))
                    days = max(0, (datetime.datetime.now(timezone.utc)-t).days)
                    it["release_recency"] = max(0.0, 90.0 - float(days))  # 최근일수 반비례(최대 90)
                except Exception:
                    pass
            ok += 1
            if ok >= 8:  # 너무 많이 때리지 않음
                break
        except Exception:
            continue
    log.append(f"enrich_ok={ok}")


def enrich_metrics_precise(items, log):
    """
    GitHub REST API로 지표 보강:
      - stars (총합)
      - commits30 (지난 30일 커밋 수, 최대 200 카운트)
      - contributors (대략치: /contributors?per_page=100 길이)
      - release_recency: 최신 release published_at 또는 updated_at 기반 (최근일수 → 90-일수)
    ※ 레이트리밋 고려해서 상위 10개 중 앞쪽 몇 개만 상세 조회.
    """
    import os, requests, datetime
    from datetime import timezone, timedelta
    token = os.getenv("GITHUB_TOKEN")
    headers = {"User-Agent": "BYTE-DASH/1.0"}
    if token:
        headers["Authorization"] = f"token {token}"

    now = datetime.datetime.now(timezone.utc)
    since = (now - timedelta(days=30)).isoformat()

    def get_json(url, params=None, timeout=10):
        try:
            r = requests.get(url, headers=headers, params=params or {}, timeout=timeout)
            if r.status_code == 403:
                # 레이트리밋
                return None
            if r.status_code >= 400:
                return None
            return r.json()
        except Exception:
            return None

    # 너무 많이 때리지 않도록 최대 8개만 정밀 보강
    count = 0
    for it in items:
        full = it.get("repo","")
        if "/" not in full: continue
        # /repos — stars & updated_at
        meta = get_json(f"{GH}/repos/{full}")
        if meta:
            it["stars"] = int(meta.get("stargazers_count", it.get("stars",0)) or 0)
            # 최신 release 우선
            rel = get_json(f"{GH}/repos/{full}/releases/latest")
            last_dt = None
            if rel and isinstance(rel, dict) and rel.get("published_at"):
                from datetime import datetime as dt
                try:
                    last_dt = dt.fromisoformat(rel["published_at"].replace("Z","+00:00"))
                except Exception:
                    last_dt = None
            if not last_dt and meta.get("updated_at"):
                from datetime import datetime as dt
                try:
                    last_dt = dt.fromisoformat(meta["updated_at"].replace("Z","+00:00"))
                except Exception:
                    last_dt = None
            if last_dt:
                days = max(0, (now - last_dt).days)
                it["release_recency"] = max(0.0, 90.0 - float(days))

        # /commits — 지난 30일 커밋 (최대 200개 카운트)
        commits_cnt = 0
        page = 1
        while page <= 2:  # 두 페이지만
            arr = get_json(f"{GH}/repos/{full}/commits", params={"since": since, "per_page": 100, "page": page})
            if not isinstance(arr, list): break
            commits_cnt += len(arr)
            if len(arr) < 100: break
            page += 1
        it["commits30"] = max(int(it.get("commits30",0) or 0), commits_cnt)

        # /contributors — 대략치 (첫 100명 길이)
        contrib = get_json(f"{GH}/repos/{full}/contributors", params={"per_page": 100, "anon": "1"})
        if isinstance(contrib, list) and contrib:
            it["contributors"] = max(int(it.get("contributors",0) or 0), len(contrib))

        count += 1
        if count >= 8:
            break

    log.append(f"enrich_precise_ok={count}")



def _get_json(url, headers, params=None, timeout=10):
    """requests GET → (status_code, json_or_None)"""
    import requests
    r = requests.get(url, headers=headers, params=params or {}, timeout=timeout)
    ct = r.headers.get("content-type","")
    data = None
    if ct.startswith("application/json"):
        try: data = r.json()
        except Exception: data = None
    return r.status_code, data

def _commit_activity_30d(owner_repo, headers, log, max_wait=30):
    """
    /stats/commit_activity:
      52주 주간 total 배열 반환. 최신 4주 합 ≒ 최근 28일 커밋 근사.
      처음엔 202(계산중)가 많이 뜨므로 짧게 재시도.
    """
    import time
    url = f"{GH}/repos/{owner_repo}/stats/commit_activity"
    waited = 0
    while waited <= max_wait:
        code, data = _get_json(url, headers)
        if code == 202:
            time.sleep(2); waited += 2; continue
        if isinstance(data, list) and data:
            return int(sum(w.get("total",0) for w in data[-4:]))
        break
    log.append(f"stats_commit_activity_waited={waited}")
    return 0

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

    # 간단 메트릭 보강(API 여유분으로 몇 개만)
    try:
        enrich_metrics(items, log)
    except Exception as e:
        log.append(f"enrich_error={type(e).__name__}")
    # 정밀 보강 (토큰 있으면 더 정확)
    try:
        enrich_metrics_precise(items, log)
    except Exception as e:
        log.append(f"enrich_precise_error={type(e).__name__}")

    # 스코어 계산(기존 score 있으면 유지)
    for it in items:
        calc = round(_score(it), 1)
        if it.get('score') is None or calc > 0:
            it['score'] = max(float(it.get('score',0) or 0), calc)

    out = {"generated_at": now_iso(), "items": items, "meta": {"log": log}}
    write_json(write_to, out)
    return out


def add_star_deltas(items, log):
    """/repos -> stargazers_count만으로는 증가량을 정확히 못 구한다.
       스냅샷(data/github_trends.json)을 활용해 7d/30d 근사."""
    import json, os
    from pathlib import Path
    snap = {}
    sp = Path("data/github_trends.json")
    if sp.exists():
        try:
            snap = json.loads(sp.read_text())
        except Exception:
            snap = {}
    hist = { (it.get("repo") or it.get("url","")): it for it in snap.get("items",[]) }
