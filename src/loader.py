import logging
import os
from urllib.parse import urlsplit

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHAT_ID = os.getenv('CHAT_ID')
PROXY_URL = os.getenv('PROXY_URL') or None

logger = logging.getLogger(__name__)
logger.info('Loader initialized chat_id=%s channel_id=%s', CHAT_ID, CHANNEL_ID)
if PROXY_URL:
    proxy_parts = urlsplit(PROXY_URL)
    logger.info('Telegram API via proxy %s://%s:%s', proxy_parts.scheme, proxy_parts.hostname, proxy_parts.port)
bot = Bot(token=TOKEN, proxy=PROXY_URL)
dp = Dispatcher(bot, storage=MemoryStorage())
