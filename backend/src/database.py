"""
Модуль для работы с базой данных.

Этот файл содержит:
- Настройку SQLAlchemy для асинхронной работы с PostgreSQL
- Базовый класс для всех моделей
- Функции для создания и управления подключениями
- Инициализацию глобальных таблиц при запуске
"""

import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import text, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from .config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.

    Все модели (глобальные и динамические) будут наследоваться от этого класса.
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

    # Отключаем пул для некоторых случаев (например, тестирование)
    poolclass=NullPool if settings.app.is_testing else None,

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
    expire_on_commit=False,  # Не истекать объекты после коммита
    autoflush=False,  # Не автоматически флашить изменения
    autocommit=False,  # Не автоматически коммитить транзакции
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных в FastAPI.

    Эта функция используется как зависимость в роутах FastAPI.
    Автоматически создает сессию, предоставляет ее роуту,
    и закрывает после завершения запроса.

    Yields:
        AsyncSession: Асинхронная сессия базы данных

    Example:
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_db_session)):
            # Используем db для запросов к базе данных
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            # В случае ошибки откатываем транзакцию
            await session.rollback()
            raise
        finally:
            # Всегда закрываем сессию
            await session.close()


@asynccontextmanager
async def get_db_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для получения сессии вне FastAPI.

    Используется в сервисах или других местах, где нужна сессия БД,
    но нет доступа к dependency injection FastAPI.

    Example:
        async with get_db_session_context() as db:
            result = await db.execute(select(User))
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

    Returns:
        bool: True если подключение успешно, False если есть проблемы
    """
    try:
        async with get_db_session_context() as db:
            # Выполняем простой запрос для проверки
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

        # Импортируем все модели по одной, чтобы они зарегистрировались в metadata
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


async def drop_all_tables() -> None:
    """
    Удаляет все таблицы из базы данных.

    ⚠️ ОСТОРОЖНО: Эта функция удаляет ВСЕ таблицы!
    Используется только для тестирования или полной переустановки.
    """
    try:
        logger.warning("🗑️ Удаление всех таблиц...")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        logger.warning("✅ Все таблицы удалены")

    except Exception as e:
        logger.error(f"❌ Ошибка удаления таблиц: {e}")
        raise


async def init_database() -> None:
    """
    Полная инициализация базы данных.

    Выполняет следующие шаги:
    1. Проверяет подключение к БД
    2. Создает глобальные таблицы
    3. Инициализирует начальные данные (если нужно)
    """
    logger.info("🚀 Инициализация базы данных...")

    # Проверяем подключение
    if not await check_database_connection():
        raise Exception("Не удалось подключиться к базе данных")

    # Создаем глобальные таблицы
    await create_global_tables()

    # Здесь можно добавить инициализацию начальных данных
    # await create_initial_data()

    logger.info("✅ База данных инициализирована успешно")


async def close_database() -> None:
    """
    Закрывает подключения к базе данных при завершении приложения.
    """
    logger.info("🔌 Закрытие подключений к базе данных...")
    await engine.dispose()
    logger.info("✅ Подключения к базе данных закрыты")


# Дополнительные утилиты для работы с базой данных

async def execute_raw_sql(sql: str, parameters: Optional[dict] = None) -> None:
    """
    Выполняет сырой SQL запрос.

    Полезно для выполнения сложных запросов или DDL операций.

    Args:
        sql: SQL запрос для выполнения
        parameters: Параметры для запроса (опционально)
    """
    async with get_db_session_context() as db:
        await db.execute(text(sql), parameters or {})


async def table_exists(table_name: str) -> bool:
    """
    Проверяет существование таблицы в базе данных.

    Args:
        table_name: Имя таблицы для проверки

    Returns:
        bool: True если таблица существует
    """
    sql = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = :table_name
    );
    """

    async with get_db_session_context() as db:
        result = await db.execute(text(sql), {"table_name": table_name})
        return result.scalar()


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
    "create_global_tables",
    "execute_raw_sql",
    "table_exists",
]
