
import os, json
from datetime import datetime, timezone
from scripts.utils import write_json, now_iso
from scripts.ai.searchers import gen_note if False else None  # placeholder

def _read(path):
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return {}

def _arr(obj): 
    return obj if isinstance(obj, list) else obj.get("items", []) if isinstance(obj, dict) else []

def _brief_daily(platforms, repos, news):
    # platforms: 상위 10 중 움직임 2개
    pf = sorted(platforms, key=lambda x: -float(x.get("delta7",0)))[:2]
    gh = repos[:1]
    nw = news[:2]
    lines = []
    if pf: lines.append(f"플랫폼: {pf[0]['name']}↑{pf[0].get('delta7',0)} / " + (pf[1]['name']+f"↑{pf[1].get('delta7',0)}" if len(pf)>1 else ""))
    if gh: lines.append(f"GitHub: {gh[0].get('repo')} 활동↑ (c{gh[0].get('commits30',0)}, u{gh[0].get('contributors',0)})")
    if nw:
        for n in nw: lines.append(f"뉴스: {n.get('source') or n.get('host','')} — {n.get('title','')[:36]}…")
    lines.append("TL;DR: 빅3 경쟁 심화 + 엔터프라이즈 전환 가속")
    return "\n".join(lines)

def _brief_weekly(platforms, repos, news):
    # 상위 변화/기술/정책/비즈 시그널 구성
    lines = []
    topg = sorted(platforms, key=lambda x:-float(x.get("delta30",0)))[:3]
    if topg: lines.append("성장 Top3: " + ", ".join([f"{x['name']}(+{x.get('delta30',0)})" for x in topg]))
    lines.append("기술: LLM-Tool/에이전트 · 경량 추론 · 서버비 절감")
    lines.append("정책: 규제 가이드/AI Act 후속")
    lines.append("비즈: 엔터프라이즈 도입·워크스페이스 침투")
    for n in news[:4]: lines.append(f"뉴스: {n.get('host','')} — {n.get('title','')[:36]}…")
    lines.append("결론: 제품→운영 자동화로 이동, 데이터 거버넌스 중요")
    return "\n".join(lines[:10])

def run(write_to="data/ai_note.json"):
    plats = _arr(_read("data/platform_rankings.json"))
    repos = _arr(_read("data/github.json"))
    news  = _arr(_read("data/news.json"))
    out = {
        "period":"daily",
        "date": now_iso()[:10],
        "items":[{"type":"platform","text": _brief_daily(plats, repos, news)}]
    }
    write_json(write_to, out)
    return out
