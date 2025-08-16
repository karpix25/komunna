"""
Базовые классы для всех моделей.

Содержит общие миксины и базовый класс, которые используются
во всех моделях для обеспечения единообразия.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, declarative_mixin

from ..database import Base


@declarative_mixin
class TimestampMixin:
    """
    Миксин для добавления временных меток создания и обновления.

    Автоматически добавляет поля created_at и updated_at
    во все таблицы, которые используют этот миксин.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата и время создания записи"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Дата и время последнего обновления записи"
    )


@declarative_mixin
class SoftDeleteMixin:
    """
    Миксин для мягкого удаления записей.

    Добавляет поле deleted_at, которое позволяет "удалять" записи
    без физического удаления из базы данных.
    """

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Дата и время мягкого удаления записи"
    )

    @property
    def is_deleted(self) -> bool:
        """Проверяет, удалена ли запись."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Помечает запись как удаленную."""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Восстанавливает удаленную запись."""
        self.deleted_at = None


class BaseModel(Base, TimestampMixin):
    """
    Базовый класс для всех моделей.

    Содержит общие поля и методы, которые есть у всех моделей:
    - Первичный ключ id
    - Временные метки создания и обновления
    - Общие методы для работы с моделью
    """

    __abstract__ = True  # Эта модель не создает таблицу

    # Первичный ключ - BigInteger для поддержки больших чисел (Telegram ID могут быть большими)
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Уникальный идентификатор записи"
    )

    def __repr__(self) -> str:
        """Строковое представление модели для отладки."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict:
        """
        Преобразует модель в словарь.

        Полезно для сериализации или отладки.
        Не включает приватные атрибуты и relationship.
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Преобразуем datetime в ISO строку для JSON сериализации
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    @classmethod
    def get_table_name(cls) -> str:
        """Возвращает имя таблицы модели."""
        return cls.__tablename__


class BaseModelWithSoftDelete(BaseModel, SoftDeleteMixin):
    """
    Базовый класс для моделей с мягким удалением.

    Наследуется от BaseModel и добавляет функциональность мягкого удаления.
    Используется для моделей, где важно сохранить историю удаленных записей.
    """

    __abstract__ = True
