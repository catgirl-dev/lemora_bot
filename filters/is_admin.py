from aiogram.filters import BaseFilter
from aiogram.types import Message, ChatMemberOwner, ChatMemberAdministrator, ChatMember

from configuration.environment import bot

# Когда человек пишет от имени чата/канала, за него сообщения отправляет Channel Bot
CHANNEL_BOT_ID = 136817688


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id == CHANNEL_BOT_ID:
            # Если айди чата, от которого пишет человек, совпадает с айди чата или канала,
            # привязанного к чату, где отправлено сообщение, значит он админ
            return message.sender_chat.id in [message.chat.id, message.chat.linked_chat_id]

        chat_member: ChatMember = await bot.get_chat_member(message.chat.id, message.from_user.id)

        if not isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator)):
            await message.reply('Вы не являетесь администратором данного чата!')
            return False
        return True
