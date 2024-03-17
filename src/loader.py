from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import os


load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
CHAT_ID = os.getenv('CHAT_ID')

print(TOKEN, CHAT_ID, CHANNEL_ID)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())