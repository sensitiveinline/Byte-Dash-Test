from datetime import datetime
def platforms_agent():
    return {
        "items": [
            {"rank":1,"name":"OpenAI","score":98},
            {"rank":2,"name":"Google DeepMind","score":95},
            {"rank":3,"name":"Anthropic","score":90}
        ],
        "meta":{"updated": datetime.utcnow().isoformat()+"Z", "source":"stub"}
    }
