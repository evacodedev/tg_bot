from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


token = 'REDACTED_TOKEN'
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())