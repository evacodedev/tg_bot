import asyncio
import logging
from pprint import pprint
from datetime import datetime

from aiogram import types
import aiohttp

from keyboards.inline import handle_markup, consult_keyboard
from loader import dp, bot, TOKEN, CHAT_ID, CHANNEL_ID
from utils import get_published_post_type
import requests

logger = logging.getLogger(__name__)
logger.info('Group handler initialized chat_id=%s channel_id=%s', CHAT_ID, CHANNEL_ID)

pressed_buttons = {}


def _has_consult_keyboard(message: types.Message, data_type: str) -> bool:
    if not message.reply_markup or not message.reply_markup.inline_keyboard:
        return False

    first_row = message.reply_markup.inline_keyboard[0]
    if not first_row:
        return False

    button = first_row[0]
    return (
        button.text == "✅   Связаться с консультантом   🛍️✅"
        and button.callback_data == f'consult:{data_type}'
    )


@dp.edited_channel_post_handler()
async def restore_consult_keyboard(message: types.Message):
    logger.info('edited_channel_post chat_id=%s message_id=%s', message.chat.id, message.message_id)
    data_type = get_published_post_type(message.chat.id, message.message_id)
    if not data_type:
        logger.info('No published post record for chat_id=%s message_id=%s', message.chat.id, message.message_id)
        return

    if _has_consult_keyboard(message, data_type):
        logger.info('Keyboard already present for chat_id=%s message_id=%s', message.chat.id, message.message_id)
        return

    try:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=consult_keyboard(data_type),
        )
        logger.info('Restored consult keyboard chat_id=%s message_id=%s data_type=%s', message.chat.id, message.message_id, data_type)
    except Exception as error:
        logger.exception(
            'Failed to restore consult keyboard chat_id=%s message_id=%s data_type=%s',
            message.chat.id,
            message.message_id,
            data_type,
        )


@dp.channel_post_handler()
async def log_channel_post(message: types.Message):
    logger.info(
        'channel_post chat_id=%s message_id=%s text=%s caption=%s content_type=%s',
        message.chat.id,
        message.message_id,
        message.text,
        message.caption,
        message.content_type,
    )


@dp.callback_query_handler(text_startswith='consult:')
async def consulting(callback_data: types.CallbackQuery):
    username = callback_data.from_user.username
    caption = ''
    print(f'log: consulting {datetime.now()}', username)
    if not username:
        await callback_data.answer('Извините, пока что мы не можем обработать ваш запрос. '
                                   'Обратитесь напрямую к менеджерам.', show_alert=True)
        return
    await callback_data.answer('Консультант свяжется с вами в ближайшее время!', show_alert=True)
    user_id = callback_data.from_user.id
    post_id = callback_data.message.message_id
    if (user_id, post_id, 'consultation') not in pressed_buttons:
        pressed_buttons[(user_id, post_id, 'consultation')] = True
        if 'video' in dict(callback_data.message):
            if callback_data.message.caption:
                caption = callback_data.message.caption[:800]
            await bot.send_video(chat_id=CHAT_ID,
                                 caption= f'{caption}\nНик клиента: @{username}',
                                 reply_markup=handle_markup, video=callback_data.message.video.file_id)
            return None
        elif 'photo' in dict(callback_data.message):
            if callback_data.message.caption:
                caption = callback_data.message.caption[:800]
            await bot.send_photo(chat_id=CHAT_ID,
                                 caption=f'{caption}\nНик клиента: @{username}',
                                 reply_markup=handle_markup, photo=callback_data.message.photo[0].file_id)
            return None
        elif 'consult:media_group' in callback_data.data:
            transition_state = callback_data.data.split('-')
            num_of_media = int(transition_state[-1])
            album_messages = sorted([callback_data.message.message_id - i for i in range(1, num_of_media + 1)])
            result_string = "[" + ",".join(map(str, album_messages)) + "]"
            request_url = f'https://api.telegram.org/bot{TOKEN}/forwardMessages'
            async with aiohttp.ClientSession() as session:
                params = {
                    'chat_id': CHAT_ID,
                    'from_chat_id' : CHANNEL_ID,
                    'message_ids': result_string,
                }
                async with session.get(request_url, params=params) as resp:
                    print(f"log: consulting resp {resp.status}")
                    print(f"log: consulting answer resp {await resp.text()}")

        await bot.send_message(chat_id=CHAT_ID,
                               text=f"{callback_data.message.text}\nНик клиента: @{username}",
                               reply_markup=handle_markup)


@dp.callback_query_handler(text_startswith='handle')
async def handle_request(callback_data: types.CallbackQuery):
    # pprint(dict(callback_data))
    print(f'log: handle_request {datetime.now()}', callback_data.from_user.username)
    if 'caption' in dict(callback_data.message):
        print(len(callback_data.message.caption))
        if 'Обработано: @' in callback_data.message.caption:
            pass
        elif 'video' in dict(callback_data.message):
            await callback_data.message.edit_caption(
                caption=callback_data.message.caption + f'\nОбработано: @{callback_data.from_user.username}')
        elif 'photo' in dict(callback_data.message):
            await callback_data.message.edit_caption(
                caption=callback_data.message.caption + f'\nОбработано: @{callback_data.from_user.username}')
    elif 'text' in dict(callback_data.message):
        if 'Обработано: @' in callback_data.message.text:
            pass
        else:
            await callback_data.message.edit_text(
                text=callback_data.message.text + f'\nОбработано: @{callback_data.from_user.username}')

    try:
        await callback_data.message.edit_reply_markup(reply_markup=None)
    except:
        pass
