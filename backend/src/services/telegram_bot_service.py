# backend/src/services/telegram_bot_service.py
# Сервис для взаимодействия с Telegram Bot

import aiohttp
import asyncio
import logging
import os
from typing import Optional, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
import json

logger = logging.getLogger(__name__)


class TelegramBotService:
    """Сервис для валидации пользователей через Telegram Bot API"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot_service_url = os.getenv("BOT_SERVICE_URL", "http://bot:8001")
        self.bot = None

        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
        else:
            logger.warning("TELEGRAM_BOT_TOKEN не установлен - bot service недоступен")

    async def validate_user_by_id(self, telegram_id: str) -> Dict[str, Any]:
        """
        Валидирует пользователя по Telegram ID через Bot API
        """
        if not self.bot:
            return {
                "valid": False,
                "user": None,
                "error": "Bot token not configured"
            }

        try:
            telegram_id_int = int(telegram_id)

            # Получаем информацию о пользователе
            chat_member = await self.bot.get_chat_member(
                chat_id=telegram_id_int,
                user_id=telegram_id_int
            )

            user = chat_member.user

            # Формируем данные пользователя
            user_data = {
                "telegram_id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_bot": user.is_bot,
                "is_premium": getattr(user, 'is_premium', False),
                "language_code": getattr(user, 'language_code', None),
                "validation_method": "telegram_bot_api",
                "chat_member_status": chat_member.status
            }

            logger.info(f"Пользователь {telegram_id} успешно валидирован через Bot API")

            return {
                "valid": True,
                "user": user_data,
                "error": None
            }

        except ValueError:
            return {
                "valid": False,
                "user": None,
                "error": "Invalid telegram_id format"
            }
        except TelegramError as e:
            logger.error(f"Telegram API error for user {telegram_id}: {str(e)}")
            return {
                "valid": False,
                "user": None,
                "error": f"Telegram API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error validating user {telegram_id}: {str(e)}")
            return {
                "valid": False,
                "user": None,
                "error": f"Validation error: {str(e)}"
            }

    async def send_validation_message(self, telegram_id: str, message: str) -> bool:
        """
        Отправляет сообщение пользователю для подтверждения валидации
        """
        if not self.bot:
            logger.error("Bot не инициализирован")
            return False

        try:
            await self.bot.send_message(
                chat_id=int(telegram_id),
                text=message
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения пользователю {telegram_id}: {str(e)}")
            return False

    async def request_user_validation(self, telegram_id: str) -> Dict[str, Any]:
        """
        Запрашивает у пользователя подтверждение через бота
        """
        validation_message = f"""
🔐 Запрос валидации аккаунта

Система Communa запрашивает подтверждение вашего аккаунта.
Для подтверждения нажмите /validate

ID запроса: {telegram_id}
"""

        message_sent = await self.send_validation_message(telegram_id, validation_message)

        if message_sent:
            return {
                "valid": True,
                "user": None,
                "error": None,
                "message": "Validation request sent to user"
            }
        else:
            return {
                "valid": False,
                "user": None,
                "error": "Failed to send validation request"
            }

    async def check_bot_status(self) -> Dict[str, Any]:
        """
        Проверяет статус бота и доступность Bot API
        """
        if not self.bot:
            return {
                "status": "unavailable",
                "error": "Bot token not configured"
            }

        try:
            bot_info = await self.bot.get_me()
            return {
                "status": "available",
                "bot_info": {
                    "id": bot_info.id,
                    "username": bot_info.username,
                    "first_name": bot_info.first_name,
                    "can_join_groups": bot_info.can_join_groups,
                    "can_read_all_group_messages": bot_info.can_read_all_group_messages,
                    "supports_inline_queries": bot_info.supports_inline_queries
                },
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Глобальный экземпляр сервиса
telegram_bot_service = TelegramBotService()

# ========================================================================
# backend/src/api/v1/endpoints/telegram.py
# Обновленный эндпоинт с полной интеграцией

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import logging
from ...services.telegram_bot_service import telegram_bot_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])


class TelegramUserValidate(BaseModel):
    telegram_id: str = Field(..., description="ID пользователя в Telegram")
    username: Optional[str] = Field(None, description="Username пользователя")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    request_confirmation: Optional[bool] = Field(False, description="Запросить подтверждение у пользователя")


class TelegramValidateResponse(BaseModel):
    valid: bool
    user: Optional[dict]
    error: Optional[str]
    confirmation_requested: Optional[bool] = False


# Замените это на вашу реальную функцию авторизации
async def get_current_user():
    return {"user_id": "authenticated_user"}


@router.post("/validate", response_model=TelegramValidateResponse)
async def validate_telegram_user(
        user_data: TelegramUserValidate,
        background_tasks: BackgroundTasks,
        current_user=Depends(get_current_user)
):
    """
    Полная валидация пользователя Telegram через Bot API

    Поддерживает:
    - Прямую валидацию через Bot API
    - Запрос подтверждения от пользователя
    - Получение актуальных данных профиля
    """

    try:
        logger.info(f"Начинаем валидацию пользователя: {user_data.telegram_id}")

        # Проверяем статус бота
        bot_status = await telegram_bot_service.check_bot_status()
        if bot_status["status"] != "available":
            raise HTTPException(
                status_code=503,
                detail=f"Main bot service unavailable: {bot_status.get('error', 'Unknown error')}"
            )

        # Если запрошено подтверждение от пользователя
        if user_data.request_confirmation:
            result = await telegram_bot_service.request_user_validation(user_data.telegram_id)
            return TelegramValidateResponse(
                valid=result["valid"],
                user=result["user"],
                error=result["error"],
                confirmation_requested=True
            )

        # Прямая валидация через Bot API
        result = await telegram_bot_service.validate_user_by_id(user_data.telegram_id)

        # Если прямая валидация не удалась, можем запросить подтверждение
        if not result["valid"] and "Forbidden" in str(result.get("error", "")):
            # Пользователь не начинал диалог с ботом
            background_tasks.add_task(
                telegram_bot_service.request_user_validation,
                user_data.telegram_id
            )

            return TelegramValidateResponse(
                valid=False,
                user=None,
                error="User needs to start dialog with bot first. Validation request sent.",
                confirmation_requested=True
            )

        return TelegramValidateResponse(
            valid=result["valid"],
            user=result["user"],
            error=result["error"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка валидации: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal validation error: {str(e)}"
        )


@router.get("/bot-status")
async def get_bot_status(current_user=Depends(get_current_user)):
    """Получить статус Telegram бота"""
    return await telegram_bot_service.check_bot_status()


@router.post("/send-message/{telegram_id}")
async def send_message_to_user(
        telegram_id: str,
        message: str,
        current_user=Depends(get_current_user)
):
    """Отправить сообщение пользователю через бота"""
    success = await telegram_bot_service.send_validation_message(telegram_id, message)

    if success:
        return {"success": True, "message": "Message sent successfully"}
    else:
        raise HTTPException(
            status_code=400,
            detail="Failed to send message"
        )
    