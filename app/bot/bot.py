from app.exc.db_exceptions import URLAlreadyExistsError
from pydantic import ValidationError
from aiogram import Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from app.api.schemas.url_schema import URLShortenerRequestModel
from app.data.repository.repository import Repository
from app.exc.bot_exceptions import (
    NoSiteHostProvidedError,
    TelegramAPIKeyNotProvidedError,
)
from app.services.url_service import URLService
from app.settings import app_settings

from .states import ShorteningUrlState

if not app_settings.telegram_api_key:
    raise TelegramAPIKeyNotProvidedError()

if not app_settings.site_host:
    raise NoSiteHostProvidedError()

bot = Bot(token=app_settings.telegram_api_key)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def start_command(msg: Message):
    await msg.answer("Привет! Для получения справки напиши команду /help")

@dp.message(Command("help"))
async def help_message(msg: Message):
    await msg.answer("/start - начало работы <br> /all - все доступные сокращенные ссылки и их оригиналы <br> /shorten - сгенерировать новую сокращенную ссылку")


@dp.message(Command("shorten"))
async def start_generation(msg: Message, state: FSMContext):
    await state.set_state(ShorteningUrlState.enters_url)
    await msg.answer("Введи сслылку для сокращения")


@dp.message(ShorteningUrlState.enters_url)
async def generate_shorten_url(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Ошибка: Отсутствует текст для генерации ссылки!")
        return
    try:
        filtred_url = URLShortenerRequestModel(url=message.text)  # ty:ignore[invalid-argument-type]
        url_service = URLService(repository=Repository(app_settings.db_name))
        short_code = url_service.create_url_pair(str(filtred_url.url))
        final_url = f"{app_settings.site_host}/{short_code}"
        await message.answer(f"Готово! Ваша сокращенная ссылка - {final_url}")
    except ValidationError:
        await message.answer("Ошибка: Предоставлен неверный URL для генерации. Пример - https://example.com")
    except URLAlreadyExistsError:
        await message.answer("Ошибка: Данный URL уже существует в базе! Для просмотра всех доступных URL воспользуйтесь командой /all")
    finally:
        await state.clear()

@dp.message(Command("all"))
async def all_url_pairs(message: Message):
    url_service = URLService(repository=Repository(app_settings.db_name))
    pairs = url_service.get_all_url_pairs_from_db()
    result = str()
    for pair in pairs:
        result += f"Оригинал: {pair.original_url} -> {app_settings.site_host}/{pair.shortened_url_code}<br>"

    await message.answer(result)

async def run_bot():
    await dp.start_polling(bot)