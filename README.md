# MyApp - Полнофункциональное веб-приложение

Современное веб-приложение с Next.js фронтендом, Python (FastAPI) бэкендом и Telegram ботом.

## 🚀 Быстрый старт

### Первоначальная настройка
```bash
git clone <your-repo-url>
cd myapp
make setup
```

### Запуск в режиме разработки
```bash
make dev
```

### Доступ к сервисам
- Frontend: http://localhost:3001
- Backend API: http://localhost:8001
- Database: localhost:5433

## 📁 Структура проекта

```
myapp/
├── frontend/          # Next.js приложение
├── backend/           # FastAPI сервер
├── bot/              # Telegram бот
├── nginx/            # Nginx конфигурация
├── scripts/          # Утилиты
└── docs/            # Документация
```

## 🛠️ Команды разработки

```bash
make dev              # Запуск dev среды
make prod            # Запуск prod среды
make test            # Запуск всех тестов
make logs            # Просмотр логов
make clean           # Очистка контейнеров
```

## 📚 Документация

- [API Documentation](docs/API.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 🤝 Contributing

См. [CONTRIBUTING.md](docs/CONTRIBUTING.md) для деталей по разработке.

## 📄 License

MIT License
