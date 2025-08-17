from datetime import datetime
def note_agent():
    return [
        {"title":"(stub) Daily Briefing","content":"stub note","date":datetime.utcnow().date().isoformat()}
    ]
