from aiogram.filters import BaseFilter
from aiogram.types import Message, ChatMember

from configuration.environment import bot


class CanRestrict(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        chat_member: ChatMember = await bot.get_chat_member(message.chat.id, message.from_user.id)

        if 'ChatMemberOwner' in chat_member:
            return True
        elif chat_member.can_restrict_members:
            return True
        else:
            return False
