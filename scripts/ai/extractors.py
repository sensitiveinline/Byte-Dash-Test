import os
from typing import Dict, Any

try:
    # google-genai가 설치되어 있지 않아도 동작하도록 선택적 임포트
    from google import genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None  # 라이브러리 미존재 시에도 파이프라인이 진행되도록

_EMPTY = {"users": None, "traffic": None, "growth": None}

def ai_extract_metrics_from_page(url: str) -> Dict[str, Any]:
    """
    주어진 URL에서 사용자수/트래픽/성장률 같은 지표를 추출.
    - GOOGLE_API_KEY 없거나, 라이브러리/호출 실패 시: 빈 지표 반환(_EMPTY)
    - 키가 있어도 현재는 보수적으로 빈 지표를 반환(추후 실제 파싱 로직 연결)
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or genai is None:
        return dict(_EMPTY)

    try:
        # 필요 시 여기에 실제 추출 로직을 연결하세요.
        # client = genai.Client(api_key=api_key)
        # ... 모델 호출/크롤링/파싱 ...
        return dict(_EMPTY)
    except Exception:
        return dict(_EMPTY)
