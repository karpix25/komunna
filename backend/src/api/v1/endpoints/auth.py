# backend/src/api/v1/endpoints/auth.py
import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ....database import get_db_session
from ....models.user import User
from ....models.community import Community
from ....models.community_admin import CommunityAdmin, CommunityRole
from ....schemas.telegram import TelegramValidationResponse, TelegramUserSchema
from ....schemas.bootstrap import (
    BootstrapResponse, CommunityAggregate, CommunityBrief,
    BotBrief, GroupBrief
)
from ....core.auth import verify_telegram_webapp, get_current_user
from ....services.telegram_factory import telegram_factory
from ....core.auth_detector import auth_detector

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Authentication"])


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
    try:
        auth_type, community_id = auth_detector.detect_auth_type(request)
        webapp_user = await verify_telegram_webapp(request, db)
        user = await get_current_user(webapp_user, db)

        if auth_type == "main":
            auth_service = telegram_factory.get_main_bot_service()
        else:
            auth_service = await telegram_factory.get_community_bot_service(community_id, db)

        if not auth_service:
            logger.error(f"❌ Не удалось получить сервис авторизации для {auth_type}")
            return TelegramValidationResponse(valid=False, error="Service unavailable")

        user_schema = auth_service.convert_to_frontend_schema(webapp_user)

        logger.info(
            f"✅ Успешная валидация пользователя {user.telegram_id} через {auth_type}"
            + (f" сообщества {community_id}" if community_id else "")
        )

        return TelegramValidationResponse(valid=True, user=user_schema)

    except HTTPException as e:
        logger.warning(f"❌ Ошибка авторизации: {e.detail}")
        return TelegramValidationResponse(valid=False, error=e.detail)
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка валидации: {e}")
        return TelegramValidationResponse(valid=False, error="Внутренняя ошибка сервера")


@router.get(
    "/me",
    response_model=TelegramUserSchema,
    summary="Получить текущего пользователя",
    description="Возвращает информацию о текущем авторизованном пользователе"
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> TelegramUserSchema:
    return TelegramUserSchema(
        id=current_user.telegram_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        username=current_user.username,
        language_code=current_user.language_code,
        is_premium=current_user.is_premium,
        photo_url=current_user.photo_url
    )


# 🆕 Новый агрегирующий эндпоинт на загрузку
@router.get(
    "/me/bootstrap",
    response_model=BootstrapResponse,
    summary="Bootstrap профиля",
    description="Создаёт/обновляет пользователя и возвращает агрегированные данные: все его сообщества, бот и группы каждого сообщества"
)
async def bootstrap_me(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> BootstrapResponse:
    """
    1) verify_telegram_webapp -> WebAppUser
    2) get_current_user -> upsert в БД
    3) собираем:
       - сообщества пользователя (владелец)
       - сообщества, где он админ/модератор
       - по каждому сообществу: бот, main_group, additional_group
    """
    # 1-2: авторизация и upsert
    webapp_user = await verify_telegram_webapp(request, db)
    user = await get_current_user(webapp_user, db)

    # 3a) Сообщества, где он владелец
    owned_stmt = (
        select(Community)
        .where(Community.owner_id == user.id)
        .options(
            selectinload(Community.telegram_bot),
            selectinload(Community.main_group),
            selectinload(Community.additional_group),
        )
    )
    owned_res = await db.execute(owned_stmt)
    owned = list(owned_res.scalars())

    # 3b) Сообщества, где он админ/модератор
    admin_stmt = (
        select(CommunityAdmin)
        .where(CommunityAdmin.user_id == user.id)
        .options(
            selectinload(CommunityAdmin.community)
            .selectinload(Community.telegram_bot),
            selectinload(CommunityAdmin.community)
            .selectinload(Community.main_group),
            selectinload(CommunityAdmin.community)
            .selectinload(Community.additional_group),
        )
    )
    admin_res = await db.execute(admin_stmt)
    admin_links = list(admin_res.scalars())

    # Сюда соберем аггрегат без дублей (owner приоритетнее)
    by_id: dict[int, CommunityAggregate] = {}

    # владелец
    for c in owned:
        by_id[c.id] = CommunityAggregate(
            community=_to_community_brief(c),
            role="owner",
            bot=_to_bot_brief(c.telegram_bot),
            main_group=_to_group_brief(c.main_group),
            additional_group=_to_group_brief(c.additional_group),
        )

    # админ/модератор (не затираем owner)
    for link in admin_links:
        c = link.community
        if not c:
            continue
        if c.id in by_id:
            continue
        role = None
        if link.role == CommunityRole.ADMIN:
            role = "admin"
        elif link.role == CommunityRole.MODERATOR:
            role = "moderator"

        by_id[c.id] = CommunityAggregate(
            community=_to_community_brief(c),
            role=role,
            bot=_to_bot_brief(c.telegram_bot),
            main_group=_to_group_brief(c.main_group),
            additional_group=_to_group_brief(c.additional_group),
        )

    # Финальный ответ
    return BootstrapResponse(
        user=TelegramUserSchema(
            id=user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
            is_premium=user.is_premium,
            photo_url=user.photo_url,
        ),
        communities=list(by_id.values()),
    )


# --- сериализаторы в схемы ---

def _to_community_brief(c: Community) -> CommunityBrief:
    return CommunityBrief(
        id=c.id,
        table_key=c.table_key,
        domain=c.domain,
    )

def _to_bot_brief(bot) -> Optional[BotBrief]:
    if not bot:
        return None
    # token не отдаём наружу
    return BotBrief(
        id=bot.id,
        username=bot.username,
        name=bot.name,
        telegram_id=bot.telegram_id,
        is_active=bot.is_active,
        bot_url=f"https://t.me/{bot.username}" if bot.username else None,
    )

def _to_group_brief(g) -> Optional[GroupBrief]:
    if not g:
        return None
    return GroupBrief(
        id=g.id,
        telegram_id=g.telegram_id,
        name=g.name,
        type=str(g.type.value) if hasattr(g, "type") and g.type else "group",
        is_active=g.is_active,
        photo=getattr(g, "photo", None),
    )
