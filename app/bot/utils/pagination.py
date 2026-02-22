from aiogram.utils.keyboard import InlineKeyboardBuilder


def paginate_keyboard(
    items: list[tuple[str, str]],
    page: int,
    total_pages: int,
    prefix: str,
) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()

    for label, callback_data in items:
        b.button(text=label, callback_data=callback_data)

    b.adjust(1)

    if total_pages > 1:
        nav = InlineKeyboardBuilder()
        if page > 1:
            nav.button(text="\u00ab", callback_data=f"{prefix}:page:{page - 1}")
        nav.button(text=f"{page}/{total_pages}", callback_data="noop")
        if page < total_pages:
            nav.button(text="\u00bb", callback_data=f"{prefix}:page:{page + 1}")
        nav.adjust(3)
        b.attach(nav)

    return b
