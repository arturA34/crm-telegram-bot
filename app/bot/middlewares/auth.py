import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class AutoRegisterMiddleware(BaseMiddleware):
    """Automatically registers new users on their first interaction."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = getattr(event, "from_user", None)
        if tg_user is None:
            return await handler(event, data)

        session: AsyncSession = data["session"]
        repo = UserRepository(session)

        user = await repo.get_by_telegram_id(tg_user.id)
        if user is None:
            user = await repo.create(
                telegram_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
            )
            logger.info("New user registered: telegram_id=%d", tg_user.id)

        data["user"] = user
        return await handler(event, data)
