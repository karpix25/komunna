# bot/src/main.py
# ИСПРАВЛЕННАЯ версия Telegram бота

import asyncio
import logging
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ИСПРАВЛЕННАЯ конфигурация
BOT_TOKEN = os.getenv("TELEGRAM_MAIN_BOT_TOKEN") or os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ВАЖНО: Правильный URL для WebApp
WEBAPP_URL = "https://n8n-karpix-communa.g44y6r.easypanel.host"

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_MAIN_BOT_TOKEN environment variable is required")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище для временных данных пользователей
user_validation_data = {}


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """
    ИСПРАВЛЕННАЯ команда /start с правильной WebApp кнопкой
    """
    user = message.from_user

    # Сохраняем данные пользователя
    user_validation_data[user.id] = {
        "telegram_id": str(user.id),
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_bot": user.is_bot,
        "is_premium": getattr(user, 'is_premium', False),
        "language_code": user.language_code,
        "last_interaction": message.date.isoformat()
    }

    # ИСПРАВЛЕННАЯ клавиатура с правильной WebApp кнопкой
    keyboard = InlineKeyboardBuilder()
    
    # ГЛАВНАЯ кнопка для открытия WebApp
    keyboard.add(InlineKeyboardButton(
        text="🚀 Открыть Kommuna App",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    ))
    
    # Дополнительные кнопки
    keyboard.add(InlineKeyboardButton(
        text="🔐 Тест валидации",
        callback_data=f"validate_{user.id}"
    ))
    keyboard.add(InlineKeyboardButton(
        text="ℹ️ Мои данные",
        callback_data=f"info_{user.id}"
    ))
    
    # Размещаем кнопки в столбец
    keyboard.adjust(1)

    welcome_text = f"""
🎓 Добро пожаловать в Kommuna!

👤 Привет, {user.first_name}!

• **ID:** `{user.id}`
• **Username:** @{user.username or 'не указан'}
• **Имя:** {user.first_name or 'не указано'}
• **Premium:** {'✅' if getattr(user, 'is_premium', False) else '❌'}

🌟 **Kommuna** - это платформа для создания курсов и обучения в Telegram.

**Нажмите кнопку ниже, чтобы открыть приложение!** 👇
"""

    await message.answer(
        welcome_text,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )


@dp.message(Command("app"))
async def cmd_app(message: Message):
    """Быстрый доступ к приложению"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="🚀 Открыть Kommuna App",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    ))

    await message.answer(
        "🎓 **Kommuna App**\n\nНажмите кнопку, чтобы открыть приложение:",
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )


@dp.message(Command("debug"))
async def cmd_debug(message: Message):
    """Команда для отладки конфигурации"""
    user = message.from_user
    
    debug_info = f"""
🔧 **Debug информация:**

**Конфигурация:**
• Bot Token: `{'✅ Настроен' if BOT_TOKEN else '❌ Отсутствует'}`
• Backend URL: `{BACKEND_URL}`
• WebApp URL: `{WEBAPP_URL}`
• Webhook URL: `{WEBHOOK_URL or 'Не настроен (polling mode)'}`

**Ваши данные:**
• ID: `{user.id}`
• Username: `{user.username or 'не указан'}`
• First Name: `{user.first_name}`
• Language: `{user.language_code or 'не указан'}`
• Premium: `{'✅' if getattr(user, 'is_premium', False) else '❌'}`

**Статус в системе:**
• Сохранен в боте: `{'✅' if user.id in user_validation_data else '❌'}`
"""
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="🚀 Тест WebApp",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    ))
    
    await message.answer(
        debug_info,
        reply_markup=keyboard.as_markup(),
        parse_mode="Markdown"
    )


@dp.message(Command("validate"))
async def cmd_validate(message: Message):
    """Команда /validate - тест валидации через API"""
    user = message.from_user

    try:
        # Формируем данные для отправки в backend
        user_data = {
            "telegram_id": str(user.id),
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_premium": getattr(user, 'is_premium', False),
            "language_code": user.language_code,
            "validation_method": "telegram_bot_direct"
        }

        # Отправляем в backend
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/api/auth/telegram/bot-validate",
                json=user_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result_data = await response.json()
                    validation_text = f"""
✅ **Валидация через API успешна!**

📋 **Ваши данные переданы в backend:**
• Telegram ID: `{user_data['telegram_id']}`
• Username: `@{user_data['username'] or 'не указан'}`
• Имя: `{user_data['first_name']}`
• Premium: `{'✅' if user_data['is_premium'] else '❌'}`

🔐 **Данные сохранены в системе Kommuna.**
"""
                else:
                    validation_text = f"❌ **Ошибка API:** {response.status}"

    except Exception as e:
        validation_text = f"❌ **Ошибка валидации:** {str(e)}"

    await message.answer(validation_text, parse_mode="Markdown")


# Обработчики callback кнопок
@dp.callback_query(lambda c: c.data.startswith("validate_"))
async def process_validate_callback(callback_query: types.CallbackQuery):
    """Обработчик кнопки валидации"""
    user_id = int(callback_query.data.split("_")[1])

    if callback_query.from_user.id != user_id:
        await callback_query.answer("❌ Вы можете валидировать только свой аккаунт")
        return

    await callback_query.message.edit_text(
        "✅ **Тест валидации запущен!**\n\n" +
        "🔐 Попробуйте открыть WebApp для проверки полной валидации.",
        parse_mode="Markdown"
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data.startswith("info_"))
async def process_info_callback(callback_query: types.CallbackQuery):
    """Обработчик кнопки информации"""
    user_id = int(callback_query.data.split("_")[1])

    if callback_query.from_user.id != user_id:
        await callback_query.answer("❌ Вы можете смотреть только свою информацию")
        return

    user = callback_query.from_user

    info_text = f"""
📊 **Ваша информация:**

🆔 **ID:** `{user.id}`
👤 **Username:** `@{user.username or 'не указан'}`
📝 **Имя:** `{user.first_name or 'не указано'}`
📝 **Фамилия:** `{user.last_name or 'не указана'}`
🌍 **Язык:** `{user.language_code or 'не указан'}`
⭐ **Premium:** `{'✅ Да' if getattr(user, 'is_premium', False) else '❌ Нет'}`

🔗 **WebApp URL:** `{WEBAPP_URL}`
"""

    await callback_query.message.edit_text(info_text, parse_mode="Markdown")
    await callback_query.answer()


# Webhook обработчик
async def webhook_handler(request):
    """Обработчик webhook запросов от Telegram"""
    try:
        update_data = await request.json()
        update = types.Update(**update_data)
        await dp.feed_update(bot, update)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}")
        return web.Response(status=500)


# Функция отправки данных в backend
async def send_validation_to_backend(user_data: dict):
    """Отправляет валидированные данные в backend"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BACKEND_URL}/api/auth/telegram/bot-validate",
                json=user_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ Данные пользователя {user_data['telegram_id']} отправлены в backend")
                else:
                    logger.error(f"❌ Ошибка отправки в backend: {response.status}")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к backend: {str(e)}")


# Основная функция запуска
async def main():
    """Основная функция запуска бота"""
    logger.info("🤖 Запуск Telegram Bot для Kommuna...")

    # Устанавливаем команды бота
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🚀 Начать работу с ботом"),
        types.BotCommand(command="app", description="🎓 Открыть Kommuna App"),
        types.BotCommand(command="validate", description="🔐 Тест валидации"),
        types.BotCommand(command="debug", description="🔧 Отладочная информация"),
    ])

    if WEBHOOK_URL:
        # Режим webhook для продакшена
        logger.info("🌐 Настройка webhook для продакшена...")
        
        webhook_path = "/webhook"
        full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}{webhook_path}"
        
        await bot.set_webhook(full_webhook_url)
        logger.info(f"✅ Webhook установлен: {full_webhook_url}")
        
        # Создаем веб-сервер
        app = web.Application()
        app.router.add_post(webhook_path, webhook_handler)
        
        # Health check
        async def health_check(request):
            return web.json_response({
                "status": "ok", 
                "bot": "running",
                "webapp_url": WEBAPP_URL,
                "backend_url": BACKEND_URL
            })
        
        app.router.add_get("/health", health_check)
        
        # Запускаем сервер
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8001)
        await site.start()
        
        logger.info("🚀 Webhook сервер запущен на порту 8001")
        logger.info("✅ Бот готов принимать webhook запросы!")
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал завершения")
        finally:
            await runner.cleanup()
            await bot.session.close()
    else:
        # Режим polling для разработки
        logger.info("🔄 Запуск в режиме polling...")
        logger.info(f"🌐 WebApp URL: {WEBAPP_URL}")
        logger.info(f"🔗 Backend URL: {BACKEND_URL}")
        
        try:
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            logger.info("🛑 Получен сигнал завершения")
        finally:
            await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
