from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def consult_keyboard(data_type=''):
    consult_button = InlineKeyboardButton(text="Консультация", callback_data="consult:" + data_type)
    return InlineKeyboardMarkup().add(consult_button)


handle_markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text="ОБРАБОТАНО", callback_data="handle"))
