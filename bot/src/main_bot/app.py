import logging

from aiogram import Dispatcher
from .handlers.start import router as start_router


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(start_router)
    return dp