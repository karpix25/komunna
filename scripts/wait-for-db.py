#!/usr/bin/env python3
# scripts/wait-for-db.py
"""
Скрипт ожидания готовности базы данных.
"""

import asyncio
import asyncpg
import sys
import os
import time


async def wait_for_db():
    """Ждет готовности PostgreSQL."""

    db_host = os.getenv("DB_HOST", "postgres")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_user = os.getenv("DB_USER", "owner")
    db_password = os.getenv("DB_PASSWORD", "Gfhjkm123.")
    db_name = os.getenv("DB_NAME", "kommuna")

    max_attempts = 30
    delay = 1

    print(f"🔍 Ожидание готовности PostgreSQL на {db_host}:{db_port}...")

    for attempt in range(max_attempts):
        try:
            conn = await asyncpg.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name,
                timeout=5
            )
            await conn.execute("SELECT 1")
            await conn.close()

            print(f"✅ PostgreSQL готов! (попытка {attempt + 1})")
            return True

        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"⏳ Попытка {attempt + 1}/{max_attempts}: {e}")
                time.sleep(delay)
            else:
                print(f"❌ PostgreSQL недоступен после {max_attempts} попыток")
                return False

    return False


if __name__ == "__main__":
    result = asyncio.run(wait_for_db())
    sys.exit(0 if result else 1)