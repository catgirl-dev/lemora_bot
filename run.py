import asyncio
from configuration.logging_config import setup_logging

from configuration.environment import bot, dp, scheduler

from routers.base import base
from routers.captcha.captcha_config import captcha_config
from routers.commands import commands
from routers.lifecycle import lifecycle
from routers.captcha.captcha import captcha
from routers.admin_commands import admin

#  _._     _,-'""`-._
# (,-.`._,'(      |\`-/|
#     `-.-' \ )-`( , o o) ノ harro everynyan :з
#          `-    \`_`"'

async def main():
    setup_logging()
    scheduler.start()

    dp.include_routers(base, commands, lifecycle, captcha, admin, captcha_config)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
