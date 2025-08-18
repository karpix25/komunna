"""
Детектор типа авторизации для определения какой бот использовать.

Анализирует запрос и определяет нужен ли главный бот или бот сообщества.
"""

import logging
from typing import Optional, Tuple
from urllib.parse import urlparse

from fastapi import Request

logger = logging.getLogger(__name__)


class AuthTypeDetector:
    """Детектор типа авторизации."""

    @staticmethod
    def detect_auth_type(request: Request) -> Tuple[str, Optional[int]]:
        """
        Определяет тип авторизации на основе запроса.

        Логика определения:
        1. Если есть заголовок X-Community-ID -> используем бот сообщества
        2. Если URL содержит /community/{id}/ -> используем бот сообщества
        3. Если поддомен указывает на сообщество -> используем бот сообщества
        4. Во всех остальных случаях -> главный бот

        Args:
            request: HTTP запрос

        Returns:
            Tuple[str, Optional[int]]: (тип_авторизации, community_id)
            где тип_авторизации: "main" или "community"
        """
        # Метод 1: Явный заголовок с ID сообщества
        community_id_header = request.headers.get("X-Community-ID")
        if community_id_header:
            try:
                community_id = int(community_id_header)
                logger.info(f"🎯 Определен тип авторизации: community (ID: {community_id}) через заголовок")
                return "community", community_id
            except ValueError:
                logger.warning(f"❌ Невалидный X-Community-ID заголовок: {community_id_header}")

        # Метод 2: URL содержит community/{id}
        url_path = request.url.path
        if "/community/" in url_path:
            try:
                # Ищем паттерн /community/{id}/
                parts = url_path.split("/")
                community_idx = parts.index("community")
                if community_idx + 1 < len(parts):
                    community_id = int(parts[community_idx + 1])
                    logger.info(f"🎯 Определен тип авторизации: community (ID: {community_id}) через URL")
                    return "community", community_id
            except (ValueError, IndexError):
                logger.warning(f"❌ Не удалось извлечь community_id из URL: {url_path}")

        # Метод 3: Поддомен указывает на сообщество
        host = request.headers.get("host", "")
        community_id = AuthTypeDetector._extract_community_from_subdomain(host)
        if community_id:
            logger.info(f"🎯 Определен тип авторизации: community (ID: {community_id}) через поддомен")
            return "community", community_id

        # Метод 4: По умолчанию - главный бот
        logger.info("🎯 Определен тип авторизации: main (главное приложение)")
        return "main", None

    @staticmethod
    def _extract_community_from_subdomain(host: str) -> Optional[int]:
        """
        Извлекает ID сообщества из поддомена.

        Поддерживаемые форматы:
        - community-123.yourdomain.com -> 123
        - comm123.yourdomain.com -> 123
        - school-456.yourdomain.com -> 456

        Args:
            host: Хост из заголовка запроса

        Returns:
            ID сообщества или None
        """
        try:
            if not host or "localhost" in host or "127.0.0.1" in host:
                return None

            # Извлекаем поддомен
            parts = host.split(".")
            if len(parts) < 3:  # Нет поддомена
                return None

            subdomain = parts[0]

            # Ищем паттерны с ID сообщества
            patterns = [
                "community-",
                "comm",
                "school-",
                "c-"
            ]

            for pattern in patterns:
                if subdomain.startswith(pattern):
                    id_part = subdomain[len(pattern):]
                    if id_part.isdigit():
                        return int(id_part)

            return None

        except Exception as e:
            logger.warning(f"❌ Ошибка извлечения community_id из поддомена {host}: {e}")
            return None


# Создаем глобальный экземпляр детектора
auth_detector = AuthTypeDetector()
