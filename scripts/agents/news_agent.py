from datetime import datetime
def run(raw=None):
    now = datetime.utcnow().isoformat()+"Z"
    items = [
        {"title":"Gemini, Docs/Gmail 통합 확대","source":"Google AI Blog",
         "url":"https://ai.googleblog.com/example","published_at":now,
         "summary":"워크스페이스 내 요약·자동화 기능 확대.","takeaway":"생산성 스택 침투 가속.",
         "category":"모델·제품","ts":now,
         "ai":{"confidence":0.84,"evidence":[]}},
        {"title":"LLaMA 기반 기업 배포 사례 증가","source":"TechCrunch",
         "url":"https://techcrunch.com/example","published_at":now,
         "summary":"엔터프라이즈 도입 속도 증가.","takeaway":"TCO 경쟁 본격화.",
         "category":"정책·투자","ts":now,
         "ai":{"confidence":0.75,"evidence":[]}},
    ]
    return {"items": items}
