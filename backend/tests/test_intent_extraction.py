import pytest
from services.intent_extraction import (
    _fallback_keyword_extraction,
    normalize_preferences,
    validate_intent,
)


class TestIntentExtraction:
    def test_fallback_extracts_location(self):
        result = _fallback_keyword_extraction("Suggest me a restaurant in Thamel")
        assert result["location"] == "Thamel"

    def test_fallback_extracts_location_and_cuisine(self):
        result = _fallback_keyword_extraction("Korean restaurant near Patan")
        assert result["location"] == "Patan"
        assert "korean" in result["cuisine"]

    def test_fallback_extracts_budget(self):
        result = _fallback_keyword_extraction("Restaurant under Rs. 1000 in Baneshwor")
        assert result["budget_max"] == 1000

    def test_fallback_vague_query(self):
        result = _fallback_keyword_extraction("Suggest me something nice")
        assert result["clarification_required"] is True

    def test_validate_intent_invalid_location(self):
        intent = {"location": "Tokyo"}
        result = validate_intent(intent)
        assert result["location"] is None

    def test_normalize_cheap_to_low_price(self):
        intent = {"location": "Thamel", "cuisine": ["Korean"]}
        result = normalize_preferences(intent, original_message="I want cheap food")
        assert result["price_level"] == "low"

    def test_normalize_study_purpose(self):
        intent = {"location": "Patan"}
        result = normalize_preferences(intent, original_message="I need to study")
        assert result["purpose"] == "study"

    def test_fallback_veg_restaurant(self):
        result = _fallback_keyword_extraction("veg restaurant in Patan")
        assert result["dietary"] == "vegetarian"

    def test_fallback_veg_only(self):
        result = _fallback_keyword_extraction("veg only restaurant in Patan")
        assert result["dietary"] == "vegetarian_only"

    def test_fallback_non_veg(self):
        result = _fallback_keyword_extraction("non veg restaurant in Patan")
        assert result["dietary"] == "non_vegetarian"

    def test_fallback_non_veg_only(self):
        result = _fallback_keyword_extraction("non veg only restaurant in Patan")
        assert result["dietary"] == "non_vegetarian_only"

    def test_normalize_veg_only(self):
        intent = {"location": "Patan"}
        result = normalize_preferences(intent, original_message="veg only restaurant in Patan")
        assert result["dietary"] == "vegetarian_only"

    def test_normalize_non_veg_only(self):
        intent = {"location": "Patan"}
        result = normalize_preferences(intent, original_message="non veg only restaurant in Patan")
        assert result["dietary"] == "non_vegetarian_only"
