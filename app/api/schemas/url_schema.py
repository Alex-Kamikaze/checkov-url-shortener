from pydantic import BaseModel, HttpUrl, field_validator

class URLShortenerRequestModel(BaseModel):
    """
    Запрос на сокращение URL

    Attributes:
        url (HttpUrl): URL для сокращения
    """

    url: HttpUrl

class ShortenedUrlCodeResponseModel(BaseModel):
    """
    Ответ с сокращенным URL
    
    Attributes:
        short_code (str): Код для сокращенного URL
    """

    short_code: str

    @field_validator("short_code", mode="before")
    @classmethod
    def validate_short_code(cls, value: str) -> str:
        if len(value) not in range(1, 21):
            raise ValueError("Некорректная длина сокращенного URL!")

        return value

class URLPairResponseModel(BaseModel):
    """
    Ответ для запроса на выдачу всех URL из базы
    
    Attributes:
        original_url (HttpUrl): Исходный URL
        short_code (str): Его сокращенная версия
    """
    original_url: HttpUrl
    short_code: str