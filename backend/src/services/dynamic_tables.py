"""
Сервис для создания и управления динамическими таблицами.

Этот модуль отвечает за:
- Создание уникальных ключей для новых сообществ
- Генерацию DDL для динамических таблиц
- Создание и удаление наборов таблиц для сообществ
- Получение моделей для работы с динамическими данными
"""

import logging
import uuid
from typing import Dict, Type, Optional, List
from datetime import datetime

from sqlalchemy import (
    BigInteger, Integer, String, Text, Boolean, DateTime, JSON,
    Enum, ForeignKey, Index, UniqueConstraint, text
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import Base, engine, execute_raw_sql, table_exists
from ..models.base import TimestampMixin, SoftDeleteMixin

logger = logging.getLogger(__name__)


class DynamicTableFactory:
    """
    Фабрика для создания динамических таблиц сообществ.

    Создает уникальные таблицы для каждого сообщества
    с использованием table_key как суффикса.
    """

    @staticmethod
    def generate_table_key() -> str:
        """
        Генерирует уникальный ключ для нового сообщества.

        Returns:
            str: Уникальный ключ в формате 'comm_xxxxx'
        """
        # Генерируем короткий UUID (первые 8 символов)
        short_uuid = str(uuid.uuid4()).replace('-', '')[:8]
        return f"comm_{short_uuid}"

    @staticmethod
    def get_table_name(base_name: str, table_key: str) -> str:
        """
        Формирует полное имя таблицы с ключом сообщества.

        Args:
            base_name: Базовое имя таблицы (например, 'courses')
            table_key: Ключ сообщества

        Returns:
            str: Полное имя таблицы (например, 'courses_comm_12345678')
        """
        return f"{base_name}_{table_key}"

    @classmethod
    async def create_community_tables(cls, table_key: str) -> None:
        """
        Создает полный набор таблиц для нового сообщества.

        Args:
            table_key: Уникальный ключ сообщества

        Raises:
            Exception: Если не удалось создать таблицы
        """
        logger.info(f"🔨 Создание таблиц для сообщества с ключом: {table_key}")

        try:
            # Получаем DDL для всех динамических таблиц
            ddl_statements = cls._get_all_table_ddl(table_key)

            # Выполняем каждый DDL запрос
            for table_name, ddl in ddl_statements.items():
                logger.debug(f"Создание таблицы: {table_name}")
                await execute_raw_sql(ddl)

            # Создаем индексы
            await cls._create_indexes(table_key)

            logger.info(f"✅ Таблицы для сообщества {table_key} созданы успешно")

        except Exception as e:
            logger.error(f"❌ Ошибка создания таблиц для {table_key}: {e}")
            # Пытаемся удалить частично созданные таблицы
            await cls.drop_community_tables(table_key)
            raise

    @classmethod
    async def drop_community_tables(cls, table_key: str) -> None:
        """
        Удаляет все таблицы сообщества.

        Args:
            table_key: Ключ сообщества для удаления
        """
        logger.warning(f"🗑️ Удаление таблиц для сообщества: {table_key}")

        table_names = [
            "media_files", "points_ledger", "communities_levels",
            "lesson_progress", "lessons", "course_modules",
            "courses", "community_users"
        ]

        for base_name in table_names:
            table_name = cls.get_table_name(base_name, table_key)
            try:
                if await table_exists(table_name):
                    await execute_raw_sql(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                    logger.debug(f"Удалена таблица: {table_name}")
            except Exception as e:
                logger.error(f"Ошибка удаления таблицы {table_name}: {e}")

    @classmethod
    def _get_all_table_ddl(cls, table_key: str) -> Dict[str, str]:
        """
        Генерирует DDL для всех динамических таблиц.

        Args:
            table_key: Ключ сообщества

        Returns:
            Dict[str, str]: Словарь {имя_таблицы: DDL_запрос}
        """
        return {
            cls.get_table_name("community_users", table_key): cls._get_community_users_ddl(table_key),
            cls.get_table_name("courses", table_key): cls._get_courses_ddl(table_key),
            cls.get_table_name("course_modules", table_key): cls._get_course_modules_ddl(table_key),
            cls.get_table_name("lessons", table_key): cls._get_lessons_ddl(table_key),
            cls.get_table_name("lesson_progress", table_key): cls._get_lesson_progress_ddl(table_key),
            cls.get_table_name("communities_levels", table_key): cls._get_communities_levels_ddl(table_key),
            cls.get_table_name("points_ledger", table_key): cls._get_points_ledger_ddl(table_key),
            cls.get_table_name("media_files", table_key): cls._get_media_files_ddl(table_key),
        }

    @classmethod
    def _get_community_users_ddl(cls, table_key: str) -> str:
        """DDL для таблицы пользователей сообщества."""
        table_name = cls.get_table_name("community_users", table_key)
        return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'pending')),
            joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_activity TIMESTAMP WITH TIME ZONE,
            xp_points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            deleted_at TIMESTAMP WITH TIME ZONE
        );
        """

    @classmethod
    def _get_courses_ddl(cls, table_key: str) -> str:
        """DDL для таблицы курсов."""
        table_name = cls.get_table_name("courses", table_key)
        community_users_table = cls.get_table_name("community_users", table_key)
        return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            cover_url TEXT,
            status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
            is_locked BOOLEAN DEFAULT FALSE,
            requirements JSON,
            tags JSON,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by BIGINT REFERENCES {community_users_table}(id) ON DELETE SET NULL,
            deleted_at TIMESTAMP WITH TIME ZONE,
            published_at TIMESTAMP WITH TIME ZONE
        );
        """

    @classmethod
    def _get_course_modules_ddl(cls, table_key: str) -> str:
        """DDL для таблицы модулей курсов."""
        table_name = cls.get_table_name("course_modules", table_key)
        courses_table = cls.get_table_name("courses", table_key)
        community_users_table = cls.get_table_name("community_users", table_key)
        return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            course_id BIGINT NOT NULL REFERENCES {courses_table}(id) ON DELETE CASCADE,
            title VARCHAR(500) NOT NULL,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            deleted_at TIMESTAMP WITH TIME ZONE,
            created_by BIGINT REFERENCES {community_users_table}(id) ON DELETE SET NULL
        );
        """

    @classmethod
    def _get_lessons_ddl(cls, table_key: str) -> str:
        """DDL для таблицы уроков."""
        table_name = cls.get_table_name("lessons", table_key)
        courses_table = cls.get_table_name("courses", table_key)
        modules_table = cls.get_table_name("course_modules", table_key)
        community_users_table = cls.get_table_name("community_users", table_key)
        return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            course_id BIGINT REFERENCES {courses_table}(id) ON DELETE CASCADE,
            module_id BIGINT REFERENCES {modules_table}(id) ON DELETE CASCADE,
            title VARCHAR(500) NOT NULL,
            content_tiptap JSONB,
            is_published BOOLEAN DEFAULT FALSE,
            sort_order INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            deleted_at TIMESTAMP WITH TIME ZONE,
            created_by BIGINT REFERENCES {community_users_table}(id) ON DELETE SET NULL
        );
        """

    @classmethod
    def _get_lesson_progress_ddl(cls, table_key: str) -> str:
        """DDL для таблицы прогресса уроков."""
        table_name = cls.get_table_name("lesson_progress", table_key)
        community_users_table = cls.get_table_name("community_users", table_key)
        lessons_table = cls.get_table_name("lessons", table_key)
        return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES {community_users_table}(id) ON DELETE CASCADE,
            lesson_id BIGINT NOT NULL REFERENCES {lessons_table}(id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed')),
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            UNIQUE(user_id, lesson_id)
        );
        """

    @classmethod
    def _get_communities_levels_ddl(cls, table_key: str) -> str:
        """DDL для таблицы уровней сообщества."""
        table_name = cls.get_table_name("communities_levels", table_key)
        community_users_table = cls.get_table_name("community_users", table_key)
        return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            level_id INTEGER NOT NULL,
            level_name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            deleted_at TIMESTAMP WITH TIME ZONE,
            created_by BIGINT REFERENCES {community_users_table}(id) ON DELETE SET NULL,
            UNIQUE(level_id)
        );
        """

    @classmethod
    def _get_points_ledger_ddl(cls, table_key: str) -> str:
        """DDL для таблицы журнала очков."""
        table_name = cls.get_table_name("points_ledger", table_key)
        community_users_table = cls.get_table_name("community_users", table_key)
        return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL REFERENCES {community_users_table}(id) ON DELETE CASCADE,
            points INTEGER NOT NULL,
            description VARCHAR(500),
            rule_id BIGINT REFERENCES gamification_rules(id) ON DELETE SET NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            get_by BIGINT REFERENCES {community_users_table}(id) ON DELETE SET NULL
        );
        """

    @classmethod
    def _get_media_files_ddl(cls, table_key: str) -> str:
        """DDL для таблицы медиафайлов."""
        table_name = cls.get_table_name("media_files", table_key)
        community_users_table = cls.get_table_name("community_users", table_key)
        lessons_table = cls.get_table_name("lessons", table_key)
        return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id BIGSERIAL PRIMARY KEY,
            uploaded_by BIGINT NOT NULL REFERENCES {community_users_table}(id) ON DELETE CASCADE,
            original_filename VARCHAR(500) NOT NULL,
            file_path TEXT NOT NULL,
            file_type VARCHAR(10) NOT NULL,
            lesson_id BIGINT REFERENCES {lessons_table}(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            deleted_at TIMESTAMP WITH TIME ZONE
        );
        """

    @classmethod
    async def _create_indexes(cls, table_key: str) -> None:
        """
        Создает индексы для всех динамических таблиц.

        Args:
            table_key: Ключ сообщества
        """
        logger.debug(f"Создание индексов для сообщества: {table_key}")

        indexes = [
            # community_users индексы
            f"CREATE INDEX IF NOT EXISTS ix_community_users_{table_key}_user_id ON community_users_{table_key}(user_id);",
            f"CREATE INDEX IF NOT EXISTS ix_community_users_{table_key}_status ON community_users_{table_key}(status);",
            f"CREATE INDEX IF NOT EXISTS ix_community_users_{table_key}_xp_points ON community_users_{table_key}(xp_points);",
            f"CREATE INDEX IF NOT EXISTS ix_community_users_{table_key}_level ON community_users_{table_key}(level);",

            # courses индексы
            f"CREATE INDEX IF NOT EXISTS ix_courses_{table_key}_status ON courses_{table_key}(status);",
            f"CREATE INDEX IF NOT EXISTS ix_courses_{table_key}_created_by ON courses_{table_key}(created_by);",
            f"CREATE INDEX IF NOT EXISTS ix_courses_{table_key}_sort_order ON courses_{table_key}(sort_order);",
            f"CREATE INDEX IF NOT EXISTS ix_courses_{table_key}_tags ON courses_{table_key} USING GIN(tags);",

            # course_modules индексы
            f"CREATE INDEX IF NOT EXISTS ix_course_modules_{table_key}_course_id ON course_modules_{table_key}(course_id);",
            f"CREATE INDEX IF NOT EXISTS ix_course_modules_{table_key}_sort_order ON course_modules_{table_key}(sort_order);",

            # lessons индексы
            f"CREATE INDEX IF NOT EXISTS ix_lessons_{table_key}_course_id ON lessons_{table_key}(course_id);",
            f"CREATE INDEX IF NOT EXISTS ix_lessons_{table_key}_module_id ON lessons_{table_key}(module_id);",
            f"CREATE INDEX IF NOT EXISTS ix_lessons_{table_key}_is_published ON lessons_{table_key}(is_published);",
            f"CREATE INDEX IF NOT EXISTS ix_lessons_{table_key}_sort_order ON lessons_{table_key}(sort_order);",

            # lesson_progress индексы
            f"CREATE INDEX IF NOT EXISTS ix_lesson_progress_{table_key}_user_id ON lesson_progress_{table_key}(user_id);",
            f"CREATE INDEX IF NOT EXISTS ix_lesson_progress_{table_key}_lesson_id ON lesson_progress_{table_key}(lesson_id);",
            f"CREATE INDEX IF NOT EXISTS ix_lesson_progress_{table_key}_status ON lesson_progress_{table_key}(status);",

            # points_ledger индексы
            f"CREATE INDEX IF NOT EXISTS ix_points_ledger_{table_key}_user_id ON points_ledger_{table_key}(user_id);",
            f"CREATE INDEX IF NOT EXISTS ix_points_ledger_{table_key}_created_at ON points_ledger_{table_key}(created_at);",
            f"CREATE INDEX IF NOT EXISTS ix_points_ledger_{table_key}_rule_id ON points_ledger_{table_key}(rule_id);",

            # communities_levels индексы
            f"CREATE INDEX IF NOT EXISTS ix_communities_levels_{table_key}_level_id ON communities_levels_{table_key}(level_id);",

            # media_files индексы
            f"CREATE INDEX IF NOT EXISTS ix_media_files_{table_key}_uploaded_by ON media_files_{table_key}(uploaded_by);",
            f"CREATE INDEX IF NOT EXISTS ix_media_files_{table_key}_lesson_id ON media_files_{table_key}(lesson_id);",
            f"CREATE INDEX IF NOT EXISTS ix_media_files_{table_key}_file_type ON media_files_{table_key}(file_type);",
        ]

        for index_sql in indexes:
            try:
                await execute_raw_sql(index_sql)
            except Exception as e:
                logger.warning(f"Не удалось создать индекс: {e}")

    @classmethod
    async def check_community_tables_exist(cls, table_key: str) -> bool:
        """
        Проверяет существование всех таблиц сообщества.

        Args:
            table_key: Ключ сообщества

        Returns:
            bool: True если все таблицы существуют
        """
        required_tables = [
            "community_users", "courses", "course_modules", "lessons",
            "lesson_progress", "communities_levels", "points_ledger", "media_files"
        ]

        for base_name in required_tables:
            table_name = cls.get_table_name(base_name, table_key)
            if not await table_exists(table_name):
                return False

        return True

    @classmethod
    async def get_community_table_stats(cls, table_key: str) -> Dict[str, int]:
        """
        Получает статистику по таблицам сообщества.

        Args:
            table_key: Ключ сообщества

        Returns:
            Dict[str, int]: Словарь с количеством записей в каждой таблице
        """
        stats = {}
        table_names = [
            "community_users", "courses", "course_modules", "lessons",
            "lesson_progress", "communities_levels", "points_ledger", "media_files"
        ]

        for base_name in table_names:
            table_name = cls.get_table_name(base_name, table_key)
            try:
                # Выполняем COUNT запрос
                from ..database import get_db_session_context
                async with get_db_session_context() as db:
                    result = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    stats[base_name] = count
            except Exception as e:
                logger.error(f"Ошибка получения статистики для {table_name}: {e}")
                stats[base_name] = 0

        return stats


class DynamicTableManager:
    """
    Менеджер для работы с динамическими таблицами сообществ.

    Предоставляет высокоуровневые методы для управления
    таблицами сообществ и работы с ними.
    """

    def __init__(self):
        self.factory = DynamicTableFactory()

    async def create_new_community_tables(self, community_name: str) -> str:
        """
        Создает таблицы для нового сообщества.

        Args:
            community_name: Название сообщества (для логирования)

        Returns:
            str: Сгенерированный table_key

        Raises:
            Exception: Если не удалось создать таблицы
        """
        table_key = self.factory.generate_table_key()

        logger.info(f"🏗️ Создание нового сообщества '{community_name}' с ключом '{table_key}'")

        try:
            await self.factory.create_community_tables(table_key)
            logger.info(f"✅ Сообщество '{community_name}' создано успешно")
            return table_key
        except Exception as e:
            logger.error(f"❌ Ошибка создания сообщества '{community_name}': {e}")
            raise

    async def delete_community_tables(self, table_key: str, community_name: str = None) -> None:
        """
        Удаляет все таблицы сообщества.

        Args:
            table_key: Ключ сообщества
            community_name: Название сообщества (для логирования)
        """
        name_info = f" '{community_name}'" if community_name else ""
        logger.warning(f"🗑️ Удаление сообщества{name_info} с ключом '{table_key}'")

        await self.factory.drop_community_tables(table_key)
        logger.warning(f"✅ Сообщество{name_info} удалено")

    async def verify_community_tables(self, table_key: str) -> bool:
        """
        Проверяет целостность таблиц сообщества.

        Args:
            table_key: Ключ сообщества

        Returns:
            bool: True если все таблицы в порядке
        """
        return await self.factory.check_community_tables_exist(table_key)

    async def repair_community_tables(self, table_key: str) -> None:
        """
        Восстанавливает отсутствующие таблицы сообщества.

        Args:
            table_key: Ключ сообщества для восстановления
        """
        logger.info(f"🔧 Восстановление таблиц для сообщества '{table_key}'")

        # Проверяем какие таблицы отсутствуют и создаем их
        required_tables = [
            "community_users", "courses", "course_modules", "lessons",
            "lesson_progress", "communities_levels", "points_ledger", "media_files"
        ]

        ddl_statements = self.factory._get_all_table_ddl(table_key)

        for base_name in required_tables:
            table_name = self.factory.get_table_name(base_name, table_key)

            if not await table_exists(table_name):
                logger.info(f"Восстановление таблицы: {table_name}")
                await execute_raw_sql(ddl_statements[table_name])

        # Восстанавливаем индексы
        await self.factory._create_indexes(table_key)

        logger.info(f"✅ Восстановление таблиц для '{table_key}' завершено")

    async def get_community_info(self, table_key: str) -> Dict:
        """
        Получает информацию о сообществе и его таблицах.

        Args:
            table_key: Ключ сообщества

        Returns:
            Dict: Информация о сообществе
        """
        exists = await self.verify_community_tables(table_key)
        stats = await self.factory.get_community_table_stats(table_key) if exists else {}

        return {
            "table_key": table_key,
            "tables_exist": exists,
            "table_stats": stats,
            "total_records": sum(stats.values()) if stats else 0
        }


# Создаем глобальный экземпляр менеджера
dynamic_table_manager = DynamicTableManager()

# Экспортируем основные классы и функции
__all__ = [
    "DynamicTableFactory",
    "DynamicTableManager",
    "dynamic_table_manager",
]
