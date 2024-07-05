from aiogram.fsm.state import State, StatesGroup

class TextToVideo(StatesGroup):
    choose_dimensions = State()
    choose_length = State()
    choose_prompt = State()
    choose_negative_prompt = State()


class TextToImage(StatesGroup):
    choose_dimensions = State()
    choose_prompt = State()
    choose_negative_prompt = State()

class ImageToVideo(StatesGroup):
    choose_dimensions = State()
    choose_length = State()
    choose_prompt = State()