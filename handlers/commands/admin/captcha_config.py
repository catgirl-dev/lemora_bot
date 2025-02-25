import logging

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from database.models import WelcomeMessages, CaptchaConfigs
from filters.is_admin import IsAdmin
from filters.is_group import IsGroup

captcha_config = Router()
captcha_config.message.filter(IsGroup(), IsAdmin())

@captcha_config.message(Command('change_welcome'))
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


@captcha_config.message(Command('change_ban_time'))
async def change_ban_time(message: Message, command: CommandObject):
    time_to_add = command.args

    if not time_to_add:
        await message.reply(
            'Введите время бана при неправильно введённой капче в секундах. Например: /change_ban_time 60.'
            'Если вы не хотите, чтобы пользователь блокировался перманентно, выберите число в диапазоне '
            'от 30 до 31622400.')
        return

    if not time_to_add.isdigit() or int(time_to_add) == 0:
        await message.reply('Ошибка. Аргумент команды должен являться целым положительным числом больше нуля! '
                            'Например: /change_ban_time 60')
        return

    is_confirmed = time_to_add[0] == '!'
    if time_to_add[0] == '!':
        time_to_add = time_to_add[1:]

    if time_to_add not in (30, 31622400) and not is_confirmed:
        await message.reply('Вы ввели число менее 30 секунд или более 31622400. Так пользователь будет блокироваться перманентно.'
                            'Это специфика Telegram.'
                            'Если вы хотите этого, введите команду ещё раз, поставив перед числом восклицательный знак.'
                            'Например: /change_ban_time !20. Если это не то, что вы планировали, выберите число в диапазоне'
                            'от 30 до 31622400.')

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


@captcha_config.message(Command('change_captcha_time'))
async def change_captcha_time(message: Message, command: CommandObject):
    time_to_add = command.args
    if not time_to_add:
        await message.reply(
            'Введите время на прохождение капчи в часах. Например: /change_captcha_time 2.')
        return

    if not time_to_add.isdigit() or int(time_to_add) == 0:
        await message.reply('Ошибка. Аргумент команды должен являться целым положительным числом больше нуля и меньше 120.'
                            'Например: /change_captcha_time 40')

    if int(time_to_add) not in (1, 120):
        await message.reply('Ошибка. Выберите число в диапазоне от 1 до 120 часов.')
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
