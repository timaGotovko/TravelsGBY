from aiogram.fsm.state import StatesGroup, State

class GPTDialog(StatesGroup):
    chatting = State()
