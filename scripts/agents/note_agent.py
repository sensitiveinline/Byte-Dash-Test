from datetime import datetime
def run(platforms, github, news, period="daily"):
    date = datetime.utcnow().date().isoformat()
    p = platforms["items"]; g = github["items"]; n = news["items"]
    highlights = [
        {"category":"모델·제품","title": n[0]["title"], "takeaway": n[0].get("takeaway",""), "links":[n[0]["url"]]},
        {"category":"생태계","title":"경량·오픈 확산", "takeaway":"개발자 레이더는 ‘작게, 빠르게’.", "links":[]}
    ]
    cross = [
        {"entity":"Gemini","signal":"플랫폼 점수↑·Workspace 업데이트","insight":"제품 업데이트가 사용 지표로 연결"},
        {"entity":"LLaMA","signal":"GitHub 기여자↑·뉴스 확산","insight":"오픈소스 파급이 기업 도입 촉진"}
    ]
    summary = {
        "market":"배포 속도가 승부처—생산성 스택 내 기본값 경쟁.",
        "risk":"단기 리스크는 비용/안정성; 규제는 기준 정교화 흐름.",
        "next":"온디바이스 확대·추론 단가 인하·기업 파일럿 발표 주시."
    }
    return {
        "period": period, "date": date,
        "source_counts": {"platform": len(p), "github": len(g), "news": len(n)},
        "highlights": highlights, "cross_signals": cross, "summary": summary
    }
