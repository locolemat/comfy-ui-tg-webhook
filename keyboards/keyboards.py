from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from configuration.localisation import language

def generation_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text=language.button_generate_text_image, callback_data=language.button_generate_text_image))
    builder.add(types.InlineKeyboardButton(text=language.button_generate_text_video, callback_data=language.button_generate_text_video))
    builder.add(types.InlineKeyboardButton(text=language.button_generate_image_video, callback_data=language.button_generate_image_video))

    builder.adjust(1)

    return builder.as_markup()


def dimensions_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text=language.dimension_square, callback_data="d_1:1"))
    builder.add(types.InlineKeyboardButton(text=language.dimension_landscape, callback_data="d_4:3"))
    builder.add(types.InlineKeyboardButton(text=language.dimension_portrait, callback_data="d_3:4"))

    builder.adjust(3)

    return builder.as_markup()


def greeting_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text=language.user_payment, callback_data="payment"))
    builder.add(types.InlineKeyboardButton(text=language.choose_model, callback_data="choose_model"))
    builder.add(types.InlineKeyboardButton(text=language.generate_begin, callback_data="generate"))

    builder.adjust(2)
    return builder.as_markup()
