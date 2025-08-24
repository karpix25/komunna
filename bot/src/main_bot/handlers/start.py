# main_bot/handlers/start.py
import os
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

router = Router(name="start")

WEBAPP_URL = os.getenv("TELEGRAM_WEBAPP_URL") or os.getenv("FRONTEND_WEBAPP_URL") or ""

@router.message(CommandStart())
async def on_start(msg: Message):
    if not WEBAPP_URL:
        await msg.answer("WEB-app URL ещё не настроен.")
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть Kommuna 🚀", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    await msg.answer("Готово! Запускай мини-приложение:", reply_markup=kb)
