from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Using the new SettingsConfigDict instead of the deprecated Config class
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=False,
        protected_namespaces=()
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
