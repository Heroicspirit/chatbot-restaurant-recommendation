import pytest
from services.response_generation import _hallucination_check


SAMPLE_RECOMMENDATIONS = [
    {"restaurant_id": "R001", "name": "Momo Hut", "area": "Thamel"},
    {"restaurant_id": "R002", "name": "The Korean Bowl", "area": "Thamel"},
    {"restaurant_id": "R003", "name": "Patan Cafe", "area": "Patan"},
]


class TestHallucination:
    def test_response_with_dataset_restaurants_passes(self):
        response = "I recommend Momo Hut in Thamel and Patan Cafe in Patan."
        assert _hallucination_check(response, SAMPLE_RECOMMENDATIONS) is True

    def test_response_with_invented_restaurant_fails(self):
        response = "I recommend Momo Hut and The Fake Restaurant that doesn't exist."
        result = _hallucination_check(response, SAMPLE_RECOMMENDATIONS)
        assert result is False

    def test_empty_response_passes(self):
        assert _hallucination_check("", SAMPLE_RECOMMENDATIONS) is True

    def test_response_only_mentions_dataset_items(self):
        response = "Based on your preferences, here are The Korean Bowl and Momo Hut."
        assert _hallucination_check(response, SAMPLE_RECOMMENDATIONS) is True

    def test_lowercase_mention_passes(self):
        response = "You might like momo hut or patan cafe."
        assert _hallucination_check(response, SAMPLE_RECOMMENDATIONS) is True
