import asyncio
import logging

from app.bot.factory import create_bot, create_dispatcher
from app.core.logging import setup_logging
from app.core.redis import create_redis
from app.core.settings import get_settings
from app.db.session import create_engine, create_session_factory
from app.services.reminder import start_reminder_loop

logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    logger.info("Starting CRM Telegram Bot")

    # Initialize infrastructure
    engine = create_engine(settings.database_url, echo=settings.debug)
    session_factory = create_session_factory(engine)
    redis = create_redis(settings.redis_url)

    # Create bot and dispatcher
    bot = create_bot(settings.bot_token)
    dp = create_dispatcher(redis, session_factory)

    # Start reminder background task
    reminder_task = asyncio.create_task(start_reminder_loop(bot, session_factory))

    try:
        logger.info("Bot is starting polling")
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down")
        reminder_task.cancel()
        await redis.aclose()
        await engine.dispose()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
