import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from database.models import WelcomeMessages, CaptchaConfigs
from filters.is_admin import IsAdmin
from filters.is_group import ChatTypeFilter

captcha_config = Router()

@captcha_config.message(Command('change_welcome'), ChatTypeFilter(), IsAdmin())
async def change_welcome_message(message: Message, command: CommandObject):
    """ Устанавливает текст приветственного сообщения для чата.
    Поддержка переносов на новую строку работает только когда админ пишет команду
    реплаем на сообщение с текстом """

    if message.reply_to_message:  # Если админ отвечает на сообщение, берём текст этого сообщения
        text_to_add = message.reply_to_message.text
    else:
        text_to_add = command.args  # Если нет, то берём аргумент команды

    if not text_to_add:
        await message.reply(
            'Пожалуйста, введите текст сообщения после команды или ответьте на сообщение, '
            'текст которого хотите использовать. \n'
            'Например: /change_welcome Добро пожаловать!\n '
            'Или ответом на сообщение, если у вас текст с переходом на новую строку!'
        )
        return

    try:
        text, created = WelcomeMessages.get_or_create(
            chat_id=message.chat.id,
            defaults={"welcome_message": text_to_add}
        )

        if text.welcome_message != text_to_add:
            text.welcome_message = text_to_add
            text.save()
            logging.info(f'Приветственное сообщение обновлено для чата {message.chat.id}')

        await message.reply('Приветственное сообщение успешно обновлено!')

    except Exception as e:
        logging.error(f'Ошибка при обновлении приветственного сообщения: {e}')
        await message.reply('Произошла ошибка при обновлении приветственного сообщения. '
                            'Попробуйте позже или свяжитесь с автором бота.')


@captcha_config.message(Command('change_ban_time'), ChatTypeFilter(), IsAdmin())
async def change_ban_time(message: Message, command: CommandObject):
    time_to_add = command.args
    if not time_to_add:
        await message.reply('Введите время бана при неправильно введённой капче в секундах. Например: /change_ban_time 60.')
        # TODO: сделать так, чтобы нельзя было подсунуть буквы или флот а ещё ограничение не менее 35 секунд и не более не помню сколько
        return

    try:
        time, created = CaptchaConfigs.get_or_create(chat_id=message.chat.id, defaults={"captcha_ban_time": time_to_add})

        if time != time_to_add:
            time.captcha_ban_time = time_to_add
            time.save()
            logging.info('Время бана пользователя успешно обновлено для чата {message.chat.id}')

        await message.reply('Время бана успешно обновлено!')

    except Exception as e:
        logging.error(f'Ошибка при обновлении времени бана пользователя: {e}')
        await message.reply('Произошла ошибка при обновлении времени бана пользователя. '
                            'Попробуйте позже или свяжитесь с автором бота.')


@captcha_config.message(Command('change_captcha_time'), ChatTypeFilter(), IsAdmin())
async def change_captcha_time(message: Message, command: CommandObject):
    time_to_add = command.args
    if not time_to_add:
        await message.reply(
            'Введите время на прохождение капчи в часах. Например: /change_captcha_time 2.')
        # TODO: сделать так, чтобы нельзя было подсунуть буквы или флот, тоже ограничить, типо не дольше 500 часов
        return

    try:
        time, created = CaptchaConfigs.get_or_create(chat_id=message.chat.id,
                                                     defaults={"captcha_time": time_to_add})

        if time != time_to_add:
            time.captcha_time = time_to_add
            time.save()
            logging.info('Время на прохождение капчи успешно обновлено для чата {message.chat.id}')

        await message.reply('Время на прохождение капчи успешно обновлено!')

    except Exception as e:
        logging.error(f'Ошибка при обновлении времени на прохождение капчи: {e}')
        await message.reply('Произошла ошибка при обновлении времени на прохождение капчи. '
                            'Попробуйте позже или свяжитесь с автором бота.')
