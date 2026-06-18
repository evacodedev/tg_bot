import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHAT_ID = os.getenv('CHAT_ID')

logger = logging.getLogger(__name__)
logger.info('Loader initialized chat_id=%s channel_id=%s', CHAT_ID, CHANNEL_ID)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
