from config import settings
import numpy as np
from typing import Optional

_model: Optional[any] = None
_embeddings: dict[str, np.ndarray] = {}
_restaurant_texts: dict[str, str] = {}


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def build_embedding_text(restaurant: dict) -> str:
    return (
        f"Restaurant Name: {restaurant.get('name', '')}. "
        f"Area: {restaurant.get('area', '')}. "
        f"Cuisine: {restaurant.get('cuisine', '')}. "
        f"Ambience: {restaurant.get('ambience_tags', '')}. "
        f"Suitable for: {restaurant.get('suitable_for', '')}. "
        f"Description: {restaurant.get('description', '')}."
    )


def index_restaurants(restaurants: list[dict]):
    global _embeddings, _restaurant_texts
    model = _get_model()
    _restaurant_texts = {}
    texts = []
    ids = []
    for r in restaurants:
        text = build_embedding_text(r)
        _restaurant_texts[r["restaurant_id"]] = text
        texts.append(text)
        ids.append(r["restaurant_id"])
    embeddings = model.encode(texts, show_progress_bar=False)
    for rid, emb in zip(ids, embeddings):
        _embeddings[rid] = emb


def search_similar(query: str, top_k: int = 20) -> dict[str, float]:
    if not _embeddings:
        return {}
    model = _get_model()
    query_emb = model.encode(query)
    scores = {}
    for rid, emb in _embeddings.items():
        sim = float(np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb)))
        scores[rid] = max(0, sim)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return dict(sorted_scores[:top_k])
