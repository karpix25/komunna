# Makefile for CommunaApp Backend
# Набор команд для удобного управления проектом

.PHONY: help install dev prod test clean lint format

# Показывает список доступных команд
help:
	@echo "CommunaApp Backend - Доступные команды:"
	@echo ""
	@echo "  make install    - Установка зависимостей"
	@echo "  make dev        - Запуск в режиме разработки"
	@echo "  make prod       - Запуск в продакшн режиме"
	@echo "  make test       - Запуск тестов"
	@echo "  make lint       - Проверка кода линтерами"
	@echo "  make format     - Форматирование кода"
	@echo "  make clean      - Очистка временных файлов"
	@echo "  make db-init    - Инициализация базы данных"
	@echo "  make db-migrate - Создание миграций"
	@echo "  make db-upgrade - Применение миграций"
	@echo "  make logs       - Просмотр логов"
	@echo ""

# Установка зависимостей
install:
	@echo "📦 Установка зависимостей..."
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "✅ Зависимости установлены"

# Запуск в режиме разработки
dev:
	@echo "🚀 Запуск в режиме разработки..."
	docker-compose -f docker-compose.dev.yml up --build

# Запуск в фоне для разработки
dev-d:
	@echo "🚀 Запуск в фоне (режим разработки)..."
	docker-compose -f docker-compose.dev.yml up -d --build

# Остановка dev среды
dev-stop:
	@echo "🛑 Остановка dev среды..."
	docker-compose -f docker-compose.dev.yml down

# Запуск в продакшн режиме
prod:
	@echo "🚀 Запуск в продакшн режиме..."
	docker-compose up -d --build

# Остановка prod среды
prod-stop:
	@echo "🛑 Остановка prod среды..."
	docker-compose down

# Запуск тестов
test:
	@echo "🧪 Запуск тестов..."
	pytest tests/ -v --cov=src --cov-report=html

# Проверка кода линтерами
lint:
	@echo "🔍 Проверка кода..."
	flake8 src/ tests/
	mypy src/
	@echo "✅ Проверка завершена"

# Форматирование кода
format:
	@echo "✨ Форматирование кода..."
	black src/ tests/
	isort src/ tests/
	@echo "✅ Код отформатирован"

# Очистка временных файлов
clean:
	@echo "🧹 Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "✅ Очистка завершена"

# Инициализация базы данных
db-init:
	@echo "📊 Инициализация базы данных..."
	python -c "from src.database import init_database; import asyncio; asyncio.run(init_database())"
	@echo "✅ База данных инициализирована"

# Создание новой миграции
db-migrate:
	@echo "📝 Создание миграции..."
	@read -p "Введите описание миграции: " desc; \
	alembic revision --autogenerate -m "$$desc"
	@echo "✅ Миграция создана"

# Применение миграций
db-upgrade:
	@echo "⬆️ Применение миграций..."
	alembic upgrade head
	@echo "✅ Миграции применены"

# Откат миграций
db-downgrade:
	@echo "⬇️ Откат миграций..."
	@read -p "На сколько шагов откатить? " steps; \
	alembic downgrade -$$steps
	@echo "✅ Откат завершен"

# Просмотр логов
logs:
	@echo "📋 Просмотр логов..."
	docker-compose logs -f backend

# Просмотр логов dev среды
logs-dev:
	@echo "📋 Просмотр логов (dev)..."
	docker-compose -f docker-compose.dev.yml logs -f backend

# Подключение к контейнеру backend
shell:
	@echo "💻 Подключение к backend контейнеру..."
	docker-compose exec backend bash

# Подключение к dev контейнеру
shell-dev:
	@echo "💻 Подключение к backend dev контейнеру..."
	docker-compose -f docker-compose.dev.yml exec backend bash

# Подключение к базе данных
db-shell:
	@echo "💾 Подключение к базе данных..."
	docker-compose exec postgres psql -U postgres -d communaapp

# Подключение к dev базе данных
db-shell-dev:
	@echo "💾 Подключение к dev базе данных..."
	docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres -d communaapp_dev

# Создание резервной копии БД
db-backup:
	@echo "💾 Создание резервной копии..."
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	docker-compose exec postgres pg_dump -U postgres communaapp > database/backups/backup_$$timestamp.sql
	@echo "✅ Резервная копия создана"

# Восстановление из резервной копии
db-restore:
	@echo "📥 Восстановление из резервной копии..."
	@ls database/backups/
	@read -p "Введите имя файла резервной копии: " filename; \
	docker-compose exec -T postgres psql -U postgres communaapp < database/backups/$$filename
	@echo "✅ Восстановление завершено"

# Полная перезагрузка dev среды
dev-reset:
	@echo "🔄 Полная перезагрузка dev среды..."
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml up --build -d
	@echo "✅ Dev среда перезагружена"

# Мониторинг ресурсов
monitor:
	@echo "📊 Мониторинг ресурсов..."
	docker stats

# Проверка состояния сервисов
status:
	@echo "🔍 Состояние сервисов..."
	docker-compose ps

# Обновление зависимостей
update-deps:
	@echo "📦 Обновление зависимостей..."
	pip-compile requirements.in
	pip-compile requirements-dev.in
	@echo "✅ Зависимости обновлены"

# Генерация документации
docs:
	@echo "📚 Генерация документации..."
	mkdocs build
	@echo "✅ Документация сгенерирована"

# Запуск локального сервера документации
docs-serve:
	@echo "📚 Запуск сервера документации..."
	mkdocs serve

# Безопасность - сканирование зависимостей
security-check:
	@echo "🔒 Проверка безопасности..."
	safety check
	bandit -r src/
	@echo "✅ Проверка безопасности завершена"