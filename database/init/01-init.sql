-- Инициализация базы данных Kommuna
-- Создаем необходимые расширения PostgreSQL

-- UUID расширение для генерации уникальных идентификаторов
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Расширение для полнотекстового поиска
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Расширение для работы с JSON
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Устанавливаем временную зону по умолчанию
SET timezone = 'UTC';

-- Создаем схему для логов (опционально)
-- CREATE SCHEMA IF NOT EXISTS logs;

-- Можно добавить начальные данные или настройки
COMMENT ON DATABASE kommuna IS 'База данных платформы Kommuna для обучения в Telegram';

-- Устанавливаем права доступа
-- GRANT ALL PRIVILEGES ON DATABASE kommuna TO postgres;