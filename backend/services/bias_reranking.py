def bias_aware_rerank(candidates: list[dict], top_k: int = 3) -> list[dict]:
    if not candidates:
        return []

    selected = []

    # 1. Best overall match
    best_overall = max(candidates, key=lambda x: x["final_score"])
    selected.append(best_overall)
    remaining = [c for c in candidates if c["restaurant_id"] != best_overall["restaurant_id"]]

    if not remaining:
        return selected[:top_k]

    # 2. Best budget match (lowest price among remaining)
    best_budget = min(remaining, key=lambda x: x.get("avg_price_per_person", 9999))
    if best_budget["restaurant_id"] not in [s["restaurant_id"] for s in selected]:
        selected.append(best_budget)
    remaining = [c for c in remaining if c["restaurant_id"] not in [s["restaurant_id"] for s in selected]]

    if not remaining:
        return selected[:top_k]

    # 3. Best ambience/purpose match based on purpose_score from ranking
    best_vibe = max(remaining, key=lambda x: (
        x.get("final_score", 0) * 0.3 +
        (1.0 if any(
            tag in ",".join(x.get("ambience_tags", "").split(","))
            for tag in ["quiet", "cozy", "romantic", "study-friendly", "lively"]
        ) else 0.0) * 0.7
    ))
    if best_vibe["restaurant_id"] not in [s["restaurant_id"] for s in selected]:
        selected.append(best_vibe)
    remaining = [c for c in remaining if c["restaurant_id"] not in [s["restaurant_id"] for s in selected]]

    # 4. Remove near-duplicates (same area + same cuisine)
    to_remove_ids = set()
    for r in remaining:
        for s in selected:
            if (r.get("area") == s.get("area") and
                    r.get("cuisine") == s.get("cuisine")):
                to_remove_ids.add(r["restaurant_id"])
    remaining = [c for c in remaining if c["restaurant_id"] not in to_remove_ids]

    # 5. Fill remaining slots with highest scored
    while len(selected) < top_k and remaining:
        best_remaining = max(remaining, key=lambda x: x["final_score"])
        selected.append(best_remaining)
        remaining = [c for c in remaining if c["restaurant_id"] != best_remaining["restaurant_id"]]

    return selected[:top_k]
