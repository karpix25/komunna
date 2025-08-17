# bot/src/main.py
# Основной файл Telegram бота для валидации пользователей

import asyncio
import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище для временных данных пользователей
user_validation_data = {}


class TelegramUserValidator:
    """Класс для валидации пользователей через Telegram Bot API"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def validate_user_by_id(self, user_id: int) -> dict:
        """
        Валидирует пользователя по его Telegram ID
        Возвращает полную информацию о пользователе
        """
        try:
            # Получаем информацию о пользователе через Bot API
            chat_member = await self.bot.get_chat_member(chat_id=user_id, user_id=user_id)
            user = chat_member.user

            # Формируем данные для валидации
            user_data = {
                "telegram_id": str(user.id),
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_bot": user.is_bot,
                "is_premium": getattr(user, 'is_premium', False),
                "language_code": getattr(user, 'language_code', None),
                "validation_method": "telegram_bot_api",
                "validated_at": None  # Будет установлено в backend
            }

            return {
                "success": True,
                "user_data": user_data,
                "error": None
            }

        except Exception as e:
            logger.error(f"Ошибка валидации пользователя {user_id}: {str(e)}")
            return {
                "success": False,
                "user_data": None,
                "error": str(e)
            }

    async def validate_user_by_username(self, username: str) -> dict:
        """
        Попытка валидации пользователя по username
        (ограниченная функциональность в Bot API)
        """
        try:
            # Убираем @ если есть
            if username.startswith('@'):
                username = username[1:]

            # В Bot API нет прямого способа получить пользователя по username
            # Можно только если пользователь взаимодействовал с ботом
            return {
                "success": False,
                "user_data": None,
                "error": "Validation by username requires user interaction with bot"
            }

        except Exception as e:
            logger.error(f"Ошибка валидации по username {username}: {str(e)}")
            return {
                "success": False,
                "user_data": None,
                "error": str(e)
            }


# Инициализируем валидатор
validator = TelegramUserValidator(bot)


# API для внешних запросов
class BotAPIHandler:
    """Обработчик API запросов от backend"""

    @staticmethod
    async def validate_user(request_data: dict) -> dict:
        """
        Основная функция валидации пользователя
        Принимает данные от backend API
        """
        telegram_id = request_data.get("telegram_id")
        username = request_data.get("username")

        if telegram_id:
            # Валидация по telegram_id
            result = await validator.validate_user_by_id(int(telegram_id))
        elif username:
            # Валидация по username
            result = await validator.validate_user_by_username(username)
        else:
            return {
                "success": False,
                "user_data": None,
                "error": "telegram_id or username is required"
            }

        return result


# Обработчики команд бота

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start - приветствие и регистрация пользователя"""
    user = message.from_user

    # Сохраняем данные пользователя для будущей валидации
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

    # Клавиатура для действий
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text="🔐 Валидировать аккаунт",
        callback_data=f"validate_{user.id}"
    ))
    keyboard.add(InlineKeyboardButton(
        text="ℹ️ Мои данные",
        callback_data=f"info_{user.id}"
    ))

    welcome_text = f"""
🤖 Добро пожаловать в Communa Bot!

👤 Ваши данные:
• ID: {user.id}
• Username: @{user.username or 'не указан'}
• Имя: {user.first_name or 'не указано'}
• Фамилия: {user.last_name or 'не указана'}

Этот бот используется для валидации пользователей в системе Communa.
"""

    await message.answer(
        welcome_text,
        reply_markup=keyboard.as_markup()
    )


@dp.message(Command("validate"))
async def cmd_validate(message: Message):
    """Команда /validate - запуск валидации"""
    user = message.from_user

    # Получаем актуальные данные пользователя
    result = await validator.validate_user_by_id(user.id)

    if result["success"]:
        user_data = result["user_data"]

        validation_text = f"""
✅ Валидация успешна!

📋 Ваши валидированные данные:
• Telegram ID: {user_data['telegram_id']}
• Username: @{user_data['username'] or 'не указан'}
• Имя: {user_data['first_name'] or 'не указано'}
• Фамилия: {user_data['last_name'] or 'не указана'}
• Premium: {'Да' if user_data['is_premium'] else 'Нет'}
• Язык: {user_data['language_code'] or 'не указан'}

🔐 Эти данные можно использовать для авторизации в системе.
"""

        # Отправляем данные в backend (если нужно)
        await send_validation_to_backend(user_data)

    else:
        validation_text = f"❌ Ошибка валидации: {result['error']}"

    await message.answer(validation_text)


@dp.message(Command("info"))
async def cmd_info(message: Message):
    """Команда /info - информация о пользователе"""
    user = message.from_user

    info_text = f"""
📊 Информация о вашем аккаунте:

🆔 Основные данные:
• Telegram ID: {user.id}
• Username: @{user.username or 'не указан'}
• Имя: {user.first_name or 'не указано'}
• Фамилия: {user.last_name or 'не указана'}

🔧 Технические данные:
• Бот: {'Да' if user.is_bot else 'Нет'}
• Premium: {'Да' if getattr(user, 'is_premium', False) else 'Нет'}
• Язык: {user.language_code or 'не указан'}

💾 Статус в системе:
• Сохранен в боте: {'Да' if user.id in user_validation_data else 'Нет'}
"""

    await message.answer(info_text)


# Обработчики callback кнопок
@dp.callback_query(lambda c: c.data.startswith("validate_"))
async def process_validate_callback(callback_query: types.CallbackQuery):
    """Обработчик кнопки валидации"""
    user_id = int(callback_query.data.split("_")[1])

    if callback_query.from_user.id != user_id:
        await callback_query.answer("❌ Вы можете валидировать только свой аккаунт")
        return

    # Выполняем валидацию
    result = await validator.validate_user_by_id(user_id)

    if result["success"]:
        await callback_query.message.edit_text(
            "✅ Аккаунт успешно валидирован!\n\n" +
            "Данные отправлены в систему Communa."
        )

        # Отправляем в backend
        await send_validation_to_backend(result["user_data"])
    else:
        await callback_query.message.edit_text(
            f"❌ Ошибка валидации: {result['error']}"
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
📊 Ваша информация:

🆔 ID: {user.id}
👤 Username: @{user.username or 'не указан'}
📝 Имя: {user.first_name or 'не указано'}
📝 Фамилия: {user.last_name or 'не указана'}
⭐ Premium: {'Да' if getattr(user, 'is_premium', False) else 'Нет'}
"""

    await callback_query.message.edit_text(info_text)
    await callback_query.answer()


# Функция отправки данных в backend
async def send_validation_to_backend(user_data: dict):
    """Отправляет валидированные данные в backend"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{BACKEND_URL}/api/v1/telegram/bot-validate",
                    json=user_data,
                    headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info(f"Данные пользователя {user_data['telegram_id']} отправлены в backend")
                else:
                    logger.error(f"Ошибка отправки в backend: {response.status}")
    except Exception as e:
        logger.error(f"Ошибка подключения к backend: {str(e)}")


# Webhook обработчик для API запросов
async def handle_validation_request(request_data: dict) -> dict:
    """
    Обработчик запросов валидации от backend API
    Эта функция будет вызываться из backend
    """
    return await BotAPIHandler.validate_user(request_data)


# Основная функция запуска
async def main():
    """Основная функция запуска бота"""
    logger.info("🤖 Запуск Telegram Bot для валидации пользователей...")

    # Устанавливаем команды бота
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🚀 Начать работу с ботом"),
        types.BotCommand(command="validate", description="🔐 Валидировать аккаунт"),
        types.BotCommand(command="info", description="ℹ️ Информация об аккаунте"),
    ])

    if WEBHOOK_URL:
        # Настройка webhook для продакшена
        await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"🌐 Webhook установлен: {WEBHOOK_URL}")
    else:
        # Запуск в режиме polling для разработки
        logger.info("🔄 Запуск в режиме polling...")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())