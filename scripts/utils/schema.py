from pydantic import BaseModel, Field, HttpUrl, ValidationError
from typing import List, Optional, Any, Dict
from datetime import datetime

class AIFields(BaseModel):
    insight: Optional[str] = None
    tags: List[str] = []
    confidence: Optional[float] = None
    evidence: List[Dict[str, Any]] = []
    guardrail_flags: List[str] = []

class PlatformItem(BaseModel):
    id: str
    name: str
    url: Optional[HttpUrl] = None
    score: float
    rank: int
    delta7: Optional[float] = None
    delta30: Optional[float] = None
    ts: str
    ai: Optional[AIFields] = None
    method: Optional[str] = "rule+ai/post-hoc"

class RepoItem(BaseModel):
    repo: str
    url: Optional[HttpUrl] = None
    new_stars30: Optional[int] = None
    forks: Optional[int] = None
    contributors: Optional[int] = None
    score: float
    rank: int
    delta7: Optional[float] = None
    ts: str
    ai: Optional[AIFields] = None
    noise_flag: Optional[bool] = False
    method: Optional[str] = "rule+ai/post-hoc"

class NewsItem(BaseModel):
    title: str
    source: str
    url: HttpUrl
    published_at: Optional[str] = None
    summary: Optional[str] = None
    takeaway: Optional[str] = None
    category: Optional[str] = None
    ts: str
    ai: Optional[AIFields] = None
    method: Optional[str] = "ai/summary"

class NoteHighlight(BaseModel):
    category: str
    title: str
    takeaway: str
    links: List[str] = []

class CrossSignal(BaseModel):
    entity: str
    signal: str
    insight: str

class NoteDoc(BaseModel):
    period: str
    date: str
    source_counts: Dict[str, int]
    highlights: List[NoteHighlight]
    cross_signals: List[CrossSignal]
    summary: Dict[str, str]

def wrap(items: list, period: Optional[str] = None):
    meta = {"generatedAt": datetime.utcnow().isoformat() + "Z"}
    if period: meta["period"] = period
    return {"items": items, "meta": meta}

def validate_and_fix(model_cls, payload):
    items = payload if isinstance(payload, list) else payload.get("items", [])
    fixed = []
    for it in items:
        try:
            fixed.append(model_cls(**it).model_dump())
        except ValidationError:
            continue
    return wrap(fixed)
