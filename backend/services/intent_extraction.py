import json
import re
import os
import httpx
from config import settings

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_PATH = os.path.join(_BACKEND_DIR, "prompts", "intent_extraction_prompt.txt")

_ollama_available: bool | None = None
_restaurant_names: set[str] = set()

COMMANDS = ["areas", "cuisines", "show all", "more", "next", "the best", "best", "reset"]

GREETINGS = {"hi", "hello", "hey", "namaste", "yo", "hiya", "sup", "greetings", "good morning", "good evening", "good afternoon"}

KNOWN_AREAS = {
    "thamel", "patan", "baneshwor", "jhamsikhel", "boudha",
    "lazimpat", "naxal", "durbarmarg", "new road", "baluwatar",
    "maharajgunj", "kupondole"
}

KNOWN_CUISINES = {
    "korean", "nepali", "newari", "indian", "italian", "japanese",
    "chinese", "continental", "cafe", "bakery", "fast food",
    "vegetarian", "multi-cuisine"
}


def _load_restaurant_names():
    """Load restaurant names from the database for recognition."""
    global _restaurant_names
    try:
        from database import SessionLocal
        from models import Restaurant
        db = SessionLocal()
        try:
            restaurants = db.query(Restaurant).all()
            _restaurant_names = {r.name.lower() for r in restaurants}
            print(f"Loaded {len(_restaurant_names)} restaurant names from database")
        finally:
            db.close()
    except Exception as e:
        print(f"Database load failed: {e}, trying CSV fallback")
        # Fallback to CSV if database not available
        try:
            import pandas as pd
            df = pd.read_csv(settings.data_path)
            _restaurant_names = {name.lower() for name in df["name"].dropna()}
            print(f"Loaded {len(_restaurant_names)} restaurant names from CSV")
        except Exception as e2:
            print(f"CSV load also failed: {e2}")
            pass


def _check_ollama() -> bool:
    global _ollama_available
    if _ollama_available is not None:
        return _ollama_available
    try:
        r = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=3)
        _ollama_available = r.status_code == 200
    except Exception:
        _ollama_available = False
    return _ollama_available


def _load_prompt() -> str:
    with open(PROMPT_PATH, "r") as f:
        return f.read()


def _call_ollama(prompt: str) -> str:
    response = httpx.post(
        f"{settings.ollama_base_url}/api/generate",
        json={
            "model": settings.llm_model,
            "prompt": prompt,
            "temperature": settings.llm_temperature,
            "stream": False,
        },
        timeout=8,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def _parse_json_from_response(text: str) -> dict:
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError("No JSON found in LLM response")


SYNONYM_MAP = {
    "cheap": "price_level:low",
    "affordable": "price_level:low",
    "budget": "price_level:low",
    "inexpensive": "price_level:low",
    "expensive": "price_level:high",
    "fancy": "price_level:high",
    "upscale": "price_level:high",
    "premium": "price_level:high",
    "date place": "purpose:date",
    "romantic spot": "purpose:date",
    "romantic": "purpose:date",
    "peaceful": "ambience:quiet",
    "calm": "ambience:quiet",
    "silent": "ambience:quiet",
    "not too crowded": "ambience:quiet",
    "hangout": "purpose:friends",
    "chill": "purpose:friends",
    "study": "purpose:study",
    "laptop": "purpose:study",
    "work": "purpose:study",
    "homework": "purpose:study",
    "non veg only": "dietary:non_vegetarian_only",
    "only non veg": "dietary:non_vegetarian_only",
    "non-veg only": "dietary:non_vegetarian_only",
    "only non-veg": "dietary:non_vegetarian_only",
    "non veg": "dietary:non_vegetarian",
    "non-vegetarian": "dietary:non_vegetarian",
    "veg only": "dietary:vegetarian_only",
    "only veg": "dietary:vegetarian_only",
    "vegetarian only": "dietary:vegetarian_only",
    "only vegetarian": "dietary:vegetarian_only",
    "veggie": "dietary:vegetarian",
    "no meat": "dietary:vegetarian",
    "veg": "dietary:vegetarian",
    "vegetarian": "dietary:vegetarian",
}


def _resolve_or_alternatives(intent: dict, text: str) -> dict:
    """If the user offers alternatives with "or" (e.g. "veg restaurant or cafe"),
    keep only the first-mentioned food preference instead of combining them
    into hard AND filters that would wrongly return no matches."""
    if not re.search(r"\bor\b", text):
        return intent

    dietary_pos = -1
    if intent.get("dietary"):
        dietary = str(intent["dietary"]).lower().replace("-", "_")
        if dietary in ("non_vegetarian", "non_vegetarian_only"):
            m = re.search(r"\bnon[- ]?veg\b", text)
        else:
            m = re.search(r"\bveg(?:etarian)?\b", text)
        dietary_pos = m.start() if m else -1
    cuisine_pos = -1
    if intent.get("cuisine"):
        c = re.escape(intent["cuisine"][0].lower())
        m = re.search(r"\b" + c + r"\b", text)
        cuisine_pos = m.start() if m else text.find(intent["cuisine"][0].lower())

    if dietary_pos >= 0 and cuisine_pos >= 0:
        if dietary_pos < cuisine_pos:
            intent["cuisine"] = None  # "veg restaurant or cafe" -> keep veg
        else:
            intent["dietary"] = None  # "cafe or veg restaurant" -> keep cafe
    return intent


def normalize_preferences(intent: dict, original_message: str = "") -> dict:
    text = original_message.lower()
    for expr, normalized in SYNONYM_MAP.items():
        if expr.lower() in text:
            field, value = normalized.split(":", 1)
            if not intent.get(field):
                if field in ("ambience", "cuisine"):
                    intent[field] = [value]
                else:
                    intent[field] = value
    return _resolve_or_alternatives(intent, text)


def validate_intent(intent: dict) -> dict:
    if not isinstance(intent, dict):
        return {"clarification_required": True, "missing_fields": ["all"]}
    allowed_locations = [
        "thamel", "patan", "baneshwor", "boudha", "jhamsikhel",
        "lazimpat", "durbarmarg", "new road", "baluwatar",
        "maharajgunj", "kupondole", "naxal"
    ]
    if intent.get("location") and intent["location"].lower() not in allowed_locations:
        intent["location"] = None
        if "location" not in intent.get("missing_fields", []):
            intent.setdefault("missing_fields", []).append("location")
    return intent


def classify_intent(message: str) -> str:
    """Classify message intent BEFORE any LLM call. Deterministic router."""
    text = message.lower().strip()

    if text in GREETINGS:
        return "greeting"

    if text in ("reset", "start over", "new session", "clear"):
        return "reset"

    if text in ("more", "next", "more results", "next page"):
        return "pagination_next"

    if text in ("show all", "show everything", "all restaurants", "all", "everything", "see all"):
        return "list_inventory"

    if text in ("best", "the best", "top rated", "highest rated", "best rated"):
        return "sort_best"

    if text in ("areas", "area", "locations", "location", "what areas", "list areas"):
        return "list_areas"

    if text in ("cuisines", "cuisine", "food types", "food", "what cuisines", "what food"):
        return "list_cuisines"

    if text.isdigit():
        return "set_budget"

    if re.match(r"^(under|below|max|within|upto|up to)?\s*\d+$", text):
        return "set_budget"

    if text in KNOWN_AREAS:
        return "set_area"

    if text in KNOWN_CUISINES:
        return "set_cuisine"

    # Check for restaurant name (if any restaurant name is contained in the message)
    if not _restaurant_names:
        _load_restaurant_names()
    for name in _restaurant_names:
        if name in text:
            return "restaurant_name"

    return "recommend"


def detect_command(message: str) -> str | None:
    intent_type = classify_intent(message)
    mapping = {
        "greeting": None,
        "reset": "reset",
        "pagination_next": "more",
        "list_inventory": "show_all",
        "sort_best": "best",
        "list_areas": "areas",
        "list_cuisines": "cuisines",
        "set_budget": None,
        "set_area": None,
        "set_cuisine": None,
        "restaurant_name": None,
        "recommend": None,
    }
    return mapping.get(intent_type)


def extract_intent(user_message: str) -> dict:
    intent_type = classify_intent(user_message)

    if intent_type == "greeting":
        return {
            "greeting": True,
            "location": None, "cuisine": None, "budget_max": None,
            "price_level": None, "purpose": None, "ambience": None,
            "dietary": None, "meal_time": None,
            "clarification_required": False, "missing_fields": [],
        }

    command = detect_command(user_message)
    if command:
        return {
            "command": command,
            "location": None, "cuisine": None, "budget_max": None,
            "price_level": None, "purpose": None, "ambience": None,
            "dietary": None, "meal_time": None,
            "clarification_required": False, "missing_fields": [],
        }

    if intent_type == "restaurant_name":
        return _handle_restaurant_name(user_message)

    if intent_type in ("set_area", "set_cuisine", "set_budget"):
        return _handle_single_field(intent_type, user_message)

    if _check_ollama():
        prompt_template = _load_prompt()
        prompt = prompt_template.replace("{{USER_MESSAGE}}", user_message)
        try:
            raw_response = _call_ollama(prompt)
            intent = _parse_json_from_response(raw_response)
            intent = validate_intent(intent)
            intent = normalize_preferences(intent, user_message)
            return intent
        except Exception:
            pass

    intent = _fallback_keyword_extraction(user_message)
    intent = validate_intent(intent)
    intent = normalize_preferences(intent, user_message)
    return intent


def _handle_restaurant_name(message: str) -> dict:
    """Handle when user types a specific restaurant name."""
    text = message.lower().strip()
    
    # Load restaurant names if not already loaded
    if not _restaurant_names:
        _load_restaurant_names()
    
    # Check if any restaurant name is contained in the message
    matched_name = None
    for name in _restaurant_names:
        if name in text:
            matched_name = name
            break
    
    if not matched_name:
        # Fallback to keyword extraction if no restaurant name found
        return _fallback_keyword_extraction(message)
    
    # Find the restaurant in database
    try:
        from database import SessionLocal
        from models import Restaurant
        db = SessionLocal()
        try:
            restaurant = db.query(Restaurant).filter(
                Restaurant.name.ilike(matched_name)
            ).first()
            if restaurant:
                return {
                    "restaurant_name": restaurant.name,
                    "restaurant_id": restaurant.restaurant_id,
                    "location": restaurant.area,
                    "cuisine": [c.strip() for c in restaurant.cuisine.split(",")],
                    "budget_max": restaurant.avg_price_per_person,
                    "price_level": restaurant.price_level,
                    "clarification_required": False,
                    "missing_fields": [],
                }
        finally:
            db.close()
    except Exception:
        pass
    
    # Fallback to keyword extraction if database lookup fails
    return _fallback_keyword_extraction(message)


def _handle_single_field(intent_type: str, message: str) -> dict:
    intent = {
        "location": None, "cuisine": None, "budget_max": None,
        "price_level": None, "purpose": None, "ambience": None,
        "dietary": None, "meal_time": None,
        "clarification_required": False, "missing_fields": [],
    }
    text = message.lower().strip()
    if intent_type == "set_area":
        intent["location"] = text.capitalize()
    elif intent_type == "set_cuisine":
        intent["cuisine"] = [text]
    elif intent_type == "set_budget":
        nums = re.findall(r"\d+", text)
        if nums:
            intent["budget_max"] = int(nums[0])
    return intent


def _fallback_keyword_extraction(text: str) -> dict:
    intent = {
        "location": None,
        "cuisine": None,
        "budget_max": None,
        "price_level": None,
        "purpose": None,
        "ambience": None,
        "dietary": None,
        "meal_time": None,
        "clarification_required": False,
        "missing_fields": [],
    }

    t = text.lower()

    area_keywords = {
        "thamel": "Thamel", "patan": "Patan", "baneshwor": "Baneshwor",
        "boudha": "Boudha", "jhamsikhel": "Jhamsikhel", "lazimpat": "Lazimpat",
        "durbar": "Durbarmarg", "new road": "New Road", "baluwatar": "Baluwatar",
        "maharajgunj": "Maharajgunj", "kupondole": "Kupondole", "naxal": "Naxal",
    }
    for keyword, area in area_keywords.items():
        if keyword in t:
            intent["location"] = area
            break

    known_cuisines = [
        "nepali", "newari", "indian", "korean", "japanese", "chinese",
        "italian", "continental", "cafe", "bakery", "fast food", "vegetarian"
    ]
    matched = [c for c in known_cuisines if c in t]
    if matched:
        intent["cuisine"] = matched

    other_cuisines = [
        "mexican", "thai", "french", "spanish", "greek", "turkish",
        "american", "mediterranean", "vietnamese", "thai", "malaysian"
    ]
    for oc in other_cuisines:
        if oc in t:
            if intent["cuisine"] is None:
                intent["cuisine"] = []
            intent["cuisine"].append(oc)

    budget_match = re.search(r"(?:under|below|less than|max|budget of|around|approximately|within|up to)\s*(?:rs\.?\s*|npr\s*)?(\d+)", t)
    if budget_match:
        intent["budget_max"] = int(budget_match.group(1))

    purpose_patterns = [
        (r"\bdate\b", "date"),
        (r"\bstudy(?:ing)?\b", "study"),
        (r"\bfriends?\b", "friends"),
        (r"\bfamily\b", "family"),
        (r"\bbirthday\b", "birthday"),
        (r"\bbusiness\b", "business"),
        (r"\bcasual\b", "casual"),
    ]
    for pattern, value in purpose_patterns:
        if re.search(pattern, t):
            intent["purpose"] = value
            break

    meal_patterns = [
        (r"\bbreakfast\b", "breakfast"),
        (r"\blunch\b", "lunch"),
        (r"\bdinner\b", "dinner"),
    ]
    for pattern, value in meal_patterns:
        if re.search(pattern, t):
            intent["meal_time"] = value
            break

    # Dietary preferences
    has_non_veg = re.search(r"\bnon[- ]?veg\b", t) or re.search(r"\bno[- ]?veg\b", t)
    has_only = re.search(r"\bonly\b", t)
    if has_non_veg:
        if has_only:
            intent["dietary"] = "non_vegetarian_only"
        else:
            intent["dietary"] = "non_vegetarian"
    elif re.search(r"\bonly[- ]?veg\b", t) or re.search(r"\bveg[- ]?only\b", t) or re.search(r"\bonly\s+vegetarian\b", t):
        intent["dietary"] = "vegetarian_only"
    elif re.search(r"\bveg(?:etarian)?\b", t) and not has_non_veg:
        intent["dietary"] = "vegetarian"

    intent = _resolve_or_alternatives(intent, t)

    if not intent.get("location") and not intent.get("cuisine") and not intent.get("budget_max") and not intent.get("purpose") and not intent.get("price_level"):
        intent["clarification_required"] = True
        intent["missing_fields"] = ["location", "cuisine"]

    return intent
