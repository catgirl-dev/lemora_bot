from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from texts.base import help_message_text

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
