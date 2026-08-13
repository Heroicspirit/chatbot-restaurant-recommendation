FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATABASE_URL=sqlite:///./ataraxia.db
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
