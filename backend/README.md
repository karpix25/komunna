# CommunaApp Backend

Telegram платформа для онлайн обучения с мультитенантной архитектурой и динамическими таблицами.

## 🏗️ Архитектура проекта

### Основные принципы:
- **Мультитенантность**: Каждое сообщество имеет изолированные данные
- **Динамические таблицы**: Автоматическое создание таблиц для новых сообществ
- **Микросервисная архитектура**: Разделение на backend, bot и frontend
- **Асинхронность**: Полностью асинхронный код на FastAPI + SQLAlchemy

## 🗂️ Структура базы данных

### Глобальные таблицы (общие для всей платформы):
- `users` - Базовая информация о пользователях из Telegram
- `telegram_bots` - Информация о ботах сообществ
- `telegram_groups` - Группы и каналы Telegram
- `communities` - Основная таблица сообществ с `table_key`
- `community_admins` - Администраторы сообществ
- `gamification_rules` - Правила начисления очков
- `level_rules` - Правила системы уровней

### Динамические таблицы (создаются для каждого сообщества):
- `community_users_{key}` - Пользователи сообщества с XP и уровнями
- `courses_{key}` - Курсы сообщества
- `course_modules_{key}` - Модули курсов
- `lessons_{key}` - Уроки с TipTap контентом
- `lesson_progress_{key}` - Прогресс изучения
- `communities_levels_{key}` - Кастомные уровни сообщества
- `points_ledger_{key}` - Журнал операций с очками
- `media_files_{key}` - Медиафайлы уроков

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонируем репозиторий
git clone <repository-url>
cd CommunaApp

# Переходим в backend директорию
cd backend

# Копируем пример конфигурации
cp .env.example .env

# Редактируем .env файл с вашими настройками
nano .env
```

### 2. Настройка переменных окружения

```bash
# Обязательные настройки в .env:
DB_PASSWORD=ваш_пароль_бд
JWT_SECRET_KEY=ваш-супер-секретный-ключ-jwt
ENCRYPTION_KEY=ваш-ключ-шифрования-32-символа
TELEGRAM_WEBHOOK_DOMAIN=https://yourdomain.com
TELEGRAM_WEBHOOK_SECRET=ваш-webhook-секрет
```

### 3. Запуск в режиме разработки

```bash
# Запуск всех сервисов (PostgreSQL + Redis + Backend)
make dev

# Или вручную:
docker-compose -f docker-compose.dev.yml up --build
```

### 4. Проверка работоспособности

```bash
# API должно быть доступно по адресу:
curl http://localhost:8000

# Документация API:
open http://localhost:8000/docs

# Adminer для управления БД:
open http://localhost:8080
```

## 🛠️ Разработка

### Основные команды

```bash
# Показать все доступные команды
make help

# Установка зависимостей
make install

# Запуск в режиме разработки
make dev

# Запуск тестов
make test

# Форматирование кода
make format

# Проверка кода линтерами
make lint

# Очистка временных файлов
make clean
```

### Работа с базой данных

```bash
# Инициализация БД (создание глобальных таблиц)
make db-init

# Создание новой миграции
make db-migrate

# Применение миграций
make db-upgrade

# Подключение к БД
make db-shell-dev
```

### Работа с сообществами

```bash
# Создание тестового сообщества
curl -X POST "http://localhost:8000/test/create-community/test_school"

# Получение информации о сообществе
curl "http://localhost:8000/test/community-info/comm_12345678"

# Удаление сообщества
curl -X DELETE "http://localhost:8000/test/community/comm_12345678"
```

## 📁 Структура кода

```
backend/
├── src/                          # Исходный код
│   ├── __init__.py
│   ├── main.py                   # Главный файл FastAPI приложения
│   ├── config.py                 # Конфигурация из переменных окружения
│   ├── database.py               # Подключение к БД и инициализация
│   │
│   ├── models/                   # SQLAlchemy модели
│   │   ├── __init__.py
│   │   ├── base.py              # Базовые классы моделей
│   │   ├── user.py              # Модель пользователя
│   │   ├── telegram_bot.py      # Модель Telegram бота
│   │   ├── telegram_group.py    # Модель группы/канала
│   │   ├── community.py         # Модель сообщества
│   │   ├── community_admin.py   # Модель администратора
│   │   └── gamification.py      # Модели геймификации
│   │
│   ├── services/                 # Бизнес-логика
│   │   ├── __init__.py
│   │   └── dynamic_tables.py    # Фабрика динамических таблиц
│   │
│   ├── api/                     # HTTP API endpoints
│   │   ├── __init__.py
│   │   └── v1/                  # API версии 1
│   │       ├── __init__.py
│   │       └── endpoints/       # Конкретные endpoints
│   │
│   ├── schemas/                 # Pydantic схемы
│   │   └── __init__.py
│   │
│   ├── core/                    # Основная функциональность
│   │   └── __init__.py
│   │
│   └── shared/                  # Общие утилиты
│       └── __init__.py
│
├── tests/                       # Тесты
├── requirements.txt             # Python зависимости
├── requirements-dev.txt         # Зависимости для разработки
├── Dockerfile                   # Production контейнер
├── Dockerfile.dev              # Development контейнер
└── .env.example                # Пример конфигурации
```

## 🔧 Как работают динамические таблицы

### 1. Создание сообщества:
```python
# Генерируется уникальный table_key
table_key = "comm_12345678"

# Создается запись в глобальной таблице communities
community = Community(
    table_key=table_key,
    owner_id=user_id,
    domain="myschool.communaapp.com"
)

# Автоматически создаются 8 таблиц:
# - community_users_comm_12345678
# - courses_comm_12345678
# - course_modules_comm_12345678
# - lessons_comm_12345678
# - lesson_progress_comm_12345678
# - communities_levels_comm_12345678
# - points_ledger_comm_12345678
# - media_files_comm_12345678
```

### 2. Работа с данными:
```python
# В API определяем к какому сообществу относится запрос
community_id = get_community_from_request(request)
table_key = get_table_key_by_community_id(community_id)

# Формируем имя таблицы
table_name = f"courses_{table_key}"

# Выполняем запросы к правильной таблице
courses = await db.execute(f"SELECT * FROM {table_name}")
```

## 🔐 Безопасность

### Шифрование конфиденциальных данных:
- Токены Telegram ботов шифруются с помощью `ENCRYPTION_KEY`
- JWT токены подписываются `JWT_SECRET_KEY`
- Все пароли и секреты хранятся в переменных окружения

### Изоляция данных:
- Каждое сообщество имеет собственные таблицы
- Невозможно случайно получить доступ к чужим данным
- Soft delete для возможности восстановления

## 📊 Мониторинг и логирование

### Логи:
```bash
# Просмотр логов в реальном времени
make logs-dev

# Логи сохраняются в ./logs/app.log
tail -f logs/app.log
```

### Мониторинг:
```bash
# Мониторинг ресурсов контейнеров
make monitor

# Состояние сервисов
make status
```

## 🧪 Тестирование

### Запуск тестов:
```bash
# Все тесты
make test

# Тесты с покрытием
pytest tests/ -v --cov=src --cov-report=html

# Просмотр отчета покрытия
open htmlcov/index.html
```

### Типы тестов:
- **Unit тесты**: Тестирование отдельных функций и методов
- **Integration тесты**: Тестирование взаимодействия компонентов
- **API тесты**: Тестирование HTTP endpoints
- **Database тесты**: Тестирование работы с БД

## 🚢 Деплой

### Production деплой:
```bash
# Сборка и запуск
make prod

# Или вручную:
docker-compose up -d --build
```

### На EasyPanel:
1. Загрузите проект на сервер
2. Создайте базу данных PostgreSQL
3. Настройте переменные окружения
4. Запустите через EasyPanel interface

## 🔄 Миграции базы данных

### Создание миграций:
```bash
# Автоматическая генерация миграции
make db-migrate

# Ввести описание изменений
# Например: "Add user avatar field"
```

### Применение миграций:
```bash
# Применить все новые миграции
make db-upgrade

# Откатить на N шагов назад
make db-downgrade
```

## 🐛 Отладка

### Подключение к контейнеру:
```bash
# Backend контейнер
make shell-dev

# База данных
make db-shell-dev
```

### Полезные команды для отладки:
```bash
# Проверка состояния таблиц сообщества
curl "http://localhost:8000/test/community-info/comm_12345678"

# Просмотр структуры БД
\dt  # в psql показать все таблицы

# Просмотр логов конкретного сервиса
docker-compose -f docker-compose.dev.yml logs postgres
```

## 📚 Дополнительные ресурсы

### Документация:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Полезные ссылки:
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🤝 Участие в разработке

### Workflow:
1. Создайте feature ветку: `git checkout -b feature/new-feature`
2. Внесите изменения и добавьте тесты
3. Запустите линтеры: `make lint`
4. Отформатируйте код: `make format`
5. Запустите тесты: `make test`
6. Создайте Pull Request

### Стандарты кода:
- Используйте type hints для всех функций
- Добавляйте docstrings к публичным методам
- Следуйте PEP 8 (автоматически через black)
- Покрытие тестами должно быть > 80%

## ❓ FAQ

### Q: Как добавить новое поле в динамическую таблицу?
A: 
1. Обновите DDL в `services/dynamic_tables.py`
2. Создайте миграцию: `make db-migrate`
3. Примените ко всем существующим таблицам через специальный скрипт

### Q: Что делать если таблицы сообщества повреждены?
A: Используйте команду восстановления:
```bash
# Через API
curl -X POST "http://localhost:8000/admin/repair-community/comm_12345678"

# Или через менеджер
python -c "
from src.services.dynamic_tables import dynamic_table_manager
import asyncio
asyncio.run(dynamic_table_manager.repair_community_tables('comm_12345678'))
"
```

### Q: Как создать резервную копию конкретного сообщества?
A:
```bash
# Создание дампа таблиц сообщества
pg_dump -U postgres -t "*_comm_12345678" communaapp > backup_community.sql
```

### Q: Как мигрировать данные между серверами?
A:
1. Экспортируйте глобальные таблицы
2. Экспортируйте динамические таблицы нужных сообществ  
3. Импортируйте на новом сервере
4. Обновите домены в таблице communities

### Q: Почему используются динамические таблицы а не partition?
A: 
- Полная изоляция данных между сообществами
- Возможность кастомизации структуры для разных типов школ
- Простое масштабирование (перенос отдельных сообществ)
- Легкое удаление всех данных сообщества

## 🔧 Настройка IDE

### VS Code:
Создайте `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.sortImports.args": ["--profile", "black"],
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

### PyCharm:
1. Откройте проект
2. Настройте интерпретатор Python на venv
3. Включите Black как форматтер
4. Настройте isort для сортировки импортов

## 📈 Производительность

### Мониторинг запросов:
```python
# В config.py установите
DEBUG = True  # для логирования SQL запросов

# Мониторинг медленных запросов в PostgreSQL
# В postgresql.conf:
log_min_duration_statement = 1000  # логировать запросы > 1сек
```

### Оптимизация:
- Используйте индексы для часто запрашиваемых полей
- Кэшируйте результаты с помощью Redis
- Пагинируйте большие списки данных
- Используйте JOIN вместо множественных запросов

## 🛡️ Безопасность в продакшене

### Обязательные настройки:
```bash
# .env для продакшена
ENVIRONMENT=production
DEBUG=false
SHOW_TRACEBACK=false

# Сильные ключи
JWT_SECRET_KEY=случайная-строка-64-символа
ENCRYPTION_KEY=случайная-строка-32-символа

# HTTPS
TELEGRAM_WEBHOOK_DOMAIN=https://yourdomain.com
```

### Рекомендации:
- Используйте SSL сертификаты
- Настройте firewall
- Регулярно обновляйте зависимости
- Мониторьте логи на подозрительную активность
- Настройте автобэкапы

## 🚀 Следующие шаги разработки

После настройки базовой архитектуры:

1. **API Endpoints** - создание REST API для работы с курсами
2. **Авторизация** - JWT токены и Telegram WebApp авторизация  
3. **Файловое хранилище** - загрузка и обработка медиафайлов
4. **Telegram Bot** - интеграция с ботами сообществ
5. **Уведомления** - система push уведомлений
6. **Платежи** - интеграция с Telegram Payments
7. **Аналитика** - сбор метрик и статистики

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `make logs-dev`
2. Убедитесь что все сервисы запущены: `make status`
3. Проверьте переменные окружения в `.env`
4. Посмотрите документацию API: `http://localhost:8000/docs`

---

**ComunnaApp** - Современная платформа для онлайн обучения в Telegram 🚀