"""
Главный файл FastAPI приложения Kommuna.
Базовая настройка без эндпоинтов - только здоровье и инициализация БД.
"""

import os
import logging
from contextlib import asynccontextmanager
from urllib.parse import urlparse
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aiogram import Bot
from bot.src.main_bot.app import build_dispatcher

from .config import settings
from .database import init_database, close_database, check_database_connection

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.logging.level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

WEBHOOK_PATH = "/bot/webhook"  # <- путь, по которому слушаем
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


def _build_webhook_url() -> str | None:
    # Позволяем задать готовый полный URL, если хочешь
    full = (os.getenv("TELEGRAM_WEBHOOK_URL") or "").strip()
    if full:
        return full

    domain = (os.getenv("TELEGRAM_WEBHOOK_DOMAIN") or "").strip()
    if not domain:
        return None

    # Принимаем домен в любом виде: "e5940...", "https://e5940.../",
    # "https://e5940.../что-то" — и приводим к "https://host"
    parsed = urlparse(domain if domain.startswith("http") else f"https://{domain}")
    host = parsed.netloc or parsed.path  # если передали просто "e5940..."
    host = host.rstrip("/")              # убираем хвостовой "/"
    return f"https://{host}{WEBHOOK_PATH}"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Управление жизненным циклом приложения.
    Инициализирует БД при запуске и очищает ресурсы при завершении.
    """
    # ========== ЗАПУСК ПРИЛОЖЕНИЯ ==========
    logger.info(f"🚀 Запуск {settings.app.project_name} в режиме {settings.app.environment}")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(token=token)
    dp = build_dispatcher()

    def _iter_routers(r):
        # обойдём дерево рекурсивно
        for child in getattr(r, "sub_routers", []):
            yield child
            yield from _iter_routers(child)

    names = [r.name or "<noname>" for r in _iter_routers(dp)]
    logger.info("DP routers connected: %s", names)

    await dp.emit_startup(bot=bot)  # <--- важно
    logger.info("DP startup emitted")
    app.state.bot = bot
    app.state.dp = dp
    logger.info("Aiogram Bot & Dispatcher initialized")

    url = _build_webhook_url()
    logger.info("Computed webhook URL: %r", url)

    if url:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.set_webhook(
                url=url,
                secret_token=WEBHOOK_SECRET or None,
                allowed_updates=["message", "callback_query"],
            )
            logger.info("Webhook set to %s", url)
        except Exception as e:
            logger.exception("Failed to set webhook: %s", e)

    try:
        yield
    finally:
        # --- shutdown ---
        try:
            # ✅ и событие завершения
            await dp.emit_shutdown(bot=bot)  # <--- важно
            logger.info("DP shutdown emitted")
        except Exception:
            logger.exception("DP shutdown failed")
        await bot.session.close()
        logger.info("Bot session closed")

    try:
        # Инициализируем базу данных
        logger.info("📊 Инициализация базы данных...")
        await init_database()

        # Проверяем подключение
        if await check_database_connection():
            logger.info("✅ База данных готова к работе")
        else:
            raise Exception("Не удалось подключиться к базе данных")

        logger.info(f"🎉 {settings.app.project_name} успешно запущен!")
        logger.info(f"📡 API доступно по адресу: http://{settings.app.host}:{settings.app.port}")
        if not settings.app.is_production:
            logger.info(f"📚 Документация: http://{settings.app.host}:{settings.app.port}/docs")

        yield

    except Exception as e:
        logger.error(f"❌ Ошибка запуска приложения: {e}")
        raise
    finally:
        await bot.session.close()
        logger.info("Bot session closed")

    # ========== ПРИЛОЖЕНИЕ РАБОТАЕТ ==========
    yield

    # ========== ЗАВЕРШЕНИЕ ПРИЛОЖЕНИЯ ==========
    logger.info("🛑 Завершение работы приложения...")

    try:
        # Закрываем подключения к базе данных
        await close_database()
        logger.info("✅ Приложение завершено корректно")
    except Exception as e:
        logger.error(f"❌ Ошибка при завершении: {e}")


def create_application() -> FastAPI:
    """
    Создает и настраивает экземпляр FastAPI приложения.
    """
    # Создаем приложение с настройками
    app = FastAPI(
        title=settings.app.project_name,
        description="API платформы Kommuna для обучения в Telegram",
        version="1.0.0",
        docs_url="/docs" if not settings.app.is_production else None,
        redoc_url="/redoc" if not settings.app.is_production else None,
        openapi_url="/openapi.json" if not settings.app.is_production else None,
        lifespan=lifespan,
        debug=settings.app.debug
    )

    from .api.v1.endpoints.telegram_webhook import router as telegram_webhook_router
    app.include_router(telegram_webhook_router)

    # Настраиваем CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.app.is_development else [
            settings.telegram.webhook_domain,
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Базовые роуты
    setup_routes(app)

    return app


def setup_routes(app: FastAPI) -> None:
    """Настраивает базовые роуты."""

    @app.get("/")
    async def root():
        """Базовый endpoint."""
        return {
            "message": f"Добро пожаловать в {settings.app.project_name} API!",
            "version": "1.0.0",
            "environment": settings.app.environment,
        }

    @app.get("/health")
    async def health_check():
        """Проверка состояния сервиса."""
        db_healthy = await check_database_connection()

        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.app.environment
        }


# Создаем экземпляр приложения
app = create_application()


def main():
    """Точка входа для запуска приложения."""
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload and settings.app.is_development,
        log_level=settings.logging.level.lower(),
    )


if __name__ == "__main__":
    main()