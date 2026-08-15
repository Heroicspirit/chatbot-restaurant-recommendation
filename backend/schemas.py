from pydantic import BaseModel
from typing import Optional


class IntentResult(BaseModel):
    location: Optional[str] = None
    cuisine: Optional[list[str]] = None
    budget_max: Optional[int] = None
    price_level: Optional[str] = None
    purpose: Optional[str] = None
    ambience: Optional[list[str]] = None
    dietary: Optional[str] = None
    meal_time: Optional[str] = None
    clarification_required: bool = False
    missing_fields: list[str] = []


class RestaurantResponse(BaseModel):
    restaurant_id: str
    name: str
    area: str
    cuisine: str
    price_level: str
    avg_price_per_person: int
    rating: float
    veg_available: bool
    serves_both: bool = False
    ambience_tags: str
    suitable_for: str
    description: str
    final_score: float = 0.0
    matched_factors: list[str] = []
    missing_factors: list[str] = []
    reason: str = ""
    match_type: str = "exact"
    match_status: str = "exact"


class ChatRequest(BaseModel):
    session_id: str
    message: str
    top_k: int = 3


class ChatResponse(BaseModel):
    session_id: str
    intent: IntentResult
    recommendations: list[RestaurantResponse]
    response: str
    clarification_question: Optional[str] = None
    hallucination_check: str = "passed"
    match_status: str = "none"
    active_filters: dict = {}
    result_count: int = 0
