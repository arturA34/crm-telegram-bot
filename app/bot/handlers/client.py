from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.client import (
    get_client_actions,
    get_confirm_delete_keyboard,
    get_edit_field_keyboard,
    get_status_keyboard,
)
from app.bot.keyboards.menu import add_main_menu_button
from app.bot.states.client import CreateClientStates, EditClientStates
from app.bot.states.reminder import SetReminderStates
from app.bot.utils.pagination import paginate_keyboard
from app.db.models.user import User
from app.db.repositories.user import UserRepository
from app.services.client import ClientService

router = Router(name="client")


# --- Create client FSM ---


@router.callback_query(F.data == "menu:add_client")
async def create_client_start(
    callback: CallbackQuery,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    await state.set_state(CreateClientStates.name)
    if isinstance(callback.message, Message):
        await callback.message.answer(texts["client_enter_name"])
    await callback.answer()


@router.message(CreateClientStates.name)
async def create_client_name(
    message: Message,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    await state.update_data(name=message.text)
    await state.set_state(CreateClientStates.phone)
    await message.answer(texts["client_enter_phone"])


@router.message(CreateClientStates.phone, Command("skip"))
async def create_client_skip_phone(
    message: Message,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    await state.update_data(phone=None)
    await state.set_state(CreateClientStates.source)
    await message.answer(texts["client_enter_source"])


@router.message(CreateClientStates.phone)
async def create_client_phone(
    message: Message,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    await state.update_data(phone=message.text)
    await state.set_state(CreateClientStates.source)
    await message.answer(texts["client_enter_source"])


@router.message(CreateClientStates.source, Command("skip"))
async def create_client_skip_source(
    message: Message,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    await state.update_data(source=None)
    await state.set_state(CreateClientStates.budget)
    await message.answer(texts["client_enter_budget"])


@router.message(CreateClientStates.source)
async def create_client_source(
    message: Message,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    await state.update_data(source=message.text)
    await state.set_state(CreateClientStates.budget)
    await message.answer(texts["client_enter_budget"])


@router.message(CreateClientStates.budget, Command("skip"))
async def create_client_skip_budget(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    await state.update_data(budget=0)
    await _finish_create_client(message, state, session, user, texts)


@router.message(CreateClientStates.budget)
async def create_client_budget(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    try:
        budget = Decimal(message.text)
    except (InvalidOperation, TypeError, ValueError):
        await message.answer(texts["client_invalid_budget"])
        return

    await state.update_data(budget=float(budget))
    await _finish_create_client(message, state, session, user, texts)


async def _finish_create_client(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    data = await state.get_data()
    await state.clear()

    service = ClientService(session)
    result = await service.create_client(user, data)

    kb = InlineKeyboardBuilder()
    add_main_menu_button(kb, texts)
    if result["ok"]:
        client = result["client"]
        await message.answer(
            texts["client_created"].format(name=client.name),
            reply_markup=kb.as_markup(),
        )
    else:
        await message.answer(texts["error"], reply_markup=kb.as_markup())


# --- Client list ---


@router.callback_query(F.data == "menu:clients")
async def my_clients(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    await _show_client_list(callback, session, user, texts, page=1)


async def _show_client_list(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
    page: int = 1,
    status: str | None = None,
) -> None:
    service = ClientService(session)
    result = await service.get_clients(user, status=status, page=page)

    if not result["clients"]:
        await callback.answer(texts["client_list_empty"], show_alert=True)
        return

    items = [
        (
            f"{c.name} [{texts[f'status_{c.status}']}]",
            f"client:view:{c.id}",
        )
        for c in result["clients"]
    ]

    prefix = f"clients:{status or 'all'}"
    kb = paginate_keyboard(items, page, result["total_pages"], prefix, texts=texts)
    status_label = texts[f"status_{status}"] if status else texts["btn_my_clients"]

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["client_list_title"].format(status=status_label),
            reply_markup=kb.as_markup(),
        )
    await callback.answer()


@router.callback_query(F.data.regexp(r"^clients:.+:page:(\d+)$"))
async def client_list_page(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    parts = callback.data.split(":")
    status_val = parts[1] if parts[1] != "all" else None
    page = int(parts[-1])

    service = ClientService(session)
    result = await service.get_clients(user, status=status_val, page=page)

    items = [
        (
            f"{c.name} [{texts[f'status_{c.status}']}]",
            f"client:view:{c.id}",
        )
        for c in result["clients"]
    ]

    prefix = f"clients:{status_val or 'all'}"
    kb = paginate_keyboard(items, page, result["total_pages"], prefix, texts=texts)

    if isinstance(callback.message, Message):
        status_label = texts[f"status_{status_val}"] if status_val else texts["btn_my_clients"]
        await callback.message.edit_text(
            texts["client_list_title"].format(status=status_label),
            reply_markup=kb.as_markup(),
        )
    await callback.answer()


# --- Client detail ---


@router.callback_query(F.data.startswith("client:view:"))
async def client_detail(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    client_id = int(callback.data.split(":")[-1])
    service = ClientService(session)
    result = await service.get_client_detail(user, client_id)

    if not result["ok"]:
        await callback.answer(texts[result["error"]], show_alert=True)
        return

    client = result["client"]
    user_repo = UserRepository(session)
    manager = await user_repo.get_by_id(client.manager_id)
    manager_name = (manager.first_name or manager.username or str(manager.telegram_id)) if manager else "?"

    reminder_str = (
        client.reminder_at.strftime("%d.%m.%Y %H:%M") if client.reminder_at else texts["reminder_none"]
    )

    text = texts["client_detail"].format(
        name=client.name,
        phone=client.phone or "\u2014",
        source=client.source or "\u2014",
        budget=f"{client.budget:,.2f}",
        status=texts[f"status_{client.status}"],
        manager=manager_name,
        reminder=reminder_str,
        created=client.created_at.strftime("%d.%m.%Y"),
    )

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            text, reply_markup=get_client_actions(texts, client.id).as_markup()
        )
    await callback.answer()


# --- Change status ---


@router.callback_query(F.data.startswith("client:status:"))
async def client_status_menu(
    callback: CallbackQuery,
    texts: dict[str, str],
) -> None:
    client_id = int(callback.data.split(":")[-1])
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["client_select_status"],
            reply_markup=get_status_keyboard(texts, client_id).as_markup(),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("client:setstatus:"))
async def client_set_status(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    parts = callback.data.split(":")
    client_id = int(parts[2])
    status = parts[3]

    service = ClientService(session)
    result = await service.change_status(user, client_id, status)

    if not result["ok"]:
        await callback.answer(texts[result["error"]], show_alert=True)
        return

    kb = InlineKeyboardBuilder()
    add_main_menu_button(kb, texts)
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["client_status_changed"].format(status=texts[f"status_{status}"]),
            reply_markup=kb.as_markup(),
        )
    await callback.answer()


# --- Edit client ---


@router.callback_query(F.data.startswith("client:edit:"))
async def client_edit_menu(
    callback: CallbackQuery,
    texts: dict[str, str],
) -> None:
    client_id = int(callback.data.split(":")[-1])
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["client_select_field"],
            reply_markup=get_edit_field_keyboard(texts, client_id).as_markup(),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("client:editfield:"))
async def client_edit_field(
    callback: CallbackQuery,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    parts = callback.data.split(":")
    client_id = int(parts[2])
    field = parts[3]

    await state.set_state(EditClientStates.waiting_value)
    await state.update_data(edit_client_id=client_id, edit_field=field)

    if isinstance(callback.message, Message):
        await callback.message.answer(texts["client_enter_new_value"])
    await callback.answer()


@router.message(EditClientStates.waiting_value)
async def client_edit_value(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    data = await state.get_data()
    await state.clear()

    client_id = data["edit_client_id"]
    field = data["edit_field"]
    value = message.text

    if field == "budget":
        try:
            value = Decimal(value)
        except (InvalidOperation, TypeError, ValueError):
            await message.answer(texts["client_invalid_budget"])
            return

    service = ClientService(session)
    result = await service.update_client(user, client_id, {field: value})

    kb = InlineKeyboardBuilder()
    add_main_menu_button(kb, texts)
    if result["ok"]:
        await message.answer(texts["client_updated"], reply_markup=kb.as_markup())
    else:
        await message.answer(texts[result["error"]], reply_markup=kb.as_markup())


# --- Delete client ---


@router.callback_query(F.data.startswith("client:delete:"))
async def client_delete_confirm(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    client_id = int(callback.data.split(":")[-1])
    service = ClientService(session)
    result = await service.get_client_detail(user, client_id)

    if not result["ok"]:
        await callback.answer(texts[result["error"]], show_alert=True)
        return

    client = result["client"]
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            texts["client_confirm_delete"].format(name=client.name),
            reply_markup=get_confirm_delete_keyboard(texts, client_id).as_markup(),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("client:confirmdelete:"))
async def client_delete_execute(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    client_id = int(callback.data.split(":")[-1])
    service = ClientService(session)
    result = await service.delete_client(user, client_id)

    kb = InlineKeyboardBuilder()
    add_main_menu_button(kb, texts)
    if isinstance(callback.message, Message):
        if result["ok"]:
            await callback.message.edit_text(texts["client_deleted"], reply_markup=kb.as_markup())
        else:
            await callback.message.edit_text(texts[result["error"]], reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "client:canceldelete")
async def client_delete_cancel(
    callback: CallbackQuery,
    texts: dict[str, str],
) -> None:
    kb = InlineKeyboardBuilder()
    add_main_menu_button(kb, texts)
    if isinstance(callback.message, Message):
        await callback.message.edit_text(texts["cancelled"], reply_markup=kb.as_markup())
    await callback.answer()


# --- Set reminder ---


@router.callback_query(F.data.startswith("client:reminder:"))
async def client_reminder_start(
    callback: CallbackQuery,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    client_id = int(callback.data.split(":")[-1])
    await state.set_state(SetReminderStates.date)
    await state.update_data(reminder_client_id=client_id)

    if isinstance(callback.message, Message):
        await callback.message.answer(texts["reminder_enter_date"])
    await callback.answer()


@router.message(SetReminderStates.date)
async def client_reminder_date(
    message: Message,
    state: FSMContext,
    texts: dict[str, str],
) -> None:
    try:
        day, month, year = message.text.strip().split(".")
        date_val = datetime(int(year), int(month), int(day), tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        await message.answer(texts["reminder_invalid_date"])
        return

    await state.update_data(reminder_date=date_val.isoformat())
    await state.set_state(SetReminderStates.time)
    await message.answer(texts["reminder_enter_time"])


@router.message(SetReminderStates.time)
async def client_reminder_time(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    texts: dict[str, str],
) -> None:
    try:
        hour, minute = message.text.strip().split(":")
        hour, minute = int(hour), int(minute)
    except (ValueError, AttributeError):
        await message.answer(texts["reminder_invalid_time"])
        return

    data = await state.get_data()
    await state.clear()

    date_val = datetime.fromisoformat(data["reminder_date"])
    reminder_at = date_val.replace(hour=hour, minute=minute)

    service = ClientService(session)
    result = await service.set_reminder(user, data["reminder_client_id"], reminder_at)

    kb = InlineKeyboardBuilder()
    add_main_menu_button(kb, texts)
    if result["ok"]:
        await message.answer(
            texts["reminder_set"].format(
                datetime=reminder_at.strftime("%d.%m.%Y %H:%M")
            ),
            reply_markup=kb.as_markup(),
        )
    else:
        await message.answer(texts[result["error"]], reply_markup=kb.as_markup())
