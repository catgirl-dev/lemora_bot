import logging
import time

from aiogram import F, Router
from aiogram.types import Message, ChatMemberOwner, ChatMemberAdministrator, CallbackQuery, ChatMemberBanned, ChatMember

from captcha_config import muted_permissions, captcha_symbols
from configuration.environment import bot, scheduler
from database.models import User, WelcomeMessage, CaptchaConfig
from keyboards.captcha_inline_keyboard import generate_captcha_keyboard
from utils.captcha.captcha_tools import generate_captcha, generate_captcha_config, \
    restrict_if_not_admin, get_or_create_user, send_captcha_message, schedule_failed_captcha, \
    save_bot_message_id

captcha: Router = Router()

@captcha.message(F.content_type == 'new_chat_members')
async def new_chat_member(message: Message):
    """ Генерация капчи для зашедшего в чат пользователя """

    # Когда Лемора бот впервые добавляется в чат, в таблице CaptchaConfig
    # генерируются стандартные настройки капчи для чата
    if message.from_user.id == bot.id:
        generate_captcha_config(message.chat.id)
        return

    # Не генерируем капчу для ботов
    if message.new_chat_members[0].is_bot:
        return

    # Мут человека, пока он не прошёл капчу
    await restrict_if_not_admin(bot, message.chat, message.new_chat_members[0].id, muted_permissions)

    captcha_text, mixed_captcha, captcha_image = generate_captcha()

    user = get_or_create_user(
        chat_id=message.chat.id,
        user_id=message.new_chat_members[0].id,
        message_id=message.message_id,
        captcha="".join(captcha_text)
    )

    keyboard = generate_captcha_keyboard(captcha_symbols)

    message_response = await send_captcha_message(bot, message, captcha_image, keyboard)
    save_bot_message_id(user, message_response)

    captcha_config = CaptchaConfig.get_or_create(chat_id=message.chat.id)

    captcha_time = int(str(captcha_config.captcha_time))

    link = message.from_user.mention_html()
    schedule_failed_captcha(
        message.chat.id, message.new_chat_members[0].id, user.message_id, link, captcha_time
    )


# TODO: отрефакторить
@captcha.callback_query()
async def captcha_inline_callback(callback: CallbackQuery):
    """ Обработка нажатий пользователем на кнопки капчи """

    # Чтобы кнопки мог нажимать только тот, кому предназначается капча
    user = User.get_or_none(
        User.user_id == callback.from_user.id,
        User.chat_id == callback.message.chat.id,
        User.message_id == callback.message.reply_to_message.message_id
    )
    if not user:
        logging.info('Не пройденная проверка по ID')
        await callback.answer('Эта капча не для тебя!')
        return

    user_answer: str = str(user.answer)
    user_captcha: str = str(user.captcha)

    link: str = callback.from_user.mention_html()

    # TODO: Выглядит не очень, надо бы разобраться
    answer_buffer: str = user_answer + callback.data
    user.answer = answer_buffer
    user.save()
    user_answer = answer_buffer

    if len(user_answer) < len(user_captcha):
        await callback.answer('')
        return

    message_id: int = int(str(user.message_id))

    if user_answer == user_captcha:
        logging.info('Введённая верно капча')

        chat_member: ChatMember = await bot.get_chat_member(
            callback.message.chat.id,
            callback.from_user.id
        )

        # Анмут человека прошедшего капчу
        if not isinstance(
                chat_member, (ChatMemberOwner, ChatMemberAdministrator)):
            await callback.message.chat.restrict(
                user_id=callback.from_user.id,
                permissions=(
                    await bot.get_chat(callback.message.chat.id)).permissions)

        welcome_message = WelcomeMessage.get_or_none(chat_id=callback.message.chat.id)
        welcome_message_text: str = str(welcome_message.welcome_message)

        await bot.send_message(
            callback.message.chat.id,
            f'{link}, {welcome_message_text}',
            reply_to_message_id=message_id,
            parse_mode="HTML",
            disable_web_page_preview=True
            )

        await callback.message.delete()
        scheduler.remove_job(
            str(callback.message.chat.id) + '_' +
            str(callback.from_user.id) + '_' +
            str(message_id)
        )

        user.delete_instance()
        logging.info('База данных очищена')

    else:
        logging.info('Не пройденная пользователем капча')

        # У пользователя 3 попытки на то, чтобы пройти капчу
        if int(user.attempt_counter) < 2:
            user.attempt_counter = user.attempt_counter + 1
            user.answer = ''
            user.save()
            await callback.answer('Не верно! Попробуйте снова!')
            return

        chat_member: ChatMember = await bot.get_chat_member(
            callback.message.chat.id,
            callback.from_user.id
        )

        if not isinstance(chat_member, ChatMemberBanned):
            await bot.send_message(
                callback.message.chat.id,
                f'{link}, Вы не прошли капчу! Попробуйте снова.',
                reply_to_message_id=message_id,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

            captcha_config = CaptchaConfig.get_or_create(chat_id=callback.message.chat.id)
            captcha_ban_time = int(str(captcha_config.captcha_ban_time))

            if not isinstance(
                    chat_member, (ChatMemberAdministrator, ChatMemberOwner)):
                await bot.ban_chat_member(
                    chat_id=callback.message.chat.id,
                    user_id=callback.from_user.id,
                    until_date=time.time() + captcha_ban_time
                )

            await callback.message.delete()
            scheduler.remove_job(str(callback.message.chat.id) + '_' +
                                 str(callback.from_user.id) + '_' +
                                 str(message_id))
            user.delete_instance()
            logging.info('База данных очищена')


@captcha.message(F.content_type == "left_chat_member")
async def left_chat_member(message: Message):
    """ Если пользователь вышел из чата, не пройдя капчу, записи в базе данных, связанные с ним,
    чистятся. Задание планировщика и сообщение бота с капчей удаляются."""

    user = User.get_or_none(
        User.user_id == message.from_user.id,
        User.chat_id == message.chat.id
    )

    if user:
        message_id = user.message_id
        scheduler.remove_job(str(message.chat.id) + '_' +
                             str(message.from_user.id) + '_' +
                             str(message_id)
                             )

        await bot.delete_message(message.chat.id, user.bot_message_id)
        user.delete_instance()
