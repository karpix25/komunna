"""
Модели для системы геймификации.

Содержит глобальные правила начисления очков и уровней,
которые используются во всех сообществах.
"""

from sqlalchemy import Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class GamificationRule(BaseModel):
    """
    Глобальные правила геймификации.

    Определяет за какие действия и сколько очков начисляется.
    Используется во всех сообществах как базовые правила.
    """

    __tablename__ = "gamification_rules"

    # Название правила (для отображения)
    rule_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Читаемое название правила"
    )

    # Тип события, за которое начисляются очки
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Тип события (lesson_completed, course_started, etc.)"
    )

    # Количество очков за действие
    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Количество очков, начисляемых за действие"
    )

    def __repr__(self) -> str:
        """Строковое представление правила."""
        return f"<GamificationRule(id={self.id}, event_type='{self.event_type}', points={self.points})>"

    @property
    def gives_points(self) -> bool:
        """Проверяет, начисляет ли правило очки."""
        return self.points > 0

    @property
    def takes_points(self) -> bool:
        """Проверяет, списывает ли правило очки."""
        return self.points < 0

    def is_event_type(self, event_type: str) -> bool:
        """
        Проверяет, соответствует ли правило типу события.

        Args:
            event_type: Тип события для проверки

        Returns:
            bool: True если правило применимо к этому событию
        """
        return self.event_type == event_type


class LevelRule(BaseModel):
    """
    Глобальные правила уровней.

    Определяет сколько очков нужно для достижения каждого уровня.
    Используется как базовая система уровней во всех сообществах.
    """

    __tablename__ = "level_rules"

    # Номер уровня
    level_number: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        nullable=False,
        comment="Номер уровня (1, 2, 3, ...)"
    )

    # Название уровня
    level_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Название уровня (Новичок, Ученик, Эксперт, ...)"
    )

    # Количество очков, необходимое для достижения уровня
    required_points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Количество очков, необходимое для достижения уровня"
    )

    def __repr__(self) -> str:
        """Строковое представление уровня."""
        return f"<LevelRule(id={self.id}, level_number={self.level_number}, level_name='{self.level_name}', required_points={self.required_points})>"

    def can_reach_with_points(self, points: int) -> bool:
        """
        Проверяет, можно ли достичь этого уровня с заданным количеством очков.

        Args:
            points: Количество очков пользователя

        Returns:
            bool: True если очков достаточно для этого уровня
        """
        return points >= self.required_points

    @classmethod
    def get_level_for_points(cls, points: int) -> int:
        """
        Определяет уровень по количеству очков.

        Эта функция должна использоваться в сервисах для определения
        текущего уровня пользователя.

        Args:
            points: Количество очков пользователя

        Returns:
            int: Номер уровня, соответствующий количеству очков
        """
        # Эта функция будет реализована в сервисе
        # Здесь только документируем логику
        pass


# Создаем индексы для оптимизации запросов
Index("ix_gamification_rules_event_type", GamificationRule.event_type)
Index("ix_gamification_rules_points", GamificationRule.points)

Index("ix_level_rules_level_number", LevelRule.level_number)
Index("ix_level_rules_required_points", LevelRule.required_points)
