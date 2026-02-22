from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.language import LANGUAGES, get_language_keyboard
from app.db.models.user import User
from app.db.repositories.user import UserRepository

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    await message.answer(
        f"Welcome, {user.first_name or 'there'}!\n\n"
        "Please select your language:",
        reply_markup=get_language_keyboard(),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def on_language_selected(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
) -> None:
    lang_code = callback.data.split(":", maxsplit=1)[1] if callback.data else ""
    if lang_code not in LANGUAGES:
        await callback.answer("Unknown language")
        return

    repo = UserRepository(session)
    await repo.update_language(user, lang_code)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            f"Language set to {LANGUAGES[lang_code]}"
        )
    await callback.answer()
