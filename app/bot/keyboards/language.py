from aiogram.utils.keyboard import InlineKeyboardBuilder

LANGUAGES = {
    "en": "\U0001f1ec\U0001f1e7 English",
    "ru": "\U0001f1f7\U0001f1fa Русский",
}

LANGUAGE_CODES: set[str] = {"en", "ru"}


def get_language_keyboard() -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    for code, label in LANGUAGES.items():
        b.button(text=label, callback_data=f"lang:{code}")
    b.adjust(1)
    return b
