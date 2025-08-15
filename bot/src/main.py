import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot token (replace with your token)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    """Handle /start command"""
    await message.answer("Hello! Welcome to MyApp Bot!")

async def main():
    """Main function to start the bot"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
