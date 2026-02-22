from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

LANGUAGES = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "uk": "🇺🇦 Українська",
}


def get_language_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"lang:{code}")]
        for code, label in LANGUAGES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
