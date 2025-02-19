from aiogram.filters import BaseFilter
from aiogram.types import Message

from configuration.environment import LEMORA_CHAT_ID


class IsLemoraChat(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.id == LEMORA_CHAT_ID:
            return True
        await message.reply('Команда доступна только в Лемора чате!')
        return False
