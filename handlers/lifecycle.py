import logging

from aiogram import Router

from configuration.environment import dp, scheduler
from database.models import db, Users, Rules, WelcomeMessages, CaptchaConfigs, Chats
from utils.admins_actualization import get_all_admins

lifecycle: Router = Router()


@dp.startup()
async def on_startup():
    db.connect()
    db.create_tables([Chats, Users, Rules, WelcomeMessages, CaptchaConfigs])
    await get_all_admins()



@dp.shutdown()
async def on_shutdown():
    db.close()
    scheduler.shutdown()
