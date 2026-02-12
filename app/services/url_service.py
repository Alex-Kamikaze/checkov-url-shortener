from typing import List
from hashlib import sha384
from base62 import encodebytes
from dataclasses import dataclass

from pydantic import ValidationError

from app.data.db.models import URLPairModel
from app.exc.url_exceptions import IncorrectURLSuppliedError
from app.data.repository.repository import Repository

@dataclass
class URLService():
    repository: Repository

    def _create_short_url(self, origin_url: str) -> str:
        """
        Создает сокращенную ссылку из длинной
        ! Только для внутренного использования

        Args:
            original_url (str): Исходный URL

        Returns:
            str: Сокращенный URL
        """
        hash = sha384(origin_url.encode("utf-8")).digest()[:10]
        result: str = encodebytes(hash)
        return result[:10]

    def _insert_url_pair_in_database(self, pair: URLPairModel):
        """
        Записывает в базу данных пару оригинальный/сокращенный URL
        ! Только для внутреннего использования

        Args:
            pair (URLPairModel): Пара для записи

        Raises:
            URLAlreadyExistsError: Если оригинальный или сокращенный URL уже существует в базе
        """
        self.repository.insert_new_url_pair(pair)

    def _initialize_url_pair_model(self, origin_url: str) -> URLPairModel:
        """
        Фабрика для создания `URLPairModel` для дальнейшего использования в функции `__insert_url_pair_in_database`
        ! Только для внутреннего использования

        """
        short_url = self._create_short_url(origin_url)
        pair = URLPairModel(original_url=origin_url, shortened_url_code=short_url)  # ty:ignore[invalid-argument-type]
        return pair

    def create_url_pair(self, origin_url: str) -> str:
        """
        Создает в базе пару оригинальный/сокращенный URL и возвращает сокращенный URL

        Args:
            original_url (str): Исходный URL для сокращения

        Returns:
            str: Сокращенный URL

        Raises:
            URLAlreadyExistsError: Если оригинальный или сокращенный URL уже существует в базе
        """
        pair = self._initialize_url_pair_model(origin_url)
        self._insert_url_pair_in_database(pair)
        return pair.shortened_url_code

    def get_original_url_from_short(self, short_url: str) -> str:
        """
        Ищет в базе исходный URL по его сокращенной версии и возвращает его

        Args:
            short_url (str): Сокращенный URL

        Returns:
            str: Исходный URL

        Raises:
            URLDoesNotExistsError: Если URL не найден в базе
        """
        return self.repository.get_original_url_from_shortened(short_url)

    def delete_url_pair_from_original_url(self, origin_url: str):
        """
        Удаляет из пары связку URL по оригинальному URL  


        Args:
            origin_url (str): Оригинальный URL
        Raises:
            `URLNotFoundError`: Если указанного URL нет в базе
            `IncorrectURLSuppliedError`: Если в функцию предоставлен неверный URL
        """
        try:
            filtred_url = URLPairModel(original_url=origin_url, shortened_url_code="val")  # ty:ignore[invalid-argument-type]
            self.repository.delete_url_pair(str(filtred_url.original_url))
        except ValidationError:
            raise IncorrectURLSuppliedError()

    def get_all_url_pairs_from_db(self) -> List[URLPairModel]:
        return self.repository.get_all_pairs()