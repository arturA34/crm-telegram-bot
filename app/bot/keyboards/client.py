from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.enums import ClientStatus


def get_client_actions(texts: dict[str, str], client_id: int) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.button(text=texts["btn_edit_client"], callback_data=f"client:edit:{client_id}")
    b.button(text=texts["btn_change_status"], callback_data=f"client:status:{client_id}")
    b.button(text=texts["btn_set_reminder"], callback_data=f"client:reminder:{client_id}")
    b.button(text=texts["btn_delete_client"], callback_data=f"client:delete:{client_id}")
    b.adjust(2)
    return b


def get_status_keyboard(texts: dict[str, str], client_id: int) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    for s in ClientStatus:
        b.button(
            text=texts[f"status_{s.value}"],
            callback_data=f"client:setstatus:{client_id}:{s.value}",
        )
    b.adjust(1)
    return b


def get_edit_field_keyboard(texts: dict[str, str], client_id: int) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.button(text=texts["btn_edit_name"], callback_data=f"client:editfield:{client_id}:name")
    b.button(text=texts["btn_edit_phone"], callback_data=f"client:editfield:{client_id}:phone")
    b.button(text=texts["btn_edit_source"], callback_data=f"client:editfield:{client_id}:source")
    b.button(text=texts["btn_edit_budget"], callback_data=f"client:editfield:{client_id}:budget")
    b.adjust(2)
    return b


def get_confirm_delete_keyboard(
    texts: dict[str, str], client_id: int
) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.button(text=texts["btn_confirm_yes"], callback_data=f"client:confirmdelete:{client_id}")
    b.button(text=texts["btn_confirm_no"], callback_data="client:canceldelete")
    b.adjust(2)
    return b
