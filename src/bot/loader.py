import asyncio

from aiogram import Bot
from aiogram.types import ParseMode

from loguru import logger
from pathlib import Path

from .databases import ComicsDatabase, UsersDatabase, create_pool
from .config import API_TOKEN, DATABASE_URL

root = Path(__file__).parent.parent.parent
static_path = root.joinpath('static')
logs_path = root.joinpath('logs')
path_to_json = root.joinpath('static/ru_data_from_xkcd_ru_tg_channel.json')

from .xkcd_parser import Parser

bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
loop = asyncio.get_event_loop()
pool = loop.run_until_complete(create_pool(DATABASE_URL))

users_db = UsersDatabase(pool)
comics_db = ComicsDatabase(pool)

parser = Parser()

loop.run_until_complete(users_db.create())
loop.run_until_complete(comics_db.create())
loop.run_until_complete(parser.create())

logger.add(f'{logs_path}/actions.log', rotation='5 MB', level='INFO')
logger.add(f'{logs_path}/errors.log', rotation='500 KB', level='ERROR', backtrace=True, diagnose=True)
