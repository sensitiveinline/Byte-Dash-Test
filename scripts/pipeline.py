from pathlib import Path
import json, datetime as dt

# .env 있으면 사용 (없어도 무시)
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

def write(path: Path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def ensure(path: Path, payload):
    if not path.exists():
        write(path, payload)

now = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

ensure(DATA / "platform_rankings.json", {
    "items": [
        {"rank": 1, "name": "OpenAI", "score": 98},
        {"rank": 2, "name": "Google DeepMind", "score": 95},
        {"rank": 3, "name": "Anthropic", "score": 90}
    ],
    "meta": {"updated": now, "source": "pipeline-min"}
})

ensure(DATA / "github.json", {
    "items": [
        {"repo": "openai/gpt-4", "stars": 250000},
        {"repo": "deepmind/alphafold", "stars": 180000}
    ],
    "meta": {"updated": now, "source": "pipeline-min"}
})

ensure(DATA / "news.json", {
    "items": [
        {"title": "OpenAI launches new model", "link": "https://openai.com", "summary": "Latest multimodal release."},
        {"title": "Google DeepMind breakthrough", "link": "https://deepmind.com", "summary": "New paper on RL."}
    ],
    "meta": {"updated": now, "source": "pipeline-min"}
})

ensure(DATA / "ai_note.json", [
    {"title": "Daily Briefing", "content": "샘플 노트입니다.", "date": now[:10]}
])

print("✅ pipeline.py: ensured data/*.json exist")
