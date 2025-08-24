# backend/src/api/v1/endpoints/telegram_webhook.py
from fastapi import APIRouter, Request, Header, HTTPException, Response
from aiogram.types import Update
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

@router.post("/bot/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(default=""),
):
    # проверка секрета
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Bad secret")

    payload = await request.json()
    logger.info("Incoming /bot/webhook: %s", payload)

    # >>> ВАЖНО: скармливаем апдейт в aiogram
    update = Update.model_validate(payload)
    await request.app.state.dp.feed_update(
        bot=request.app.state.bot,
        update=update,
    )

    return Response(status_code=200)
