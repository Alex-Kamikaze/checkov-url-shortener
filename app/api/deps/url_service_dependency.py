from typing import Annotated

from fastapi import Depends

from app.data.repository.repository import Repository
from app.services.url_service import URLService
from app.settings import app_settings


def provide_database_name() -> str:
    """
    Возвращает строку для подключения к базе данных
    """
    return app_settings.db_name


def provide_repository():
    """
    Возвращает репозиторий с подключением к базе данных
    """
    with Repository(provide_database_name()) as repo:
        repo.initialize_database()
        yield repo


def provide_url_service(repository: Annotated[Repository, Depends(provide_repository)]):
    """
    Возвращает сервис для работы с парами URL и репозиторием

    Args:
        repository (Repository): Экземпляр репозитория. По умолчанию получает экземпляр из `provide_repository`
    """

    return URLService(repository)
