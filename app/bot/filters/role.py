from typing import Any

from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from app.db.models.user import User


class RoleFilter(BaseFilter):
    """Filter that checks if user has one of the allowed roles."""

    def __init__(self, roles: list[str]) -> None:
        self.roles = roles

    async def __call__(
        self,
        event: Message | CallbackQuery,
        user: User,
        **kwargs: Any,
    ) -> bool:
        return user.role in self.roles


class TeamRequiredFilter(BaseFilter):
    """Filter that checks if user belongs to a team."""

    async def __call__(
        self,
        event: Message | CallbackQuery,
        user: User,
        **kwargs: Any,
    ) -> bool:
        return user.team_id is not None
