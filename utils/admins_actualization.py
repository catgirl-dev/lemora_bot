import logging

from configuration.environment import bot
from database.models import Chats, CaptchaConfigs

admins: dict = {}

async def fetch_admins(chat_id: int) -> None:
    """ Получает список администраторов для чата и добавляет их в словарь """
    chat_admins = await bot.get_chat_administrators(chat_id)
    admins[chat_id] = {admin.user.id for admin in chat_admins}
    logging.info(f'Добавлены администраторы для чата {chat_id}')


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
