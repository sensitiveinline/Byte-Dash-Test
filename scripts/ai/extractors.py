import os
try:
    from google import genai
except Exception:
    genai = None

def ai_extract_metrics_from_page(url: str) -> dict:
    """추출 실패/미설정이어도 파이프라인은 계속 진행되도록 안전 반환."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or genai is None:
        return {"users": None, "traffic": None, "growth": None}
    try:
        client = genai.Client(api_key=api_key)
        # TODO: 실제 추출 로직 (현재는 안전 반환)
        return {"users": None, "traffic": None, "growth": None}
    except Exception:
        return {"users": None, "traffic": None, "growth": None}
