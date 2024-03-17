from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUser

# start_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
#     [
#         KeyboardButton(text='Опубликовать объявление')
#     ],
#     [
#         KeyboardButton(text='Добавить группу'),
#         KeyboardButton(text='Удалить группу')
#     ]
# ])

start_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        # KeyboardButton(text='Опубликовать объявление'),
        KeyboardButton(text='Добавить менеджера', request_user=KeyboardButtonRequestUser(request_id=1))
    ]
])


