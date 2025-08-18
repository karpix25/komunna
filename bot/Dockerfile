# bot/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY src/ ./src/

# Установка переменных окружения по умолчанию
ENV PYTHONPATH=/app

# Команда запуска
CMD ["python", "src/main.py"]

# ========================================================================
# bot/Dockerfile.dev (для разработки)
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей для разработки
COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Монтируем код для hot-reload
VOLUME ["/app/src"]

ENV PYTHONPATH=/app

CMD ["python", "src/main.py"]

# ========================================================================
# bot/requirements.txt
aiogram==3.4.1
aiohttp==3.9.3
python-telegram-bot==21.0.1
python-dotenv==1.0.1
asyncio-mqtt==0.16.1

# ========================================================================
# bot/requirements-dev.txt
pytest==8.0.2
pytest-asyncio==0.23.5
black==24.2.0
flake8==7.0.0

# ========================================================================
# bot/.env.example
# Переменные окружения для Telegram Bot

# Токен вашего Telegram бота (получите у @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# URL backend сервиса
BACKEND_URL=http://backend:8000

# URL для webhook (только для продакшена)
WEBHOOK_URL=

# Уровень логирования
LOG_LEVEL=INFO

# ========================================================================
# Обновление docker-compose.yml
# Добавьте в ваш существующий docker-compose.yml:

services:
  # ... ваши существующие сервисы ...

  bot:
    build:
      context: ./bot
      dockerfile: Dockerfile.dev
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - BACKEND_URL=http://backend:8000
      - LOG_LEVEL=INFO
    volumes:
      - ./bot/src:/app/src
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - app-network

  backend:
    # ... ваша существующая конфигурация backend ...
    environment:
      # Добавьте эти переменные к существующим
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - BOT_SERVICE_URL=http://bot:8001
    depends_on:
      - database
      # Уберите зависимость от bot если она есть

networks:
  app-network:
    driver: bridge

# ========================================================================
# .env файл (в корне проекта)
# Добавьте эти переменные к вашим существующим:

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Database Configuration (если еще нет)
DATABASE_URL=postgresql://postgres:password@database:5432/communaapp