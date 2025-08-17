import os, time, requests, math, datetime
from scripts.utils import write_json, now_iso
from scripts.ai.searcher import ai_search_urls
from bs4 import BeautifulSoup

GH = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")
H = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

def gh(url, **params):
    r = requests.get(url, headers=H, params=params, timeout=15)
    r.raise_for_status(); return r.json()

def since_days(days):
    return (datetime.datetime.utcnow() - datetime.timedelta(days=days)).isoformat()+"Z"

def repo_commits_30d(owner, repo):
    try:
        commits = gh(f"{GH}/repos/{owner}/{repo}/commits", since=since_days(30), per_page=100)
        authors = set()
        for c in commits:
            a = (c.get("author") or {}).get("login") or (c.get("commit") or {}).get("author",{}).get("email")
            if a: authors.add(a)
        return len(commits), len(authors)
    except: return 0,0

def release_recency(owner, repo):
    try:
        rel = gh(f"{GH}/repos/{owner}/{repo}/releases/latest")
        published = rel.get("published_at")
        if not published: return 0.0
        dt = datetime.datetime.fromisoformat(published.replace("Z","+00:00"))
        hours = (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - dt).total_seconds()/3600.0
        # 최신일수록 높은 점수(0~1)
        s = 1.0/(1.0+math.exp((hours-240)/48))  # 10일 중심
        return s
    except: return 0.0

def trending_fallback(items):
    """GitHub Trending HTML 파싱 (로그인·토큰 불필요). items가 10개 미만일 때 채움."""
    import requests, re
    try:
        html = requests.get("https://github.com/trending?since=daily", timeout=15, headers={"User-Agent":"BYTE-DASH/1.0"}).text
        soup = BeautifulSoup(html, "lxml")
        repos = soup.select("article.Box-row h2 a")
        for a in repos:
            full = " ".join(a.get_text(strip=True).split()).replace(" / ", "/")
            if "/" not in full: continue
            url = "https://github.com/" + full
            items.append({
                "repo": full, "url": url, "description": "",
                "stars": 0, "new_stars30": 0, "commits30": 0, "contributors": 0,
                "release_recency": 0.0, "score": 8.0
            })
            if len(items) >= 10: break
    except Exception:
        pass

def run(write_to="data/github.json"):
    # 후보 검색(최근 업데이트 & 별)
    q = "topic:ai OR machine-learning OR deep-learning"
    res = gh(f"{GH}/search/repositories", q=q, sort="stars", order="desc", per_page=40)
    items=[]
    for r in res.get("items",[]):
        full=r["full_name"]; owner,repo = full.split("/")
        stars = r.get("stargazers_count",0)
        pushed = r.get("pushed_at")
        recent_boost = 1.0
        if pushed:
            # 최근 푸시일수록 boost
            dt = datetime.datetime.fromisoformat(pushed.replace("Z","+00:00"))
            hours = (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)-dt).total_seconds()/3600.0
            recent_boost = 1.0/(1.0+math.exp((hours-240)/48))
        commits, contributors = repo_commits_30d(owner, repo)
        rel = release_recency(owner, repo)
        new_stars30 = stars*recent_boost   # 근사치
        score = 0.45*new_stars30 + 0.25*commits + 0.2*contributors + 0.1*rel*100
        items.append({
            "repo": full,
            "url": r["html_url"],
            "description": r.get("description") or "",
            "stars": stars,
            "new_stars30": round(new_stars30,1),
            "commits30": commits,
            "contributors": contributors,
            "release_recency": round(rel,3),
            "score": round(score,1)
        })
    items.sort(key=lambda x: x["score"], reverse=True)
    out={"generated_at": now_iso(), "items": items[:10]}
    write_json(write_to, out); return out

if __name__=="__main__":
    run()
