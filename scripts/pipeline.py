
# --- robust import guards (auto) ---
import sys, pathlib, importlib, json
from typing import Tuple

# repo root on sys.path so 'scripts.*' works under any runner
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

# dotenv is optional
try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass

# === Safe bindings (auto) ===
news_agent = news_agent_mod
github_agent = github_agent_mod
platforms_agent = platforms_agent_mod
note_agent = note_agent_mod
# ==============================

def _load_collectors():
    """Support BOTH layouts:
    A) scripts/collectors.py               (attrs: news_agent, github_agent)
    B) scripts/collectors/news_agent.py    (package submodules)
       scripts/collectors/github_agent.py
    Returns (news_agent_mod, github_agent_mod)
    """
    try:
        na = importlib.import_module("scripts.collectors.news_agent")
        ga = importlib.import_module("scripts.collectors.github_agent")
        return na, ga
    except ModuleNotFoundError:
        # fallback: single-file module
        mod = importlib.import_module("scripts.collectors")
        na = getattr(mod, "news_agent", None)
        ga = getattr(mod, "github_agent", None)
        if na is None or ga is None:
            raise ImportError("collectors: 'news_agent' or 'github_agent' not found in single-file collectors.py")
        return na, ga

def _load_scorers():
    try:
        return importlib.import_module("scripts.scorers.platforms_agent")
    except ModuleNotFoundError:
        mod = importlib.import_module("scripts.scorers")
        pa = getattr(mod, "platforms_agent", None)
        if pa is None:
            raise ImportError("scorers: 'platforms_agent' not found")
        return pa

def _load_notes():
    try:
        return importlib.import_module("scripts.notes.note_agent")
    except ModuleNotFoundError:
        mod = importlib.import_module("scripts.notes")
        na = getattr(mod, "note_agent", None)
        if na is None:
            raise ImportError("notes: 'note_agent' not found")
        return na

# Bind modules (if import fails later, caller can catch)
try:
    news_agent_mod, github_agent_mod = _load_collectors()
    platforms_agent_mod = _load_scorers()
    note_agent_mod = _load_notes()
except Exception as _e:
    news_agent_mod = github_agent_mod = platforms_agent_mod = note_agent_mod = None
# --- end robust import guards ---


# --- explicit submodule imports (importlib) ---
import importlib
news_agent      = importlib.import_module("scripts.collectors.news_agent")
github_agent    = importlib.import_module("scripts.collectors.github_agent")
platforms_agent = importlib.import_module("scripts.scorers.platforms_agent")
note_agent      = importlib.import_module("scripts.notes.note_agent")
# ----------------------------------------------

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

import importlib
# replaced by importlib below


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
