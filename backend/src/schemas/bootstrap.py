# backend/src/schemas/bootstrap.py
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

from .telegram import TelegramUserSchema  # уже есть

# Короткие карточки сущностей для фронта
class BotBrief(BaseModel):
    id: int
    username: Optional[str] = None
    name: Optional[str] = None
    telegram_id: Optional[int] = None
    is_active: bool = True
    bot_url: Optional[str] = None

class GroupBrief(BaseModel):
    id: int
    telegram_id: int
    name: str
    type: str
    is_active: bool = True
    photo: Optional[str] = None

class CommunityBrief(BaseModel):
    id: int
    table_key: str
    domain: str

class CommunityAggregate(BaseModel):
    community: CommunityBrief
    role: Optional[Literal["owner", "admin", "moderator"]] = None
    bot: Optional[BotBrief] = None
    main_group: Optional[GroupBrief] = None
    additional_group: Optional[GroupBrief] = None

class BootstrapResponse(BaseModel):
    user: TelegramUserSchema
    communities: List[CommunityAggregate] = Field(default_factory=list)
