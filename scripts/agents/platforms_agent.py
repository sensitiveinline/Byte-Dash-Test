from datetime import datetime
def run(raw=None):
    now = datetime.utcnow().isoformat()+"Z"
    items = [
        {"id":"openai-chatgpt","name":"ChatGPT","url":"https://chat.openai.com",
         "score":92.4,"rank":1,"delta7":1.1,"delta30":3.2,"ts":now,
         "ai":{"insight":"대중성 최강—기업 전환률이 관건.","tags":["distribution"],"confidence":0.75,"evidence":[]}},
        {"id":"google-gemini","name":"Gemini","url":"https://gemini.google.com",
         "score":89.8,"rank":2,"delta7":1.4,"delta30":2.1,"ts":now,
         "ai":{"insight":"Workspace 기본탑재 확대로 업무 침투 가속.","tags":["workspace"],"confidence":0.78,"evidence":[]}},
    ]
    return {"items": items}
