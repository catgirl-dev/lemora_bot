import asyncio
import logging

from configuration.logging_config import setup_logging

from configuration.environment import bot, dp, scheduler

from handlers.commands.base import base
from handlers.commands.admin.captcha_config import captcha_config
from handlers.commands.user import commands
from handlers.lifecycle import lifecycle
from handlers.chat_updates import chat_updates
from handlers.commands.admin.moderation import admin

#  _._     _,-'""`-._
# (,-.`._,'(      |\`-/|
#     `-.-' \ )-`( , o o) ノ harro everynyan :з
#          `-    \`_`"'

async def main():
    setup_logging()
    scheduler.start()

    dp.include_routers(base, commands, lifecycle, chat_updates, admin, captcha_config)
    logging.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
