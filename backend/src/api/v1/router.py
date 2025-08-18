"""
Главный роутер для API v1.

Объединяет все endpoints версии 1.
"""

from fastapi import APIRouter

from .endpoints.auth import router as auth_router

api_router = APIRouter()

# Подключаем роутеры endpoints
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

# Здесь будут подключаться другие роутеры:
# api_router.include_router(courses_router, prefix="/courses", tags=["Courses"])
# api_router.include_router(lessons_router, prefix="/lessons", tags=["Lessons"])
