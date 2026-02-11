import sqlite3
from typing import List

from app.data.db.models import URLPairModel
from app.exc.db_exceptions import URLAlreadyExistsError, URLNotFoundError


class Repository:
    """
    Репозиторий для взаимодействия с базой данных

    Attributes:
        db: Подключение к базе
        cursor: Курсор для работы с запросами
    """

    def __init__(self, conn_str: str):
        """
        Конструктор репозитория

        Args:
            conn_str: Строка для подключения к базе
        """

        self.db: sqlite3.Connection = sqlite3.connect(conn_str, check_same_thread=False)
        self.cursor = self.db.cursor()

    def initialize_database(self):
        """
        Создает в базе необходимую таблицу для работы с парами URL
        """

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS urls 
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT UNIQUE,
                shortened_url VARCHAR(5) UNIQUE
            );
            """
        )

        self.db.commit()

    def insert_new_url_pair(self, pair: URLPairModel):
        """
        Вставляет в базу данных новую пару связанных URL

        Args:
            pair (`URLPairModel`): Пара связанных URL

        Raises:
            `URLAlreadyExistsError`: Если происходит попытка вставить не оригинальный URL
        """
        try:
            self.cursor.execute(
                "INSERT INTO urls (original_url, shortened_url) VALUES (?, ?)",
                (str(pair.original_url), pair.shortened_url_code),
            )
            self.db.commit()

        except sqlite3.IntegrityError:
            raise URLAlreadyExistsError()

    def get_original_url_from_shortened(self, short_url: str) -> str:
        """
        Возвращает из базы оригинальный URL по его сокращенной версии

        Args:
            short_url (str): Сокращенный URL

        Returns:
            str: Оригинальный URL
        """

        self.cursor.execute(
            "SELECT original_url FROM urls WHERE shortened_url = ?", (short_url,)
        )
        url = self.cursor.fetchone()
        if url is None:
            raise URLNotFoundError()

        return url[0]

    def delete_url_pair(self, original_url: str):
        """
        Удаляет из базы связку URL

        Args:
            original_url (str): Оригинальный URL для поиска на удаление

        Raises:
            URLNotFoundError: Если URL не найден в базе
        """
        self.cursor.execute("SELECT shortened_url FROM urls WHERE original_url = ?", (str(original_url), ))
        url = self.cursor.fetchone()
        if not url:
            raise URLNotFoundError()
        self.cursor.execute("DELETE FROM urls WHERE original_url = ?", (str(original_url),))
        self.db.commit()

    def get_all_pairs(self) -> List[URLPairModel]:
        self.cursor.execute("SELECT * FROM urls")
        urls = self.cursor.fetchall()
        return [URLPairModel(original_url=pair[1], shortened_url_code=pair[2]) for pair in urls]

    def __del__(self):
        self.cursor.close()
        self.db.close()
