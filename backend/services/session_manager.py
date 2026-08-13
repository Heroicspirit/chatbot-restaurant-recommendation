import uuid
from datetime import datetime, timedelta
from typing import Optional

SESSION_TIMEOUT_MINUTES = 30


def is_complete_new_query(intent: dict) -> bool:
    has_location = bool(intent.get("location"))
    has_cuisine = bool(intent.get("cuisine"))
    has_purpose = bool(intent.get("purpose"))
    has_ambience = bool(intent.get("ambience"))
    return has_location and (has_cuisine or has_purpose or has_ambience)


class SessionState:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.last_location: Optional[str] = None
        self.last_cuisine: Optional[list[str]] = None
        self.last_budget_max: Optional[int] = None
        self.last_price_level: Optional[str] = None
        self.last_purpose: Optional[str] = None
        self.last_ambience: Optional[list[str]] = None
        self.dietary: Optional[str] = None
        self.previous_recommendations: list[str] = []
        self.conversation_turns: int = 0
        self.last_updated: datetime = datetime.now()

    def is_expired(self) -> bool:
        return datetime.now() - self.last_updated > timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    def reset(self):
        self.last_location = None
        self.last_cuisine = None
        self.last_budget_max = None
        self.last_price_level = None
        self.last_purpose = None
        self.last_ambience = None
        self.dietary = None
        self.previous_recommendations = []
        self.conversation_turns = 0
        self.last_updated = datetime.now()

    def update(self, intent: dict):
        if intent.get("location"):
            self.last_location = intent["location"]
        if intent.get("cuisine"):
            self.last_cuisine = intent["cuisine"]
        if intent.get("budget_max"):
            self.last_budget_max = intent["budget_max"]
        if intent.get("price_level"):
            self.last_price_level = intent["price_level"]
        if intent.get("purpose"):
            self.last_purpose = intent["purpose"]
        if intent.get("ambience"):
            self.last_ambience = intent["ambience"]
        if intent.get("dietary"):
            self.dietary = intent["dietary"]
        self.conversation_turns += 1
        self.last_updated = datetime.now()

    def merge_with_intent(self, intent: dict) -> dict:
        merged = dict(intent)

        if is_complete_new_query(merged):
            return merged

        user_has_location = merged.get("location") is not None
        user_has_cuisine = merged.get("cuisine") is not None
        user_has_budget = merged.get("budget_max") is not None
        user_refining = bool(
            merged.get("price_level")
            or merged.get("purpose")
            or merged.get("ambience")
            or merged.get("dietary")
        )

        if not user_has_location and not user_has_cuisine and not user_has_budget and not user_refining:
            return merged

        if not user_has_location and self.last_location:
            merged["location"] = self.last_location
        if not user_has_cuisine and self.last_cuisine:
            merged["cuisine"] = self.last_cuisine
        if not merged.get("budget_max") and self.last_budget_max:
            merged["budget_max"] = self.last_budget_max
        if not merged.get("price_level") and self.last_price_level:
            merged["price_level"] = self.last_price_level
        if not merged.get("purpose") and self.last_purpose:
            merged["purpose"] = self.last_purpose
        if not merged.get("ambience") and self.last_ambience:
            merged["ambience"] = self.last_ambience
        if not merged.get("dietary") and self.dietary:
            merged["dietary"] = self.dietary
        return merged

    def add_recommendations(self, rec_ids: list[str]):
        self.previous_recommendations.extend(rec_ids)
        self.last_updated = datetime.now()

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "last_location": self.last_location,
            "last_cuisine": self.last_cuisine,
            "last_budget_max": self.last_budget_max,
            "last_price_level": self.last_price_level,
            "last_purpose": self.last_purpose,
            "last_ambience": self.last_ambience,
            "dietary": self.dietary,
            "previous_recommendations": self.previous_recommendations,
            "conversation_turns": self.conversation_turns,
        }


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, SessionState] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> SessionState:
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            if not session.is_expired():
                return session
        new_id = session_id or str(uuid.uuid4())
        session = SessionState(new_id)
        self._sessions[new_id] = session
        return session

    def reset_session(self, session_id: str):
        if session_id in self._sessions:
            self._sessions[session_id].reset()

    def cleanup_expired(self):
        expired = [sid for sid, s in self._sessions.items() if s.is_expired()]
        for sid in expired:
            del self._sessions[sid]


session_manager = SessionManager()