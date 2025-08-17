"""
Конфигурация приложения.

Этот файл отвечает за загрузку и валидацию всех настроек приложения
из переменных окружения. Использует Pydantic для автоматической валидации.
"""

from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Настройки подключения к базе данных PostgreSQL."""

    host: str = Field(default="localhost", description="Хост базы данных")
    port: int = Field(default=5432, description="Порт базы данных")
    name: str = Field(default="communaapp", description="Имя базы данных")
    user: str = Field(default="postgres", description="Пользователь БД")
    password: str = Field(description="Пароль БД")

    # Настройки пула подключений
    pool_size: int = Field(default=20, description="Размер пула подключений")
    max_overflow: int = Field(default=30, description="Максимальное количество дополнительных подключений")
    connect_timeout: int = Field(default=30, description="Таймаут подключения в секундах")

    @property
    def url(self) -> str:
        """Генерирует URL подключения к базе данных."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        """Генерирует синхронный URL для Alembic миграций."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = SettingsConfigDict(env_prefix="DB_")


class RedisSettings(BaseSettings):
    """Настройки подключения к Redis."""

    url: str = Field(default="redis://localhost:6379/0", description="URL подключения к Redis")
    cache_ttl: int = Field(default=3600, description="Время жизни кэша по умолчанию (сек)")

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class SecuritySettings(BaseSettings):
    """Настройки безопасности и авторизации."""

    jwt_secret_key: str = Field(description="Секретный ключ для JWT токенов")
    jwt_algorithm: str = Field(default="HS256", description="Алгоритм шифрования JWT")
    jwt_access_token_expire_minutes: int = Field(default=1440, description="Время жизни JWT токена (мин)")
    encryption_key: str = Field(description="Ключ для шифрования конфиденциальных данных")

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key_length(cls, v: str) -> str:
        """Проверяет, что ключ шифрования имеет правильную длину."""
        if len(v) != 32:
            raise ValueError("Ключ шифрования должен быть длиной 32 символа")
        return v


class TelegramSettings(BaseSettings):
    """Настройки для работы с Telegram API."""

    webhook_domain: str = Field(description="Домен для webhook URL")
    webhook_secret: str = Field(description="Секрет для webhook безопасности")

    main_bot_token: Optional[str] = Field(None, description="Токен главного бота приложения")

    @property
    def webhook_base_url(self) -> str:
        """Базовый URL для webhooks."""
        return f"{self.webhook_domain}/api/v1/telegram/webhook"

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_")


class FileStorageSettings(BaseSettings):
    """Настройки файлового хранилища."""

    upload_path: str = Field(default="./uploads", description="Путь для загрузки файлов")
    max_file_size: int = Field(default=52428800, description="Максимальный размер файла (байты)")
    allowed_file_types: str = Field(
        default="jpg,jpeg,png,gif,pdf,mp4,mp3,docx,xlsx",
        description="Разрешенные типы файлов"
    )

    @property
    def allowed_extensions(self) -> set[str]:
        """Возвращает множество разрешенных расширений файлов."""
        return set(ext.strip().lower() for ext in self.allowed_file_types.split(','))

    model_config = SettingsConfigDict(env_prefix="UPLOAD_")


class LoggingSettings(BaseSettings):
    """Настройки логирования."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Уровень логирования"
    )
    format: Literal["json", "text"] = Field(default="json", description="Формат логов")
    file: Optional[str] = Field(default="logs/app.log", description="Файл для записи логов")

    model_config = SettingsConfigDict(env_prefix="LOG_")


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
    debug: bool = Field(default=False, description="Включить отладочный режим")
    reload: bool = Field(default=False, description="Автоперезагрузка при изменении кода")
    show_traceback: bool = Field(default=False, description="Показывать трейсбеки в ответах")

    # Мониторинг
    enable_metrics: bool = Field(default=True, description="Включить сбор метрик")
    metrics_port: int = Field(default=9090, description="Порт для метрик")

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
        extra="ignore"  # Игнорируем лишние переменные окружения
    )


class Settings:
    """
    Главный класс настроек, объединяющий все секции конфигурации.

    Этот класс создает единую точку доступа ко всем настройкам приложения.
    При инициализации автоматически загружает и валидирует все настройки.
    """

    def __init__(self):
        """Инициализирует все секции настроек."""
        self.app = AppSettings()
        self.database = DatabaseSettings()
        self.redis = RedisSettings()
        self.security = SecuritySettings()
        self.telegram = TelegramSettings()
        self.file_storage = FileStorageSettings()
        self.logging = LoggingSettings()

    def get_database_url(self) -> str:
        """Возвращает URL подключения к базе данных."""
        return self.database.url

    def get_redis_url(self) -> str:
        """Возвращает URL подключения к Redis."""
        return self.redis.url


# Создаем глобальный экземпляр настроек
# Этот объект будет импортироваться в других модулях
settings = Settings()

# Дополнительные константы для удобства
DATABASE_URL = settings.get_database_url()
REDIS_URL = settings.get_redis_url()

# Экспортируем основные настройки для удобного импорта
__all__ = [
    "settings",
    "Settings",
    "DATABASE_URL",
    "REDIS_URL",
]
