import copy
from pprint import pprint
from typing import List

from filters import SwearCheck, isPrivate
from datetime import datetime
from keyboards import start_menu
from loader import dp
from aiogram import types

from utils import distribution_publications, add_manager
from aiogram.dispatcher import FSMContext


# from aiogram.dispatcher.filters import Media
# @dp.message_handler(commands='start')
# async def hello(m: types.Message):
#     print('Hello world!')

@dp.message_handler(isPrivate(), commands='start')
async def start(message: types.Message, state: FSMContext):
    print(f'log: check {datetime.now()}')
    # print(message.from_user.id)
    await message.answer(text=f'Привет, {message.from_user.first_name}',
                         reply_markup=start_menu)


@dp.message_handler(content_types=types.ContentType.USER_SHARED)
async def all_m(message: types.Message):
    print(f'log: all_m {datetime.now()}')
    add_manager(message.user_shared.user_id)
    await message.answer(f'Менеджер был успешно добавлен!')


# @dp.message_handler(isPrivate(), text='Опубликовать объявление')
# async def add_publication(message: types.Message):
#     await message.answer("Перешлите объявление")
#     await PublicationState.text.set()


# @dp.message_handler(isPrivate(), is_media_group=True, content_types=types.ContentType.ANY, state=PublicationState.text)
@dp.message_handler(isPrivate(), is_media_group=True, content_types=types.ContentType.ANY)
async def check_publication_media_group(message: types.Message, album: List[types.Message], state: FSMContext):
    """This handler will receive a complete album of any type."""
    print(f'log: check_publication_media_group {datetime.now()}')
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
            if n == len(album):
                caption = message.caption
            media_group.attach({"media": file_id, "type": obj.content_type, })
        except ValueError:
            return await message.answer("This type of album is not supported by aiogram.")

    media_group_copy = copy.deepcopy(media_group)
    media_group_copy.media[0]['caption'] = caption
    await message.answer_media_group(media_group_copy)
    print(media_group.media[0])

    await state.finish()

    keyboard = types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton('Опубликовать✅', callback_data=f'publish:{message.message_id}')) \
        .add(types.InlineKeyboardButton('Отменить', callback_data=f'delete:{message.message_id}'))
    await message.answer('Проверьте правильность объявления и нажмите кнопку "Опубликовать"',
                         reply_markup=keyboard)

    await state.update_data(message_id=message.message_id, message_group=media_group, test_message=message,
                            file_type=None)


# @dp.message_handler(isPrivate(), state=PublicationState.text)
@dp.message_handler(isPrivate())
async def check_publication_with_text(message: types.Message, state: FSMContext):
    message_id = await message.answer(message.text)
    print(f'log: check_publication_with_text {datetime.now()}')
    await state.finish()

    keyboard = types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton('Опубликовать✅', callback_data=f'publish:{message.message_id}')) \
        .add(types.InlineKeyboardButton('Отменить', callback_data=f'delete:{message.message_id}'))
    await message.answer('Проверьте правильность объявления и нажмите кнопку "Опубликовать"',
                         reply_markup=keyboard)

    await state.update_data(message_id=message_id.message_id, message_group=None, test_message=message, file_type=None)


# @dp.message_handler(isPrivate(), content_types=types.ContentTypes.ANY, state=PublicationState.text)
@dp.message_handler(isPrivate(), content_types=types.ContentTypes.ANY)
async def check_publication(message: types.Message, state: FSMContext):
    print(f'log: check_publication_photo {datetime.now()}')
    # pprint(dict(message))
    file_type = "photo"
    await message.forward(message.from_user.id)
    keyboard = types.InlineKeyboardMarkup() \
        .add(types.InlineKeyboardButton('Опубликовать✅', callback_data=f'publish:{message.message_id}')) \
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
    print(f'log: publish_publication {datetime.now()}')
    messages = await state.get_data()
    if await distribution_publications(message_group=messages['message_group'], test_message=messages['test_message'],
                                       file_type=messages['file_type']):
        await callback_data.message.edit_text('Публикация успешно завершена')
        # await callback_data.message.delete_reply_markup()


@dp.callback_query_handler(isPrivate(), text_startswith='delete:')
async def decline_publish_publication(callback_data: types.CallbackQuery):
    print(f'log: decline_publish_publication {datetime.now()}')
    await callback_data.message.edit_text('Публикация отменена')
    try:
        await callback_data.message.edit_reply_markup(reply_markup=None)
    except:
        pass


@dp.message_handler()
async def echo_data(m: types.Message):
    pprint(dict(m))