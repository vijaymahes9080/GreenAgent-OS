"""
Application Configuration for GreenAgent OS
Supports local-first zero-GPU execution, deterministic simulation, and Ollama integration.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "GreenAgent OS"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "greenagent-os-super-secret-dev-key-change-in-prod"
    API_KEY_HEADER_NAME: str = "X-API-Key"
    DEFAULT_API_KEY: str = "ga-dev-test-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./greenagent.db"
    
    # Ollama / Local Inference
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    SIMULATE_INFERENCE_IF_UNAVAILABLE: bool = True
    
    # Datacenter / Energy Modeling Defaults
    DATACENTER_PUE: float = 1.25  # Power Usage Effectiveness
    DEFAULT_REGION: str = "us-east"
    EMISSION_FACTOR_SOURCE: str = "simulated_regional_grid_v1"
    
    # Semantic Cache Defaults
    CACHE_SIMILARITY_THRESHOLD: float = 0.90
    CACHE_DEFAULT_TTL_SECONDS: int = 86400  # 24 hours
    
    # Optimization Weights Default (alpha=energy, beta=carbon, gamma=cost, delta=latency, epsilon=quality_loss)
    OPT_ALPHA: float = 0.25
    OPT_BETA: float = 0.35
    OPT_GAMMA: float = 0.20
    OPT_DELTA: float = 0.10
    OPT_EPSILON: float = 0.10

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
