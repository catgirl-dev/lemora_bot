import logging

from aiogram import F, Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, LEFT, RESTRICTED, MEMBER, \
    ADMINISTRATOR, CREATOR, IS_NOT_MEMBER
from aiogram.types import Message, CallbackQuery, \
    ChatMemberUpdated

from captcha_config import muted_permissions, captcha_symbols
from configuration.environment import bot, scheduler
from database.models import Users, CaptchaConfigs
from keyboards.captcha_inline_keyboard import generate_captcha_keyboard
from texts.base import help_message_text
from utils.admins_actualization import admins, add_chat_to_db, remove_chat_id_from_db
from utils.captcha.captcha_tools import generate_captcha, generate_captcha_config, \
    restrict_if_not_admin, get_or_create_user, send_captcha_message, schedule_failed_captcha, \
    save_bot_message_id, handle_correct_captcha, handle_failed_captcha

chat_updates: Router = Router()

@chat_updates.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed= (ADMINISTRATOR | MEMBER) >> (KICKED | LEFT | RESTRICTED)
    )
)
async def bot_left(event: ChatMemberUpdated):
    """ Обработка события, когда бот удалён из чата """
    await remove_chat_id_from_db(event.chat.id)
    logging.info(f"Бот был удалён из чата: event.chat_id")


@chat_updates.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR
    )
)
async def bot_added_as_admin(event: ChatMemberUpdated):
    """ Обработка события, когда бота добавили в чат, как админа """
    # Генерируем настройки капчи по умолчанию
    generate_captcha_config(event.chat.id)
    await add_chat_to_db(event.chat.id)
    await event.answer(help_message_text, parse_mode='Markdown')
    logging.info(f"Бот добавлен в чат {event.bot.id} как администратор.")

@chat_updates.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR
    )
)
async def bot_added_as_admin(event: ChatMemberUpdated):
    """ Обработка события, когда бота добавили в чат, как админа """
    if event.chat_member.user.id == event.bot.id:
        # Генерируем настройки капчи по умолчанию
        generate_captcha_config(event.chat.id)
        await add_chat_to_db(event.chat.id)
        await event.answer(help_message_text, parse_mode='Markdown')
        logging.info(f"Бот добавлен в чат {event.bot.id} как администратор.")



@chat_updates.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> MEMBER
    )
)
async def bot_added_as_member(event: ChatMemberUpdated, bot: Bot):
    """ Обработка события, когда бота добавили, как простого участника """
    chat_info = await bot.get_chat(event.chat.id)
    if chat_info.permissions.can_send_messages:
        generate_captcha_config(event.chat.id)
        await add_chat_to_db(event.chat.id)
        await event.answer(help_message_text, parse_mode='Markdown')
        logging.info(f"Бот добавлен в чат {event.bot.id} как обычный пользователь")
    else:
        logging.error(f'Что-то пошло не так при добавлении бота в чат: "{event.chat.id}" как обычного пользователя.'
                      f'У бота не было прав на отправку сообщений.')


@chat_updates.chat_member(F.new_chat_member.status == "kicked")
async def bot_removed_from_chat(event: ChatMemberUpdated):
    """ Обработка события удаления бота из чата """
    if event.old_chat_member.user.id == event.bot.id:
        logging.info(f"Бот был удалён из чата {event.chat.id}")
        await remove_chat_id_from_db(event.chat.id)


@chat_updates.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        >>
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_promoted(event: ChatMemberUpdated):
    """ Обработка повышения до администратора """
    if event.chat.id not in admins:
        admins[event.chat.id] = {}

    admins[event.chat.id][event.new_chat_member.user.id] = event.new_chat_member.can_restrict_members

    logging.info(f"{event.new_chat_member.user.first_name} был(а) повышен(а) до администратора")


@chat_updates.chat_member(ChatMemberUpdatedFilter())
async def admin_rights_updated(event: ChatMemberUpdated):
    """ Обработка изменения прав пользователя на бан """
    if event.chat.id not in admins:
        admins[event.chat.id] = {}

    admins[event.chat.id][event.new_chat_member.user.id] = event.new_chat_member.can_restrict_members

    logging.info(f"Права пользователя {event.new_chat_member.user.first_name} были изменены")


@chat_updates.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=
        (KICKED | LEFT | RESTRICTED | MEMBER)
        <<
        (ADMINISTRATOR | CREATOR)
    )
)
async def admin_demoted(event: ChatMemberUpdated):
    """ Обработка понижения администратора до обычного пользователя """
    chat_id = event.chat.id
    user_id = event.new_chat_member.user.id

    if chat_id in admins and user_id in admins[chat_id]:
        del admins[chat_id][user_id]

    logging.info(f"{event.new_chat_member.user.first_name} был(а) понижен(а) с роли администратора")


@chat_updates.message(F.content_type == 'new_chat_members')
async def new_chat_member(message: Message):
    """ Генерация капчи для зашедшего в чат пользователя """
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

    message_response = await send_captcha_message(message, captcha_image, keyboard)
    save_bot_message_id(user, message_response)

    captcha_config = CaptchaConfigs.get_or_create(chat_id=message.chat.id)

    captcha_time = int(str(captcha_config.captcha_time))

    link = message.from_user.mention_html()
    schedule_failed_captcha(
        message.chat.id, message.new_chat_members[0].id, int(str(user.message_id)), link, captcha_time
    )


@chat_updates.callback_query()
async def captcha_inline_callback(callback: CallbackQuery):
    """ Обработка нажатий пользователем на кнопки капчи """
    # Чтобы кнопки мог нажимать только тот, кому предназначается капча
    user = Users.get_or_none(
        Users.user_id == callback.from_user.id,
        Users.chat_id == callback.message.chat.id,
        Users.message_id == callback.message.reply_to_message.message_id
    )
    if not user:
        logging.info('Не пройденная проверка по ID')
        await callback.answer('Эта капча не для тебя!')
        return

    user_answer: str = str(user.answer)
    user_captcha: str = str(user.chat_updates)

    link: str = callback.from_user.mention_html()

    user_answer: str = f"{user_answer}{callback.data}"

    if len(user_answer) < len(user_captcha):
        await callback.answer('')
        return

    message_id: int = int(str(user.message_id))

    if user_answer == user_captcha:
        await handle_correct_captcha(callback, user, link, message_id)

    else:
        await handle_failed_captcha(callback, user, link, message_id)


@chat_updates.message(F.content_type == "left_chat_member")
async def left_chat_member(message: Message):
    """ Если пользователь вышел из чата, не пройдя капчу, записи в базе данных, связанные с ним,
    чистятся. Задание планировщика и сообщение бота с капчей удаляются."""
    user = Users.get_or_none(
        Users.user_id == message.from_user.id,
        Users.chat_id == message.chat.id
    )

    if user:
        message_id = user.message_id
        scheduler.remove_job(str(message.chat.id) + '_' +
                             str(message.from_user.id) + '_' +
                             str(message_id)
                             )

        await bot.delete_message(message.chat.id, user.bot_message_id)
        user.delete_instance()
