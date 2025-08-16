"""
Модели базы данных.

Этот пакет содержит все модели SQLAlchemy для глобальных таблиц.
Динамические таблицы создаются через фабрику в services/dynamic_tables.py

Импортируем все модели здесь, чтобы они зарегистрировались в metadata
при импорте пакета models.
"""

from .base import BaseModel, TimestampMixin, SoftDeleteMixin
from .user import User
from .telegram_bot import TelegramBot
from .telegram_group import TelegramGroup
from .community import Community
from .community_admin import CommunityAdmin
from .gamification import GamificationRule, LevelRule

# Экспортируем все модели для удобного импорта
__all__ = [
    # Базовые классы
    "BaseModel",
    "TimestampMixin",
    "SoftDeleteMixin",

    # Глобальные модели
    "User",
    "TelegramBot",
    "TelegramGroup",
    "Community",
    "CommunityAdmin",
    "GamificationRule",
    "LevelRule",
]