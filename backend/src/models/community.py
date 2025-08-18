"""
Модель сообщества.

Центральная модель, которая связывает все остальные компоненты:
боты, группы, пользователи, и определяет ключ для динамических таблиц.
"""

from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, ForeignKey, Index, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelWithSoftDelete


class Community(BaseModelWithSoftDelete):
    """
    Модель сообщества (школы).

    Главная сущность системы. Каждое сообщество:
    - Имеет уникальный ключ для создания динамических таблиц
    - Связано с ботом для взаимодействия с пользователями
    - Может иметь основную и дополнительную группы
    - Имеет владельца и настройки
    """

    __tablename__ = "communities"

    # Уникальный ключ для динамических таблиц (САМОЕ ВАЖНОЕ ПОЛЕ!)
    table_key: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Уникальный ключ для создания динамических таблиц"
    )

    # Владелец сообщества
    owner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID владельца сообщества"
    )

    # Домен/поддомен для доступа
    domain: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="Домен или поддомен для доступа к сообществу"
    )

    # Связанный Telegram бот
    telegram_bot_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("telegram_bots.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID связанного Telegram бота"
    )

    # Основная группа для общения
    main_group_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("telegram_groups.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID основной группы сообщества"
    )

    # Дополнительная группа (например, для уведомлений)
    additional_group_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("telegram_groups.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID дополнительной группы сообщества"
    )

    # Настройки сообщества в JSON формате
    settings: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Настройки сообщества в JSON формате"
    )

    # Разрешить уведомления о курсах в группе
    allow_course_notifications: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Разрешить отправку уведомлений о курсах в группу"
    )

    # Связи с другими моделями
    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_id],
        lazy="select"
    )

    telegram_bot: Mapped[Optional["TelegramBot"]] = relationship(
        "TelegramBot",
        foreign_keys=[telegram_bot_id],
        lazy="select"
    )

    main_group: Mapped[Optional["TelegramGroup"]] = relationship(
        "TelegramGroup",
        foreign_keys=[main_group_id],
        lazy="select"
    )

    additional_group: Mapped[Optional["TelegramGroup"]] = relationship(
        "TelegramGroup",
        foreign_keys=[additional_group_id],
        lazy="select"
    )

    def __repr__(self) -> str:
        """Строковое представление сообщества."""
        return f"<Community(id={self.id}, table_key='{self.table_key}', domain='{self.domain}')>"

    @property
    def full_domain_url(self) -> str:
        """Возвращает полный URL сообщества."""
        if self.domain.startswith(('http://', 'https://')):
            return self.domain
        return f"https://{self.domain}"

    @property
    def has_telegram_bot(self) -> bool:
        """Проверяет, есть ли у сообщества связанный бот."""
        return self.telegram_bot_id is not None

    @property
    def has_main_group(self) -> bool:
        """Проверяет, есть ли у сообщества основная группа."""
        return self.main_group_id is not None

    @property
    def has_additional_group(self) -> bool:
        """Проверяет, есть ли у сообщества дополнительная группа."""
        return self.additional_group_id is not None

    def get_setting(self, key: str, default=None):
        """
        Получает значение настройки по ключу.

        Args:
            key: Ключ настройки
            default: Значение по умолчанию

        Returns:
            Значение настройки или default
        """
        if not self.settings:
            return default
        return self.settings.get(key, default)

    def set_setting(self, key: str, value) -> None:
        """
        Устанавливает значение настройки.

        Args:
            key: Ключ настройки
            value: Значение настройки
        """
        if not self.settings:
            self.settings = {}
        self.settings[key] = value

    def update_settings(self, new_settings: dict) -> None:
        """
        Обновляет настройки сообщества.

        Args:
            new_settings: Словарь с новыми настройками
        """
        if not self.settings:
            self.settings = {}
        self.settings.update(new_settings)

    def enable_course_notifications(self) -> None:
        """Включает уведомления о курсах."""
        self.allow_course_notifications = True

    def disable_course_notifications(self) -> None:
        """Отключает уведомления о курсах."""
        self.allow_course_notifications = False

    def link_telegram_bot(self, bot_id: int) -> None:
        """
        Связывает сообщество с Telegram ботом.

        Args:
            bot_id: ID бота для связи
        """
        self.telegram_bot_id = bot_id

    def unlink_telegram_bot(self) -> None:
        """Отвязывает Telegram бота от сообщества."""
        self.telegram_bot_id = None

    def link_main_group(self, group_id: int) -> None:
        """
        Связывает сообщество с основной группой.

        Args:
            group_id: ID группы для связи
        """
        self.main_group_id = group_id

    def unlink_main_group(self) -> None:
        """Отвязывает основную группу от сообщества."""
        self.main_group_id = None

    def link_additional_group(self, group_id: int) -> None:
        """
        Связывает сообщество с дополнительной группой.

        Args:
            group_id: ID группы для связи
        """
        self.additional_group_id = group_id

    def unlink_additional_group(self) -> None:
        """Отвязывает дополнительную группу от сообщества."""
        self.additional_group_id = None


# Создаем индексы для оптимизации запросов
Index("ix_communities_table_key", Community.table_key)
Index("ix_communities_domain", Community.domain)
Index("ix_communities_owner_id", Community.owner_id)
Index("ix_communities_telegram_bot_id", Community.telegram_bot_id)
Index("ix_communities_main_group_id", Community.main_group_id)
Index("ix_communities_additional_group_id", Community.additional_group_id)
