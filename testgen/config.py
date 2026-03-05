import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: str = "gpt-4o"
    coverage_target: int = 3
    include_edge_cases: bool = True
    include_mocks: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

def get_config() -> Config:
    return Config()
