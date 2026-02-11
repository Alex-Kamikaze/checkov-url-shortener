from aiogram.fsm.state import State, StatesGroup

class ShorteningUrlState(StatesGroup):
    enters_url = State()