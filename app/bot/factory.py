from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.error_handler import router as error_router
from app.bot.handlers.start import router as start_router
from app.bot.middlewares.auth import AutoRegisterMiddleware
from app.bot.middlewares.database import DatabaseMiddleware


def create_bot(token: str) -> Bot:
    return Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(
    redis: Redis,
    session_factory: async_sessionmaker[AsyncSession],
) -> Dispatcher:
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    # Register middleware (order matters: database first, then auth)
    dp.message.middleware(DatabaseMiddleware(session_factory))
    dp.callback_query.middleware(DatabaseMiddleware(session_factory))
    dp.message.middleware(AutoRegisterMiddleware())
    dp.callback_query.middleware(AutoRegisterMiddleware())

    # Register routers
    dp.include_router(error_router)
    dp.include_router(start_router)

    return dp
