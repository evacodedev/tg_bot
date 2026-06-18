import json
import logging
import random
import re
import time
from pathlib import Path
from pprint import pprint

from keyboards.inline import consult_keyboard
from loader import bot
from loader import CHANNEL_ID

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / 'data'
SWEARS_FILE = DATA_DIR / 'swears.txt'
ADMINS_FILE = DATA_DIR / 'admins.txt'
PUBLISHED_POSTS_FILE = DATA_DIR / 'published_posts.json'
MAX_PUBLISHED_POSTS = 1000
KEYBOARD_REPAIR_BATCH_SIZE = 50


def _load_published_posts():
    if not PUBLISHED_POSTS_FILE.exists():
        return {}

    try:
        with PUBLISHED_POSTS_FILE.open('r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        logger.warning('Failed to load published posts: %s', error)
        return {}


def _save_published_posts(posts):
    PUBLISHED_POSTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = PUBLISHED_POSTS_FILE.with_suffix('.json.tmp')
    with temp_file.open('w', encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=2)
    temp_file.replace(PUBLISHED_POSTS_FILE)


def register_published_post(chat_id, message_id, data_type):
    posts = _load_published_posts()
    posts[f'{chat_id}:{message_id}'] = {
        'data_type': data_type,
        'updated_at': int(time.time()),
    }
    if len(posts) > MAX_PUBLISHED_POSTS:
        oldest_post_key = min(
            posts,
            key=lambda post_key: posts[post_key].get('updated_at', 0)
        )
        del posts[oldest_post_key]
    _save_published_posts(posts)
    logger.info(
        'Registered published post chat_id=%s message_id=%s data_type=%s total=%s',
        chat_id,
        message_id,
        data_type,
        len(posts),
    )


def get_published_post_type(chat_id, message_id):
    posts = _load_published_posts()
    post_data = posts.get(f'{chat_id}:{message_id}')
    if not post_data:
        return None
    return post_data.get('data_type')


def get_recent_published_posts(limit=KEYBOARD_REPAIR_BATCH_SIZE):
    posts = _load_published_posts()
    sorted_posts = sorted(
        posts.items(),
        key=lambda item: item[1].get('updated_at', 0),
        reverse=True,
    )
    recent_posts = []
    for post_key, post_data in sorted_posts[:limit]:
        chat_id, message_id = post_key.split(':', 1)
        recent_posts.append({
            'chat_id': chat_id,
            'message_id': int(message_id),
            'data_type': post_data.get('data_type'),
        })
    return recent_posts


async def restore_recent_post_keyboards(limit=KEYBOARD_REPAIR_BATCH_SIZE):
    recent_posts = get_recent_published_posts(limit=limit)
    restored = 0
    failed = 0
    for post in recent_posts:
        try:
            await bot.edit_message_reply_markup(
                chat_id=post['chat_id'],
                message_id=post['message_id'],
                reply_markup=consult_keyboard(post['data_type']),
            )
            restored += 1
        except Exception as error:
            error_text = str(error).lower()
            if 'message is not modified' in error_text:
                continue
            failed += 1
            logger.warning(
                'Failed to repair keyboard chat_id=%s message_id=%s data_type=%s error=%s',
                post['chat_id'],
                post['message_id'],
                post['data_type'],
                error,
            )

    if restored or failed:
        logger.info(
            'Keyboard repair cycle completed restored=%s failed=%s checked=%s',
            restored,
            failed,
            len(recent_posts),
        )


def check_swears(text):
    profanity_list = [i[:-1] for i in SWEARS_FILE.open('r', encoding='utf-8').readlines()[:-1]]
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
        logger.exception("Ошибка при получении сообщения")
        return None


async def distribution_publications(message_group=None, test_message=None, file_type=None):
    group_list = [CHANNEL_ID,]
    if message_group:
        for group in group_list:
            await bot.send_media_group(chat_id=group, media=message_group)
            message = await bot.send_message(
                chat_id=group,
                text=test_message.caption,
                reply_markup=consult_keyboard(f'media_group-{len(message_group.media)}'),
                parse_mode='HTML'
            )
            register_published_post(group, message.message_id, f'media_group-{len(message_group.media)}')
    elif file_type == 'video':
        for group in group_list:
            video_info = test_message.video
            # video_file = await bot.download_file_by_id(video_info.file_id)

            message = await bot.send_video(
                chat_id=group,
                caption=test_message.caption,
                video=video_info.file_id,
                reply_markup=consult_keyboard('video')
            )
            register_published_post(group, message.message_id, 'video')
    elif file_type == 'photo':
        for group in group_list:
            # print('heloo')
            # await bot.forward_message(chat_id=group, from_chat_id=chat_id, message_id=message_id)
            photo_info = test_message.photo[-1]
            photo_file = await bot.download_file_by_id(photo_info.file_id)
            # print(photo_file, photo_info.file_id)

            message = await bot.send_photo(
                chat_id=group,
                caption=test_message.caption,
                photo=photo_file,
                reply_markup=consult_keyboard('photo')
            )
            register_published_post(group, message.message_id, 'photo')
    else:
        for group in group_list:
            # print('heloo')
            # await bot.forward_message(chat_id=group, from_chat_id=chat_id, message_id=message_id)
            message = await bot.send_message(chat_id=group, text=test_message.text)
            await bot.edit_message_reply_markup(
                chat_id=group,
                message_id=message.message_id,
                reply_markup=consult_keyboard('text')
            )
            register_published_post(group, message.message_id, 'text')
    return True


def is_admin_check(user_id):
    admins_list = [i[:-1] for i in ADMINS_FILE.open('r', encoding='utf-8').readlines()]
    return str(user_id) in admins_list


def add_manager(manager_id):
    with ADMINS_FILE.open('a+', encoding='utf-8') as f:
        f.seek(0)
        id_list = [i[:-1] for i in f.readlines()]
        print(id_list)
        if not(str(manager_id) in id_list):
            f.write(str(manager_id) + '\n')
