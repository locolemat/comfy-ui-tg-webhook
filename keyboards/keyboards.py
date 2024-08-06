from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from configuration.localisation import language, LanguageModel
from configuration.gen_models import image_models, video_models

def generation_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.button_generate_text_image), callback_data='t2i'))
    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.button_generate_text_video), callback_data='t2v'))
    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.button_generate_image_video), callback_data='i2v'))

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

    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.choose_model), callback_data="choose_model"))
    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.choose_video_model), callback_data="choose_video_model"))
    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.user_payment), callback_data="payment"))
    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.generate_begin), callback_data="generate"))

    builder.adjust(1)
    return builder.as_markup()


def choose_model_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    for model in image_models.values():
        builder.add(types.InlineKeyboardButton(text=model.name_text, callback_data=model.get_button_callback()))
    # builder.add(types.InlineKeyboardButton(text=language.model_turbovisionxl, callback_data="model:turbovisionxlSuperFastXL.safetensors"))

    builder.adjust(3)
    return builder.as_markup()


def choose_video_model_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    for model in video_models.values():
        builder.add(types.InlineKeyboardButton(text=model.name_text, callback_data=model.get_button_callback()))

    builder.adjust(2)
    return builder.as_markup()


def confirm_model_keyboard(model_name: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.model_confirm), callback_data=f'confirm_model:{model_name}'))
    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.model_reject), callback_data='choose_model'))

    builder.adjust(2)
    return builder.as_markup()


def confirm_video_model_keyboard(model_name: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.model_confirm), callback_data=f'confirm_v_model:{model_name}'))
    builder.add(types.InlineKeyboardButton(text=LanguageModel.with_emojis(language.model_reject), callback_data='choose_video_model'))

    builder.adjust(2)
    return builder.as_markup()
