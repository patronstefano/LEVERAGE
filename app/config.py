import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()

DEFAULT_SECRET_KEY = "a0f99bb52dfc4e07834c0c5bc1f56c9e7b6f6c4c7ed44d92a122d9c7a4f2b2d0"


@dataclass(frozen=True)
class Settings:
    app_env: str = os.environ.get("APP_ENV", "development")
    database_url: str = os.environ.get("DATABASE_URL", "sqlite:///./leverage.db")
    secret_key: str = os.environ.get(
        "SECRET_KEY",
        DEFAULT_SECRET_KEY,
    )
    access_token_expire_minutes: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    frontend_base_url: str = os.environ.get("FRONTEND_BASE_URL", "http://localhost:3000")
    cors_origins: str = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://localhost:5174,"
        "http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:5174",
    )
    email_token_expire_minutes: int = int(os.environ.get("EMAIL_TOKEN_EXPIRE_MINUTES", "30"))
    password_reset_expire_minutes: int = int(os.environ.get("PASSWORD_RESET_EXPIRE_MINUTES", "30"))
    auth_email_cooldown_seconds: int = int(os.environ.get("AUTH_EMAIL_COOLDOWN_SECONDS", "60"))
    max_login_attempts: int = int(os.environ.get("MAX_LOGIN_ATTEMPTS", "5"))
    login_lock_minutes: int = int(os.environ.get("LOGIN_LOCK_MINUTES", "15"))
    smtp_host: Optional[str] = os.environ.get("SMTP_HOST")
    smtp_port: int = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user: Optional[str] = os.environ.get("SMTP_USER")
    smtp_password: Optional[str] = os.environ.get("SMTP_PASSWORD")
    email_from: Optional[str] = os.environ.get("EMAIL_FROM") or os.environ.get("SMTP_USER")
    ai_suggestions_provider: str = os.environ.get("AI_SUGGESTIONS_PROVIDER", "disabled")
    openai_api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
    openai_base_url: str = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.environ.get("OPENAI_MODEL", "gpt-5")
    ai_suggestions_timeout_seconds: float = float(os.environ.get("AI_SUGGESTIONS_TIMEOUT_SECONDS", "30"))
    world_gymnastics_timeout_seconds: float = float(os.environ.get("WORLD_GYMNASTICS_TIMEOUT_SECONDS", "10"))


settings = Settings()


def get_cors_origins() -> list[str]:
    return [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]


def validate_runtime_settings() -> None:
    if settings.app_env.lower() in {"production", "staging"} and settings.secret_key == DEFAULT_SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be set in production-like environments")

    if settings.app_env.lower() == "development" and settings.secret_key == DEFAULT_SECRET_KEY:
        print("[LEVERAGE] Using development fallback SECRET_KEY. Set SECRET_KEY in .env for safer local usage.")

    if settings.app_env.lower() in {"production", "staging"}:
        if not all((settings.smtp_host, settings.smtp_user, settings.smtp_password, settings.email_from)):
            raise RuntimeError("SMTP settings must be configured in production-like environments")
        if not settings.frontend_base_url.lower().startswith("https://"):
            raise RuntimeError("FRONTEND_BASE_URL must use HTTPS in production-like environments")
