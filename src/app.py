import asyncio
import logging
import sys
from typing import Union

from aiogram import executor, types
from handlers import dp
# from filters import setup
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler

from handlers.group.group_start import pressed_buttons

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)
ALLOWED_UPDATES = [
    'message',
    'edited_message',
    'channel_post',
    'edited_channel_post',
    'callback_query',
]


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


async def update_pressed_buttons():
    while True:
        pressed_buttons.clear()
        await asyncio.sleep(86400)


async def on_start_up(dp):
    logger.info('Bot startup initiated')
    webhook_info = await dp.bot.get_webhook_info()
    logger.info(
        'Webhook status url=%s pending_update_count=%s last_error_date=%s last_error_message=%s',
        webhook_info.url,
        webhook_info.pending_update_count,
        webhook_info.last_error_date,
        webhook_info.last_error_message,
    )
    if webhook_info.url:
        logger.warning('Active webhook detected, deleting it before polling startup')
        await dp.bot.delete_webhook(drop_pending_updates=True)
        logger.info('Webhook deleted')
    await dp.bot.set_my_commands([
        types.BotCommand('start', 'Запуск бота'),
        # types.BotCommand('help', 'Помощь'),
        # types.BotCommand('menu', 'Вывести меню')
    ])
    asyncio.create_task(update_pressed_buttons())
    logger.info('Bot startup completed')


if __name__ == '__main__':
    dp.middleware.setup(AlbumMiddleware())
    logger.info('Starting polling allowed_updates=%s', ALLOWED_UPDATES)
    executor.start_polling(
        dp,
        on_startup=on_start_up,
        skip_updates=True,
        allowed_updates=ALLOWED_UPDATES,
    )
