from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from configuration.localisation import language

def greeting_keyboard() -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()

    builder.add(types.KeyboardButton(text=language.button_generate_text_image))
    builder.add(types.KeyboardButton(text=language.button_generate_text_video))
    builder.add(types.KeyboardButton(text=language.button_generate_image_video))

    builder.adjust(3)

    return builder.as_markup(resize_keyboard=True)


