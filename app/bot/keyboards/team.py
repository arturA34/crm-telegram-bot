from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.menu import add_main_menu_button
from app.core.enums import UserRole
from app.db.models.user import User


def get_team_menu(texts: dict[str, str], user: User) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()

    if user.team_id is None:
        b.button(text=texts["btn_create_team"], callback_data="team:create")
        b.button(text=texts["btn_join_team"], callback_data="team:join")
    else:
        b.button(text=texts["btn_members"], callback_data="team:members")
        if user.role == UserRole.OWNER:
            b.button(text=texts["btn_remove_member"], callback_data="team:remove")
        else:
            b.button(text=texts["btn_leave_team"], callback_data="team:leave")

    b.adjust(1)
    add_main_menu_button(b, texts)
    return b


def get_members_keyboard(
    members: list[User], texts: dict[str, str], action: str = "team:kick"
) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    for m in members:
        name = m.first_name or m.username or str(m.telegram_id)
        b.button(text=name, callback_data=f"{action}:{m.id}")
    b.adjust(1)
    add_main_menu_button(b, texts)
    return b
