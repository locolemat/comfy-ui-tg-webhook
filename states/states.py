from aiogram.fsm.state import State, StatesGroup

class TextToVideo(StatesGroup):
    choose_dimensions = State()
    choose_prompt = State()
