import logging

from aiogram import Router
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)

router = Router(name="errors")


@router.error()
async def global_error_handler(event: ErrorEvent) -> bool:
    logger.exception(
        "Unhandled exception in update %s: %s",
        event.update.update_id if event.update else "unknown",
        event.exception,
    )

    # Try to notify the user that something went wrong
    update = event.update
    message = None
    if update.message:
        message = update.message
    elif update.callback_query and update.callback_query.message:
        message = update.callback_query.message

    if message:
        try:
            await message.answer(
                "An unexpected error occurred. Please try again later."
            )
        except Exception:
            logger.debug("Failed to send error message to user")

    return True
