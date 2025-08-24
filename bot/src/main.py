"""
Telegram бот Kommuna на aiogram 3.
Обрабатывает только команду /start и работает через webhook.
"""

import asyncio
import logging
import os
from typing import Optional

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web, ClientSession
from aiohttp.web_app import Application

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_DOMAIN = os.getenv("TELEGRAM_WEBHOOK_DOMAIN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

if not WEBHOOK_DOMAIN:
    raise ValueError("TELEGRAM_WEBHOOK_DOMAIN environment variable is required")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """
    Обработчик команды /start.
    Приветствует пользователя и предоставляет информацию о платформе.
    """
    user = message.from_user

    welcome_text = f"""
🎓 Добро пожаловать в Kommuna!

👋 Привет, {user.first_name}!

Kommuna — это платформа для создания образовательных курсов и развития сообществ в Telegram.

🚀 Возможности:
• Создание интерактивных курсов
• Система прогресса и достижений  
• Управление сообществом
• Аналитика вовлеченности

📱 Для начала работы перейдите в веб-приложение или свяжитесь с администратором.

Ваш ID: {user.id}
"""

    try:
        await message.answer(welcome_text)
        logger.info(f"✅ Отправлено приветствие пользователю {user.id} (@{user.username})")

        # Можно добавить логику сохранения пользователя в БД через backend API
        # await register_user_in_backend(user)

    except Exception as e:
        logger.error(f"❌ Ошибка отправки приветствия: {e}")


async def register_user_in_backend(user: types.User) -> None:
    """
    Регистрирует пользователя в backend API (опционально).
    """
    try:
        user_data = {
            "telegram_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language_code": user.language_code,
            "is_premium": getattr(user, 'is_premium', False)
        }

        async with ClientSession() as session:
            async with session.post(
                    f"{BACKEND_URL}/api/users/register",
                    json=user_data
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ Пользователь {user.id} зарегистрирован в backend")
                else:
                    logger.warning(f"⚠️ Не удалось зарегистрировать пользователя: {response.status}")

    except Exception as e:
        logger.error(f"❌ Ошибка регистрации пользователя в backend: {e}")


async def setup_webhook() -> None:
    """
    Настраивает webhook для бота.
    """
    webhook_url = f"{WEBHOOK_DOMAIN}/webhook"

    try:
        # Удаляем старый webhook
        await bot.delete_webhook(drop_pending_updates=True)

        # Устанавливаем новый webhook
        await bot.set_webhook(
            url=webhook_url,
            secret_token=os.getenv("WEBHOOK_SECRET")
        )

        logger.info(f"✅ Webhook установлен: {webhook_url}")

        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот запущен: @{bot_info.username} ({bot_info.first_name})")

    except Exception as e:
        logger.error(f"❌ Ошибка настройки webhook: {e}")
        raise


async def create_app() -> Application:
    """
    Создает aiohttp приложение для обработки webhook.
    """
    # Регистрируем router в dispatcher
    dp.include_router(router)

    # Создаем веб-приложение
    app = web.Application()

    # Настраиваем webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path="/webhook")

    # Добавляем health check endpoint
    async def health_check(request):
        return web.json_response({
            "status": "ok",
            "service": "kommuna_bot",
            "bot_id": bot.id if hasattr(bot, 'id') else None
        })

    app.router.add_get("/health", health_check)

    # Настраиваем приложение для работы с aiogram
    setup_application(app, dp, bot=bot)

    return app


async def main() -> None:
    """
    Основная функция запуска бота.
    """
    logger.info("🚀 Запуск Telegram бота Kommuna...")

    try:
        # Настраиваем webhook
        await setup_webhook()

        # Создаем веб-приложение
        app = await create_app()

        # Запускаем веб-сервер
        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, '0.0.0.0', 8000)
        await site.start()

        logger.info("🎉 Бот успешно запущен и готов принимать webhook запросы!")
        logger.info("📡 Webhook endpoint: /webhook")
        logger.info("🏥 Health check: /health")

        # Ожидание завершения
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал завершения")
        finally:
            await runner.cleanup()
            await bot.session.close()

    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Фатальная ошибка: {e}")
        exit(1)