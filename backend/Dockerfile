FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Системные зависимости (для healthcheck'а нужен curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

# 1) Python-зависимости backend
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

# 2) Устанавливаем пакет бота (из папки bot)
#    Ожидается, что в bot/ есть pyproject.toml (как я предлагал).
COPY bot /app/bot
RUN pip install --no-cache-dir /app/bot

# 3) Исходники backend
COPY backend/src /app/src

# 4) Логи + non-root пользователь
RUN mkdir -p /app/logs \
 && adduser --disabled-password --gecos '' appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
