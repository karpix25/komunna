"""
Модуль для работы с базой данных PostgreSQL.
Настройка SQLAlchemy, создание соединений и инициализация таблиц.
"""

import logging
from typing import AsyncGenerator, Any, Optional, Mapping
from contextlib import asynccontextmanager

from sqlalchemy import text, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase

from .config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Содержит общие настройки для всех таблиц.
    """

    # Настройка именования ограничений для миграций
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


# Создаем асинхронный движок базы данных
engine = create_async_engine(
    settings.database.url,
    # Настройки пула подключений
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.connect_timeout,

    # Для разработки - показываем SQL запросы
    echo=settings.app.is_development,

    # Настройки для PostgreSQL
    connect_args={
        "server_settings": {
            "application_name": settings.app.project_name,
        }
    }
)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных в FastAPI.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для получения сессии вне FastAPI.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """
    Проверяет подключение к базе данных.
    """
    try:
        async with get_db_session_context() as db:
            result = await db.execute(text("SELECT 1"))
            result.scalar()
            logger.info("✅ Подключение к базе данных успешно")
            return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к базе данных: {e}")
        return False


async def create_global_tables() -> None:
    """
    Создает все глобальные таблицы при запуске приложения.
    """
    try:
        logger.info("🔨 Создание глобальных таблиц...")

        # Импортируем все модели, чтобы они зарегистрировались в metadata
        from .models.user import User
        from .models.telegram_bot import TelegramBot
        from .models.telegram_group import TelegramGroup
        from .models.community import Community
        from .models.community_admin import CommunityAdmin
        from .models.gamification import GamificationRule, LevelRule

        # Создаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Глобальные таблицы созданы успешно")

    except Exception as e:
        logger.error(f"❌ Ошибка создания глобальных таблиц: {e}")
        raise


async def init_database() -> None:
    """
    Полная инициализация базы данных.
    """
    logger.info("🚀 Инициализация базы данных...")

    # Проверяем подключение
    if not await check_database_connection():
        raise Exception("Не удалось подключиться к базе данных")

    # Создаем глобальные таблицы
    await create_global_tables()

    logger.info("✅ База данных инициализирована успешно")


async def close_database() -> None:
    """
    Закрывает подключения к базе данных при завершении приложения.
    """
    logger.info("🔌 Закрытие подключений к базе данных...")
    await engine.dispose()
    logger.info("✅ Подключения к базе данных закрыты")


async def execute_raw_sql(
    sql: str,
    params: Optional[Mapping[str, Any]] = None,
    *,
    autocommit: bool = True,
) -> None:
    """
    Выполнить произвольный SQL (DDL/DML). Ничего не возвращает.
    Используется динамическими таблицами для CREATE/DROP/ALTER.
    """
    async with engine.begin() as conn:
        if params:
            await conn.execute(text(sql), params)
        else:
            await conn.execute(text(sql))
    # engine.begin() сам коммитит транзакцию; autocommit здесь для совместимости с прошлым кодом


async def table_exists(table_name: str, schema: str = "public") -> bool:
    """
    Проверяет существование таблицы в схеме (по умолчанию public).
    """
    query = text("""
        SELECT to_regclass(:qualified) IS NOT NULL
    """)
    qualified = f"{schema}.{table_name}" if schema else table_name
    async with engine.begin() as conn:
        res = await conn.execute(query, {"qualified": qualified})
        return bool(res.scalar())


# Экспортируем основные объекты
__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_db_session",
    "get_db_session_context",
    "init_database",
    "close_database",
    "check_database_connection",
    "execute_raw_sql",
    "table_exists",
]