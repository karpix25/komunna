"""
Модель глобального пользователя.

Хранит базовую информацию о всех пользователях платформы,
полученную из Telegram при первой авторизации.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModelWithSoftDelete


class User(BaseModelWithSoftDelete):
    """
    Глобальная модель пользователя.

    Содержит базовую информацию о пользователе из Telegram.
    Один пользователь может быть участником множества сообществ.
    """

    __tablename__ = "users"

    # Telegram ID пользователя - уникальный идентификатор в Telegram
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        comment="Уникальный идентификатор пользователя в Telegram"
    )

    # Имя пользователя в Telegram (может отсутствовать)
    username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Username пользователя в Telegram (без @)"
    )

    # Имя пользователя
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Имя пользователя"
    )

    # Фамилия пользователя (может отсутствовать)
    last_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Фамилия пользователя"
    )

    # Код языка пользователя (например, 'ru', 'en')
    language_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="Код языка пользователя в формате ISO 639-1"
    )

    # URL фотографии профиля
    photo_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="URL фотографии профиля пользователя"
    )

    # Статус Telegram Premium
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Имеет ли пользователь подписку Telegram Premium"
    )

    # Время последней активности
    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время последней активности пользователя"
    )

    def __repr__(self) -> str:
        """Строковое представление пользователя."""
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"

    @property
    def full_name(self) -> str:
        """Возвращает полное имя пользователя."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    @property
    def display_name(self) -> str:
        """Возвращает отображаемое имя (username или полное имя)."""
        if self.username:
            return f"@{self.username}"
        return self.full_name

    def update_last_activity(self) -> None:
        """Обновляет время последней активности."""
        self.last_active_at = datetime.utcnow()

    def update_from_telegram(
            self,
            username: Optional[str] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            language_code: Optional[str] = None,
            photo_url: Optional[str] = None,
            is_premium: Optional[bool] = None,
    ) -> None:
        """
        Обновляет данные пользователя из Telegram.

        Args:
            username: Новый username
            first_name: Новое имя
            last_name: Новая фамилия
            language_code: Новый код языка
            photo_url: Новый URL фото
            is_premium: Новый статус Premium
        """
        if username is not None:
            self.username = username
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name
        if language_code is not None:
            self.language_code = language_code
        if photo_url is not None:
            self.photo_url = photo_url
        if is_premium is not None:
            self.is_premium = is_premium

        # Обновляем время последней активности
        self.update_last_activity()


# Создаем индексы для оптимизации запросов
Index("ix_users_telegram_id", User.telegram_id)
Index("ix_users_username", User.username)
Index("ix_users_last_active_at", User.last_active_at)
Index("ix_users_created_at", User.created_at)
