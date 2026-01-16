"""Configuration management for Mirage simulation."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # App settings
    app_name: str = "Mirage Simulation"
    debug: bool = False
    
    # Firm settings
    default_firm_id: int = Field(default=1, ge=1, le=6)
    current_period: int = Field(default=0)
    
    # Data paths
    data_dir: Path = Field(default=Path("data"))
    decisions_file: Optional[Path] = None
    results_file: Optional[Path] = None
    
    # Display settings
    currency: str = "KEUR"
    decimal_places: int = 2
    
    class Config:
        env_prefix = "MIRAGE_"
        env_file = ".env"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the current settings instance."""
    return settings


def update_settings(**kwargs) -> Settings:
    """Update settings with new values."""
    global settings
    current_dict = settings.model_dump()
    current_dict.update(kwargs)
    settings = Settings(**current_dict)
    return settings
