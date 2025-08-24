"""
Базовые классы для всех моделей.
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
    """

    __abstract__ = True

    # Первичный ключ - BigInteger для поддержки больших чисел (Telegram ID)
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
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            # Преобразуем datetime в ISO строку для JSON сериализации
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result


class BaseModelWithSoftDelete(BaseModel, SoftDeleteMixin):
    """
    Базовый класс для моделей с мягким удалением.
    """

    __abstract__ = True