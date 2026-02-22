from aiogram.fsm.state import State, StatesGroup


class SetReminderStates(StatesGroup):
    date = State()
    time = State()
