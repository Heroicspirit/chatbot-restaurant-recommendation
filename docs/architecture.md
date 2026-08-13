# Ataraxia System Architecture

## High-Level Architecture

```
User → React Frontend (Vite)
         ↓ HTTP POST /chat
       FastAPI Backend
         ↓
       Conversation Manager → Session Context (in-memory)
         ↓
       LLM Intent Extraction (Ollama)
         ↓
       Preference Validator
         ↓
       ┌──────────────────────┐
       │   Hybrid Retrieval   │
       │  ┌────────────────┐  │
       │  │ Structured     │  │  → area, cuisine, budget, dietary filters
       │  │ Filter         │  │
       │  └────────────────┘  │
       │  ┌────────────────┐  │
       │  │ Semantic       │  │  → sentence-transformers + cosine similarity
       │  │ Search Layer   │  │
       │  └────────────────┘  │
       └────────┬─────────────┘
                ↓
       Weighted Ranking Engine
                ↓
       Bias-Aware Re-ranking Layer
                ↓
       Grounded Response Builder (LLM)
                ↓
       Response → Chat Interface
```

## Data Flow

1. User sends natural language query via React chat interface
2. Backend receives query at `/chat` endpoint
3. Session manager loads/creates session state
4. Intent extraction calls Ollama LLM to parse structured preferences
5. If query is too vague, clarification question is returned
6. Preferences merged with session context (multi-turn support)
7. Structured filters applied: area, cuisine, budget, dietary
8. Semantic search computes similarity scores for all restaurants
9. Hybrid retrieval combines structured + semantic results
10. Weighted ranking scores each candidate (7 criteria)
11. Bias-aware re-ranking ensures diversity (best overall, best budget, best vibe)
12. Grounded response generation sends ONLY retrieved data to LLM
13. Hallucination check validates response
14. Response returned to frontend

## Component Responsibilities

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React 18 + Vite | Chat UI with recommendation cards |
| API Server | FastAPI | Request routing, business logic orchestration |
| Database | SQLite | Restaurant data storage |
| LLM Interface | Ollama HTTP API | Intent extraction + response generation |
| Embeddings | sentence-transformers | Semantic search for soft queries |
| Session State | In-memory dict | Multi-turn conversation context |
