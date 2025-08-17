# --- import path & dotenv guards (auto-injected) ---
import sys, pathlib
# add repo root to sys.path so 'scripts.*' imports work no matter how it's run
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass
# --- end guards ---

try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass
import json, pathlib, time

from scripts.collectors import news_agent, github_agent
from scripts.scorers import platforms_agent
from scripts.notes import note_agent

DATA = pathlib.Path("data"); DATA.mkdir(exist_ok=True)

def _save(path, obj):
    p = pathlib.Path(path)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)

def main():
    news  = news_agent.run();              _save("data/news.json", news); time.sleep(1)
    gh    = github_agent.run();            _save("data/github_trends.json", gh); time.sleep(1)
    plats = platforms_agent.run();         _save("data/platform_rankings.json", plats); time.sleep(1)
    note  = note_agent.run("data/news.json","data/github_trends.json","data/ai_note.json")
    print("OK: data updated")

if __name__ == "__main__":
    main()
