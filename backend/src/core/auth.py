# backend/src/core/auth.py
"""
Верификация Telegram WebApp через aiogram.safe_parse_webapp_init_data.
Сохраняем автоопределение типа авторизации (main/community) и upsert пользователя.
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db_session
from ..models.user import User
from ..schemas.telegram import WebAppUser
from ..services.telegram_factory import telegram_factory
from .auth_detector import auth_detector

logger = logging.getLogger(__name__)


async def verify_telegram_webapp(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> WebAppUser:
    init_data = request.headers.get("Authorization")
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    # 1) Определяем тип авторизации (main/community)
    auth_type, community_id = auth_detector.detect_auth_type(request)

    # 2) Берём соответствующий TelegramAuthService
    if auth_type == "main":
        auth_service = telegram_factory.get_main_bot_service()
        if not auth_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Main bot token not configured",
            )
    elif auth_type == "community":
        if community_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Community ID is required",
            )
        auth_service = await telegram_factory.get_community_bot_service(community_id, db)
        if not auth_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Community bot service unavailable",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown auth type",
        )

    # 3) Валидируем initData через aiogram: получаем AiogramUser
    aiogram_user = auth_service.verify_webapp_init_data(init_data)
    if not aiogram_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram auth data",
        )

    # ВАЖНО: AiogramUser не гарантирует поле is_premium.
    # auth_service сохранил признак premium во время verify_webapp_init_data,
    # поэтому передаём его дальше как второй (необязательный) аргумент:
    webapp_user = auth_service.get_user_from_telegram_data(aiogram_user)

    logger.info(
        "✅ Telegram WebApp auth ok: user=%s via %s%s",
        webapp_user.telegram_user_id,
        auth_type,
        f" community={community_id}" if community_id else "",
    )
    return webapp_user


async def get_current_user(
    webapp_user: WebAppUser = Depends(verify_telegram_webapp),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    stmt = select(User).where(User.telegram_id == webapp_user.telegram_user_id)
    res = await db.execute(stmt)
    user: Optional[User] = res.scalar_one_or_none()

    if user:
        user.update_from_telegram(
            username=webapp_user.username,
            first_name=webapp_user.first_name,
            last_name=webapp_user.last_name,
            language_code=webapp_user.language_code,
            is_premium=webapp_user.is_premium,
            photo_url=webapp_user.photo_url,
        )
        logger.info("🔄 User updated: %s", user.telegram_id)
    else:
        user = User(
            telegram_id=webapp_user.telegram_user_id,
            username=webapp_user.username,
            first_name=webapp_user.first_name,
            last_name=webapp_user.last_name,
            language_code=webapp_user.language_code,
            is_premium=webapp_user.is_premium,
            photo_url=webapp_user.photo_url,
        )
        db.add(user)
        logger.info("➕ User created: %s", webapp_user.telegram_user_id)

    await db.commit()
    await db.refresh(user)
    return user
