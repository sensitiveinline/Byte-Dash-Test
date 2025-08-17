from datetime import datetime
def news_agent():
    return {
        "items": [
            {"title":"(stub) OpenAI launches new model","link":"https://openai.com","summary":"stub"},
            {"title":"(stub) DeepMind update","link":"https://deepmind.com","summary":"stub"}
        ],
        "meta":{"updated": datetime.utcnow().isoformat()+"Z", "source":"stub"}
    }
def github_agent():
    return {
        "items": [
            {"repo":"openai/gpt-4","stars":250000},
            {"repo":"deepmind/alphafold","stars":180000}
        ],
        "meta":{"updated": datetime.utcnow().isoformat()+"Z", "source":"stub"}
    }
