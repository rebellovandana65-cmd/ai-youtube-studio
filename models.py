from typing import Literal
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    idea: str = Field(min_length=8, max_length=500)
    duration_minutes: int = Field(default=10, ge=8, le=12)
    shorts_count: int = Field(default=5, ge=1, le=5)

class Scene(BaseModel):
    number: int
    duration_seconds: int
    purpose: str
    narration: str
    visual_prompt: str
    camera: str
    sound: str

class ProductionPackage(BaseModel):
    concept: str
    titles: list[str]
    hook: str
    thumbnail_concepts: list[str]
    script: str
    scenes: list[Scene]
    editing_plan: list[str]
    shorts: list[dict]
    quality_check: list[str]
