from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsGroup(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.type not in ['group', 'supergroup']:
            await message.reply('Чтобы использовать команду, добавьте бота в чат!')
            return False
        return True
