from __future__ import annotations
import os
from typing import List

HAS_GOOGLE = bool(os.getenv("GOOGLE_API_KEY"))
_genai = None

def ai_available() -> bool:
    return HAS_GOOGLE

def _ensure_google():
    global _genai
    if _genai is None:
        import google.generativeai as genai
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        _genai = genai
    return _genai

def summarize_bullets(lines: List[str], max_bullets: int = 5) -> List[str]:
    """
    Gemini가 있으면 요약 bullet 생성, 없으면 룰 기반 상위 N개 반환
    """
    text = "\n".join(f"- {x}" for x in lines if x)
    if not ai_available():
        return [ln.strip(" -•\t") for ln in lines[:max_bullets]]
    genai = _ensure_google()
    m = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""다음 정보를 한국어로 {max_bullets}줄 핵심 요약 bullet로 만들어줘. 각 줄은 간결한 한 문장:
{text}"""
    try:
        out = m.generate_content(prompt).text or ""
        bullets = [ln.strip(" -•\t") for ln in out.splitlines() if ln.strip()]
        return bullets[:max_bullets] or [ln.strip(" -•\t") for ln in lines[:max_bullets]]
    except Exception:
        return [ln.strip(" -•\t") for ln in lines[:max_bullets]]

def simple_relevance(title: str, summary: str, keywords: List[str]) -> float:
    """
    Gemini로 0~1 관련도 숫자 산출. 실패/미사용 시 키워드 매칭 빈도로 근사.
    """
    blob = f"{title}\n{summary}".strip()
    if not blob:
        return 0.0
    if not ai_available():
        low = blob.lower()
        hits = sum(1 for k in keywords if k.lower() in low)
        return hits / max(1, len(keywords))
    genai = _ensure_google()
    m = genai.GenerativeModel("gemini-1.5-flash")
    q = f"아래 글이 {', '.join(keywords)} 와 얼마나 관련 있는지 0~1 숫자만 답해줘.\n\n{blob}\n\n숫자만:"
    try:
        out = (m.generate_content(q).text or "").strip()
        val = float(out.split()[0])
        return max(0.0, min(1.0, val))
    except Exception:
        low = blob.lower()
        hits = sum(1 for k in keywords if k.lower() in low)
        return hits / max(1, len(keywords))
