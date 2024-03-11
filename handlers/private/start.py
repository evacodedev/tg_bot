from pprint import pprint
from typing import List

from filters import SwearCheck, isPrivate
from loader import dp, bot
from aiogram import types
import keyboards

from utils import generate_code, distribution_publications, is_admin_check, add_manager
from aiogram.dispatcher import FSMContext
from states import PublicationState, EstateState, SwearState


# from aiogram.dispatcher.filters import Media
# @dp.message_handler(commands='start')
# async def hello(m: types.Message):
#     print('Hello world!')

@dp.message_handler(isPrivate(), commands='start')
async def start(message: types.Message, state: FSMContext):
    print('check')
    # print(message.from_user.id)
    await message.answer(text=f'Привет, {message.from_user.first_name}',
                         reply_markup=keyboards.create_menu(is_admin_check(message.from_user.username)))


@dp.message_handler(isPrivate(), text='Опубликовать объявление')
async def add_publication(message: types.Message):
    await message.answer("Перешлите объявление")
    await PublicationState.text.set()


# @dp.message_handler(isPrivate(), text='Добавить менеджера')
# async def add_manager(message: types.Message):


# @dp.message_handler(content_types=types.ContentTypes.PHOTO)
# async def handle_photo(message: types.Message):
#     # Получаем список всех фотографий из альбома
#     photos = message.photo
#     # Отправляем каждую фотографию в альбоме в том же чате
#     for photo in photos:
#         await bot.forward_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=message.message_id)


# @dp.message_handler(content_types=types.ContentTypes.PHOTO, state=PublicationState.text)
# # @dp.message_handler(MediaGroupFilter, content_types=types.ContentType.ANY)
# async def check_publication(message: types.Message, state: FSMContext):
#     print(message.message_id)
#     messages = await bot.get_message()
#     # print(album)
#     # await message.reply_media_group()
#     await message.forward(message.from_user.id)
#     print(message.photo[0].file_unique_id)
#     keyboard = types.InlineKeyboardMarkup() \
#         .add(types.InlineKeyboardButton('Опубликовать во всех группах', callback_data=f'publish:{message.message_id}')) \
#         .add(types.InlineKeyboardButton('Отменить', callback_data=f'delete:{message.message_id}'))
#     await message.answer('Проверьте правильность объявления и нажмите кнопку "Опубликовать"',
#                          reply_markup=keyboard)
#
#     await state.finish()
#     await state.update_data(message_id=message.message_id)


@dp.message_handler(isPrivate(), is_media_group=True, content_types=types.ContentType.ANY, state=PublicationState.text)
async def check_publication_media_group(message: types.Message, album: List[types.Message], state: FSMContext):
    """This handler will receive a complete album of any type."""
    print('check_publication_media_group')
    pprint(dict(message))
    media_group = types.MediaGroup()
    n = 0
    caption = None
    for obj in album:
        n += 1
        if obj.photo:
            file_id = obj.photo[-1].file_id
        else:
            file_id = obj[obj.content_type].file_id

        try:
            # We can also add a caption to each file by specifying `"caption": "text"`
            # if n == len(album):
            #     caption = message.caption
            media_group.attach({"media": file_id, "type": obj.content_type, "caption": caption, })
        except ValueError:
            return await message.answer("This type of album is not supported by aiogram.")
    await message.answer_media_group(media_group)
    # print(t_message)

    await state.finish()

    keyboard = types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton('Опубликовать во всех группах', callback_data=f'publish:{message.message_id}')) \
        .add(types.InlineKeyboardButton('Отменить', callback_data=f'delete:{message.message_id}'))
    await message.answer('Проверьте правильность объявления и нажмите кнопку "Опубликовать"',
                         reply_markup=keyboard)

    await state.update_data(message_id=message.message_id, message_group=media_group, test_message=message,
                            file_type=None)


@dp.message_handler(isPrivate(), state=PublicationState.text)
async def check_publication_with_text(message: types.Message, state: FSMContext):
    message_id = await message.answer(message.text)
    print('check_publication_with_text')
    await state.finish()

    keyboard = types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton('Опубликовать во всех группах', callback_data=f'publish:{message.message_id}')) \
        .add(types.InlineKeyboardButton('Отменить', callback_data=f'delete:{message.message_id}'))
    await message.answer('Проверьте правильность объявления и нажмите кнопку "Опубликовать"',
                         reply_markup=keyboard)

    await state.update_data(message_id=message_id.message_id, message_group=None, test_message=message, file_type=None)


@dp.message_handler(isPrivate(), content_types=types.ContentTypes.ANY, state=PublicationState.text)
async def check_publication(message: types.Message, state: FSMContext):
    print('check_publication')
    pprint(dict(message))
    file_type = None
    await message.forward(message.from_user.id)
    keyboard = types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton('Опубликовать во всех группах', callback_data=f'publish:{message.message_id}')) \
        .add(types.InlineKeyboardButton('Отменить', callback_data=f'delete:{message.message_id}'))
    await message.answer('Проверьте правильность объявления и нажмите кнопку "Опубликовать"',
                         reply_markup=keyboard)
    if "video" in dict(message):
        file_type = 'video'
    print(file_type, hasattr(dict(message), "video"))
    await state.finish()
    await state.update_data(message_group=None, test_message=message, file_type=file_type)


@dp.callback_query_handler(isPrivate(), text_startswith='publish:')
async def publish_publication(callback_data: types.CallbackQuery, state: FSMContext):
    messages = await state.get_data()
    if await distribution_publications(message_group=messages['message_group'], test_message=messages['test_message'],
                                       file_type=messages['file_type']):
        await callback_data.message.edit_text('Публикация успешно завершена')
        # await callback_data.message.delete_reply_markup()


@dp.callback_query_handler(isPrivate(), text_startswith='delete:')
async def decline_publish_publication(callback_data: types.CallbackQuery):
    await callback_data.message.answer('Публикация отменена')


# @dp.callback_query_handler(lambda query: query.data.startswith('contact:'))
# async def all_c(callback_data: types.CallbackQuery):
#     print(callback_data.data)


@dp.message_handler(content_types=types.ContentType.USER_SHARED)
async def all_m(message: types.Message):
    add_manager(message.user_shared.user_id)
    await message.answer(f'Менеджер был успешно добавлен!')