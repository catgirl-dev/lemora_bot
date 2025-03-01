import random

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.models import Rules
from filters.is_group import IsGroup
from texts.random_command_answers import random_answers

commands: Router = Router()


@commands.message(Command('random'))
async def rand(message: Message):
    """ Cлучайная фраза из списка random_answers """
    await message.reply(random.choice(random_answers))


@commands.message(Command('rules'), IsGroup())
async def send_rules(message: Message):
    """ Отправляет сообщение со ссылкой на правила чата """
    rules = Rules.get_or_none(chat_id=message.chat.id)
    if not rules:
        await message.reply('В базе данных нет ссылки на правила вашего чата.'
                            'Вы можете добавить их командой /change_rules. '
                            'Например: /change_rules https://telegra.ph/Pravila')
        return

    rules_to_reply: str = str(rules.rules)

    await message.reply(
        f'<a href="{rules_to_reply}">Правила чата</a>',
        parse_mode="HTML",
        disable_web_page_preview=True
    )


