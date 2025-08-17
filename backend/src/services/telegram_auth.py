"""
Сервис для авторизации и валидации Telegram пользователей.

Использует aiogram для проверки данных Telegram WebApp.
"""

import logging
from typing import Optional

from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram.types import User as AiogramUser

from ..schemas.telegram import WebAppUser, TelegramUserSchema

logger = logging.getLogger(__name__)


class TelegramAuthService:
    """Сервис для работы с Telegram авторизацией."""

    def __init__(self, bot_token: str, bot_type: str = "main", community_id: Optional[int] = None):
        """
        Инициализирует сервис с токеном бота.

        Args:
            bot_token: Токен Telegram бота для валидации
            bot_type: Тип бота ("main" или "community")
            community_id: ID сообщества (для ботов сообществ)
        """
        self.bot_token = bot_token
        self.bot_type = bot_type
        self.community_id = community_id

        logger.info(f"🤖 Инициализирован {bot_type} Telegram сервис" +
                   (f" для сообщества {community_id}" if community_id else ""))

    def verify_webapp_init_data(self, init_data: str) -> Optional[AiogramUser]:
        """
        Проверяет подлинность данных Telegram WebApp.

        Args:
            init_data: Строка с данными инициализации от Telegram

        Returns:
            AiogramUser или None если данные невалидны
        """
        try:
            # Используем aiogram для безопасной проверки данных
            parsed_data = safe_parse_webapp_init_data(
                token=self.bot_token,
                init_data=init_data
            )

            if parsed_data and parsed_data.user:
                logger.info(
                    f"✅ Успешная валидация пользователя: {parsed_data.user.id} "
                    f"через {self.bot_type} бот" +
                    (f" сообщества {self.community_id}" if self.community_id else "")
                )
                return parsed_data.user
            else:
                logger.warning(f"❌ Невалидные данные WebApp для {self.bot_type} бота")
                return None

        except Exception as e:
            logger.error(f"❌ Ошибка валидации WebApp данных для {self.bot_type} бота: {e}")
            return None

    def get_user_from_telegram_data(self, telegram_user: AiogramUser) -> WebAppUser:
        """
        Преобразует данные Telegram пользователя в нашу модель.

        Args:
            telegram_user: Пользователь от aiogram

        Returns:
            WebAppUser: Наша модель пользователя
        """
        return WebAppUser(
            telegram_user_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            language_code=telegram_user.language_code,
            is_premium=telegram_user.is_premium or False,
            allows_write_to_pm=getattr(telegram_user, 'allows_write_to_pm', None),
            photo_url=None  # aiogram не предоставляет photo_url напрямую
        )

    def convert_to_frontend_schema(self, webapp_user: WebAppUser) -> TelegramUserSchema:
        """
        Преобразует WebAppUser в схему для frontend.

        Args:
            webapp_user: Внутренняя модель пользователя

        Returns:
            TelegramUserSchema: Схема для frontend
        """
        return TelegramUserSchema(
            id=webapp_user.telegram_user_id,
            first_name=webapp_user.first_name,
            last_name=webapp_user.last_name,
            username=webapp_user.username,
            language_code=webapp_user.language_code,
            is_premium=webapp_user.is_premium,
            photo_url=webapp_user.photo_url
        )

    @property
    def is_main_bot(self) -> bool:
        """Проверяет, является ли это главным ботом."""
        return self.bot_type == "main"

    @property
    def is_community_bot(self) -> bool:
        """Проверяет, является ли это ботом сообщества."""
        return self.bot_type == "community"
