"""
Модель Telegram группы/канала.

Хранит информацию о группах и каналах Telegram,
которые связаны с сообществами.
"""

import enum
from typing import Optional

from sqlalchemy import BigInteger, Boolean, String, Enum, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModelWithSoftDelete


class TelegramGroupType(enum.Enum):
    """Типы Telegram групп."""
    GROUP = "group"  # Обычная группа
    SUPERGROUP = "supergroup"  # Супергруппа
    CHANNEL = "channel"  # Канал


class TelegramGroup(BaseModelWithSoftDelete):
    """
    Модель Telegram группы или канала.

    Сообщества могут быть связаны с группами/каналами для:
    - Основного общения участников
    - Уведомлений о новых курсах
    - Дополнительных дискуссий
    """

    __tablename__ = "telegram_groups"

    # Название группы/канала
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Название группы или канала"
    )

    # Telegram ID группы/канала
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        comment="Уникальный идентификатор группы/канала в Telegram"
    )

    # URL фотографии группы
    photo: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="URL фотографии группы/канала"
    )

    # Тип группы
    type: Mapped[TelegramGroupType] = mapped_column(
        Enum(TelegramGroupType),
        nullable=False,
        comment="Тип группы: group, supergroup или channel"
    )

    # Активна ли группа
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Активна ли группа в данный момент"
    )

    def __repr__(self) -> str:
        """Строковое представление группы."""
        return f"<TelegramGroup(id={self.id}, telegram_id={self.telegram_id}, name='{self.name}', type='{self.type.value}')>"

    @property
    def is_channel(self) -> bool:
        """Проверяет, является ли это каналом."""
        return self.type == TelegramGroupType.CHANNEL

    @property
    def is_group(self) -> bool:
        """Проверяет, является ли это группой."""
        return self.type in (TelegramGroupType.GROUP, TelegramGroupType.SUPERGROUP)

    @property
    def is_supergroup(self) -> bool:
        """Проверяет, является ли это супергруппой."""
        return self.type == TelegramGroupType.SUPERGROUP

    def activate(self) -> None:
        """Активирует группу."""
        self.is_active = True

    def deactivate(self) -> None:
        """Деактивирует группу."""
        self.is_active = False

    def update_info(
            self,
            name: Optional[str] = None,
            photo: Optional[str] = None,
            group_type: Optional[TelegramGroupType] = None
    ) -> None:
        """
        Обновляет информацию о группе.

        Args:
            name: Новое название группы
            photo: Новое фото группы
            group_type: Новый тип группы
        """
        if name is not None:
            self.name = name
        if photo is not None:
            self.photo = photo
        if group_type is not None:
            self.type = group_type


# Создаем индексы для оптимизации запросов
Index("ix_telegram_groups_telegram_id", TelegramGroup.telegram_id)
Index("ix_telegram_groups_type", TelegramGroup.type)
Index("ix_telegram_groups_is_active", TelegramGroup.is_active)
Index("ix_telegram_groups_name", TelegramGroup.name)
