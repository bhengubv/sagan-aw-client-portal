"""Application configuration. Secrets come from the environment, never code (spec 13)."""
import os

from sqlalchemy.pool import StaticPool


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    # Railway volume path in production; local file by default (spec 6.3).
    _db_path = os.environ.get("RAILWAY_DATABASE_PATH",
                              os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                           "instance", "aw_portal.db"))
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{_db_path}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 60 * 60  # 1 hour idle window (spec 8.6)
    CANVA_API_KEY = os.environ.get("CANVA_API_KEY")  # only if Canva export is enabled

    # Public base URL for client-facing links (onboarding, expense worksheet).
    PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://127.0.0.1:5000")

    # Email (spec 8.10). If SMTP_HOST is unset, email is recorded to the Outbox
    # (viewable in-app) rather than sent — functional without a live mail server.
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    SMTP_FROM = os.environ.get("SMTP_FROM", "no-reply@awportal.local")
    SMTP_STARTTLS = os.environ.get("SMTP_STARTTLS", "1") == "1"

    # AI (spec 12). Optional: if ANTHROPIC_API_KEY is set the extraction agent can use
    # the LLM; without it, the deterministic extractor runs (no feature is disabled).
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    ANTHROPIC_BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    LLM_MODEL = os.environ.get("LLM_MODEL", "claude-opus-4-8")


class TestConfig(Config):
    TESTING = True
    # One shared in-memory connection so data persists across requests within a test.
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret"
    # Hermetic: never touch real external services from tests regardless of the env.
    ANTHROPIC_API_KEY = None
    SMTP_HOST = None
    PUBLIC_BASE_URL = "http://testserver"
