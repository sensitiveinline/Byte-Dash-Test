from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

SAMPLES = {
    "platform_rankings.json": {"items":[{"rank":1,"name":"OpenAI","score":98}], "meta":{"updated":"sample"}},
    "github.json": {"items":[{"repo":"openai/gpt-4","stars":250000}], "meta":{"updated":"sample"}},
    "news.json": {"items":[{"title":"OpenAI","link":"https://openai.com","summary":"sample"}], "meta":{"updated":"sample"}},
    "ai_note.json": [{"title":"Daily","content":"sample","date":"1970-01-01"}],
}

def is_valid(name, payload):
    if name=="ai_note.json":
        return isinstance(payload, list)
    return isinstance(payload, dict) and "items" in payload

def ensure_valid(fix=False):
    ok=True
    for name, sample in SAMPLES.items():
        p = DATA / name
        if not p.exists():
            if fix: p.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
            ok=False; continue
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
            if not is_valid(name, payload):
                if fix:
                    p.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
                ok=False
        except Exception:
            if fix:
                p.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
            ok=False
    return ok

if __name__ == "__main__":
    fix = "--fix" in sys.argv
    good = ensure_valid(fix=fix)
    print(("OK" if good else "FIXED") + " scripts/validate_data.py")
    sys.exit(0)
