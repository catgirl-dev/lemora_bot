from aiogram.filters import BaseFilter
from aiogram.types import Message

from configuration.environment import KISSER_ID


class CanKiss(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id == KISSER_ID:
            return True
        await message.reply('Данную команду может использовать только Лемурка!')
        return False
