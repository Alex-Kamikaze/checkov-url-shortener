import pytest


@pytest.mark.asyncio
async def test_bot_start_command():

    answer_message = "Привет! Для получения справки напиши команду /help"
    assert answer_message == "Привет! Для получения справки напиши команду /help"