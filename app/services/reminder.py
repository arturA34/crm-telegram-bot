import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.bot.lexicon import get_texts
from app.db.repositories.client import ClientRepository
from app.db.repositories.user import UserRepository

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 60  # seconds


async def start_reminder_loop(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    logger.info("Reminder loop started")
    while True:
        try:
            await _check_reminders(bot, session_factory)
        except Exception:
            logger.exception("Error in reminder loop")
        await asyncio.sleep(CHECK_INTERVAL)


async def _check_reminders(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    now = datetime.now(timezone.utc)

    async with session_factory() as session:
        client_repo = ClientRepository(session)
        user_repo = UserRepository(session)

        due_clients = await client_repo.get_due_reminders(now)
        if not due_clients:
            return

        for client in due_clients:
            try:
                manager = await user_repo.get_by_id(client.manager_id)
                if manager is None:
                    continue

                texts = get_texts(manager.language)
                text = texts["reminder_notification"].format(
                    name=client.name,
                    status=texts[f"status_{client.status}"],
                    phone=client.phone or "\u2014",
                )

                kb = InlineKeyboardBuilder()
                kb.button(
                    text=texts["btn_change_status"],
                    callback_data=f"client:status:{client.id}",
                )
                kb.button(
                    text=texts["btn_edit_client"],
                    callback_data=f"client:view:{client.id}",
                )
                kb.adjust(2)

                await bot.send_message(
                    chat_id=manager.telegram_id,
                    text=text,
                    reply_markup=kb.as_markup(),
                )

                await client_repo.update(client, reminder_at=None)
            except Exception:
                logger.exception(
                    "Failed to send reminder for client %d", client.id
                )

        await session.commit()
