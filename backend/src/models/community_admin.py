"""
Модель администратора сообщества.

Определяет роли и права доступа пользователей
для управления конкретными сообществами.
"""

import enum
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Enum, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModelWithSoftDelete


class CommunityRole(enum.Enum):
    """Роли в сообществе."""
    OWNER = "owner"  # Владелец - полные права
    ADMIN = "admin"  # Администратор - почти все права
    MODERATOR = "moderator"  # Модератор - ограниченные права


class CommunityAdmin(BaseModelWithSoftDelete):
    """
    Модель администратора сообщества.

    Определяет кто может управлять конкретным сообществом
    и какие у него права доступа.
    """

    __tablename__ = "community_admins"

    # ID сообщества
    community_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("communities.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID сообщества"
    )

    # ID пользователя-администратора
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID пользователя-администратора"
    )

    # Роль в сообществе
    role: Mapped[CommunityRole] = mapped_column(
        Enum(CommunityRole),
        nullable=False,
        comment="Роль пользователя в сообществе"
    )

    # Права доступа в JSON формате
    permissions: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Детальные права доступа в JSON формате"
    )

    # Кто пригласил этого администратора
    invited_by: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID пользователя, который пригласил администратора"
    )

    # Связи с другими моделями
    community: Mapped["Community"] = relationship(
        "Community",
        foreign_keys=[community_id],
        lazy="select"
    )

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="select"
    )

    inviter: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[invited_by],
        lazy="select"
    )

    def __repr__(self) -> str:
        """Строковое представление администратора."""
        return f"<CommunityAdmin(id={self.id}, community_id={self.community_id}, user_id={self.user_id}, role='{self.role.value}')>"

    @property
    def is_owner(self) -> bool:
        """Проверяет, является ли пользователь владельцем."""
        return self.role == CommunityRole.OWNER

    @property
    def is_admin(self) -> bool:
        """Проверяет, является ли пользователь администратором."""
        return self.role == CommunityRole.ADMIN

    @property
    def is_moderator(self) -> bool:
        """Проверяет, является ли пользователь модератором."""
        return self.role == CommunityRole.MODERATOR

    def has_permission(self, permission: str) -> bool:
        """
        Проверяет наличие конкретного права.

        Args:
            permission: Название права для проверки

        Returns:
            bool: True если право есть
        """
        # Владелец имеет все права
        if self.is_owner:
            return True

        # Проверяем в детальных правах
        if self.permissions and permission in self.permissions:
            return self.permissions[permission]

        # Права по умолчанию для ролей
        default_permissions = self._get_default_permissions()
        return default_permissions.get(permission, False)

    def _get_default_permissions(self) -> dict:
        """Возвращает права по умолчанию для роли."""
        if self.role == CommunityRole.OWNER:
            return {
                "manage_community": True,
                "manage_admins": True,
                "manage_courses": True,
                "manage_users": True,
                "manage_bot": True,
                "manage_groups": True,
                "view_analytics": True,
                "manage_payments": True,
            }
        elif self.role == CommunityRole.ADMIN:
            return {
                "manage_community": False,
                "manage_admins": False,
                "manage_courses": True,
                "manage_users": True,
                "manage_bot": False,
                "manage_groups": False,
                "view_analytics": True,
                "manage_payments": False,
            }
        elif self.role == CommunityRole.MODERATOR:
            return {
                "manage_community": False,
                "manage_admins": False,
                "manage_courses": False,
                "manage_users": True,
                "manage_bot": False,
                "manage_groups": False,
                "view_analytics": False,
                "manage_payments": False,
            }

        return {}

    def grant_permission(self, permission: str) -> None:
        """
        Предоставляет конкретное право.

        Args:
            permission: Название права
        """
        if not self.permissions:
            self.permissions = {}
        self.permissions[permission] = True

    def revoke_permission(self, permission: str) -> None:
        """
        Отзывает конкретное право.

        Args:
            permission: Название права
        """
        if not self.permissions:
            self.permissions = {}
        self.permissions[permission] = False

    def update_permissions(self, new_permissions: dict) -> None:
        """
        Обновляет права доступа.

        Args:
            new_permissions: Словарь с новыми правами
        """
        if not self.permissions:
            self.permissions = {}
        self.permissions.update(new_permissions)

    def change_role(self, new_role: CommunityRole) -> None:
        """
        Изменяет роль администратора.

        Args:
            new_role: Новая роль
        """
        self.role = new_role
        # При смене роли сбрасываем кастомные права
        self.permissions = None


# Создаем индексы для оптимизации запросов
Index("ix_community_admins_community_id", CommunityAdmin.community_id)
Index("ix_community_admins_user_id", CommunityAdmin.user_id)
Index("ix_community_admins_role", CommunityAdmin.role)
Index("ix_community_admins_invited_by", CommunityAdmin.invited_by)

# Составной уникальный индекс - один пользователь может быть администратором
# одного сообщества только с одной ролью
Index("ix_community_admins_unique_user_community",
      CommunityAdmin.community_id, CommunityAdmin.user_id,
      unique=True)
