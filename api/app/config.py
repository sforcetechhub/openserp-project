from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from the repo root when running uvicorn locally from /api.
_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
_API_ENV = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=tuple(str(p) for p in (_ROOT_ENV, _API_ENV) if p.exists()),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openserp_base_url: str = "http://localhost:7000"
    openserp_timeout: float = 120.0
    api_key: str = ""
    port: int = 8000
    startup_retries: int = 30
    startup_retry_delay: float = 2.0

    @property
    def auth_required(self) -> bool:
        return bool(self.api_key)


settings = Settings()
