from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI
import os

# Load .env file
load_dotenv("src/.env")

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Using the new SettingsConfigDict instead of the deprecated Config class
    model_config = SettingsConfigDict(
        env_file="src/.env",
        env_file_encoding='utf-8',
        case_sensitive=False,
        protected_namespaces=()
    )

    @property
    def openai_client(self) -> OpenAI:
        return OpenAI(
            api_key=self.openai_api_key,
        )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

@lru_cache()
def get_openai_client() -> OpenAI:
    settings = get_settings()
    return settings.openai_client
