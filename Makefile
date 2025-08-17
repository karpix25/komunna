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

# Добавьте эти команды в ваш Makefile

# ========================================
# TELEGRAM BOT УПРАВЛЕНИЕ
# ========================================

# Создание бота у @BotFather
create-bot:
	@echo "🤖 Инструкция по созданию Telegram бота:"
	@echo "1. Откройте Telegram и найдите @BotFather"
	@echo "2. Отправьте команду /newbot"
	@echo "3. Введите название бота (например: Communa Validator Bot)"
	@echo "4. Введите username бота (например: communa_validator_bot)"
	@echo "5. Скопируйте токен и добавьте в .env файл:"
	@echo "   TELEGRAM_BOT_TOKEN=ваш_токен_здесь"
	@echo "6. Запустите: make setup-bot"

# Настройка bot сервиса
setup-bot:
	@echo "⚙️ Настройка Telegram bot сервиса..."
	@mkdir -p bot/src
	@cp .env.example bot/.env.example 2>/dev/null || echo "Создайте bot/.env.example"
	@echo "✅ Структура bot сервиса создана"
	@echo "📝 Не забудьте добавить TELEGRAM_BOT_TOKEN в .env файл!"

# Запуск только bot сервиса
start-bot:
	@echo "🚀 Запуск Telegram bot..."
	@docker-compose up bot -d
	@echo "✅ Bot запущен в фоновом режиме"

# Остановка bot сервиса
stop-bot:
	@echo "⏹️ Остановка Telegram bot..."
	@docker-compose stop bot
	@echo "✅ Bot остановлен"

# Перезапуск bot сервиса
restart-bot:
	@echo "🔄 Перезапуск Telegram bot..."
	@docker-compose restart bot
	@echo "✅ Bot перезапущен"

# Логи bot сервиса
logs-bot:
	@echo "📊 Логи Telegram bot:"
	@docker-compose logs -f bot

# Логи bot за последние 50 строк
logs-bot-tail:
	@echo "📊 Последние логи Telegram bot:"
	@docker-compose logs --tail=50 bot

# Статус bot сервиса
status-bot:
	@echo "📈 Статус Telegram bot:"
	@docker-compose ps bot

# Подключение к контейнеру bot
shell-bot:
	@echo "🐚 Подключение к контейнеру bot..."
	@docker-compose exec bot /bin/bash

# Тестирование bot API
test-bot-api:
	@echo "🧪 Тестирование Telegram Bot API..."
	@curl -X GET "http://localhost:8000/api/v1/telegram/bot-status" \
		-H "Authorization: Bearer your_token_here" \
		-H "Content-Type: application/json" \
		-w "\n📊 Статус ответа: %{http_code}\n" \
		-s -S || echo "❌ Ошибка подключения к API"

# Тестирование валидации через bot
test-bot-validate:
	@echo "🧪 Тестирование валидации через Telegram Bot..."
	@read -p "Введите Telegram ID для тестирования: " telegram_id; \
	curl -X POST "http://localhost:8000/api/v1/telegram/validate" \
		-H "Authorization: Bearer your_token_here" \
		-H "Content-Type: application/json" \
		-d '{"telegram_id": "'$telegram_id'", "request_confirmation": false}' \
		-w "\n📊 Статус ответа: %{http_code}\n" \
		-s -S | jq '.' || echo "❌ Ошибка при валидации"

# Полный запуск с bot
dev-with-bot:
	@echo "🚀 Запуск полной системы с Telegram Bot..."
	@docker-compose -f docker-compose.dev.yml up backend bot database -d
	@echo "✅ Система запущена:"
	@echo "  🔗 Backend: http://localhost:8000"
	@echo "  🔗 API Docs: http://localhost:8000/docs"
	@echo "  🤖 Telegram Bot: активен"
	@echo "  📊 Логи: make logs-bot"

# Проверка конфигурации bot
check-bot-config:
	@echo "🔍 Проверка конфигурации Telegram Bot..."
	@if [ -f .env ]; then \
		if grep -q "TELEGRAM_BOT_TOKEN=" .env; then \
			echo "✅ TELEGRAM_BOT_TOKEN найден в .env"; \
		else \
			echo "❌ TELEGRAM_BOT_TOKEN не найден в .env"; \
			echo "💡 Добавьте: TELEGRAM_BOT_TOKEN=ваш_токен"; \
		fi; \
	else \
		echo "❌ Файл .env не найден"; \
		echo "💡 Создайте .env файл на основе .env.example"; \
	fi
	@if [ -d bot/ ]; then \
		echo "✅ Папка bot/ существует"; \
	else \
		echo "❌ Папка bot/ не найдена"; \
		echo "💡 Запустите: make setup-bot"; \
	fi

# Очистка bot данных
clean-bot:
	@echo "🧹 Очистка данных Telegram Bot..."
	@docker-compose down bot
	@docker-compose rm -f bot
	@echo "✅ Данные bot очищены"

# Полная переустановка bot
reinstall-bot: clean-bot setup-bot start-bot
	@echo "🔄 Bot полностью переустановлен"

# Мониторинг bot в реальном времени
monitor-bot:
	@echo "📊 Мониторинг Telegram Bot в реальном времени..."
	@echo "Нажмите Ctrl+C для выхода"
	@while true; do \
		clear; \
		echo "🤖 TELEGRAM BOT MONITOR - $(date)"; \
		echo "=========================================="; \
		docker-compose ps bot; \
		echo ""; \
		echo "📊 Последние логи:"; \
		docker-compose logs --tail=10 bot; \
		echo ""; \
		echo "🔄 Обновление через 5 секунд..."; \
		sleep 5; \
	done

# Отправка тестового сообщения через bot
send-test-message:
	@echo "📤 Отправка тестового сообщения через Telegram Bot..."
	@read -p "Введите Telegram ID получателя: " telegram_id; \
	read -p "Введите сообщение: " message; \
	curl -X POST "http://localhost:8000/api/v1/telegram/send-message/$telegram_id" \
		-H "Authorization: Bearer your_token_here" \
		-H "Content-Type: application/json" \
		-d '{"message": "'$message'"}' \
		-w "\n📊 Статус ответа: %{http_code}\n" \
		-s -S | jq '.' || echo "❌ Ошибка отправки сообщения"

# ========================================
# КОМПЛЕКСНЫЕ КОМАНДЫ
# ========================================

# Полная настройка проекта с bot
full-setup: setup-bot check-bot-config
	@echo "🎯 Полная настройка проекта с Telegram Bot завершена!"
	@echo ""
	@echo "📋 Следующие шаги:"
	@echo "1. Добавьте TELEGRAM_BOT_TOKEN в .env файл"
	@echo "2. Запустите: make dev-with-bot"
	@echo "3. Протестируйте: make test-bot-validate"
	@echo "4. Мониторинг: make monitor-bot"

# Быстрая диагностика всей системы
diagnose:
	@echo "🔍 Диагностика системы..."
	@echo "=========================="
	@echo ""
	@echo "📊 Статус контейнеров:"
	@docker-compose ps
	@echo ""
	@echo "🔧 Конфигурация bot:"
	@make check-bot-config
	@echo ""
	@echo "🌐 Тест API:"
	@curl -X GET "http://localhost:8000/health" -w " (Статус: %{http_code})\n" -s -S 2>/dev/null || echo "❌ Backend недоступен"
	@echo ""
	@echo "🤖 Статус Telegram Bot:"
	@curl -X GET "http://localhost:8000/api/v1/telegram/bot-status" -H "Authorization: Bearer test" -w " (Статус: %{http_code})\n" -s -S 2>/dev/null || echo "❌ Bot API недоступен"

# Помощь по bot командам
help-bot:
	@echo "🤖 Доступные команды для Telegram Bot:"
	@echo "======================================"
	@echo ""
	@echo "📦 Настройка:"
	@echo "  make create-bot          - Инструкция создания бота"
	@echo "  make setup-bot           - Настройка структуры bot сервиса"
	@echo "  make check-bot-config    - Проверка конфигурации"
	@echo ""
	@echo "🚀 Управление:"
	@echo "  make start-bot           - Запуск bot сервиса"
	@echo "  make stop-bot            - Остановка bot сервиса"
	@echo "  make restart-bot         - Перезапуск bot сервиса"
	@echo "  make dev-with-bot        - Запуск всей системы с bot"
	@echo ""
	@echo "🧪 Тестирование:"
	@echo "  make test-bot-api        - Тест bot API"
	@echo "  make test-bot-validate   - Тест валидации через bot"
	@echo "  make send-test-message   - Отправка тестового сообщения"
	@echo ""
	@echo "📊 Мониторинг:"
	@echo "  make logs-bot            - Логи bot сервиса"
	@echo "  make status-bot          - Статус bot сервиса"
	@echo "  make monitor-bot         - Мониторинг в реальном времени"
	@echo ""
	@echo "🔧 Обслуживание:"
	@echo "  make clean-bot           - Очистка bot данных"
	@echo "  make reinstall-bot       - Полная переустановка"
	@echo "  make diagnose            - Диагностика всей системы"