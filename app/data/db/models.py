"""
Модели, к которым должны приводиться данные из базы данных (Т.к. ORM использовать нельзя, то выкручиваюсь как могу :) )

"""

from pydantic import BaseModel, HttpUrl, field_validator

class URLPairModel(BaseModel):
    """
    Пара связанных URL: Оригинальный и сокращенный
    
    Attributes:
        original_url (HttpUrl): Оригинальный URL
        shortened_url_code (str): Сокращенный URL
    """

    original_url: HttpUrl
    shortened_url_code: str

    @field_validator("shortened_url_code", mode="before")
    def validated_shortened_code(cls, code: str) -> str:
        if not len(code):
            raise ValueError("Сокращенный URL не может быть пустым!")

        if len(code) > 10:
            raise ValueError("Слишком длинный сокращенный URL!")
        return code
