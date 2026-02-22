from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.menu import add_main_menu_button
from app.db.models.user import User
from app.services.stats import StatsService

router = Router(name="stats")


@router.callback_query(F.data == "menu:stats")
async def personal_stats_cb(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    text = await _build_stats_text(session, user, texts)
    kb = InlineKeyboardBuilder()
    add_main_menu_button(kb, texts)
    if isinstance(callback.message, Message):
        await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


@router.message(Command("stats"))
async def personal_stats_cmd(
    message: Message,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    text = await _build_stats_text(session, user, texts)
    await message.answer(text)


async def _build_stats_text(
    session: AsyncSession, user: User, texts: dict[str, str]
) -> str:
    service = StatsService(session)
    result = await service.get_personal_stats(user)

    return "\n".join([
        texts["stats_title"],
        texts["stats_total"].format(total=result["total"]),
        texts["stats_won"].format(won=result["won"]),
        texts["stats_lost"].format(lost=result["lost"]),
        texts["stats_in_progress"].format(in_progress=result["in_progress"]),
        texts["stats_revenue"].format(revenue=f"{result['revenue']:,.2f}"),
        texts["stats_conversion"].format(conversion=result["conversion"]),
    ])


@router.message(Command("leaderboard"))
async def leaderboard(
    message: Message,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    service = StatsService(session)
    result = await service.get_leaderboard(user)

    if not result["ok"]:
        await message.answer(texts[result["error"]])
        return

    lines = [texts["leaderboard_title"]]
    for i, entry in enumerate(result["leaderboard"], 1):
        lines.append(
            texts["leaderboard_line"].format(
                rank=i, name=entry["name"], score=entry["score"]
            )
        )

    await message.answer("\n".join(lines))
