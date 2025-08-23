# 🎓 Kommuna - Платформа для обучения в Telegram

Современная платформа для создания образовательных курсов и развития сообществ в Telegram.

## 🏗️ Архитектура проекта

```
kommuna/
├── frontend/          # Next.js приложение
├── backend/           # FastAPI API сервер
├── bot/              # Telegram бот (aiogram 3)
├── database/         # Инициализация PostgreSQL
├── docker-compose.yml # Конфигурация Docker
├── .env.example      # Пример переменных окружения
├── Makefile          # Команды управления проектом
└── README.md         # Документация
```

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd kommuna
```

### 2. Первоначальная настройка
```bash
# Настройка проекта и создание .env файла
make setup

# Отредактируйте .env файл с вашими настройками
nano .env
```

### 3. Настройка переменных окружения

Отредактируйте `.env` файл:

```env
# База данных
DB_PASSWORD=your_strong_password_here

# Безопасность
JWT_SECRET_KEY=your_super_secret_jwt_key_minimum_32_characters_long
ENCRYPTION_KEY=your_encryption_key_exactly_32_chars

# Telegram бот
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_WEBHOOK_DOMAIN=https://your-ngrok-id.ngrok-free.app
```

### 4. Запуск проекта
```bash
# Сборка и запуск всех сервисов
make up

# Проверка статуса
make status
```

### 5. Доступ к сервисам
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📚 API Documentation: http://localhost:8000/docs
- 🗄️ PostgreSQL: localhost:5432

## 🛠️ Разработка

### Основные команды

```bash
# Показать все доступные команды
make help

# Запуск сервисов
make up                 # Запустить все
make down              # Остановить все
make restart           # Перезапустить все

# Логи
make logs              # Все логи
make logs-backend      # Логи backend
make logs-bot          # Логи бота
make logs-db           # Логи БД

# База данных
make db-shell          # Подключиться к PostgreSQL
make db-reset          # Сбросить БД (ОСТОРОЖНО!)

# Очистка
make clean             # Очистить Docker ресурсы
make clean-all         # Полная очистка (ОСТОРОЖНО!)
```

### Структура backend

```
backend/src/
├── main.py           # Основное FastAPI приложение
├── config.py         # Конфигурация из env переменных
├── database.py       # Управление БД и подключениями
└── models/           # SQLAlchemy модели
    ├── base.py       # Базовые классы моделей
    ├── user.py       # Модель пользователя
    ├── community.py  # Модель сообщества
    └── ...           # Другие модели
```

### Структура бота

```
bot/src/
└── main.py           # Основной файл бота (aiogram 3)
```

## 🗄️ База данных

### Глобальные таблицы
- `users` - Пользователи из Telegram
- `telegram_bots` - Боты сообществ
- `telegram_groups` - Группы/каналы
- `communities` - Сообщества с уникальными ключами
- `community_admins` - Администраторы сообществ
- `gamification_rules` - Правила начисления очков
- `level_rules` - Система уровней

### Динамические таблицы
Для каждого сообщества создаются отдельные таблицы:
- `community_users_{key}` - Участники сообщества
- `courses_{key}` - Курсы сообщества
- `lessons_{key}` - Уроки курсов
- `lesson_progress_{key}` - Прогресс изучения
- И другие...

## 🤖 Telegram бот

### Настройка бота

1. Создайте бота через @BotFather в Telegram
2. Получите токен и добавьте в `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
3. Настройте ngrok для локальной разработки:
   ```bash
   # Установите ngrok и запустите
   ngrok http 8000

   # Скопируйте URL в .env
   TELEGRAM_WEBHOOK_DOMAIN=https://your-id.ngrok-free.app
   ```

### Команды бота
- `/start` - Приветствие и информация о платформе

## 🌐 Деплой

### Локальная разработка с ngrok

1. Установите ngrok: https://ngrok.com/
2. Запустите туннель:
   ```bash
   ngrok http 8000
   ```
3. Обновите `TELEGRAM_WEBHOOK_DOMAIN` в `.env`
4. Перезапустите проект:
   ```bash
   make restart
   ```

### Продакшн деплой

Для продакшна используйте:
- Реальный домен с SSL сертификатом
- Внешнюю PostgreSQL БД
- Docker Swarm или Kubernetes
- Мониторинг и логирование

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|---------|
| `DB_PASSWORD` | Пароль PostgreSQL | `strong_password_123` |
| `JWT_SECRET_KEY` | Секрет для JWT токенов | `secret_key_32_chars_minimum` |
| `ENCRYPTION_KEY` | Ключ шифрования (32 символа) | `exactly_32_character_string_here` |
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather | `123456:ABC-DEF...` |
| `TELEGRAM_WEBHOOK_DOMAIN` | Домен для webhook | `https://example.com` |

### Порты

| Сервис | Порт | Описание |
|--------|------|----------|
| Frontend | 3000 | Next.js приложение |
| Backend | 8000 | FastAPI API |
| PostgreSQL | 5432 | База данных |
| Bot | - | Работает через webhook |

## 📊 Мониторинг

### Health checks
- Backend: http://localhost:8000/health
- Bot: Логи через `make logs-bot`

### Логи
```bash
# Все логи в реальном времени
make logs

# Конкретный сервис
make logs-backend
make logs-bot
make logs-db
```

## 🐛 Отладка

### Проблемы с запуском

1. **База данных не подключается**
   ```bash
   # Проверьте статус
   make status

   # Проверьте логи БД
   make logs-db
   ```

2. **Бот не получает сообщения**
   ```bash
   # Проверьте webhook настройки
   make logs-bot

   # Убедитесь что TELEGRAM_WEBHOOK_DOMAIN доступен
   curl https://your-domain.com/webhook
   ```

3. **Frontend не загружается**
   ```bash
   # Проверьте сборку
   make logs-frontend

   # Пересоберите при необходимости
   make build
   ```

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте feature ветку
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📝 TODO

- [ ] Добавить систему авторизации
- [ ] Реализовать API endpoints для курсов
- [ ] Создать админ панель
- [ ] Добавить систему уведомлений
- [ ] Интегрировать с Telegram Payments
- [ ] Добавить аналитику и метрики

## 📄 Лицензия

MIT License - см. файл LICENSE

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи: `make logs`
2. Убедитесь в правильности `.env` файла
3. Попробуйте пересоздать контейнеры: `make clean && make up`
4. Создайте Issue в репозитории

---

**Kommuna** - Создавайте. Обучайте. Развивайте сообщества. 🚀