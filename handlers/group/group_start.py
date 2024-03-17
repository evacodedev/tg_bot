import asyncio

from aiogram import types
import aiohttp

from keyboards.inline import handle_markup
from loader import dp, bot, token
import requests

manager_chat_id = open('data/manager_chat.txt', 'r').read().replace('\n', '')
chanel_chat_id = open('data/chats.txt', 'r').read().replace('\n', '')

print(manager_chat_id)

pressed_buttons = {}


@dp.callback_query_handler(text_startswith='consult:')
async def consulting(callback_data: types.CallbackQuery):
    print('consulting', pressed_buttons)
    await callback_data.answer('Консультант свяжется с вами в ближайшее время!', show_alert=True)
    user_id = callback_data.from_user.id
    post_id = callback_data.message.message_id
    if (user_id, post_id, 'consultation') not in pressed_buttons:
        pressed_buttons[(user_id, post_id, 'consultation')] = True
        # pprint(dict(callback_data.message))
        if 'video' in dict(callback_data.message):
            await bot.send_video(chat_id=manager_chat_id,
                                 caption=callback_data.message.caption + '\nНик клиента: @' + callback_data.from_user.username,
                                 reply_markup=handle_markup, video=callback_data.message.video.file_id)
            return None
        elif 'photo' in dict(callback_data.message):
            await bot.send_photo(chat_id=manager_chat_id,
                                 caption=f'{callback_data.message.caption}\nНик клиента: @' + callback_data.from_user.username,
                                 reply_markup=handle_markup, photo=callback_data.message.photo[0].file_id)
            return None
        elif 'consult:media_group' in callback_data.data:
            transition_state = callback_data.data.split('-')
            num_of_media = int(transition_state[-1])
            album_messages = sorted([callback_data.message.message_id - i for i in range(1, num_of_media + 1)])
            result_string = "[" + ",".join(map(str, album_messages)) + "]"
            # with aiohttp.ClientSession() as client:
            #     client
            #
            # answer = await asyncio.g
            answer = requests.get(
                f'https://api.telegram.org/bot{token}/forwardMessages'
                f'?chat_id={manager_chat_id}4&from_chat_id=-1002021461967&message_ids={result_string}')
            print(answer.content, type(result_string), f'https://api.telegram.org/bot{token}/forwardMessages'
                          f'?chat_id={manager_chat_id}&from_chat_id={chanel_chat_id}&message_ids={result_string}')

        await bot.send_message(chat_id=manager_chat_id,
                               text=f"{callback_data.message.text}\nНик клиента: @" + callback_data.from_user.username,
                               reply_markup=handle_markup)


@dp.callback_query_handler(text_startswith='handle')
async def handle_request(callback_data: types.CallbackQuery):
    # pprint(dict(callback_data))
    print(handle_request)
    if 'caption' in dict(callback_data.message):
        if 'video' in dict(callback_data.message):
            await callback_data.message.edit_caption(
                caption=callback_data.message.caption + f'\nОбработано: @{callback_data.from_user.username}')
        elif 'photo' in dict(callback_data.message):
            await callback_data.message.edit_caption(
                caption=callback_data.message.caption + f'\nОбработано: @{callback_data.from_user.username}')
    elif 'text' in dict(callback_data.message):
        await callback_data.message.edit_text(
            text=callback_data.message.text + f'\nОбработано: @{callback_data.from_user.username}')

    await callback_data.message.edit_reply_markup(reply_markup=None)
