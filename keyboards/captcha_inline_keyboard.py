from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def generate_captcha_keyboard(symbols: List[str]) -> InlineKeyboardMarkup:
    """ Создание инлайн-клавиатуры с символами для капчи """
    keyboard = InlineKeyboardBuilder()
    buttons = [InlineKeyboardButton(text=symbol, callback_data=symbol) for symbol in symbols]
    keyboard.row(*buttons)
    return keyboard.as_markup()
