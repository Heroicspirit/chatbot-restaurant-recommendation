# Ataraxia — Context-Aware LLM-Assisted Hybrid Restaurant Recommendation Chatbot

A thesis project for Coventry University / Softwarica College.

**Student:** Anubhav Rana Magar  
**Module:** Thesis / Final Year Project

## Overview

Ataraxia is a context-aware hybrid restaurant recommendation system for young adults in Kathmandu. It uses a local LLM (Ollama) for natural language understanding and response generation while keeping all recommendations grounded in a structured, auditable restaurant dataset.

## Architecture

```
User → Chat Interface (React) → FastAPI Backend → Intent Extraction (LLM)
       → Preference Validation → Hybrid Retrieval (Structured + Semantic)
       → Weighted Ranking → Bias-Aware Re-ranking → Grounded Response (LLM)
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama with llama3.2 (or compatible model)

### 1. Install Ollama and Pull Model

```bash
ollama pull llama3.2
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Open Browser

Navigate to `http://localhost:5173`

## Project Structure

```
ataraxia/
├── backend/          # FastAPI application
├── frontend/         # React (Vite) application
├── data/             # Restaurant dataset
├── evaluation/       # Test scenarios and results
├── docs/             # Architecture and methodology docs
└── notebooks/        # Analysis notebooks
```

## Evaluation

The system is evaluated against three baselines using 50+ scenario queries across cuisine, budget, purpose, ambience, dietary, multi-constraint, and edge cases.
