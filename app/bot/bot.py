from app.bot.services import BotService
import json
from pydantic import ValidationError
from aiogram import Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.enums import ParseMode

from loguru import logger

from app.api.schemas.url_schema import URLShortenerRequestModel
from app.exc.bot_exceptions import (
    NoSiteHostProvidedError,
    TelegramAPIKeyNotProvidedError,
)
from app.settings import app_settings

from .states import ShorteningUrlState

if not app_settings.telegram_api_key:
    logger.error("Error! Telegram API Key Not Provided!")
    raise TelegramAPIKeyNotProvidedError()

if not app_settings.api_link:
    logger.error("Error! API Host not provided!")
    raise NoSiteHostProvidedError()

bot = Bot(token=app_settings.telegram_api_key)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def start_command(msg: Message):
    await msg.answer("Привет! Для получения справки напиши команду /help")

@dp.message(Command("help"))
async def help_message(msg: Message):
    await msg.answer("/start - начало работы \n/all - все доступные сокращенные ссылки и их оригиналы \n/shorten - сгенерировать новую сокращенную ссылку", parse_mode=ParseMode.HTML)


@dp.message(Command("shorten"))
async def start_generation(msg: Message, state: FSMContext):
    await state.set_state(ShorteningUrlState.enters_url)
    await msg.answer("Введи сслылку для сокращения: ")


@dp.message(ShorteningUrlState.enters_url)
async def generate_shorten_url(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Ошибка: Отсутствует текст для генерации ссылки!")
        await state.clear()
        return
    
    try:
        url = URLShortenerRequestModel(url=message.text)  # ty:ignore[invalid-argument-type]
        short_code = BotService.call_api_for_short_link(url)
        if not short_code:
            await message.answer("Произошла ошибка на стороне сервера! Попробуйте повторить попытку позже...")
            return 
        
        await message.answer(f"Готово! Твоя сокращенная ссылка - {app_settings.api_link}/{short_code}")

    except ValidationError:
        await message.answer("Ошибка: Вы предоставили неверный URL! Пример URL - https://example.com")

    finally:
        await state.clear()

@dp.message(Command("all"))
async def all_url_pairs(message: Message):
    result = ""
    pairs = BotService.call_api_for_all_links()
    if not pairs:
        await message.answer("Произошла ошибка на сервере! Попробуйте повторить попытку позже...")
        return

    for pair in pairs:
        result += f"Оригинал: {pair.original_url} -> {app_settings.api_link}/{pair.shortened_url_code} \n"

    await message.answer(result, parse_mode=ParseMode.HTML)

async def run_bot():
    await dp.start_polling(bot)