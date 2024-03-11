from datetime import datetime, time

from aiogram.dispatcher.filters import BoundFilter
from aiogram import types

from utils import is_chat_member


class CheckSubscribe(BoundFilter):
    async def check(self, message: types.Message, *args) -> bool:
        return not await is_chat_member(int(message.from_user.id))


class IsNightTime(BoundFilter):
    async def check(self, message: types.Message, *args) -> bool:
        return not time(7) <= message.date.time() <= time(22)
