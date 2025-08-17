from datetime import datetime
def run(raw=None):
    now = datetime.utcnow().isoformat()+"Z"
    items = [
        {"repo":"huggingface/transformers","url":"https://github.com/huggingface/transformers",
         "new_stars30":20000,"forks":45000,"contributors":380,"score":88.1,"rank":1,"delta7":3.4,"ts":now,
         "ai":{"insight":"생태계 허브—튜토리얼/모델 카드 확산.","tags":["tooling"],"confidence":0.7}},
        {"repo":"meta-llama/llama","url":"https://github.com/meta-llama/llama",
         "new_stars30":15000,"forks":18000,"contributors":520,"score":86.3,"rank":2,"delta7":2.7,"ts":now,
         "ai":{"insight":"대형 모델 오픈소스—연구 확산.","tags":["llm"],"confidence":0.7}},
    ]
    return {"items": items}
