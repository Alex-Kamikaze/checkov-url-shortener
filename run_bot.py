"""
Запускает бота в телеграмме для генерации сокращенных ссылок
"""
from asyncio import run
from app.bot.bot import run_bot

run(run_bot())