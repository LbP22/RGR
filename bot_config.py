import asyncio

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State

TOKEN = "2091506588:AAFFalEFDB9S9RUkXMkvKl4nuUdqUjOBTYw"
PAYMENTS_PROVIDER_TOKEN = "632593626:TEST:sandbox_i35541414349"
admin_id = [416977980]
loop = asyncio.get_event_loop()

bot = Bot(token=TOKEN, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, loop=loop, storage=storage)


class LogIn(StatesGroup):
    reg_name = State()
    reg_mail = State()
    reg_pas = State()
    log_name = State()
    log_pas = State()
    logged = State()


class Search(StatesGroup):
    find_film = State()
    find_author = State()


class FilmAdd(StatesGroup):
    add_name = State()
    add_genre = State()
    add_trilogy = State()
    add_film_photo = State()
    add_author_name = State()
    add_author_desc = State()
    add_author_photo = State()
    add_price = State()
    add_payment = State()
    add_confirm = State()


class Buy(StatesGroup):
    buy_proceed = State()
    buy_success = State()

