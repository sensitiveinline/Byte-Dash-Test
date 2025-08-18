import os, json, requests
from google import genai
from scripts.utils import text_from_html

def fetch(url, timeout=15):
    r = requests.get(url, timeout=timeout, headers={"User-Agent":"BYTE-DASH/1.0"})
    r.raise_for_status(); return r.text

def ai_extract_metrics_from_page(url, fields=("users","traffic","growth","period")):
    """
    페이지에서 '사용자규모/트래픽/성장률(%)' 등 정량을 추출(가능한 경우)하고,
    출처/단위/기간을 함께 리턴. 실패 시 None 필드.
    """
    html = fetch(url)
    text = text_from_html(html)[:30000]  # 토큰 보호
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = f"""
아래 본문에서 다음 항목을 JSON으로 추출하라(없으면 null):
- users: 사용자 수/MAU/DAU 등 숫자와 단위(예: 1.8B monthly)
- traffic: 웹 트래픽/방문수(예: 200M visits/month)
- growth: 성장률 % (예: +24% YoY, +8% MoM)
- period: 기간 텍스트(예: 2025 Q2, last month)
- citation: 본문에서 해당 수치가 있는 문장(20~40자)
답변은 JSON만 반환.
본문:
{text}
"""
    try:
        res = client.models.generate_content(model=os.getenv("GEMINI_MODEL","gemini-2.5-flash"), contents=prompt)
        j = json.loads(res.text)
        return {"url":url, **{k:j.get(k) for k in ["users","traffic","growth","period"]}, "citation": j.get("citation")}
    except Exception:
        return {"url":url, "users":None,"traffic":None,"growth":None,"period":None,"citation":None}
