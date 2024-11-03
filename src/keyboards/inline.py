from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def consult_keyboard(data_type=""):
    text = "✅   Связаться с консультантом   🛍️✅"
    print(text)
    consult_button = InlineKeyboardButton(
        text=text, callback_data="consult:" + data_type
    )
    return InlineKeyboardMarkup().add(consult_button)


handle_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="ОБРАБОТАТЬ✅", callback_data="handle")
)
