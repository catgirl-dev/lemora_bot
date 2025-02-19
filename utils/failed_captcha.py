import logging
import time

from aiogram.types import ChatMemberOwner, ChatMemberAdministrator, ChatMember

from utils.scheduler_args import SchedulerArgs
from configuration.environment import bot
from database.models import User, CaptchaConfig


async def failed_captcha(args: SchedulerArgs):
    """ Если пользователь не успел ввести капчу, он блокируется на captcha_ban_time.
    Записи в базе данных, связанные с ним, удаляются. """
    logging.info('Пользователь не успел ввести капчу')
    user = User.get(User.user_id == args.user_id, User.chat_id == args.chat_id)
    link: str = args.link

    captcha_config = CaptchaConfig.get_or_create(chat_id=args.chat_id)
    captcha_ban_time: int = int(str(captcha_config.captcha_ban_time))

    await bot.send_message(
        args.chat_id, f'{link}, не успел(а) пройти капчу! Он(а) может присоединиться к чату'
                      f'через {captcha_ban_time} секунд и попробовать вновь.',
        reply_to_message_id=args.message_id, parse_mode="HTML",
        disable_web_page_preview=True
    )

    chat_member: ChatMember = await bot.get_chat_member(args.chat_id, args.user_id)
    if not isinstance(chat_member, (ChatMemberOwner, ChatMemberAdministrator)):
        await bot.ban_chat_member(
            chat_id=args.chat_id,
            user_id=args.user_id,
            until_date=time.time() + captcha_ban_time
        )

    user.delete_instance()
