import logging

from aiogram.enums import ChatMemberStatus

from configuration.environment import bot
from database.models import Chats

CHANNEL_BOT_ID = 136817688
admins: dict[int, dict[int, bool]] = {}

async def fetch_admins(chat_id: int) -> None:
    """ Получает список администраторов чата и их прав на бан для чата и добавляет их в словарь """
    chat_admins = await bot.get_chat_administrators(chat_id)
    admins.setdefault(chat_id, {})

    for admin in chat_admins:
        if admin.status == ChatMemberStatus.CREATOR:
            admins[chat_id][admin.user.id] = True
            continue

        elif admin.user.is_bot:
            if admin.user.id == CHANNEL_BOT_ID:
                # Если человек пишет от имени чата, и айди чата, в котором он пишет, совпадает с айди
                # чата, от которого он пишет, он является админом. Дописать функционал
                continue

        else:
            admins[chat_id][admin.user.id] = admin.can_restrict_members

    logging.info(f'Актуализированы администраторы для чата {chat_id}')


async def get_all_admins() -> None:
    """ Получает из базы данных список чатов и для него обновляет данные по администраторам """
    global admins
    admins.clear()

    try:
        chat_ids = [chat.chat_id for chat in Chats.select()]
    except Exception as e:
        logging.error(f"Ошибка при получении чатов из БД: {e}")
        logging.info(f"admins: {admins}")

    for chat_id in chat_ids:
        await fetch_admins(chat_id)

    logging.info(admins)


async def add_chat_to_db(chat_id: int):
    try:
        Chats.get_or_create(chat_id=chat_id)
        logging.info(f"Чат с ID {chat_id} успешно добавлен или уже существует в базе.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении айди чата в бд: {e}")


async def remove_chat_id_from_db(chat_id):
    try:
        Chats.delete().where(Chats.chat_id == chat_id).execute()
    except Exception as e:
        logging.error(f"Ошибка при удалении данных из бд: {e}", exc_info=True)
