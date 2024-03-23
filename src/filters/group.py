from aiogram.dispatcher.filters import BoundFilter
from aiogram import types

from loader import bot
from utils import check_swears, is_admin_check


class IsGroup(BoundFilter):
    async def check(self, message, *args, **kwargs) -> bool:
        return message.chat.type in (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP
        )


class SwearCheck(BoundFilter):
    async def check(self, message: types.Message):
        # print(check_swears(message.text))
        if message.text is None:
            return check_swears(message.caption)
        return check_swears(message.text)


class isPrivate(BoundFilter):
    async def check(self, message, *args) -> bool:
        if isinstance(message, types.CallbackQuery):
            message = message.message
        return message.chat.type in (
            types.ChatType.PRIVATE
        ) and is_admin_check(message.chat.id)
