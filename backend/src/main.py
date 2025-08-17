"""
Главный файл FastAPI приложения.

Настраивает и запускает веб-сервер с API для Telegram Skool платформы.
Инициализирует базу данных, middleware, роуты и обработчики событий.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn

from .config import settings
from .database import init_database, close_database, check_database_connection
from .services.dynamic_tables import dynamic_table_manager

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.logging.level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Управление жизненным циклом приложения.

    Выполняется при запуске и завершении приложения.
    Инициализирует базу данных и очищает ресурсы.
    """
    # ========== ЗАПУСК ПРИЛОЖЕНИЯ ==========
    logger.info(f"🚀 Запуск {settings.app.project_name} в режиме {settings.app.environment}")

    try:
        # Инициализируем базу данных
        logger.info("📊 Инициализация базы данных...")
        await init_database()

        # Проверяем подключение
        if await check_database_connection():
            logger.info("✅ База данных готова к работе")
        else:
            raise Exception("Не удалось подключиться к базе данных")

        # Здесь можно добавить инициализацию других сервисов
        # await init_redis()
        # await init_file_storage()

        logger.info(f"🎉 {settings.app.project_name} успешно запущен!")
        logger.info(f"📡 API доступно по адресу: http://{settings.app.host}:{settings.app.port}")
        logger.info(f"📚 Документация доступна: http://{settings.app.host}:{settings.app.port}{settings.app.docs_url}")

    except Exception as e:
        logger.error(f"❌ Ошибка запуска приложения: {e}")
        raise

    # ========== ПРИЛОЖЕНИЕ РАБОТАЕТ ==========
    yield

    # ========== ЗАВЕРШЕНИЕ ПРИЛОЖЕНИЯ ==========
    logger.info("🛑 Завершение работы приложения...")

    try:
        # Закрываем подключения к базе данных
        await close_database()

        # Здесь можно добавить очистку других ресурсов
        # await close_redis()
        # await cleanup_file_storage()

        logger.info("✅ Приложение завершено корректно")

    except Exception as e:
        logger.error(f"❌ Ошибка при завершении: {e}")


def create_application() -> FastAPI:
    """
    Создает и настраивает экземпляр FastAPI приложения.

    Returns:
        FastAPI: Настроенное приложение
    """
    # Создаем приложение с настройками
    app = FastAPI(
        title=settings.app.project_name,
        description="API для платформы онлайн обучения в Telegram",
        version="1.0.0",
        docs_url=settings.app.docs_url if not settings.app.is_production else None,
        redoc_url="/redoc" if not settings.app.is_production else None,
        openapi_url="/openapi.json" if not settings.app.is_production else None,
        lifespan=lifespan,
        debug=settings.app.debug
    )

    # Настраиваем middleware
    setup_middleware(app)

    # Настраиваем обработчики ошибок
    setup_exception_handlers(app)

    # Подключаем роуты
    setup_routes(app)

    return app


def setup_middleware(app: FastAPI) -> None:
    """
    Настраивает middleware для приложения.

    Args:
        app: Экземпляр FastAPI приложения
    """
    # CORS - разрешаем запросы с фронтенда
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.app.is_development else [
            "https://yourdomain.com",  # Замените на ваш домен
            "https://www.yourdomain.com"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Ограничиваем разрешенные хосты в продакшене
    if settings.app.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["yourdomain.com", "*.yourdomain.com"]  # Замените на ваши домены
        )

    # Добавляем custom middleware для логирования запросов
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Логирует входящие HTTP запросы."""
        start_time = time.time()

        # Выполняем запрос
        response = await call_next(request)

        # Логируем результат
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )

        return response


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Настраивает обработчики ошибок.

    Args:
        app: Экземпляр FastAPI приложения
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Обработчик HTTP ошибок."""
        logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Обработчик ошибок валидации."""
        logger.warning(f"Validation error: {exc.errors()} - {request.url}")
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "Ошибка валидации данных",
                "details": exc.errors(),
                "status_code": 422
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Обработчик всех остальных ошибок."""
        logger.error(f"Unexpected error: {exc} - {request.url}", exc_info=True)

        # В продакшене не показываем детали ошибки
        if settings.app.is_production:
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Внутренняя ошибка сервера",
                    "status_code": 500
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Внутренняя ошибка сервера",
                    "details": str(exc) if settings.app.show_traceback else None,
                    "status_code": 500
                }
            )


def setup_routes(app: FastAPI) -> None:
    """
    Подключает все роуты к приложению.

    Args:
        app: Экземпляр FastAPI приложения
    """

    # Базовый роут для проверки работоспособности
    @app.get("/")
    async def root():
        """Базовый endpoint для проверки работы API."""
        return {
            "message": f"Добро пожаловать в {settings.app.project_name} API!",
            "version": "1.0.0",
            "environment": settings.app.environment,
            "docs": f"{settings.app.docs_url}" if not settings.app.is_production else "Недоступно в продакшене"
        }

    @app.get("/health")
    async def health_check():
        """Endpoint для проверки состояния сервиса."""
        # Проверяем подключение к базе данных
        db_healthy = await check_database_connection()

        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "timestamp": datetime.utcnow().isoformat()
        }

    # 🆕 ДОБАВЛЕНО: Подключаем API роуты
    from .api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")

    # Пока добавляем базовые роуты для тестирования
    setup_test_routes(app)


def setup_test_routes(app: FastAPI) -> None:
    """
    Временные тестовые роуты для проверки динамических таблиц.
    Эти роуты будут удалены когда появятся настоящие API endpoints.

    Args:
        app: Экземпляр FastAPI приложения
    """

    @app.post("/test/create-community/{community_name}")
    async def test_create_community(community_name: str):
        """Тестовый endpoint для создания сообщества."""
        try:
            table_key = await dynamic_table_manager.create_new_community_tables(community_name)
            return {
                "success": True,
                "message": f"Сообщество '{community_name}' создано",
                "table_key": table_key
            }
        except Exception as e:
            logger.error(f"Ошибка создания сообщества: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/test/community-info/{table_key}")
    async def test_get_community_info(table_key: str):
        """Тестовый endpoint для получения информации о сообществе."""
        try:
            info = await dynamic_table_manager.get_community_info(table_key)
            return info
        except Exception as e:
            logger.error(f"Ошибка получения информации: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/test/community/{table_key}")
    async def test_delete_community(table_key: str):
        """Тестовый endpoint для удаления сообщества."""
        try:
            await dynamic_table_manager.delete_community_tables(table_key)
            return {
                "success": True,
                "message": f"Сообщество с ключом '{table_key}' удалено"
            }
        except Exception as e:
            logger.error(f"Ошибка удаления сообщества: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# Создаем экземпляр приложения
app = create_application()


def main():
    """
    Точка входа для запуска приложения.

    Используется при запуске через: python -m src.main
    """
    import time
    from datetime import datetime

    uvicorn.run(
        "src.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload and settings.app.is_development,
        log_level=settings.logging.level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
