import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    OPENAI_API_KEY: str = Field(default="")

    PGHOST: str = Field()
    PGPORT: int = Field(default=5432)
    PGUSER: str = Field()
    PGPASSWORD: str = Field()
    PGDATABASE: str = Field()

    MINIO_ENDPOINT: str = Field(default="minio:9000")
    MINIO_ROOT_USER: str = Field()
    MINIO_ROOT_PASSWORD: str = Field()
    MINIO_BUCKET: str = Field(default="docs")
