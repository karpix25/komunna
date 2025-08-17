"""
Основная бизнес-логика приложения.
"""

from .auth import verify_telegram_webapp, get_current_user
from .auth_detector import auth_detector

__all__ = [
    "verify_telegram_webapp",
    "get_current_user",
    "auth_detector",
]
