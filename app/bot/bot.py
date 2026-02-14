import json
from typing import Dict
from pydantic import ValidationError
from aiogram import Bot
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.enums import ParseMode

import requests

from app.api.schemas.url_schema import URLShortenerRequestModel
from app.exc.bot_exceptions import (
    NoSiteHostProvidedError,
    TelegramAPIKeyNotProvidedError,
)
from app.data.db.models import URLPairModel
from app.settings import app_settings

from .states import ShorteningUrlState

if not app_settings.telegram_api_key:
    raise TelegramAPIKeyNotProvidedError()

if not app_settings.api_link:
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
        resp = requests.post(f"{app_settings.api_link}/shorten", json={"url": str(url.url)})
        if resp.status_code > 500:
            await message.answer("Произошла ошибка на стороне сервера! Повторите попытку позже...")
        
        print()
        data: Dict[str, str] = json.loads(resp.text)
        short_code: str = data.get("short_code")
        await message.answer(f"Готово! Твоя сокращенная ссылка - {app_settings.api_link}/{short_code}")

    except ValidationError:
        await message.answer("Ошибка: Вы предоставили неверный URL! Пример URL - https://example.com")

    finally:
        await state.clear()

@dp.message(Command("all"))
async def all_url_pairs(message: Message):
    result = ""
    resp = requests.get(f"{app_settings.api_link}/all")
    if resp.status_code > 500:
        await message.answer("Произошла ошибка на стороне сервера! Попробуйте позже...")
        return 

    data = json.loads(resp.text)
    pairs = [URLPairModel(original_url=pair.get("original_url"), shortened_url_code=pair.get("short_code")) for pair in data]
    for pair in pairs:
        result += f"Оригинал: {pair.original_url} -> {app_settings.api_link}/{pair.shortened_url_code} \n"

    await message.answer(result, parse_mode=ParseMode.HTML)

async def run_bot():
    await dp.start_polling(bot)