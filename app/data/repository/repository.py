import sqlite3
from typing import List, Optional, Self
from loguru import logger

from app.data.db.models import URLPairModel
from app.exc.db_exceptions import (
    URLNotFoundError,
    ConnectionNotEstablishedError,
)


class Repository():
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
        self.conn_str = conn_str
        self.connection = None

    def __enter__(self) -> Self:
        try:
            self.connection = sqlite3.connect(self.conn_str, check_same_thread=False)
            logger.info(f"Created a new connection with database {self.conn_str}")
            return self
        except sqlite3.OperationalError as exc:
            logger.error(f"Error occured while working with DB: {str(exc)}")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.connection:
            logger.info(f"Closing connection with database {self.conn_str}")
            self.connection.close()

    def initialize_database(self):
        """
        Создает в базе необходимую таблицу для работы с парами URL

        Raises:
            `ConnectionNotEstablishedError`: Если не установлено соединение с базой
        """
        if self.connection:
            with self.connection as db:
                cursor = db.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS urls 
                    (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_url TEXT UNIQUE,
                        shortened_url VARCHAR(5) UNIQUE
                    );
                    """
                )
                db.commit()
                cursor.close()
        else:
            raise ConnectionNotEstablishedError()

    def insert_new_url_pair(self, pair: URLPairModel) -> Optional[str]:
        """
        Вставляет в базу данных новую пару связанных URL

        Args:
            pair (`URLPairModel`): Пара связанных URL
        Raises:
            `ConnectionNotEstablishedError`: Если соединение с базой не установлено
        """
        if self.connection:
            with self.connection as db:
                cursor = db.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO urls (original_url, shortened_url) VALUES (?, ?)",
                        (str(pair.original_url), pair.shortened_url_code),
                    )
                    db.commit()

                except sqlite3.IntegrityError:
                    logger.info(f"Found existing URL in DB: {pair.original_url}, retreiving its short_code instead of creating")
                    db.rollback()
                    cursor.execute(
                        "SELECT shortened_url FROM urls WHERE original_url = ?",
                        (str(pair.original_url),),
                    )
                    return cursor.fetchone()[0]

        else:
            raise ConnectionNotEstablishedError()

    def get_original_url_from_shortened(self, short_url: str) -> str:
        """
        Возвращает из базы оригинальный URL по его сокращенной версии

        Args:
            short_url (str): Сокращенный URL

        Returns:
            str: Оригинальный URL
        """
        if self.connection:
            with self.connection as db:
                cursor = db.cursor()

                cursor.execute(
                    "SELECT original_url FROM urls WHERE shortened_url = ?",
                    (short_url,),
                )
                url = cursor.fetchone()
                if url is None:
                    raise URLNotFoundError()

                return url[0]

        else:
            raise ConnectionNotEstablishedError()

    def delete_url_pair(self, shorten_url: str):
        """
        Удаляет из базы связку URL

        Args:
            shorten_url (str): Сокращенный URL для поиска на удаление

        Raises:
            URLNotFoundError: Если URL не найден в базе
        """
        if self.connection:
            with self.connection as db:
                cursor = db.cursor()
                cursor.execute(
                    "DELETE FROM urls WHERE shortened_url = ?", (shorten_url,)
                )
                if cursor.rowcount == 0:
                    raise URLNotFoundError()
                    
                db.commit()
        else:
            ConnectionNotEstablishedError()

    def get_all_pairs(self) -> List[URLPairModel]:
        """
        Возвращает все пары URL из базы

        Returns:
            List[URLPairModel]: Пары URL из базы

        Raises:
            `ConnectionNotEstablishedError`: Если не установлено соединение с базой
        """
        if self.connection:
            with self.connection as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM urls")
                urls = cursor.fetchall()
                return [
                    URLPairModel(original_url=pair[1], shortened_url_code=pair[2])
                    for pair in urls
                ]
        else:
            raise ConnectionNotEstablishedError()