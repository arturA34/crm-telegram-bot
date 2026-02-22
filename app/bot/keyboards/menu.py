from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu(texts: dict[str, str]) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    b.button(text=texts["btn_my_clients"], callback_data="menu:clients")
    b.button(text=texts["btn_add_client"], callback_data="menu:add_client")
    b.button(text=texts["btn_pipeline"], callback_data="menu:pipeline")
    b.button(text=texts["btn_stats"], callback_data="menu:stats")
    b.button(text=texts["btn_team"], callback_data="menu:team")
    b.button(text=texts["btn_settings"], callback_data="menu:settings")
    b.adjust(2)
    return b
