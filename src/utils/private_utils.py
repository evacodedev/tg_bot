import random
import re
import time
from pprint import pprint

from keyboards.inline import consult_keyboard
from loader import bot
from loader import CHANNEL_ID


def check_swears(text):
    profanity_list = [i[:-1] for i in open('data/swears.txt', 'r').readlines()[:-1]]
    found_any = any(word in str(text).lower() for word in profanity_list)
    return found_any


async def is_chat_member(member_id):
    chat_id = "-1001843717362"
    # chat_id = 'investbezgranic'
    try:
        chat_member = await bot.get_chat_member(chat_id, member_id)
        return chat_member.is_chat_member()
    except Exception:
        return True


async def get_message_by_id(chat_id, message_id):
    try:
        # Получение объекта чата
        chat = await bot.get_chat(chat_id)
        # Проверка, что чат найден
        if chat:
            # Получение объекта сообщения
            message = await chat.get_member(message_id)
            return message
        else:
            return None
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")
        return None


async def distribution_publications(message_group=None, test_message=None, file_type=None):
    group_list = [CHANNEL_ID,]
    if test_message:
        print(test_message)
    if message_group:
        for group in group_list:
            await bot.send_media_group(chat_id=group, media=message_group)
            await bot.send_message(chat_id=group, text=test_message.caption, reply_markup=consult_keyboard(f'media_group-{len(message_group.media)}'), parse_mode='HTML')
    elif file_type == 'video':
        for group in group_list:
            video_info = test_message.video
            # video_file = await bot.download_file_by_id(video_info.file_id)

            await bot.send_video(chat_id=group, caption=test_message.caption, video=video_info.file_id, reply_markup=consult_keyboard('video'))
    elif file_type == 'photo':
        for group in group_list:
            print('heloo')
            # await bot.forward_message(chat_id=group, from_chat_id=chat_id, message_id=message_id)
            photo_info = test_message.photo[-1]
            photo_file = await bot.download_file_by_id(photo_info.file_id)
            print(photo_file, photo_info.file_id)

            await bot.send_photo(chat_id=group, caption=test_message.caption, photo=photo_file, reply_markup=consult_keyboard('photo'))
    else:
        for group in group_list:
            print('heloo')
            # await bot.forward_message(chat_id=group, from_chat_id=chat_id, message_id=message_id)
            message = await bot.send_message(chat_id=group, text=test_message.text)
            await bot.edit_message_reply_markup(chat_id=group, message_id=message.message_id, reply_markup=consult_keyboard('text'))
    return True


def is_admin_check(user_id):
    admins_list = [i[:-1] for i in open('data/admins.txt', 'r').readlines()]
    return str(user_id) in admins_list


def add_manager(manager_id):
    with open('data/admins.txt', 'a+') as f:
        f.seek(0)
        id_list = [i[:-1] for i in f.readlines()]
        print(id_list)
        if not(str(manager_id) in id_list):
            f.write(str(manager_id) + '\n')