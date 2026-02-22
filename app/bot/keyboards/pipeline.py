from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.enums import ClientStatus


def get_pipeline_keyboard(
    texts: dict[str, str], pipeline: dict[str, int]
) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    for s in ClientStatus:
        count = pipeline.get(s.value, 0)
        b.button(
            text=f"{texts[f'status_{s.value}']}: {count}",
            callback_data=f"pipeline:status:{s.value}",
        )
    b.adjust(1)
    return b
