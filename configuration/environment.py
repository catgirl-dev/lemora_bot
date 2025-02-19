import os
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from configuration.scheduler_config import create_scheduler

load_dotenv()

TOKEN: str = os.getenv('BOT_TOKEN')

KISSER_ID: int = int(os.getenv('KISSER_ID') or 0)
LEMORA_CHAT_ID: int = int(os.getenv('LEMORA_CHAT_ID') or 0)

if not TOKEN:
    exit('Токен не обнаружен, пожалуйста укажите BOT_TOKEN в переменной окружения')

if os.getenv('KISSER_ID') == 0:
    logging.info('KISSER_ID не указан')
if os.getenv('LEMORA_CHAT_ID') == 0:
    logging.info('LEMORA_CHAT_ID не указан')

bot: Bot = Bot(TOKEN)

dp: Dispatcher = Dispatcher()

scheduler: AsyncIOScheduler = create_scheduler()
