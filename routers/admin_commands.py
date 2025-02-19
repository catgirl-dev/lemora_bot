from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from filters.can_restrict import CanRestrict
from filters.is_admin import IsAdmin

admin: Router = Router()


@admin.message(Command('ban'), IsAdmin(), CanRestrict())
async def ban_user(message: Message):
    """ Команда должна быть ответом на сообщение пользователя, которого хочет заблокировать
    администратор. """
    if not message.reply_to_message:
        await message.reply('Команда должна быть ответом на сообщение.')
        return

    await message.chat.ban(message.reply_to_message.from_user.id)
    await message.reply('Пользователь получил удар банхаммером!')
