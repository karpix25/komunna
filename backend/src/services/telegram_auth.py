# backend/src/services/telegram_auth.py
"""
Сервис для авторизации и валидации Telegram пользователей.
Использует aiogram.safe_parse_webapp_init_data.
"""

import logging
from typing import Optional, Tuple

from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram.types import User as AiogramUser

from ..schemas.telegram import WebAppUser, TelegramUserSchema

logger = logging.getLogger(__name__)


class TelegramAuthService:
    """Сервис для работы с Telegram авторизацией."""

    def __init__(self, bot_token: str, bot_type: str = "main", community_id: Optional[int] = None):
        self.bot_token = bot_token
        self.bot_type = bot_type
        self.community_id = community_id
        logger.info(
            "🤖 Init %s Telegram service%s",
            bot_type,
            f" (community_id={community_id})" if community_id else "",
        )

    def verify_webapp_init_data(self, init_data: str) -> Optional[AiogramUser]:
        """
        Проверяет подлинность initData и возвращает AiogramUser,
        либо None если валидация не прошла.

        ВАЖНО: aiogram.types.User может не содержать поля is_premium.
        Поэтому мы дополнительно кэшируем признак premium на уровне сервиса,
        чтобы передать его дальше в get_user_from_telegram_data(..., is_premium=...).
        """
        try:
            parsed = safe_parse_webapp_init_data(token=self.bot_token, init_data=init_data)
            if not parsed or not parsed.user:
                logger.warning("❌ Invalid WebApp data for %s bot", self.bot_type)
                return None

            # Сохраняем premium признак отдельно (если он был в initData)
            self._last_is_premium: Optional[bool] = getattr(parsed.user, "is_premium", None)

            # Приводим к aiogram.types.User (у parsed.user это уже совместимая модель)
            # Если parsed.user уже AiogramUser — вернётся как есть.
            aiogram_user: AiogramUser = parsed.user  # type: ignore[assignment]

            logger.info(
                "✅ WebApp data valid: tg_user_id=%s via %s%s",
                aiogram_user.id,
                self.bot_type,
                f" (community_id={self.community_id})" if self.community_id else "",
            )
            return aiogram_user

        except Exception as e:
            logger.error("❌ WebApp validation error for %s bot: %s", self.bot_type, e)
            return None

    def get_user_from_telegram_data(
        self,
        telegram_user: AiogramUser,
        is_premium: Optional[bool] = None,
    ) -> WebAppUser:
        """
        Преобразует AiogramUser в нашу внутреннюю модель WebAppUser.
        premium берём приоритетно из аргумента, иначе — из последнего распарсенного initData.
        """
        if is_premium is None:
            # попробуем взять из кэша, который положили в verify_webapp_init_data
            is_premium = getattr(self, "_last_is_premium", None)

        return WebAppUser(
            telegram_user_id=telegram_user.id,
            username=getattr(telegram_user, "username", None),
            first_name=getattr(telegram_user, "first_name", None),
            last_name=getattr(telegram_user, "last_name", None),
            language_code=getattr(telegram_user, "language_code", None),
            is_premium=bool(is_premium) if is_premium is not None else False,
            allows_write_to_pm=getattr(telegram_user, "allows_write_to_pm", None),
            photo_url=getattr(telegram_user, "photo_url", None),
        )

    def convert_to_frontend_schema(self, webapp_user: WebAppUser) -> TelegramUserSchema:
        return TelegramUserSchema(
            id=webapp_user.telegram_user_id,
            first_name=webapp_user.first_name,
            last_name=webapp_user.last_name,
            username=webapp_user.username,
            language_code=webapp_user.language_code,
            is_premium=webapp_user.is_premium,
            photo_url=webapp_user.photo_url,
        )

    @property
    def is_main_bot(self) -> bool:
        return self.bot_type == "main"

    @property
    def is_community_bot(self) -> bool:
        return self.bot_type == "community"
