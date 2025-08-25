"""
Pydantic схемы для работы с Telegram данными.

Схемы для валидации и сериализации данных от Telegram WebApp.
"""

from typing import Optional
from pydantic import BaseModel, Field


class TelegramUserSchema(BaseModel):
    """Схема пользователя Telegram для frontend."""

    id: int = Field(description="Telegram ID пользователя")
    first_name: str = Field(description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(None, description="Username пользователя")
    language_code: Optional[str] = Field(None, description="Код языка")
    is_premium: Optional[bool] = Field(False, description="Статус Telegram Premium")
    photo_url: Optional[str] = Field(None, description="URL фотографии профиля")


class TelegramValidationResponse(BaseModel):
    """Ответ на валидацию Telegram пользователя."""

    valid: bool = Field(description="Успешна ли валидация")
    user: Optional[TelegramUserSchema] = Field(None, description="Данные пользователя")
    error: Optional[str] = Field(None, description="Ошибка валидации")


class WebAppUser(BaseModel):
    """Внутренняя модель пользователя WebApp."""

    telegram_user_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: bool = False
    allows_write_to_pm: Optional[bool] = None
    photo_url: Optional[str] = None
    