from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.team import get_members_keyboard, get_team_menu
from app.db.models.user import User
from app.services.team import TeamService

router = Router(name="team")


class CreateTeamStates(StatesGroup):
    name = State()


class JoinTeamStates(StatesGroup):
    code = State()


@router.callback_query(F.data == "menu:team")
async def team_menu(
    callback: CallbackQuery,
    user: User,
    texts: dict[str, str],
) -> None:
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["team_menu"],
            reply_markup=get_team_menu(texts, user).as_markup(),
        )
    await callback.answer()


@router.callback_query(F.data == "team:create")
async def team_create_start(
    callback: CallbackQuery,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    await state.set_state(CreateTeamStates.name)
    if isinstance(callback.message, Message):
        await callback.message.answer(texts["team_enter_name"])
    await callback.answer()


@router.message(CreateTeamStates.name)
async def team_create_finish(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    await state.clear()
    name = message.text.strip() if message.text else ""
    if not name:
        await message.answer(texts["error"])
        return

    service = TeamService(session)
    result = await service.create_team(user, name)

    if not result["ok"]:
        await message.answer(texts[result["error"]])
        return

    team = result["team"]
    await message.answer(
        texts["team_created"].format(name=team.name, code=team.invite_code)
    )


@router.callback_query(F.data == "team:join")
async def team_join_start(
    callback: CallbackQuery,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    await state.set_state(JoinTeamStates.code)
    if isinstance(callback.message, Message):
        await callback.message.answer(texts["team_enter_code"])
    await callback.answer()


@router.message(JoinTeamStates.code)
async def team_join_finish(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    await state.clear()
    code = message.text.strip() if message.text else ""
    if not code:
        await message.answer(texts["error"])
        return

    service = TeamService(session)
    result = await service.join_team(user, code)

    if not result["ok"]:
        await message.answer(texts[result["error"]])
        return

    team = result["team"]
    await message.answer(texts["team_joined"].format(name=team.name))


@router.callback_query(F.data == "team:leave")
async def team_leave(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    service = TeamService(session)
    result = await service.leave_team(user)

    if isinstance(callback.message, Message):
        if result["ok"]:
            await callback.message.edit_text(texts["team_left"])
        else:
            await callback.message.edit_text(texts[result["error"]])
    await callback.answer()


@router.callback_query(F.data == "team:members")
async def team_members(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    service = TeamService(session)
    result = await service.get_team_info(user)

    if not result["ok"]:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(texts[result["error"]])
        await callback.answer()
        return

    team = result["team"]
    members = result["members"]
    member_lines = [
        f"  \u2022 {m.first_name or m.username or m.telegram_id} ({texts[f'role_{m.role}']})"
        for m in members
    ]
    text = texts["team_members_list"].format(
        name=team.name, members="\n".join(member_lines)
    )

    if isinstance(callback.message, Message):
        await callback.message.edit_text(text)
    await callback.answer()


@router.callback_query(F.data == "team:remove")
async def team_remove_select(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    service = TeamService(session)
    result = await service.get_members(user)

    if not result["ok"]:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(texts[result["error"]])
        await callback.answer()
        return

    members = [m for m in result["members"] if m.id != user.id]
    if not members:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(texts["team_no_members"])
        await callback.answer()
        return

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["team_select_member"],
            reply_markup=get_members_keyboard(members).as_markup(),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("team:kick:"))
async def team_kick_member(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    member_id = int(callback.data.split(":")[-1])
    service = TeamService(session)
    result = await service.remove_member(user, member_id)

    if isinstance(callback.message, Message):
        if result["ok"]:
            await callback.message.edit_text(texts["team_member_removed"])
        else:
            await callback.message.edit_text(texts[result["error"]])
    await callback.answer()
