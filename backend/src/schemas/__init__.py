"""
Pydantic схемы для валидации данных.
"""

from .telegram import TelegramUserSchema, TelegramValidationResponse, WebAppUser

__all__ = [
    "TelegramUserSchema",
    "TelegramValidationResponse",
    "WebAppUser",
]
