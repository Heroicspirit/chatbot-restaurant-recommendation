WEIGHTS = {
    "cuisine_match": 0.20,
    "location_match": 0.20,
    "budget_match": 0.15,
    "purpose_vibe_match": 0.15,
    "dietary_match": 0.10,
    "rating_strength": 0.10,
    "semantic_similarity": 0.10,
}


def score_cuisine_match(restaurant: dict, preferred_cuisines: list[str] | None) -> float:
    if not preferred_cuisines:
        return 1.0
    rest_cuisines = [c.strip().lower() for c in restaurant.get("cuisine", "").split(",")]
    preferred = [c.lower() for c in preferred_cuisines]
    matches = sum(1 for p in preferred if any(p in rc for rc in rest_cuisines))
    if matches == len(preferred):
        return 1.0
    if matches > 0:
        return 0.5
    return 0.0


def score_location_match(restaurant: dict, preferred_location: str | None) -> float:
    if not preferred_location:
        return 1.0
    rest_area = restaurant.get("area", "").lower()
    preferred = preferred_location.lower()
    if rest_area == preferred:
        return 1.0
    adjacent_areas = {
        "thamel": ["lazimpat"],
        "lazimpat": ["thamel", "naxal"],
        "naxal": ["lazimpat", "baluwatar"],
        "baluwatar": ["naxal", "maharajgunj"],
        "maharajgunj": ["baluwatar"],
        "patan": ["jhamsikhel", "kupondole"],
        "jhamsikhel": ["patan", "kupondole"],
        "kupondole": ["patan", "jhamsikhel"],
        "baneshwor": ["new road"],
        "new road": ["baneshwor", "durbarmarg"],
        "durbarmarg": ["new road"],
        "boudha": [],
    }
    adj = adjacent_areas.get(rest_area, [])
    if preferred in adj:
        return 0.5
    return 0.0


def score_budget_match(restaurant: dict, budget_max: int | None, price_level: str | None) -> float:
    price = restaurant.get("avg_price_per_person")
    if budget_max and price:
        if price <= budget_max:
            return 1.0
        if price <= budget_max * 1.3:
            return 0.5
        return 0.0
    if price_level:
        rest_level = restaurant.get("price_level", "").lower()
        if rest_level == price_level.lower():
            return 1.0
    return 1.0


def score_purpose_match(restaurant: dict, purpose: str | None) -> float:
    if not purpose:
        return 1.0
    suitable = [s.strip().lower() for s in restaurant.get("suitable_for", "").split(",")]
    if purpose.lower() in suitable:
        return 1.0
    partial_matches = {
        "date": ["romantic", "cozy"],
        "study": ["quiet", "study-friendly"],
        "friends": ["lively", "casual"],
        "family": ["family-friendly", "casual"],
        "casual": ["friends", "family"],
    }
    pm = partial_matches.get(purpose.lower(), [])
    ambience = [a.strip().lower() for a in restaurant.get("ambience_tags", "").split(",")]
    if any(p in ambience for p in pm):
        return 0.5
    return 0.0


def score_dietary_match(restaurant: dict, dietary: str | None) -> float:
    if not dietary:
        return 1.0
    if dietary.lower() == "vegetarian":
        return 1.0 if restaurant.get("veg_available") else 0.0
    return 1.0


def score_rating_strength(restaurant: dict) -> float:
    rating = restaurant.get("rating", 0)
    return min(rating / 5.0, 1.0)


def determine_match_type(restaurant: dict, preferences: dict) -> str:
    all_exact = True
    if preferences.get("cuisine"):
        c_score = score_cuisine_match(restaurant, preferences["cuisine"])
        if c_score < 1.0:
            all_exact = False
    if preferences.get("location"):
        l_score = score_location_match(restaurant, preferences["location"])
        if l_score < 1.0:
            all_exact = False
    if preferences.get("budget_max"):
        b_score = score_budget_match(restaurant, preferences["budget_max"], None)
        if b_score < 1.0:
            all_exact = False
    if preferences.get("purpose"):
        p_score = score_purpose_match(restaurant, preferences["purpose"])
        if p_score < 1.0:
            all_exact = False
    if preferences.get("dietary"):
        d_score = score_dietary_match(restaurant, preferences["dietary"])
        if d_score < 1.0:
            all_exact = False
    return "exact" if all_exact else "closest"


def build_matched_factors(preferences: dict, restaurant: dict) -> list:
    factors = []
    if preferences.get("cuisine"):
        cuisine_pref = preferences["cuisine"]
        rest_cuisines = [c.strip().lower() for c in restaurant.get("cuisine", "").split(",")]
        if any(any(p.lower() in rc for rc in rest_cuisines) for p in cuisine_pref):
            factors.append(f"{', '.join(cuisine_pref)} cuisine")
    if preferences.get("location"):
        if restaurant.get("area", "").lower() == preferences["location"].lower():
            factors.append(f"{restaurant['area']} area")
    if preferences.get("budget_max"):
        price = restaurant.get("avg_price_per_person")
        if price and price <= preferences["budget_max"]:
            factors.append(f"within your Rs. {preferences['budget_max']} budget")
    if preferences.get("purpose"):
        suitable = restaurant.get("suitable_for", "")
        if preferences["purpose"].lower() in suitable.lower():
            factors.append(f"suitable for {preferences['purpose']}")
    if preferences.get("ambience"):
        tags = restaurant.get("ambience_tags", "").lower()
        matched_vibes = [v for v in preferences["ambience"] if v.lower() in tags]
        if matched_vibes:
            factors.append(f"{', '.join(matched_vibes)} atmosphere")
    if preferences.get("dietary") == "vegetarian":
        if restaurant.get("veg_available"):
            factors.append("vegetarian options available")
    return factors


def build_reason_sentence(matched_factors: list) -> str:
    if not matched_factors:
        return "Shown as a closest available option from the dataset."
    if len(matched_factors) == 1:
        return f"Matches your request for {matched_factors[0]}."
    core = ", ".join(matched_factors[:-1])
    return f"Matches your request for {core}, and {matched_factors[-1]}."


def rank_candidates(
    restaurants: list[dict],
    preferences: dict,
    semantic_scores: dict[str, float] | None = None,
) -> list[dict]:
    scored = []
    for r in restaurants:
        cuisine_score = score_cuisine_match(r, preferences.get("cuisine"))
        location_score = score_location_match(r, preferences.get("location"))
        budget_score = score_budget_match(
            r, preferences.get("budget_max"), preferences.get("price_level")
        )
        purpose_score = score_purpose_match(r, preferences.get("purpose"))
        dietary_score = score_dietary_match(r, preferences.get("dietary"))
        rating_score = score_rating_strength(r)
        semantic_score = semantic_scores.get(r["restaurant_id"], 0) if semantic_scores else 0

        final_score = (
            cuisine_score * WEIGHTS["cuisine_match"]
            + location_score * WEIGHTS["location_match"]
            + budget_score * WEIGHTS["budget_match"]
            + purpose_score * WEIGHTS["purpose_vibe_match"]
            + dietary_score * WEIGHTS["dietary_match"]
            + rating_score * WEIGHTS["rating_strength"]
            + semantic_score * WEIGHTS["semantic_similarity"]
        )

        matched_factors = build_matched_factors(preferences, r)
        reason = build_reason_sentence(matched_factors)
        match_type = determine_match_type(r, preferences)

        scored.append({
            **r,
            "final_score": round(final_score, 3),
            "matched_factors": matched_factors,
            "missing_factors": [],
            "reason": reason,
            "match_type": match_type,
            "match_status": "exact" if match_type == "exact" else "closest",
        })

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored
