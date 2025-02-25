from aiogram.filters import BaseFilter
from aiogram.types import Message, ChatMember

from configuration.environment import bot
from utils.admins_actualization import admins


class CanRestrict(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if admins[message.chat.id][message.from_user.id]:
            return True
        else:
            return False
