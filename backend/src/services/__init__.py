"""
Сервисы бизнес-логики.
"""

from .dynamic_tables import dynamic_table_manager
from .telegram_factory import telegram_factory

__all__ = [
    "dynamic_table_manager",
    "telegram_factory",
]