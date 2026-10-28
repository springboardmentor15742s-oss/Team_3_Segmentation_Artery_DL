from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/arterysegmentation_db"
    secret_key: str = "development-only-change-this-secret-before-deployment"
    access_token_expire_minutes: int = 60
    upload_dir: str = "uploads"
    report_dir: str = "reports"
    max_upload_size_mb: int = 100
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        return path.resolve() if path.is_absolute() else (BASE_DIR / path).resolve()

    @property
    def report_path(self) -> Path:
        path = Path(self.report_dir)
        return path.resolve() if path.is_absolute() else (BASE_DIR / path).resolve()

    @property
    def allowed_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
