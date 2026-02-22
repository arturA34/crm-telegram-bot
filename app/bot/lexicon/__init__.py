from app.bot.lexicon.en import TEXTS as EN_TEXTS
from app.bot.lexicon.ru import TEXTS as RU_TEXTS

LEXICON: dict[str, dict[str, str]] = {
    "en": EN_TEXTS,
    "ru": RU_TEXTS,
}


def get_texts(language: str) -> dict[str, str]:
    return LEXICON.get(language, EN_TEXTS)
