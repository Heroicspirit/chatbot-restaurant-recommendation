import pytest
from services.ranking import (
    score_cuisine_match,
    score_location_match,
    score_budget_match,
    score_purpose_match,
    score_dietary_match,
    score_rating_strength,
    rank_candidates,
)


SAMPLE_RESTAURANT = {
    "restaurant_id": "R001",
    "name": "Test Restaurant",
    "area": "Thamel",
    "cuisine": "Korean, Asian",
    "price_level": "medium",
    "avg_price_per_person": 950,
    "rating": 4.3,
    "veg_available": True,
    "ambience_tags": "cozy, quiet",
    "suitable_for": "date, friends",
    "description": "Test description",
}


class TestRanking:
    def test_cuisine_exact_match(self):
        score = score_cuisine_match(SAMPLE_RESTAURANT, ["Korean"])
        assert score == 1.0

    def test_cuisine_no_match(self):
        score = score_cuisine_match(SAMPLE_RESTAURANT, ["Italian"])
        assert score == 0.0

    def test_location_exact_match(self):
        score = score_location_match(SAMPLE_RESTAURANT, "Thamel")
        assert score == 1.0

    def test_location_no_match(self):
        score = score_location_match(SAMPLE_RESTAURANT, "Patan")
        assert score == 0.0

    def test_budget_within_range(self):
        score = score_budget_match(SAMPLE_RESTAURANT, 1000, None)
        assert score == 1.0

    def test_budget_slightly_over(self):
        score = score_budget_match(SAMPLE_RESTAURANT, 800, None)
        assert score == 0.5

    def test_purpose_match(self):
        score = score_purpose_match(SAMPLE_RESTAURANT, "date")
        assert score == 1.0

    def test_dietary_vegetarian_available(self):
        score = score_dietary_match(SAMPLE_RESTAURANT, "vegetarian")
        assert score == 1.0

    def test_dietary_vegetarian_only_veg_restaurant(self):
        score = score_dietary_match(SAMPLE_RESTAURANT, "vegetarian_only")
        assert score == 1.0

    def test_dietary_vegetarian_only_non_veg_restaurant(self):
        non_veg = dict(SAMPLE_RESTAURANT, veg_available=False)
        score = score_dietary_match(non_veg, "vegetarian_only")
        assert score == 0.0

    def test_dietary_non_veg_only_non_veg_restaurant(self):
        non_veg = dict(SAMPLE_RESTAURANT, veg_available=False)
        score = score_dietary_match(non_veg, "non_vegetarian_only")
        assert score == 1.0

    def test_dietary_non_veg_only_veg_restaurant(self):
        score = score_dietary_match(SAMPLE_RESTAURANT, "non_vegetarian_only")
        assert score == 0.0

    def test_dietary_non_veg_matches_serves_both(self):
        both = dict(SAMPLE_RESTAURANT, veg_available=True, serves_both=True)
        score = score_dietary_match(both, "non_vegetarian")
        assert score == 1.0

    def test_rating_strength(self):
        score = score_rating_strength(SAMPLE_RESTAURANT)
        assert score == 4.3 / 5.0

    def test_rank_candidates_ordering(self):
        r2 = dict(SAMPLE_RESTAURANT)
        r2["restaurant_id"] = "R002"
        r2["rating"] = 3.0
        candidates = [SAMPLE_RESTAURANT, r2]
        ranked = rank_candidates(candidates, {"cuisine": ["Korean"], "location": "Thamel"})
        assert ranked[0]["restaurant_id"] == "R001"
        assert ranked[0]["final_score"] >= ranked[1]["final_score"]
