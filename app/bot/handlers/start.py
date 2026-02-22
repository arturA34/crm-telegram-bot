from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.language import LANGUAGE_CODES, get_language_keyboard
from app.bot.keyboards.menu import get_main_menu
from app.bot.lexicon import get_texts
from app.db.models.user import User
from app.db.repositories.user import UserRepository

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, texts: dict[str, str]) -> None:
    await message.answer(
        texts["welcome_back"].format(name=user.first_name or "there"),
        reply_markup=get_main_menu(texts).as_markup(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def on_language_selected(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
) -> None:
    lang_code = callback.data.split(":", maxsplit=1)[1] if callback.data else ""
    if lang_code not in LANGUAGE_CODES:
        await callback.answer("Unknown language")
        return

    repo = UserRepository(session)
    await repo.update_language(user, lang_code)

    texts = get_texts(lang_code)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(texts["language_set"])
        await callback.message.answer(
            texts["menu_title"],
            reply_markup=get_main_menu(texts).as_markup(),
        )
    await callback.answer()


@router.callback_query(F.data == "menu:settings")
async def settings_menu(
    callback: CallbackQuery,
    texts: dict[str, str],
) -> None:
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["settings_menu"],
            reply_markup=get_language_keyboard().as_markup(),
        )
    await callback.answer()
