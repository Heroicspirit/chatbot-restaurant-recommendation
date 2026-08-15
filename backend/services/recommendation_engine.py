import pandas as pd
from typing import Optional
from config import settings
from services.ranking import rank_candidates
from services.semantic_search import index_restaurants, search_similar
from services.bias_reranking import bias_aware_rerank


class RecommendationEngine:
    def __init__(self):
        self._restaurants: list[dict] = []
        self._df: Optional[pd.DataFrame] = None
        self._loaded = False

    def load_data(self):
        self._df = pd.read_csv(settings.data_path)
        self._restaurants = self._df.to_dict(orient="records")
        index_restaurants(self._restaurants)
        self._loaded = True

    def get_dataframe(self):
        if not self._loaded:
            self.load_data()
        return self._df

    def get_all_restaurants(self):
        if not self._loaded:
            self.load_data()
        return self._restaurants

    def _get_available_cuisines(self) -> set:
        all_cuisines = set()
        for r in self._restaurants:
            for c in r.get("cuisine", "").split(","):
                all_cuisines.add(c.strip().lower())
        return all_cuisines

    def _get_available_areas(self) -> set:
        return {r.get("area", "").lower() for r in self._restaurants if r.get("area")}

    def get_areas_list(self) -> list[str]:
        return sorted({r["area"] for r in self.get_all_restaurants() if r.get("area")})

    def get_cuisines_list(self) -> list[str]:
        cuisines = set()
        for r in self.get_all_restaurants():
            for c in r.get("cuisine", "").split(","):
                cuisines.add(c.strip())
        return sorted(cuisines)

    def get_all_cuisines_in_area(self, area: str) -> list[str]:
        df = self.get_dataframe()
        area_df = df[df["area"].str.lower() == area.lower()]
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

    def get_areas_with_cuisine(self, cuisine: str) -> list[str]:
        df = self.get_dataframe()
        matches = df[
            df["cuisine"].str.lower().str.contains(cuisine.lower(), na=False)
        ]
        return sorted(matches["area"].dropna().unique().tolist())

    def structured_filter(self, preferences: dict) -> list[dict]:
        results = self._restaurants.copy()

        if preferences.get("location"):
            loc = preferences["location"].lower()
            results = [r for r in results if r.get("area", "").lower() == loc]

        if preferences.get("cuisine"):
            preferred = [c.lower() for c in preferences["cuisine"]]
            filtered = []
            for r in results:
                rest_cuisines = [c.strip().lower() for c in r.get("cuisine", "").split(",")]
                if any(p in rc for rc in rest_cuisines for p in preferred):
                    filtered.append(r)
            results = filtered

        if preferences.get("budget_max"):
            results = [
                r for r in results
                if r.get("avg_price_per_person") and r["avg_price_per_person"] <= preferences["budget_max"]
            ]

        if preferences.get("price_level"):
            pl = preferences["price_level"].lower()
            results = [r for r in results if r.get("price_level", "").lower() == pl]

        # Note: Dietary filtering is now handled by ranking scores, not hard filtering
        # This allows showing restaurants with both options while prioritizing matches

        return results

    def hybrid_retrieve(self, user_message: str, preferences: dict) -> list[dict]:
        if not self._loaded:
            self.load_data()

        requested_cuisines = preferences.get("cuisine", [])
        if requested_cuisines:
            available = self._get_available_cuisines()
            unknown = [c for c in requested_cuisines if c.lower() not in available]
            if unknown:
                return []

        requested_location = preferences.get("location")
        if requested_location:
            available_areas = self._get_available_areas()
            if requested_location.lower() not in available_areas:
                return []

        structured_results = self.structured_filter(preferences)

        semantic_scores: dict[str, float] = {}
        if user_message:
            semantic_scores = search_similar(user_message, top_k=20)

        if not structured_results:
            return []

        ranked = rank_candidates(structured_results, preferences, semantic_scores or None)
        return ranked[:10]

    def recommend(self, user_message: str, preferences: dict, top_k: int = 3) -> list[dict]:
        candidates = self.hybrid_retrieve(user_message, preferences)
        if not candidates:
            return []
        return bias_aware_rerank(candidates, top_k=top_k)

    def get_cheapest_price(self) -> int:
        prices = [r.get("avg_price_per_person") for r in self.get_all_restaurants() if r.get("avg_price_per_person")]
        return min(prices) if prices else 0


recommendation_engine = RecommendationEngine()
