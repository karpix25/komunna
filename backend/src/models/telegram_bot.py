"""
Модель Telegram бота.

Хранит информацию о всех ботах, которые используются
в различных сообществах платформы.
"""

from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelWithSoftDelete


class TelegramBot(BaseModelWithSoftDelete):
    """
    Модель Telegram бота.

    Каждое сообщество может иметь своего бота для взаимодействия с пользователями.
    Хранит токен бота и настройки webhook.
    """

    __tablename__ = "telegram_bots"

    # Название бота (отображаемое имя)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Отображаемое название бота"
    )

    # Username бота в Telegram (без @)
    username: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Username бота в Telegram (без @)"
    )

    # Telegram ID бота
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        comment="Уникальный идентификатор бота в Telegram"
    )

    # Токен бота (зашифрован)
    token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Зашифрованный токен бота от BotFather"
    )

    # URL для webhook (если используется)
    webhook_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="URL для получения обновлений от Telegram"
    )

    # Секрет для webhook (для безопасности)
    webhook_secret: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Секретный ключ для проверки webhook запросов"
    )

    # Активен ли бот
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Активен ли бот в данный момент"
    )

    # Кто добавил бота
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID пользователя, который добавил бота"
    )

    # Связь с пользователем, который создал бота
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="select"
    )

    def __repr__(self) -> str:
        """Строковое представление бота."""
        return f"<TelegramBot(id={self.id}, username='{self.username}', name='{self.name}')>"

    @property
    def bot_url(self) -> str:
        """Возвращает URL бота в Telegram."""
        return f"https://t.me/{self.username}"

    @property
    def webhook_configured(self) -> bool:
        """Проверяет, настроен ли webhook."""
        return self.webhook_url is not None and self.webhook_secret is not None

    def activate(self) -> None:
        """Активирует бота."""
        self.is_active = True

    def deactivate(self) -> None:
        """Деактивирует бота."""
        self.is_active = False

    def update_webhook(self, url: str, secret: str) -> None:
        """
        Обновляет настройки webhook.

        Args:
            url: Новый URL для webhook
            secret: Новый секрет для webhook
        """
        self.webhook_url = url
        self.webhook_secret = secret

    def clear_webhook(self) -> None:
        """Очищает настройки webhook."""
        self.webhook_url = None
        self.webhook_secret = None


# Создаем индексы для оптимизации запросов
Index("ix_telegram_bots_telegram_id", TelegramBot.telegram_id)
Index("ix_telegram_bots_username", TelegramBot.username)
Index("ix_telegram_bots_is_active", TelegramBot.is_active)
Index("ix_telegram_bots_created_by", TelegramBot.created_by)
