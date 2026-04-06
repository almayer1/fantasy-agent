from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "llama3.2"

    # Sleeper
    sleeper_base_url: str = "https://api.sleeper.app/v1"

    # Odds
    odds_api_key: str

    # Tavily
    tavily_api_key: str

    # Rules
    max_iterations: int = 10

    model_config = {"env_file": ".env"}

settings = Settings()