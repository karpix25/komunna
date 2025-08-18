-- database/init/01-init.sql
-- Этот файл выполнится при первом запуске PostgreSQL

-- Создаем расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Можно добавить начальные данные
-- INSERT INTO ... если нужно