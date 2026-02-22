from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.pipeline import get_pipeline_keyboard
from app.bot.utils.pagination import paginate_keyboard
from app.db.models.user import User
from app.services.client import ClientService

router = Router(name="pipeline")


@router.callback_query(F.data == "menu:pipeline")
async def pipeline_overview(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    service = ClientService(session)
    result = await service.get_pipeline(user)
    pipeline = result["pipeline"]

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["pipeline_title"],
            reply_markup=get_pipeline_keyboard(texts, pipeline).as_markup(),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("pipeline:status:"))
async def pipeline_status_clients(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    status = callback.data.split(":")[-1]
    service = ClientService(session)
    result = await service.get_clients(user, status=status, page=1)

    if not result["clients"]:
        await callback.answer(texts["client_list_empty"], show_alert=True)
        return

    items = [
        (c.name, f"client:view:{c.id}")
        for c in result["clients"]
    ]

    prefix = f"clients:{status}"
    kb = paginate_keyboard(items, 1, result["total_pages"], prefix)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["client_list_title"].format(status=texts[f"status_{status}"]),
            reply_markup=kb.as_markup(),
        )
    await callback.answer()
