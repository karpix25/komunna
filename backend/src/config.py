# backend/src/config.py
"""
Конфигурация приложения Kommuna.
Добавлено поле TELEGRAM_MAIN_BOT_TOKEN.
"""

from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    host: str = Field(default="postgres")
    port: int = Field(default=5432)
    name: str = Field(default="kommuna")
    user: str = Field(default="postgres")
    password: str = Field(description="Пароль БД")

    pool_size: int = Field(default=5)
    max_overflow: int = Field(default=10)
    connect_timeout: int = Field(default=60)

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = SettingsConfigDict(env_prefix="DB_")


class TelegramSettings(BaseSettings):
    """
    Настройки для работы с Telegram API.
    Теперь включает TELEGRAM_MAIN_BOT_TOKEN, который использует фабрика сервисов.
    """
    main_bot_token: str = Field(description="Токен главного бота", alias="TELEGRAM_BOT_TOKEN")
    webhook_domain: str = Field(description="Домен для webhook URL", alias="TELEGRAM_WEBHOOK_DOMAIN")

    @property
    def webhook_base_url(self) -> str:
        return f"{self.webhook_domain}/webhook"

    model_config = SettingsConfigDict(env_prefix="", populate_by_name=True)


class SecuritySettings(BaseSettings):
    jwt_secret_key: str = Field(description="Секретный ключ для JWT токенов")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=1440)
    encryption_key: str = Field(description="Ключ для шифрования конфиденциальных данных")

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key_length(cls, v: str) -> str:
        if len(v) != 32:
            raise ValueError("Ключ шифрования должен быть длиной 32 символа")
        return v

    model_config = SettingsConfigDict(env_prefix="")


class AppSettings(BaseSettings):
    environment: Literal["development", "production", "testing"] = Field(default="development")
    project_name: str = Field(default="Kommuna")

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    debug: bool = Field(default=False)
    reload: bool = Field(default=False)

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class LoggingSettings(BaseSettings):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    model_config = SettingsConfigDict(env_prefix="LOG_")


class Settings:
    def __init__(self):
        self.app = AppSettings()
        self.database = DatabaseSettings()
        self.security = SecuritySettings()
        self.telegram = TelegramSettings()
        self.logging = LoggingSettings()


settings = Settings()

__all__ = ["settings", "Settings"]
