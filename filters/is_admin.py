from aiogram.filters import BaseFilter
from aiogram.types import Message

from utils.admins_actualization import admins

# Когда человек пишет от имени чата/канала, за него сообщения отправляет Channel Bot
CHANNEL_BOT_ID = 136817688


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id == CHANNEL_BOT_ID:
            # Если айди чата, от которого пишет человек, совпадает с айди чата или канала,
            # привязанного к чату, где отправлено сообщение, значит он админ
            return message.sender_chat.id in [message.chat.id, message.chat.linked_chat_id]

        if message.chat.id in admins and message.from_user.id in admins[message.chat.id]:
            return True
        else:
            await message.reply("Вы не являетесь администратором чата!")
            return False
