import logging
import random
from datetime import datetime, timedelta
from typing import Tuple, List, Optional

from aiogram import Bot
from aiogram.types import BufferedInputFile, Chat, ChatMember, ChatMemberOwner, \
    ChatMemberAdministrator, Message, InlineKeyboardMarkup
from captcha.image import ImageCaptcha

from captcha_config import captcha_symbols, captcha_len, image_captcha_width, image_captcha_height
from configuration.environment import scheduler
from database.models import CaptchaConfigs, Users
from utils.captcha.failed_captcha import failed_captcha
from utils.scheduler_args import SchedulerArgs


def generate_captcha() -> Tuple[str, List[str], BufferedInputFile]:
    """ Генерирует текст капчи, перемешанный вариант и изображение капчи """

    captcha: List[str] = random.sample(captcha_symbols, k=captcha_len)
    mixed_captcha: List[str] = random.sample(captcha, len(captcha))

    # Чтобы последовательность символов на кнопках была
    # отличной от последовательности на изображении
    while mixed_captcha == captcha:
        mixed_captcha = random.sample(captcha, len(captcha))

    captcha_image_generator = ImageCaptcha(
        width=image_captcha_width,
        height=image_captcha_height
    )
    captcha_image: BufferedInputFile = BufferedInputFile(
        file=captcha_image_generator.generate(''.join(captcha)).getvalue(),
        filename="captcha.png"
    )

    return "".join(captcha), mixed_captcha, captcha_image


def generate_captcha_config(chat_id: int) -> None:
    """ Создание настроек капчи по умолчанию для чата, если их нет """
    try:
        CaptchaConfigs.get_or_create(chat_id=chat_id)
    except Exception as e:
        logging.error(f"Ошибка при создании настроек капчи: {e}")


async def restrict_if_not_admin(bot: Bot, chat: Chat, user_id: int, permissions) -> None:
    """ Ограничение пользователя, если он не является администратором или владельцем чата """
    chat_member: ChatMember = await bot.get_chat_member(chat.id, user_id)

    if not isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator)):
        await chat.restrict(user_id=user_id, permissions=permissions)


def get_or_create_user(chat_id: int, user_id: int, message_id: int, captcha: str) -> Optional[Users]:
    """ Создание или получение пользователя из базы данных и возвращение его объекта """
    user, created = Users.get_or_create(
        chat_id=chat_id,
        user_id=user_id,
        defaults={
            "message_id": message_id,
            "captcha": captcha,
            "answer": "",
            "attempt_counter": 0,
            "bot_message_id": 0
        }
    )
    return user


async def send_captcha_message(message: Message, captcha_image, keyboard: InlineKeyboardMarkup) -> Message:
    """ Отправление сообщения с изображением капчи и клавиатурой """
    return await message.reply_photo(
        captcha_image,
        reply_markup=keyboard,
        caption="Нажмите на символы в том же порядке, что на изображении:"
    )


def schedule_failed_captcha(
        chat_id: int, user_id: int, message_id: int, link: str, captcha_time: int
) -> None:
    """Запуск задачи на бан пользователя, если капча не пройдена им за отведённое время """
    args = SchedulerArgs(chat_id, user_id, message_id, link)

    scheduler.add_job(
        func=failed_captcha,
        trigger="date",
        run_date=datetime.now() + timedelta(hours=captcha_time),
        args=[args],
        id=f"{chat_id}_{user_id}_{message_id}"
    )


def save_bot_message_id(user: Users, message_response: Message) -> None:
    """ Сохранение ID сообщения с капчей в базу данных для того, чтобы потом его удалить """
    user.bot_message_id = message_response.message_id
    user.save()
