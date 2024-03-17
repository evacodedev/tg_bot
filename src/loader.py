from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import os


load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
CHANEL_ID = os.getenv('CHANEL_ID')
CHAT_ID = os.getenv('CHAT_ID')

print(TOKEN, CHAT_ID, CHANEL_ID)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())