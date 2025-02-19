from aiogram import Router

from configuration.environment import dp, scheduler
from database.models import db, User, Rules, WelcomeMessage, CaptchaConfig

lifecycle: Router = Router()


@dp.startup()
async def on_startup():
    db.connect()
    db.create_tables([User, Rules, WelcomeMessage, CaptchaConfig])


@dp.shutdown()
async def on_shutdown():
    db.close()
    scheduler.shutdown()
