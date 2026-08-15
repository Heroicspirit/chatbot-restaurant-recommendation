import json
import csv
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db, SessionLocal
from models import Restaurant
from schemas import ChatRequest, ChatResponse, IntentResult, RestaurantResponse
from services.intent_extraction import extract_intent, COMMANDS
from services.recommendation_engine import recommendation_engine
from services.response_generation import generate_response
from services.session_manager import session_manager
from services.ranking import rank_candidates
from services.bias_reranking import bias_aware_rerank
import pandas as pd


@asynccontextmanager
async def lifespan(app):
    init_db()
    _seed_database()
    recommendation_engine.load_data()
    yield


app = FastAPI(title="Ataraxia - Restaurant Recommendation System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _seed_database():
    from config import settings
    df = pd.read_csv(settings.data_path)
    db = SessionLocal()
    try:
        existing = db.query(Restaurant).count()
        if existing > 0:
            return
        for _, row in df.iterrows():
            restaurant = Restaurant(
                restaurant_id=row["restaurant_id"],
                name=row["name"],
                area=row["area"],
                address=row.get("address", ""),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                cuisine=row["cuisine"],
                price_level=row["price_level"],
                avg_price_per_person=row["avg_price_per_person"],
                rating=row["rating"],
                review_count=row.get("review_count", 0),
                veg_available=bool(row["veg_available"]),
                serves_both=bool(row.get("serves_both", False)),
                ambience_tags=row.get("ambience_tags", ""),
                suitable_for=row.get("suitable_for", ""),
                opening_hours=row.get("opening_hours", ""),
                source_url=row.get("source_url", ""),
                description=row.get("description", ""),
                data_confidence=row.get("data_confidence", "medium"),
            )
            db.add(restaurant)
        db.commit()
    finally:
        db.close()


def build_active_filters(preferences: dict) -> dict:
    return {
        "location": preferences.get("location"),
        "cuisine": preferences.get("cuisine"),
        "budget_max": preferences.get("budget_max"),
        "purpose": preferences.get("purpose"),
        "dietary": preferences.get("dietary"),
        "ambience": preferences.get("ambience", []),
    }


def determine_overall_match_status(recommendations: list) -> str:
    if not recommendations:
        return "none"
    if all(r.get("match_type") == "exact" for r in recommendations):
        return "exact"
    return "closest"


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    session = session_manager.get_or_create(request.session_id)

    intent_data = extract_intent(request.message)
    command = intent_data.pop("command", None)
    is_greeting = intent_data.pop("greeting", None)
    restaurant_name = intent_data.pop("restaurant_name", None)
    restaurant_id = intent_data.pop("restaurant_id", None)

    # Check for follow-up questions about last restaurant
    t = request.message.lower().strip()
    is_followup = any(word in t for word in ["does it", "is it", "has it", "what about", "tell me about"])
    if is_followup and session.previous_recommendations:
        last_restaurant_id = session.previous_recommendations[-1]
        db = SessionLocal()
        try:
            restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == last_restaurant_id).first()
            if restaurant:
                # Answer specific questions about the restaurant
                if "veg" in t:
                    veg_status = "Yes, vegetarian options are available" if restaurant.veg_available else "No vegetarian options available"
                    return ChatResponse(
                        session_id=session.session_id,
                        intent=IntentResult(),
                        recommendations=[],
                        response=f"{restaurant.name}: {veg_status}.",
                        match_status="none",
                        active_filters={},
                    )
        finally:
            db.close()

    if is_greeting:
        return ChatResponse(
            session_id=session.session_id,
            intent=IntentResult(),
            recommendations=[],
            response=(
                "Hi! I can help you find restaurants in Kathmandu by area, cuisine, budget, or purpose.\n\n"
                "Try:\n"
                "· Korean in Thamel\n"
                "· Quiet cafe in Patan under Rs. 1000\n"
                "· Vegetarian food near Boudha\n\n"
                "You can also type a restaurant name directly, or type 'areas', 'cuisines', or 'show all'."
            ),
            match_status="none",
            active_filters={},
        )

    if restaurant_name and restaurant_id:
        # User typed a specific restaurant name - return that restaurant
        db = SessionLocal()
        try:
            restaurant = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()
            if restaurant:
                rec_response = RestaurantResponse(
                    restaurant_id=restaurant.restaurant_id,
                    name=restaurant.name,
                    area=restaurant.area,
                    cuisine=restaurant.cuisine,
                    price_level=restaurant.price_level,
                    avg_price_per_person=restaurant.avg_price_per_person,
                    rating=restaurant.rating,
                    veg_available=restaurant.veg_available,
                    ambience_tags=restaurant.ambience_tags,
                    suitable_for=restaurant.suitable_for,
                    description=restaurant.description,
                    final_score=1.0,
                    matched_factors=["exact restaurant name match"],
                    reason=f"You asked about {restaurant.name}. Here are the details:",
                    match_type="exact",
                    match_status="exact",
                )
                return ChatResponse(
                    session_id=session.session_id,
                    intent=IntentResult(**intent_data),
                    recommendations=[rec_response],
                    response=f"Here are the details for {restaurant.name}:",
                    match_status="exact",
                    active_filters=build_active_filters(intent_data),
                    result_count=1,
                )
        finally:
            db.close()

    if command == "reset":
        session_manager.reset_session(request.session_id)
        return ChatResponse(
            session_id=session.session_id,
            intent=IntentResult(),
            recommendations=[],
            response="Filters cleared. Start a new search by telling me what you're looking for.",
            match_status="none",
            active_filters={},
        )

    if command == "areas":
        areas = recommendation_engine.get_areas_list()
        return ChatResponse(
            session_id=session.session_id,
            intent=IntentResult(),
            recommendations=[],
            response="Available areas in Kathmandu:\n" + "\n".join(f"· {a}" for a in areas),
            match_status="none",
            active_filters=build_active_filters(session.to_dict()),
        )

    if command == "cuisines":
        cuisines = recommendation_engine.get_cuisines_list()
        return ChatResponse(
            session_id=session.session_id,
            intent=IntentResult(),
            recommendations=[],
            response="Available cuisines:\n" + "\n".join(f"· {c}" for c in cuisines),
            match_status="none",
            active_filters=build_active_filters(session.to_dict()),
        )

    if command == "show_all":
        session_state = session.to_dict()
        preferences = _build_preferences_from_session(session_state)

        recommendations = recommendation_engine.recommend("", preferences, top_k=request.top_k) if preferences else []
        if not recommendations and not preferences:
            all_restaurants = recommendation_engine.get_all_restaurants()
            recommendations = bias_aware_rerank(
                rank_candidates(all_restaurants, {}),
                top_k=request.top_k
            )

        rec_responses = _build_rec_responses(recommendations)
        rec_dicts = [r.model_dump() for r in rec_responses]
        response_text = generate_response(request.message, preferences, rec_dicts)
        match_status = determine_overall_match_status(rec_dicts)

        return ChatResponse(
            session_id=session.session_id,
            intent=IntentResult(),
            recommendations=rec_responses,
            response=response_text,
            match_status=match_status,
            active_filters=build_active_filters(preferences),
            result_count=len(rec_responses),
        )

    if command == "more":
        session_state = session.to_dict()
        preferences = _build_preferences_from_session(session_state)
        recommendations = recommendation_engine.recommend(request.message, preferences, top_k=request.top_k)

        if not recommendations:
            return ChatResponse(
                session_id=session.session_id,
                intent=IntentResult(),
                recommendations=[],
                response="No more results available. Try a different query or adjust your filters.",
                match_status="none",
                active_filters=build_active_filters(preferences),
            )

        rec_responses = _build_rec_responses(recommendations)
        rec_dicts = [r.model_dump() for r in rec_responses]
        response_text = generate_response(request.message, preferences, rec_dicts)
        match_status = determine_overall_match_status(rec_dicts)

        session.add_recommendations([r.restaurant_id for r in rec_responses])

        return ChatResponse(
            session_id=session.session_id,
            intent=IntentResult(),
            recommendations=rec_responses,
            response=response_text,
            match_status=match_status,
            active_filters=build_active_filters(preferences),
            result_count=len(rec_responses),
        )

    if command == "best":
        session_state = session.to_dict()
        preferences = _build_preferences_from_session(session_state)
        recommendations = recommendation_engine.recommend(request.message, preferences, top_k=request.top_k)
        recommendations.sort(key=lambda x: x.get("rating", 0), reverse=True)

        rec_responses = _build_rec_responses(recommendations)
        rec_dicts = [r.model_dump() for r in rec_responses]
        response_text = generate_response(request.message, preferences, rec_dicts)
        match_status = determine_overall_match_status(rec_dicts)

        session.add_recommendations([r.restaurant_id for r in rec_responses])

        return ChatResponse(
            session_id=session.session_id,
            intent=IntentResult(),
            recommendations=rec_responses,
            response=response_text,
            match_status=match_status,
            active_filters=build_active_filters(preferences),
            result_count=len(rec_responses),
        )

    intent = IntentResult(**intent_data)

    merged_preferences = session.merge_with_intent(intent_data)

    has_own_prefs = bool(
        intent_data.get("location")
        or intent_data.get("cuisine")
        or intent_data.get("budget_max")
        or intent_data.get("price_level")
        or intent_data.get("purpose")
        or intent_data.get("ambience")
        or intent_data.get("dietary")
    )

    is_vague = intent.clarification_required and not merged_preferences.get("location") and not merged_preferences.get("cuisine")

    if is_vague:
        return ChatResponse(
            session_id=session.session_id,
            intent=intent,
            recommendations=[],
            response=(
                "Hi! I can help you find restaurants in Kathmandu by area, cuisine, budget, or purpose.\n\n"
                "Try:\n"
                "· Korean in Thamel\n"
                "· Quiet cafe in Patan under Rs. 1000\n"
                "· Vegetarian food near Boudha\n\n"
                "You can also type 'areas', 'cuisines', or 'show all'."
            ),
            clarification_question="",
            match_status="none",
            active_filters={},
        )

    session.update(merged_preferences)

    preferences_for_search = {k: v for k, v in merged_preferences.items()
                              if k not in ("clarification_required", "missing_fields", "greeting")}

    recommendations = recommendation_engine.recommend(
        request.message, preferences_for_search, top_k=request.top_k
    )

    rec_responses = _build_rec_responses(recommendations)
    rec_dicts = [r.model_dump() for r in rec_responses]

    restaurant_df = recommendation_engine.get_dataframe()
    response_text = generate_response(request.message, preferences_for_search, rec_dicts, restaurant_df)

    session.add_recommendations([r.restaurant_id for r in rec_responses])

    match_status = determine_overall_match_status(rec_dicts)
    active_filters = build_active_filters(preferences_for_search)

    return ChatResponse(
        session_id=session.session_id,
        intent=intent,
        recommendations=rec_responses,
        response=response_text,
        match_status=match_status,
        active_filters=active_filters,
        result_count=len(rec_responses),
    )


def _build_rec_responses(recommendations: list) -> list[RestaurantResponse]:
    rec_responses = []
    for rec in recommendations:
        rec_responses.append(RestaurantResponse(
            restaurant_id=rec["restaurant_id"],
            name=rec["name"],
            area=rec.get("area", ""),
            cuisine=rec.get("cuisine", ""),
            price_level=rec.get("price_level", ""),
            avg_price_per_person=rec.get("avg_price_per_person", 0),
            rating=rec.get("rating", 0.0),
            veg_available=rec.get("veg_available", False),
            serves_both=rec.get("serves_both", False),
            ambience_tags=rec.get("ambience_tags", ""),
            suitable_for=rec.get("suitable_for", ""),
            description=rec.get("description", ""),
            final_score=rec.get("final_score", 0.0),
            matched_factors=rec.get("matched_factors", []),
            missing_factors=rec.get("missing_factors", []),
            reason=rec.get("reason", ""),
            match_type=rec.get("match_type", "exact"),
            match_status=rec.get("match_status", "exact"),
        ))
    return rec_responses


def _build_preferences_from_session(session_state: dict) -> dict:
    prefs = {}
    if session_state.get("last_location"):
        prefs["location"] = session_state["last_location"]
    if session_state.get("last_cuisine"):
        prefs["cuisine"] = session_state["last_cuisine"]
    if session_state.get("last_budget_max"):
        prefs["budget_max"] = session_state["last_budget_max"]
    if session_state.get("last_price_level"):
        prefs["price_level"] = session_state["last_price_level"]
    if session_state.get("last_purpose"):
        prefs["purpose"] = session_state["last_purpose"]
    if session_state.get("last_ambience"):
        prefs["ambience"] = session_state["last_ambience"]
    if session_state.get("dietary"):
        prefs["dietary"] = session_state["dietary"]
    return prefs


@app.get("/restaurants")
def list_restaurants():
    db = SessionLocal()
    try:
        restaurants = db.query(Restaurant).all()
        return [
            {
                "restaurant_id": r.restaurant_id,
                "name": r.name,
                "area": r.area,
                "cuisine": r.cuisine,
                "price_level": r.price_level,
                "avg_price_per_person": r.avg_price_per_person,
                "rating": r.rating,
            }
            for r in restaurants
        ]
    finally:
        db.close()


@app.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: str):
    db = SessionLocal()
    try:
        r = db.query(Restaurant).filter(Restaurant.restaurant_id == restaurant_id).first()
        if not r:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return {
            "restaurant_id": r.restaurant_id,
            "name": r.name,
            "area": r.area,
            "address": r.address,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "cuisine": r.cuisine,
            "price_level": r.price_level,
            "avg_price_per_person": r.avg_price_per_person,
            "rating": r.rating,
            "review_count": r.review_count,
            "veg_available": r.veg_available,
            "ambience_tags": r.ambience_tags,
            "suitable_for": r.suitable_for,
            "opening_hours": r.opening_hours,
            "description": r.description,
            "data_confidence": r.data_confidence,
        }
    finally:
        db.close()


@app.post("/recommend")
def recommend_raw(payload: dict):
    preferences = payload.get("preferences", {})
    message = payload.get("message", "")
    candidates = recommendation_engine.hybrid_retrieve(message, preferences)
    return {"candidates": candidates[:10]}


class EvaluateScenarioRequest(BaseModel):
    query: str
    expected_location: str = ""
    expected_cuisine: str = ""


@app.post("/evaluate/scenario")
def evaluate_scenario(request: EvaluateScenarioRequest):
    intent_data = extract_intent(request.query)
    preferences = {k: v for k, v in intent_data.items()
                   if k not in ("clarification_required", "missing_fields", "command")}
    candidates = recommendation_engine.hybrid_retrieve(request.query, preferences)
    ranked = rank_candidates(candidates, preferences)
    reranked = bias_aware_rerank(ranked, top_k=3)
    return {
        "query": request.query,
        "intent": intent_data,
        "candidate_count": len(candidates),
        "top_recommendations": reranked[:3],
    }


@app.post("/evaluate/batch")
def evaluate_batch():
    scenario_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "evaluation", "scenario_queries.csv")
    results = []
    if not os.path.exists(scenario_path):
        return {"error": "scenario_queries.csv not found", "results": []}
    with open(scenario_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            intent_data = extract_intent(row["query"])
            preferences = {k: v for k, v in intent_data.items()
                           if k not in ("clarification_required", "missing_fields", "command")}
            candidates = recommendation_engine.hybrid_retrieve(row["query"], preferences)
            ranked = rank_candidates(candidates, preferences)
            reranked = bias_aware_rerank(ranked, top_k=3)
            results.append({
                "query_id": row["query_id"],
                "query": row["query"],
                "category": row["category"],
                "intent": intent_data,
                "recommendation_count": len(reranked),
                "recommendations": [r["name"] for r in reranked[:3]],
            })
    return {"total": len(results), "results": results}


@app.get("/health")
def health():
    return {"status": "ok", "system": "Ataraxia"}


@app.get("/dataset/stats")
def dataset_stats():
    restaurants = recommendation_engine.get_all_restaurants()
    areas = recommendation_engine.get_areas_list()
    cuisines = recommendation_engine.get_cuisines_list()
    ratings = [r.get("rating", 0) for r in restaurants if r.get("rating")]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
    return {
        "total_restaurants": len(restaurants),
        "total_areas": len(areas),
        "total_cuisines": len(cuisines),
        "avg_rating": avg_rating,
    }


if __name__ == "__main__":
    import uvicorn
    from config import settings
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
