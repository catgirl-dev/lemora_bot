from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from texts.base import help_message_text
from utils.admins_actualization import get_all_admins, add_chat_to_db
from utils.captcha.captcha_tools import generate_captcha_config

base: Router = Router()


@base.message(Command('ping'))
async def ping(message: Message):
    await message.reply('pong!')


@base.message(Command('help'))
async def help_message(message: Message):
    await message.reply(help_message_text, parse_mode='Markdown')


@base.message(Command('start'))
async def start_message(message: Message):
    await message.reply(help_message_text, parse_mode='Markdown')
    generate_captcha_config(message.chat.id)
    await add_chat_to_db(message.chat.id)
    await get_all_admins()
