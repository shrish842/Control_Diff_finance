from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(
        default="sqlite+pysqlite:///artifacts/controldiff.db",
        alias="DATABASE_URL",
    )

    qdrant_mode: str = Field(default="local", alias="QDRANT_MODE")
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, alias="QDRANT_API_KEY")
    qdrant_local_path: str = Field(default="artifacts/qdrant", alias="QDRANT_LOCAL_PATH")
    qdrant_collection: str = Field(default="controldiff_controls", alias="QDRANT_COLLECTION")

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    use_background_jobs: bool = Field(default=False, alias="USE_BACKGROUND_JOBS")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )

    langfuse_enabled: bool = Field(default=False, alias="LANGFUSE_ENABLED")
    langfuse_public_key: str | None = Field(default=None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = Field(default=None, alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", alias="LANGFUSE_HOST")

    raw_data_dir: str = Field(default="data/raw", alias="RAW_DATA_DIR")
    processed_data_dir: str = Field(default="data/processed", alias="PROCESSED_DATA_DIR")
    synthetic_data_dir: str = Field(default="data/synthetic", alias="SYNTHETIC_DATA_DIR")
    golden_data_dir: str = Field(default="data/goldens", alias="GOLDEN_DATA_DIR")

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def artifacts_dir(self) -> Path:
        return self.project_root / "artifacts"

    @property
    def resolved_raw_data_dir(self) -> Path:
        return self.project_root / self.raw_data_dir

    @property
    def resolved_processed_data_dir(self) -> Path:
        return self.project_root / self.processed_data_dir

    @property
    def resolved_synthetic_data_dir(self) -> Path:
        return self.project_root / self.synthetic_data_dir

    @property
    def resolved_golden_data_dir(self) -> Path:
        return self.project_root / self.golden_data_dir

    @property
    def resolved_qdrant_local_path(self) -> Path:
        return self.project_root / self.qdrant_local_path

    @property
    def resolved_database_url(self) -> str:
        sqlite_prefixes = ("sqlite+pysqlite:///", "sqlite:///")
        for prefix in sqlite_prefixes:
            if self.database_url.startswith(prefix):
                raw_path = Path(self.database_url.removeprefix(prefix))
                db_path = raw_path if raw_path.is_absolute() else self.project_root / raw_path
                return f"{prefix}{db_path.as_posix()}"
        return self.database_url

    def ensure_runtime_directories(self) -> None:
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_processed_data_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_synthetic_data_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_golden_data_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_qdrant_local_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
