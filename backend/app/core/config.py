from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "Genvicure Treasury MIS"
    APP_ENV: str = "development"

    DATABASE_URL: str
    SECRET_KEY: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:3000"

    # Microsoft Graph / OneDrive integration
    MS_TENANT_ID: str | None = None
    MS_CLIENT_ID: str | None = None
    MS_CLIENT_SECRET: str | None = None
    MS_DRIVE_ID: str | None = None
    MS_FILE_ID: str | None = None

    MS_SYNC_ENABLED: bool = False
    MS_SYNC_INTERVAL_MINUTES: int = 5

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()