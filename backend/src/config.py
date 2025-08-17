# backend/src/config.py
"""
Конфигурация приложения с правильными настройками БД.
"""

from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Настройки подключения к базе данных PostgreSQL."""

    host: str = Field(default="postgres", description="Хост базы данных")
    port: int = Field(default=5432, description="Порт базы данных")
    name: str = Field(default="kommuna", description="Имя базы данных")
    user: str = Field(default="owner", description="Пользователь БД")
    password: str = Field(default="Gfhjkm123.", description="Пароль БД")

    # Настройки пула подключений
    pool_size: int = Field(default=5, description="Размер пула подключений")
    max_overflow: int = Field(default=10, description="Максимальное количество дополнительных подключений")
    connect_timeout: int = Field(default=60, description="Таймаут подключения в секундах")

    @property
    def url(self) -> str:
        """Генерирует URL подключения к базе данных."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        """Генерирует синхронный URL для Alembic миграций."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = SettingsConfigDict(env_prefix="DB_")


class TelegramSettings(BaseSettings):
    """Настройки для работы с Telegram API."""

    webhook_domain: str = Field(default="https://localhost", description="Домен для webhook URL")
    webhook_secret: str = Field(default="dev-webhook-secret", description="Секрет для webhook безопасности")
    main_bot_token: Optional[str] = Field(None, description="Токен главного бота приложения")

    @property
    def webhook_base_url(self) -> str:
        """Базовый URL для webhooks."""
        return f"{self.webhook_domain}/api/v1/telegram/webhook"

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")


class SecuritySettings(BaseSettings):
    """Настройки безопасности и авторизации."""

    jwt_secret_key: str = Field(
        default="fa11c75be6628d29470f634f78898ebe5672e642766311f5cc3b49698b1eea8f4ff6891486bf61ad006fd03dec7bb255ca9c92958eeddaa2a7f022306def5591",
        description="Секретный ключ для JWT токенов"
    )
    jwt_algorithm: str = Field(default="HS256", description="Алгоритм шифрования JWT")
    jwt_access_token_expire_minutes: int = Field(default=1440, description="Время жизни JWT токена (мин)")
    encryption_key: str = Field(
        default="6c193a5c8ae272bc707b0999633a14d2",
        description="Ключ для шифрования конфиденциальных данных"
    )

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key_length(cls, v: str) -> str:
        """Проверяет, что ключ шифрования имеет правильную длину."""
        if len(v) != 32:
            raise ValueError("Ключ шифрования должен быть длиной 32 символа")
        return v


class AppSettings(BaseSettings):
    """Основные настройки приложения."""

    # Общие настройки
    environment: Literal["development", "production", "testing"] = Field(
        default="development",
        description="Режим работы приложения"
    )
    project_name: str = Field(default="CommunaApp", description="Название проекта")
    api_version: str = Field(default="v1", description="Версия API")

    # Настройки сервера
    host: str = Field(default="0.0.0.0", description="Хост для запуска сервера")
    port: int = Field(default=8000, description="Порт для запуска сервера")

    # Настройки документации
    docs_url: str = Field(default="/docs", description="URL для Swagger документации")

    # Настройки разработки
    debug: bool = Field(default=True, description="Включить отладочный режим")
    reload: bool = Field(default=True, description="Автоперезагрузка при изменении кода")
    show_traceback: bool = Field(default=True, description="Показывать трейсбеки в ответах")

    @property
    def is_development(self) -> bool:
        """Проверяет, запущено ли приложение в режиме разработки."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Проверяет, запущено ли приложение в продакшне."""
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        """Проверяет, запущено ли приложение в тестовом режиме."""
        return self.environment == "testing"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class LoggingSettings(BaseSettings):
    """Настройки логирования."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Уровень логирования"
    )
    format: Literal["json", "text"] = Field(default="json", description="Формат логов")
    file: Optional[str] = Field(default="logs/app.log", description="Файл для записи логов")

    model_config = SettingsConfigDict(env_prefix="LOG_")


class Settings:
    """Главный класс настроек."""

    def __init__(self):
        """Инициализирует все секции настроек."""
        self.app = AppSettings()
        self.database = DatabaseSettings()
        self.security = SecuritySettings()
        self.telegram = TelegramSettings()
        self.logging = LoggingSettings()

    def get_database_url(self) -> str:
        """Возвращает URL подключения к базе данных."""
        return self.database.url


# Создаем глобальный экземпляр настроек
settings = Settings()

# Дополнительные константы для удобства
DATABASE_URL = settings.get_database_url()

# Экспортируем основные настройки
__all__ = [
    "settings",
    "Settings",
    "DATABASE_URL",
]