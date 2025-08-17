"""
API endpoints для авторизации.

Содержит endpoints для Telegram авторизации и валидации пользователей.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....database import get_db_session
from ....models.user import User
from ....schemas.telegram import TelegramValidationResponse, TelegramUserSchema
from ....core.auth import verify_telegram_webapp, get_current_user
from ....services.telegram_factory import telegram_factory  # 🔄 ИСПРАВЛЕНО
from ....core.auth_detector import auth_detector  # 🔄 ДОБАВЛЕНО

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/telegram/validate",
    response_model=TelegramValidationResponse,
    summary="Валидация Telegram пользователя",
    description="Проверяет подлинность данных Telegram WebApp и возвращает информацию о пользователе"
)
async def validate_telegram_user(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> TelegramValidationResponse:
    """
    Валидирует Telegram пользователя и создает/обновляет его в базе данных.

    Автоматически определяет тип авторизации:
    - Главное приложение (токен из .env)
    - Приложение сообщества (токен из БД)

    Returns:
        TelegramValidationResponse: Результат валидации с данными пользователя
    """
    try:
        # Определяем тип авторизации для логирования
        auth_type, community_id = auth_detector.detect_auth_type(request)

        # Валидируем Telegram данные (автоматически выберет нужный бот)
        webapp_user = await verify_telegram_webapp(request, db)

        # Создаем или обновляем пользователя в БД
        user = await get_current_user(webapp_user, db)

        # Получаем соответствующий сервис и преобразуем в схему для frontend
        if auth_type == "main":
            auth_service = telegram_factory.get_main_bot_service()
        else:
            auth_service = await telegram_factory.get_community_bot_service(community_id, db)

        if not auth_service:
            logger.error(f"❌ Не удалось получить сервис авторизации для {auth_type}")
            return TelegramValidationResponse(
                valid=False,
                error="Service unavailable"
            )

        user_schema = auth_service.convert_to_frontend_schema(webapp_user)

        logger.info(
            f"✅ Успешная валидация пользователя {user.telegram_id} "
            f"через {auth_type}" + (f" сообщества {community_id}" if community_id else "")
        )

        return TelegramValidationResponse(
            valid=True,
            user=user_schema
        )

    except HTTPException as e:
        # Ошибки авторизации уже обработаны в dependencies
        logger.warning(f"❌ Ошибка авторизации: {e.detail}")
        return TelegramValidationResponse(
            valid=False,
            error=e.detail
        )

    except Exception as e:
        # Неожиданные ошибки
        logger.error(f"❌ Неожиданная ошибка валидации: {e}")
        return TelegramValidationResponse(
            valid=False,
            error="Внутренняя ошибка сервера"
        )


@router.get(
    "/me",
    response_model=TelegramUserSchema,
    summary="Получить текущего пользователя",
    description="Возвращает информацию о текущем авторизованном пользователе"
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> TelegramUserSchema:
    """
    Возвращает информацию о текущем пользователе.

    Требует валидной Telegram авторизации.

    Returns:
        TelegramUserSchema: Данные текущего пользователя
    """
    return TelegramUserSchema(
        id=current_user.telegram_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        username=current_user.username,
        language_code=current_user.language_code,
        is_premium=current_user.is_premium,
        photo_url=current_user.photo_url
    )


@router.post(
    "/test",
    summary="Тестовый endpoint авторизации",
    description="Тестовый endpoint для проверки авторизации"
)
async def test_auth(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Тестовый endpoint для проверки что авторизация работает.

    Returns:
        Dict: Информация о пользователе и статус авторизации
    """
    return {
        "authenticated": True,
        "user_id": current_user.telegram_id,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "created_at": current_user.created_at.isoformat()
    }