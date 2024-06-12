from aiogram.fsm.state import State, StatesGroup

class TextToImage(StatesGroup):
    choose_dimensions = State()
    choose_prompt = State()
    