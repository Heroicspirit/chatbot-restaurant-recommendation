from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3.2"
    llm_temperature: float = 0.1
    database_url: str = "sqlite:///./ataraxia.db"
    host: str = "0.0.0.0"
    port: int = 8000
    embedding_model: str = "all-MiniLM-L6-v2"
    data_path: str = str(Path(__file__).parent.parent / "data" / "processed" / "restaurants_clean.csv")

settings = Settings()
