# backend/src/core/auth.py
"""
Зависимости и функции для авторизации в FastAPI.
Содержит dependency для проверки Telegram авторизации.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..models.user import User
from ..schemas.telegram import WebAppUser
from ..services.telegram_factory import telegram_factory
from .auth_detector import auth_detector

logger = logging.getLogger(__name__)


async def verify_telegram_webapp(
        request: Request,
        db: AsyncSession = Depends(get_db_session)
) -> WebAppUser:
    """
    Dependency для проверки Telegram WebApp авторизации.

    Автоматически определяет тип авторизации (главный бот или бот сообщества)
    и использует соответствующий токен для валидации.

    Args:
        request: HTTP запрос от FastAPI
        db: Сессия базы данных

    Returns:
        WebAppUser: Валидированные данные пользователя

    Raises:
        HTTPException: Если авторизация невалидна
    """
    # Получаем данные авторизации из заголовка
    auth_string = request.headers.get("Authorization")
    if not auth_string:
        logger.warning("❌ Отсутствует заголовок Authorization")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    # Определяем тип авторизации
    auth_type, community_id = auth_detector.detect_auth_type(request)

    # Получаем соответствующий сервис авторизации
    if auth_type == "main":
        auth_service = telegram_factory.get_main_bot_service()
        if not auth_service:
            logger.error("❌ Сервис главного бота недоступен")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Main bot service unavailable"
            )

    elif auth_type == "community":
        auth_service = await telegram_factory.get_community_bot_service(community_id, db)
        if not auth_service:
            logger.error(f"❌ Сервис бота сообщества {community_id} недоступен")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Community bot service unavailable for community {community_id}"
            )

    else:
        logger.error(f"❌ Неизвестный тип авторизации: {auth_type}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown auth type"
        )

    # Валидируем данные через соответствующий сервис
    telegram_user = auth_service.verify_webapp_init_data(auth_string)
    if not telegram_user:
        logger.warning(f"❌ Невалидные Telegram данные для {auth_type} авторизации")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram auth data"
        )

    # Преобразуем в нашу модель
    webapp_user = auth_service.get_user_from_telegram_data(telegram_user)

    logger.info(
        f"✅ Авторизован пользователь: {webapp_user.telegram_user_id} "
        f"через {auth_type}" + (f" сообщества {community_id}" if community_id else "")
    )

    return webapp_user


async def get_current_user(
        webapp_user: WebAppUser = Depends(verify_telegram_webapp),
        db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency для получения текущего пользователя из базы данных.

    Создает пользователя если его нет, или обновляет существующего.

    Args:
        webapp_user: Валидированные данные от Telegram
        db: Сессия базы данных

    Returns:
        User: Модель пользователя из базы данных
    """
    from sqlalchemy import select

    # Ищем пользователя в базе данных
    stmt = select(User).where(User.telegram_id == webapp_user.telegram_user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        # Обновляем существующего пользователя
        user.update_from_telegram(
            username=webapp_user.username,
            first_name=webapp_user.first_name,
            last_name=webapp_user.last_name,
            language_code=webapp_user.language_code,
            is_premium=webapp_user.is_premium,
            photo_url=webapp_user.photo_url
        )
        logger.info(f"🔄 Обновлен пользователь: {user.telegram_id}")
    else:
        # Создаем нового пользователя
        user = User(
            telegram_id=webapp_user.telegram_user_id,
            username=webapp_user.username,
            first_name=webapp_user.first_name,
            last_name=webapp_user.last_name,
            language_code=webapp_user.language_code,
            is_premium=webapp_user.is_premium,
            photo_url=webapp_user.photo_url
        )
        db.add(user)
        logger.info(f"➕ Создан новый пользователь: {user.telegram_id}")

    await db.commit()
    await db.refresh(user)

    return user


async def get_current_user_with_community(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session)
) -> tuple[User, Optional[int]]:
    """
    Dependency для получения пользователя с информацией о сообществе.

    Args:
        request: HTTP запрос
        current_user: Текущий пользователь
        db: Сессия базы данных

    Returns:
        tuple[User, Optional[int]]: Пользователь и ID сообщества (если есть)
    """
    auth_type, community_id = auth_detector.detect_auth_type(request)
    return current_user, community_id
