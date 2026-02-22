from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.bot.lexicon import get_texts
from app.db.models.user import User


class I18nMiddleware(BaseMiddleware):
    """Injects localized texts dict into handler data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("user")
        language = user.language if user else "en"
        data["texts"] = get_texts(language)
        return await handler(event, data)
