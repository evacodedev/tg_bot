from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(token='REDACTED_TOKEN')
dp = Dispatcher(bot, storage=MemoryStorage())