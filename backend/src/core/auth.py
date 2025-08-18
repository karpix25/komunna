# backend/src/core/auth.py
"""
ИСПРАВЛЕННАЯ версия авторизации Telegram WebApp
"""

import logging
import hmac
import hashlib
import urllib.parse
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..models.user import User
from ..schemas.telegram import WebAppUser
from ..services.telegram_factory import telegram_factory
from .auth_detector import auth_detector

logger = logging.getLogger(__name__)


def verify_telegram_webapp_data(init_data: str, bot_token: str) -> bool:
    """
    ИСПРАВЛЕННАЯ функция валидации Telegram WebApp данных.
    
    Проблемы в оригинальном коде:
    1. Неправильная обработка JSON объектов в query string
    2. Проблемы с escaped символами в URL
    3. Неправильный порядок создания HMAC
    """
    try:
        # Парсим query string
        parsed_data = urllib.parse.parse_qs(init_data)
        
        # Получаем hash и удаляем его из данных
        if 'hash' not in parsed_data:
            logger.error("❌ Hash отсутствует в initData")
            return False
            
        received_hash = parsed_data['hash'][0]
        
        # Создаем data_check_string из всех параметров кроме hash
        data_check_pairs = []
        for key, values in parsed_data.items():
            if key != 'hash':
                value = values[0]  # Берем первое значение
                # НЕ декодируем JSON объекты! Оставляем как есть в query string
                data_check_pairs.append(f"{key}={value}")
        
        # Сортируем по алфавиту
        data_check_pairs.sort()
        data_check_string = '\n'.join(data_check_pairs)
        
        logger.debug(f"🔍 Data check string: {data_check_string}")
        
        # Создаем секретный ключ: HMAC-SHA256(bot_token, "WebAppData")
        secret_key = hmac.new(
            bot_token.encode('utf-8'),
            "WebAppData".encode('utf-8'), 
            hashlib.sha256
        ).digest()
        
        # Создаем финальный hash: HMAC-SHA256(secret_key, data_check_string)
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        logger.debug(f"🔍 Calculated hash: {calculated_hash}")
        logger.debug(f"🔍 Received hash: {received_hash}")
        
        # Безопасное сравнение хешей
        is_valid = hmac.compare_digest(calculated_hash, received_hash)
        
        if is_valid:
            logger.info("✅ Telegram initData валидация успешна")
        else:
            logger.warning("❌ Telegram initData валидация провалена")
            
        return is_valid
        
    except Exception as e:
        logger.error(f"❌ Ошибка валидации initData: {e}")
        return False


def parse_telegram_user_from_init_data(init_data: str) -> Optional[WebAppUser]:
    """
    Извлекает данные пользователя из initData.
    """
    try:
        parsed_data = urllib.parse.parse_qs(init_data)
        
        if 'user' not in parsed_data:
            logger.error("❌ Данные пользователя отсутствуют в initData")
            return None
            
        user_json = parsed_data['user'][0]
        
        # Парсим JSON данные пользователя
        import json
        user_data = json.loads(user_json)
        
        return WebAppUser(
            telegram_user_id=user_data['id'],
            username=user_data.get('username'),
            first_name=user_data['first_name'],
            last_name=user_data.get('last_name'),
            language_code=user_data.get('language_code'),
            is_premium=user_data.get('is_premium', False),
            allows_write_to_pm=user_data.get('allows_write_to_pm'),
            photo_url=user_data.get('photo_url')
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка парсинга пользователя из initData: {e}")
        return None


async def verify_telegram_webapp(
        request: Request,
        db: AsyncSession = Depends(get_db_session)
) -> WebAppUser:
    """
    ИСПРАВЛЕННАЯ dependency для проверки Telegram WebApp авторизации.
    """
    # Получаем initData из заголовка Authorization
    auth_string = request.headers.get("Authorization")
    if not auth_string:
        logger.warning("❌ Отсутствует заголовок Authorization")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    # Определяем тип авторизации
    auth_type, community_id = auth_detector.detect_auth_type(request)

    # Получаем соответствующий токен бота
    if auth_type == "main":
        from ..config import settings
        bot_token = settings.telegram.main_bot_token
        if not bot_token:
            logger.error("❌ Токен главного бота не настроен")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Main bot token not configured"
            )
    elif auth_type == "community":
        # Получаем токен бота сообщества из БД
        auth_service = await telegram_factory.get_community_bot_service(community_id, db)
        if not auth_service:
            logger.error(f"❌ Сервис бота сообщества {community_id} недоступен")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Community bot service unavailable"
            )
        # Здесь нужно добавить метод для получения токена
        bot_token = "токен_из_базы"  # TODO: реализовать
    else:
        logger.error(f"❌ Неизвестный тип авторизации: {auth_type}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown auth type"
        )

    # Валидируем initData
    if not verify_telegram_webapp_data(auth_string, bot_token):
        logger.warning(f"❌ Невалидные Telegram данные для {auth_type} авторизации")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram auth data"
        )

    # Извлекаем данные пользователя
    webapp_user = parse_telegram_user_from_init_data(auth_string)
    if not webapp_user:
        logger.error("❌ Не удалось извлечь данные пользователя")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to parse user data"
        )

    logger.info(
        f"✅ Авторизован пользователь: {webapp_user.telegram_user_id} "
        f"через {auth_type}" + (f" сообщества {community_id}" if community_id else "")
    )

    return webapp_user


async def get_current_user(
        webapp_user: WebAppUser = Depends(verify_telegram_webapp),
        db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Dependency для получения текущего пользователя из базы данных.
    """
    from sqlalchemy import select

    # Ищем пользователя в базе данных
    stmt = select(User).where(User.telegram_id == webapp_user.telegram_user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        # Обновляем существующего пользователя
        user.update_from_telegram(
            username=webapp_user.username,
            first_name=webapp_user.first_name,
            last_name=webapp_user.last_name,
            language_code=webapp_user.language_code,
            is_premium=webapp_user.is_premium,
            photo_url=webapp_user.photo_url
        )
        logger.info(f"🔄 Обновлен пользователь: {user.telegram_id}")
    else:
        # Создаем нового пользователя
        user = User(
            telegram_id=webapp_user.telegram_user_id,
            username=webapp_user.username,
            first_name=webapp_user.first_name,
            last_name=webapp_user.last_name,
            language_code=webapp_user.language_code,
            is_premium=webapp_user.is_premium,
            photo_url=webapp_user.photo_url
        )
        db.add(user)
        logger.info(f"➕ Создан новый пользователь: {user.telegram_id}")

    await db.commit()
    await db.refresh(user)

    return user
