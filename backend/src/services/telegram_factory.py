"""
Фабрика для создания Telegram сервисов авторизации.
Управляет различными ботами: главный бот и боты сообществ.
"""

import logging
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.telegram_bot import TelegramBot
from ..models.community import Community
from ..config import settings
from .telegram_auth import TelegramAuthService

logger = logging.getLogger(__name__)


class TelegramServiceFactory:
    """
    Фабрика для создания сервисов Telegram авторизации.
    Поддерживает главный бот приложения (токен из .env).
    """

    def __init__(self):
        """Инициализирует фабрику."""
        self._services_cache: Dict[str, TelegramAuthService] = {}

    def get_main_bot_service(self) -> Optional[TelegramAuthService]:
        """
        Возвращает сервис для главного бота приложения.

        Returns:
            TelegramAuthService или None если токен не настроен
        """
        main_bot_token = settings.telegram.main_bot_token
        if not main_bot_token:
            logger.warning("❌ Токен главного бота не настроен")
            return None

        cache_key = "main_bot"
        if cache_key not in self._services_cache:
            self._services_cache[cache_key] = TelegramAuthService(
                bot_token=main_bot_token,
                bot_type="main"
            )
            logger.info("✅ Создан сервис для главного бота")

        return self._services_cache[cache_key]

    async def get_community_bot_service(
            self,
            community_id: int,
            db: AsyncSession
    ) -> Optional[TelegramAuthService]:
        """
        Возвращает сервис для бота конкретного сообщества.

        Args:
            community_id: ID сообщества
            db: Сессия базы данных

        Returns:
            TelegramAuthService или None если бот не найден
        """
        cache_key = f"community_{community_id}"

        if cache_key not in self._services_cache:
            # Получаем бота из базы данных
            bot_token = await self._get_community_bot_token(community_id, db)
            if not bot_token:
                logger.warning(f"❌ Бот для сообщества {community_id} не найден")
                return None

            self._services_cache[cache_key] = TelegramAuthService(
                bot_token=bot_token,
                bot_type="community",
                community_id=community_id
            )
            logger.info(f"✅ Создан сервис для бота сообщества {community_id}")

        return self._services_cache[cache_key]

    async def _get_community_bot_token(
            self,
            community_id: int,
            db: AsyncSession
    ) -> Optional[str]:
        """
        Получает токен бота сообщества из базы данных.

        Args:
            community_id: ID сообщества
            db: Сессия базы данных

        Returns:
            Расшифрованный токен бота или None
        """
        try:
            # Получаем сообщество с его ботом
            stmt = select(Community).where(Community.id == community_id)
            result = await db.execute(stmt)
            community = result.scalar_one_or_none()

            if not community or not community.telegram_bot_id:
                logger.warning(f"❌ Сообщество {community_id} или его бот не найден")
                return None

            # Получаем бота
            stmt = select(TelegramBot).where(TelegramBot.id == community.telegram_bot_id)
            result = await db.execute(stmt)
            bot = result.scalar_one_or_none()

            if not bot or not bot.is_active:
                logger.warning(f"❌ Активный бот для сообщества {community_id} не найден")
                return None

            # Возвращаем токен (в будущем здесь будет расшифровка)
            logger.info(f"✅ Получен токен бота для сообщества {community_id}")
            return bot.token

        except Exception as e:
            logger.error(f"❌ Ошибка получения токена бота для сообщества {community_id}: {e}")
            return None

    def clear_cache(self) -> None:
        """Очищает кэш сервисов."""
        self._services_cache.clear()
        logger.info("🗑️ Кэш Telegram сервисов очищен")

    def remove_community_from_cache(self, community_id: int) -> None:
        """
        Удаляет сервис сообщества из кэша.

        Args:
            community_id: ID сообщества для удаления из кэша
        """
        cache_key = f"community_{community_id}"
        if cache_key in self._services_cache:
            del self._services_cache[cache_key]
            logger.info(f"🗑️ Сервис сообщества {community_id} удален из кэша")


# Создаем глобальный экземпляр фабрики
telegram_factory = TelegramServiceFactory()
