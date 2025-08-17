import os, requests, datetime as dt

def run(_=None):
    token = os.getenv("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "byte-dash-test/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = "https://api.github.com/search/repositories?q=topic:ai+topic:machine-learning&sort=stars&order=desc&per_page=30"
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    now = dt.datetime.utcnow().isoformat()+"Z"
    items = []
    for i, repo in enumerate(r.json().get("items", []), start=1):
        items.append({
            "repo": repo["full_name"],
            "url": repo["html_url"],
            "new_stars30": repo.get("stargazers_count"),
            "forks": repo.get("forks_count"),
            "contributors": None,
            "score": repo.get("score", 0),
            "rank": i,
            "delta7": 0,
            "ts": now,
            "ai": {
                "insight": "오픈소스 인기도(Stars) 기반",
                "tags": ["gh-search"],
                "confidence": 0.5
            }
        })
    return {"items": items}
