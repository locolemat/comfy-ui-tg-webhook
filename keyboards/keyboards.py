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


def choose_model_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text=language.model_anithing, callback_data="anithing_v11Pruned.safetensors"))
    builder.add(types.InlineKeyboardButton(text=language.model_dreamshaper, callback_data="dreamshaper_8.safetensors"))
    builder.add(types.InlineKeyboardButton(text=language.model_epicrealism, callback_data="epicrealism_naturalSinRC1VAE.safetensors"))
    builder.add(types.InlineKeyboardButton(text=language.model_photon, callback_data="photon_v1.safetensors"))
    builder.add(types.InlineKeyboardButton(text=language.model_realvisxl, callback_data="realvisxlV40_v40LightningBakedvae.safetensors"))


    builder.adjust(1)
    return builder.as_markup()
