import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


def is_truthy(value: str) -> bool:
    return value.lower() in ("true", "1", "t")


@dataclass
class DatabaseSettings:
    user: str = os.getenv("POSTGRES_USER")
    password: str = os.getenv("POSTGRES_PASSWORD")
    server: str = os.getenv("POSTGRES_SERVER", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", 5432))
    db_name: str = os.getenv("POSTGRES_DB", "tdd")
    url: str = os.getenv("DB_URL", "tdd")


@dataclass
class LoggingSettings:
    level: str = os.getenv("LOG_LEVEL", "DEBUG")
    file: str = os.getenv("LOG_FILE", "app.log")
    format: str = os.getenv("LOG_FORMAT", "{time} - {level} - {message}")
    rotation: str = os.getenv("LOG_ROTATION", "100 MB")
    retention: str = os.getenv("LOG_RETENTION", "30 days")
    serialization: bool = is_truthy(os.getenv("LOG_SERIALIZATION", "false"))


@dataclass
class MailSettings:
    from_name: str = os.getenv("MAIL_FROM_NAME")
    username: str = os.getenv("MAIL_USERNAME")
    password: str = os.getenv("MAIL_PASSWORD")
    from_email: str = os.getenv("MAIL_FROM")
    port: int = int(os.getenv("MAIL_PORT"))
    server: str = os.getenv("MAIL_SERVER")
    ssl_tls: bool = is_truthy(os.getenv("MAIL_SSL_TLS", "False"))
    starttls: bool = is_truthy(os.getenv("MAIL_STARTTLS", "False"))
    use_credentials: bool = is_truthy(os.getenv("USE_CREDENTIALS", "False"))
    validate_certs: bool = is_truthy(os.getenv("VALIDATE_CERTS", "False"))
    debug: bool = is_truthy(os.getenv("MAIL_DEBUG", "True"))


@dataclass
class AppSettings:
    env: str = os.getenv("APP_ENV", "local")
    host: str = os.getenv("APP_HOST")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    project_name: str = os.getenv("PROJECT_NAME", "Todo")
    project_version: str = os.getenv("PROJECT_VERSION", "1.0.0")
    secret_key: str = os.getenv("SECRET_KEY", "secret")
    algorithm: str = os.getenv("ALGORITHM")
    forget_password_link_expire_minutes: int = int(
        os.getenv("FORGET_PASSWORD_LINK_EXPIRE_MINUTES")
    )


@dataclass
class CorsSettings:
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
    ]
    methods = ["*"]
    headers = ["*"]


@dataclass
class Settings:
    database = DatabaseSettings()
    logging = LoggingSettings()
    mail = MailSettings()
    app = AppSettings()
    cors = CorsSettings()


settings = Settings()
