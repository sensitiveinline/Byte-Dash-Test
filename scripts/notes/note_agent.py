import os, json, datetime
from google import genai
from scripts.utils import write_json, read_json, now_iso

def daily(write_to="data/ai_note.json"):
    plats = (read_json("data/platform_rankings.json", {"items":[]}) or {}).get("items",[])[:10]
    gh    = (read_json("data/github.json", {"items":[]}) or {}).get("items",[])[:5]
    news  = (read_json("data/news.json", {"items":[]}) or {}).get("items",[])[:10]

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = f"""아래 데이터를 바탕으로 한국어 데일리 브리핑 5줄:
- 1~2줄: 플랫폼 변화 핵심(랭크/델타)
- 1줄: GitHub 급등 포인트
- 1~2줄: 뉴스 인사이트
- 마지막: '오늘의 한 줄'
데이터:
[Platforms]{json.dumps(plats, ensure_ascii=False)}
[GitHub]{json.dumps(gh, ensure_ascii=False)}
[News]{json.dumps(news, ensure_ascii=False)}"""
    try:
        text = client.models.generate_content(model=os.getenv("GEMINI_MODEL","gemini-2.5-flash"), contents=prompt).text.strip()
    except Exception:
        text = "데이터 부족 또는 모델 호출 실패."

    out={"period":"daily","date":str(datetime.date.today()),"items":[{"type":"note","text":text}]}
    write_json(write_to, out); return out

def weekly(write_to="data/aggregates/weekly/ai_note_weekly.json"):
    plats = (read_json("data/platform_rankings.json", {"items":[]}) or {}).get("items",[])[:10]
    gh    = (read_json("data/github.json", {"items":[]}) or {}).get("items",[])[:10]
    news  = (read_json("data/news.json", {"items":[]}) or {}).get("items",[])[:10]
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = f"""아래 데이터를 바탕으로 한국어 주간 브리핑 10줄:
- 성장 Top3, 기술/정책/비즈 트렌드, 결론
데이터:
[Platforms]{json.dumps(plats, ensure_ascii=False)}
[GitHub]{json.dumps(gh, ensure_ascii=False)}
[News]{json.dumps(news, ensure_ascii=False)}"""
    try:
        text = client.models.generate_content(model=os.getenv("GEMINI_MODEL","gemini-2.5-flash"), contents=prompt).text.strip()
    except Exception:
        text = "주간 요약 생성 실패."
    out={"period":"weekly","week_ending":str(datetime.date.today()),"items":[{"type":"note","text":text}]}
    write_json(write_to, out); return out

if __name__=="__main__":
    daily(); weekly()
