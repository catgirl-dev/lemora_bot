import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReactionTypeEmoji

from configuration.environment import KISSER_ID, bot
from database.models import Rules
from filters.can_kiss import CanKiss
from filters.can_restrict import CanRestrict
from filters.is_admin import IsAdmin
from filters.is_group import IsGroup
from handlers.commands.user import commands
from texts.base import kiss_message

admin: Router = Router()
admin.message.filter(IsGroup(), IsAdmin())

@admin.message(Command('ban'), CanRestrict())
async def ban_user(message: Message):
    """ Команда должна быть ответом на сообщение пользователя, которого хочет заблокировать
    администратор. """
    if not message.reply_to_message:
        await message.reply('Команда должна быть ответом на сообщение.')
        return

    await message.chat.ban(message.reply_to_message.from_user.id)
    await message.reply('Пользователь получил удар банхаммером!')


@commands.message(Command('change_rules'))
async def change_rules(message: Message, command: CommandObject):
    """ Позволяет администратору установить ссылку на правила чата """
    rules_to_add: str = command.args

    if not rules_to_add:
        await message.reply(
            'Пожалуйста, вставьте ссылку после команды! '
            'Например: /change_rules https://telegra.ph/Pravila'
        )
        return

    try:
        rules, created = Rules.get_or_create(
            chat_id=message.chat.id,
            defaults={"rules": rules_to_add}
        )

        if not created:
            rules.rules = rules_to_add
            rules.save()

        await message.reply('Правила чата успешно обновлены!')
    except Exception as e:
        logging.error(f'Ошибка при добавлении правил: {e}')
        await message.reply('Произошла ошибка при обновлении правил. '
                           'Попробуйте позже или свяжитесь с автором бота.')


@commands.message(Command('kiss'), CanKiss())
async def kiss_user(message: Message):
    """ Шуточная команда, только для меня :) """
    if message.from_user.id != KISSER_ID:
        await message.reply('Эту команду может использовать только Лемурка!')
        return
    if not message.reply_to_message:
        await message.reply('Команда должна быть ответом на сообщение.')
        return

    await bot.set_message_reaction(
        chat_id=message.chat.id,
        message_id=message.reply_to_message.message_id,
        reaction=[ReactionTypeEmoji(emoji='💋')]
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text=kiss_message,
        reply_to_message_id=message.reply_to_message.message_id
    )
