import json
import os
import re
import httpx
from config import settings

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_PATH = os.path.join(_BACKEND_DIR, "prompts", "response_generation_prompt.txt")

_ollama_available: bool | None = None


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


def _hallucination_check(response_text: str, retrieved_restaurants: list[dict]) -> bool:
    retrieved_names = {r["name"].lower() for r in retrieved_restaurants}
    possible_names = re.findall(r'(?:^|\s)([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', response_text)
    for pn in possible_names:
        if pn.lower() not in retrieved_names:
            return False
    return True


def format_price_label(avg_price, price_level):
    if avg_price:
        label = {"low": "Budget-friendly", "medium": "Moderate", "high": "Premium"}.get(price_level, price_level.capitalize())
        return f"Rs. {avg_price:,}/person · {label}"
    elif price_level:
        return price_level.capitalize()
    return "Price not available"


def format_active_filters(preferences: dict) -> str:
    labels = {
        "location": "Area", "cuisine": "Cuisine", "budget_max": "Budget ≤ Rs.",
        "purpose": "Purpose", "dietary": "Dietary", "ambience": "Vibe",
        "price_level": "Price Level",
    }
    lines = []
    for key, label in labels.items():
        val = preferences.get(key)
        if val:
            display = ", ".join(val) if isinstance(val, list) else str(val)
            lines.append(f"· {label}: {display}")
    return "\n".join(lines) if lines else ""


def get_available_cuisines_in_area(restaurants_df, area: str) -> list:
    area_df = restaurants_df[restaurants_df["area"].str.lower() == area.lower()]
    return sorted(
        area_df["cuisine"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .dropna()
        .unique()
        .tolist()
    )


def get_areas_with_cuisine(restaurants_df, cuisine: str) -> list:
    matches = restaurants_df[
        restaurants_df["cuisine"].str.lower().str.contains(cuisine.lower(), na=False)
    ]
    return sorted(matches["area"].dropna().unique().tolist())


def generate_response(
    user_query: str,
    preferences: dict,
    recommendations: list[dict],
    restaurant_df=None,
) -> str:
    if not recommendations:
        return _generate_no_match_response(user_query, preferences, restaurant_df)

    if _check_ollama():
        prompt_template = _load_prompt()
        prompt = prompt_template.replace("{{USER_QUERY}}", user_query)
        prompt = prompt.replace("{{PREFERENCES_JSON}}", json.dumps(preferences, indent=2))
        prompt = prompt.replace("{{RESTAURANT_RESULTS_JSON}}", json.dumps(recommendations, indent=2))
        try:
            response = _call_ollama(prompt)
            passed = _hallucination_check(response, recommendations)
            if passed:
                return response
        except Exception:
            pass

    return _fallback_response(recommendations, preferences)


def _fallback_response(recommendations: list[dict], preferences: dict = None) -> str:
    count = len(recommendations)
    is_all_exact = all(r.get("match_type") == "exact" for r in recommendations)
    has_closest = any(r.get("match_type") == "closest" for r in recommendations)

    if is_all_exact:
        msg = f"Found {count} option{'s' if count > 1 else ''} matching your request. See the cards below for details."
    elif has_closest and count > 1:
        msg = (f"Found {count} option{'s' if count > 1 else ''}. "
               f"Some are exact matches and others are the closest alternatives available.")
    else:
        msg = "I could not find an exact match. Here is the closest option available."

    return msg


def build_no_match_sentence(preferences: dict) -> str:
    area = preferences.get("location")
    cuisine = preferences.get("cuisine")
    dietary = preferences.get("dietary")
    ambience = preferences.get("ambience")
    budget = preferences.get("budget_max")

    descriptors = []
    if dietary == "vegetarian":
        descriptors.append("vegetarian-friendly")
    if ambience:
        if isinstance(ambience, list):
            descriptors.extend(ambience)
        else:
            descriptors.append(ambience)
    if cuisine:
        descriptors.append(f"{', '.join(cuisine)} options")
    else:
        descriptors.append("restaurant options")

    sentence = "I could not find " + " ".join(descriptors)
    if area:
        sentence += f" in {area}"
    if budget:
        sentence += f" under Rs. {budget}"
    sentence += " in the current dataset."
    return sentence


def _generate_no_match_response(user_query: str, preferences: dict, restaurant_df=None) -> str:
    requested_cuisines = preferences.get("cuisine", [])
    requested_location = preferences.get("location")
    filter_summary = format_active_filters(preferences)

    base = ""
    if filter_summary:
        base = f"Using filters:\n{filter_summary}\n\n"

    base += "No exact match found.\n\n"

    sentence = build_no_match_sentence(preferences)
    base += sentence + "\n\n"

    if restaurant_df is not None and requested_location:
        available = get_available_cuisines_in_area(restaurant_df, requested_location)
        if available:
            base += f"Available cuisines in {requested_location}:\n"
            base += "\n".join(f"· {c}" for c in available) + "\n\n"
            base += _generate_area_suggestions(restaurant_df, requested_cuisines)
            return base

    if restaurant_df is not None and requested_cuisines:
        suggestions = []
        for c in requested_cuisines:
            areas = get_areas_with_cuisine(restaurant_df, c)
            if areas:
                suggestions.append(f"· {c.capitalize()} restaurants are available in: {', '.join(areas)}")
        if suggestions:
            base += "\n".join(suggestions) + "\n\n"
            base += "Try adjusting your area or budget."
            return base

    base += (
        "Available cuisines include: Nepali, Newari, Indian, Korean, Japanese, "
        "Chinese, Italian, Continental, Cafe, and Bakery.\n"
        "Available areas include: Thamel, Patan, Baneshwor, Boudha, Jhamsikhel, "
        "Lazimpat, Durbarmarg, New Road, Baluwatar, Maharajgunj, Kupondole, Naxal."
    )
    return base


def _generate_area_suggestions(restaurant_df, cuisines):
    if not cuisines:
        return ""
    suggestions = []
    for c in cuisines:
        areas = get_areas_with_cuisine(restaurant_df, c)
        if areas:
            suggestions.append(f"You can also search {c.capitalize()} restaurants in other areas like {' or '.join(areas[:3])}.")
    return "\n".join(suggestions[:2])
