import logging
import random

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ReactionTypeEmoji

from configuration.environment import KISSER_ID, bot
from database.models import Rules
from filters.can_kiss import CanKiss
from filters.is_admin import IsAdmin
from filters.is_group import ChatTypeFilter
from texts.base import kiss_message
from texts.random_command_answers import random_answers

commands: Router = Router()


@commands.message(Command('random'))
async def rand(message: Message):
    """ Cлучайная фраза из списка random_answers """
    await message.reply(random.choice(random_answers))


@commands.message(Command('change_rules'), ChatTypeFilter(), IsAdmin())
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


@commands.message(Command('rules'))
async def send_rules(message: Message):
    """ Отправляет сообщение со ссылкой на правила чата """
    rules = Rules.get_or_none(chat_id=message.chat.id)
    if not rules:
        await message.reply('В базе данных нет ссылки на правила вашего чата.'
                            'Вы можете добавить их командой /change_rules.'
                            'Например: /change_rules https://telegra.ph/Pravila')
        return

    rules_to_reply: str = str(rules.rules)

    await message.reply(
        f'<a href="{rules_to_reply}">Правила чата</a>',
        parse_mode="HTML",
        disable_web_page_preview=True
    )


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
