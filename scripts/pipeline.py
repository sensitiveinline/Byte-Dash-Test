from dotenv import load_dotenv
load_dotenv()

import json, os
from scripts.agents import platforms_agent, github_agent, news_agent, note_agent
from scripts.utils.schema import validate_and_fix, PlatformItem, RepoItem, NewsItem

DATA_DIR = "data"

def save_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)

def main():
    platforms_raw = platforms_agent.run()
    github_raw    = github_agent.run()
    news_raw      = news_agent.run()

    platforms_out = validate_and_fix(PlatformItem, platforms_raw)
    github_out    = validate_and_fix(RepoItem, github_raw)
    news_out      = validate_and_fix(NewsItem, news_raw)

    save_json(f"{DATA_DIR}/platform_rankings.json", platforms_out)
    save_json(f"{DATA_DIR}/github_trends.json", github_out)
    save_json(f"{DATA_DIR}/news.json", news_out)

    note = note_agent.run(platforms_out, github_out, news_out, period="daily")
    save_json(f"{DATA_DIR}/ai_note.json", note)

if __name__ == "__main__":
    main()
