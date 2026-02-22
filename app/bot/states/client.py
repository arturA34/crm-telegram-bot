from aiogram.fsm.state import State, StatesGroup


class CreateClientStates(StatesGroup):
    name = State()
    phone = State()
    source = State()
    budget = State()


class EditClientStates(StatesGroup):
    waiting_value = State()
